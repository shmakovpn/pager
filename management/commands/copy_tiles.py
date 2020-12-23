"""
tile/pager/management/commands/copy_tiles.py
Copy tiles from user to another
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-12-22'

from typing import Optional, List
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

def step(from_user: User, to_user: User, from_path: Optional[str]='', to_path: Optional[str]=''):
    """ Copies tiles from one user to another for single path level """
    from_path = from_path or ''
    to_path = to_path or ''
    pages: List[Page] = Page.objects.filter(user=from_user, path=from_path)
    links: List[Link] = Link.objects.filter(user=from_user, path=from_path)
    stubs: List[Stub] = Stub.objects.filter(user=from_user, path=from_path)
    for page in pages:
        page_path: str = page.get_full_path()
        page.pk = None
        page.user = to_user
        page.path = to_path
        page.save()
        step(from_user, to_user, page_path, page.get_full_path())
    for link in links:
        link.pk = None
        link.user = to_user
        link.path = to_path
        link.save()
    for stub in stubs:
        stub.pk = None
        stub.user = to_user
        stub.path = to_path
        stub.save()

class Command(BaseCommand):
    """
    Copies tiles (pages, links, stubs) from one user to another
    """
    help: str = """Copies tiles (pages, links, stubs) from one user to another"""

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('from_user', type=str)
        parser.add_argument('to_user', type=str)


    def handle(self, *args, **kwargs):
        from_username: str = kwargs['from_user']
        from_user: User = get_user(from_username) or sys.exit(1)
        to_username: str = kwargs['to_user']
        to_user: User = get_user(to_username) or sys.exit(1)
        step(from_user, to_user)
