"""
tile/pager/management/commands/discover.py
Discovers Domain Controllers
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-04-14'

from django.core.management.base import BaseCommand
from pager.models import DomainController
from pager.dns.discover_dc import DCList
from django.conf import settings
from typing import List

role: str = getattr(settings, 'DC_ROLE', 'dc')  #: domain controller server role
domain: str = getattr(settings, 'DC_DOMAIN', 'shmakovpn.ru')  #: ad realm
nameservers: List[str] = getattr(settings, 'DC_NAMESERVERS', ['192.168.58.101', ])  #: list of ip of dns servers


class Command(BaseCommand):
    """
    Discovers Domain Controllers, saves found controller into DomainController model
    2020-04-14
    """
    help = """Discovers Domain Controllers, saves found controller into DomainController model"""

    def handle(self, *args, **kwargs):
        """
        Perform dns requests
        :param args:
        :param kwargs:
        :return:
        """
        ip: str = DCList(domain=domain, role=role, name_servers=nameservers).get_available_dc_ip()
        DomainController.set(ip)
