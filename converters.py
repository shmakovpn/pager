"""
tile/pager/converters.py
URL-конвертеры
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2019-12-26'

from django.urls.converters import StringConverter


class TilePathConverter(StringConverter):
    """
    URL-converter determines path to particular page like page_id_1/page_id_2/../page_id_n
    2019-12-26
    """
    regex = r'(\d+\/)*'


class DomainUserConverter(StringConverter):
    """
    user@domain converter
    2019-12-26
    """
    regex = r'([-a-zA-Z0-9_.@]+)'
