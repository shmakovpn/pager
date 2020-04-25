"""
tile/pager/validators/py
Валидаторы полей моделей
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2019-12-27'

import re
from django.core.exceptions import ValidationError


def validate_tile_path(value):
    """
    Validator for Page.path and Link.path fields, raises Validation error if value is not valid
    2019-12-27
    :param value: value of the field
    :return: None
    """
    if value == '':
        return
    regex = re.compile(r'^((\d+\/)*\d+)?$')
    if not regex.match(value):
        raise ValidationError(f'"{value}" is not a valid tile path')
    parts = value.split('/')
    previous = int(parts.pop(0))
    for part in parts:
        part = int(part)
        if part <= previous:
            raise ValidationError(f'"{value}" is not a valid tile path, order must be like min/more/even more/max')
        previous = part


def validate_color(value):
    """
    Validator for Page.bgcolor and Link.bgcolor fields, raises Validation error if value is not valid
    2020-02-06
    :param value: value of the field
    :return: None
    """
    if not value or value == '':
        return
    regex = re.compile(r'\d{6}')
    if not regex.match(value):
        raise ValidationError(f'"{value}" is not a valid color')
