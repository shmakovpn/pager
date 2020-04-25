#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**ad_tools.py**

Some tools to use

REQUIREMENTS:
   pip install python-ldap
"""
__author__ = "shmakovpn <shmakovpn@yandex.ru>"
__date__ = "2020-04-15"

import re
import ldap
import ldap.filter


from typing import TypeVar, List

domain_suffix_pattern = re.compile(r'@.*$')  #: pattern for domain suffix
domain_prefix_pattern = re.compile(r'^[^\\]*\\')  #: patter for domain prefix
LDAP_CONNECTION = TypeVar('LDAP_CONNECTION', ldap.ldapobject.SimpleLDAPObject, type(None))


def ad_clear_username(username: str) -> str:
    """
    Removes domain suffix and prefix from the username
    2020-04-15
    :param username: active directory username
    :type username: str
    :return: cleared username without domain suffix and prefix
    :rtype: str
    """
    username = domain_suffix_pattern.sub('', username)
    username = domain_prefix_pattern.sub('', username)
    return username


def ldap_conn(dc: str, username: str, password: str) -> LDAP_CONNECTION:
    """
    Inits ldap connection, binds to ldap using username and password, returns ldap connection if binding was ok
    2020-04-15
    :param dc: an ip address of domain controller
    :type dc: str
    :param username: an active directory username
    :type username: str
    :param password: an active directory user password
    :type password: str
    :return: ldap connection if binding was ok, None otherwise
    :rtype: ldap.ldapobject.SimpleLDAPObject
    """
    conn: ldap.ldapobject.SimpleLDAPObject = ldap.initialize('ldap://%s' % dc)
    # conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)
    # conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    try:
        conn.bind_s(username, password)
        return conn
    except ldap.INVALID_CREDENTIALS:
        return None
    except ldap.SERVER_DOWN:
        return None


def user_dn(conn: ldap.ldapobject.SimpleLDAPObject, username: str, domain: str) -> str:
    """
    Requests user DN from active directory by username
    :param conn: established connection to domain controller
    :type conn: ldap.ldapobject.SimpleLDAPObject
    :param username: an active directory username
    :type username: str
    :return: DN for username if success, empty string otherwise
    :param domain: full name of active directory domain
    :type domain: str
    :rtype: str
    """
    if not conn:
        return ''
    ldap_base: str = ','.join('dc=%s' % x for x in domain.split('.'))
    search_filter: str = '(|(&(objectClass=person)(sAMAccountName=%s)))' % ad_clear_username(username)
    try:
        results: List[str] = list(
            filter(lambda x: x[0] is not None, conn.search_s(ldap_base, ldap.SCOPE_SUBTREE, search_filter, ['']))
        )
        if not len(results):
            return ''
        return results[0][0]
    except ldap.OPERATIONS_ERROR:
        return ''


def dn_groups(conn: ldap.ldapobject.SimpleLDAPObject, dn: str, domain: str) -> List[str]:
    """
    Request group names from active directory by user DN
    2020-04-15
    :param conn: established connection to domain controller
    :type conn: ldap.ldapobject.SimpleLDAPObject
    :param dn: an active directory user DN
    :type dn: str
    :param domain: full name of active directory domain
    :type domain: str
    :return: list of group names whose user with DN is member of (SUCCESS), empty list otherwise
    :rtype: List[str]
    """
    if not conn:
        return []
    ldap_base: str = ','.join('dc=%s' % x for x in domain.split('.'))
    search_filter: str = '(|(&(objectClass=group)(member=%s)))' % ldap.filter.escape_filter_chars(dn)
    try:
        results: List[str] = list(
            filter(
                lambda x: x[0] is not None,
                conn.search_s(ldap_base, ldap.SCOPE_SUBTREE, search_filter, ['sAMAccountName'])
            )
        )
        return [item[1]['sAMAccountName'][0].decode() for item in results]
    except ldap.OPERATIONS_ERROR:
        return []
