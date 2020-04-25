#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**discover_dc.py**

This script discovers for domain controllers in domain

REQUIREMENTS:
   pip install dnspython
"""
__author__ = "shmakovpn <shmakovpn@yandex.ru>"
__date__ = "2020-03-04"

from typing import List
import re
import dns.resolver
import socket

re_ip = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
"""
Pattern to match an IPv4 address
"""


class DCHostname:
    """
    Date:
        2020-03-04
    """
    def __init__(self,
                 dc_hostname: str,
                 dc_priority: int,
                 dc_port: int = 389,
                 dns_resolver: dns.resolver.Resolver = None
                 ):
        """
        2020-03-04
        :param dc_hostname:
        :type dc_hostname: str
        :param dc_priority:
        :type dc_priority: int
        :param dc_port:
        :type dc_port: int
        :param dns_resolver:
        :type dns_resolver: dns.resolver.Resolver
        """
        self.dc_hostname: str = dc_hostname
        self.dc_priority: int = dc_priority
        self.dc_port: int = dc_port
        self.dns_resolver: dns.resolver.Resolver = dns_resolver
        self.dc_ip: str = ''

    def dc_ping(self) -> bool:
        """
        Checks that this domain controller host is available
        2020-03-04
        :return: True if this domain controller host is available
        :rtype: bool
        """
        hosts: List[str] = [getattr(self, 'dc_ip', self.dc_hostname), ]
        if not self.dc_ip and not re_ip.search(self.dc_hostname) and self.dns_resolver:
            # resolve hostname
            try:
                dns_answer: dns.resolver.Answer = self.dns_resolver.query(self.dc_hostname)
                answers: List[dns.rdtypes.IN.A.A] = list(dns_answer)
                hosts: List[str] = [answer.address for answer in answers]
            except dns.exception.DNSException as e:
                raise dns.exception.DNSException(e)
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for host in hosts:
            try:
                if sock.connect_ex((host, self.dc_port,)) == 0:
                    self.dc_ip = host
                    return True
            except socket.gaierror:
                pass
        sock.close()
        return False


class DCList:
    """
    Date:
        2020-03-04

    List of domain controllers
    """
    def __init__(self, domain: str, role: str, record_type: str = 'SRV', name_servers: List[str] = None):
        """
        2020-03-04
        :param domain:
        :type domain: str
        :param role:
        :type role: str
        :param record_type:
        :type record_type: str
        :param name_servers:
        :type name_servers: list of str
        """
        self.domain: str = domain
        self.role: str = role
        self.record_type: str = record_type
        # self.dns_resolver: dns.resolver.Resolver = dns.resolver.get_default_resolver()
        self.dns_resolver: dns.resolver.Resolver = dns.resolver.Resolver()
        self.name_servers: List[str] = name_servers
        if name_servers:
            self.dns_resolver.nameservers = name_servers

    def get_dns_query_string(self) -> str:
        """
        Creates a dns query string
        :return: dns query string
        :rtype: str
        """
        return '_ldap._tcp.%s._msdcs.%s' % (self.role, self.domain, )

    def get_dc_list(self) -> List[DCHostname]:
        """
        Returns a list of domain controllers sorted by priority
        Note: this function does not check either a domain controller is available or not
        2020-03-04
        :return: a list of domain controllers' host names from DNS request sorted by priority
        :rtype: list of DCHostname
        """
        try:
            dns_answer: dns.resolver.Answer = self.dns_resolver.query(
                self.get_dns_query_string(),
                self.record_type,
                raise_on_no_answer=True,
            )
        except dns.exception.DNSException as e:
            raise dns.exception.DNSException(e)
        answers: List[dns.rdtypes.IN.SRV.SRV] = list(dns_answer)
        answers.sort(key=lambda x: x.priority)
        return [DCHostname(
            dc_hostname='.'.join([x.decode() for x in answer.target.labels[:-1]]),
            dc_priority=answer.priority,
            dc_port=answer.port,
            dns_resolver=self.dns_resolver
        ) for answer in answers]

    def get_available_dc_ip(self) -> str:
        """
        Returns a hostname of an available domain controller or empty string
        2020-03-04
        :return: a hostname of an available domain controller or empty string
        :rtype: str
        """
        dc_hostnames: List[DCHostname] = self.get_dc_list()
        for dc_hostname in dc_hostnames:
            if dc_hostname.dc_ping():
                return dc_hostname.dc_ip
        return ''
