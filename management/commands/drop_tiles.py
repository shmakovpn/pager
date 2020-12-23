"""
tile/pager/management/commands/drop_tiles.py
Drops all tiles for specified user
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-12-23'

from typing import Optional
import sys
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from pager.models import Page, Link, Stub
User = get_user_model()


def get_user(username: str) -> Optional[User]:
    """
    Returns an instance of the Django User, or None if a user does not exist
    """
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        print(f'Error: User "{username}" does not exist')
        return None


class Command(BaseCommand):
    """
    Drop all tiles (pages, links, stubs) for specified user
    """
    help: str = """Drop all tiles (pages, links, stubs) for specified user"""

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('user', type=str)

    def handle(self, *args, **kwargs):
        username: str = kwargs['user']
        user: User = get_user(username) or sys.exit(1)
        Page.objects.filter(user=user).delete()
        Link.objects.filter(user=user).delete()
        Stub.objects.filter(user=user).delete()
