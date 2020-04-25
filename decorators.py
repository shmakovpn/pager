"""
tile/pager/decorators.py
Декораторы
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2019-12-25'

from functools import wraps
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.http.request import HttpRequest


def _get_http_request_from_args(args):
    """
    Возвращает объект типа HttpRequest списка args, raises RuntimeError if an object does not exist in 'args'.
    Пояснение зачем данная функция вооюще нужна.
    Django поддерживает два типа of views: основанный на функциях и основанный на классах.
    На функциях 'def view_name(request, *args, **kwargs)' - первым аргументом будет HttpRequest
    На классах 'def get(self, request, *args, **kwargs)' - первым аргументом будет объект потомока класса View
    Чтобы обеспечить совместимость декораторов реализованных в данном файле в обоих случаях of views,
    необходим функционал для нахождения в списке переданных в view-функцию аргументов объектов HttpRequest
    :param args: Список аргументов передаваемый в view-функцию
    :return: HttpRequest
    """
    for arg in args:
        if isinstance(arg, HttpRequest):
            return arg
    raise RuntimeError(f'An error has occurred in _get_http_request_from_args. HttpRequest was not found in args')


def check_profile_exists(function):
    """
    Decorator for views that checks that the user profile is exist, raising Http404 error if necessary
    2019-12-25
    """
    @wraps(function)
    def wrapped_view(*args, **kwargs):
        username = kwargs['username']
        if not username:
            raise Http404('check_profile_exists error: required argument "username" is missed')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            raise Http404(f'check_profile_exists error: profile for user "{username}" does not exist')
        return function(*args, **kwargs)

    return wrapped_view


def check_profile_access(function):
    """
    Decorator for views that checks that the user has access to the profile, raising HttpResponseForbidden
    if necessary
    2019-12-25
    """
    @wraps(function)
    def wrapped_view(*args, **kwargs):
        username = kwargs['username']
        request = _get_http_request_from_args(args)
        if username != request.user.username:
            raise PermissionDenied(
                f'check_profile_access error: user {request.user.username} does not have access to user profile {username}')
        return function(*args, **kwargs)

    return wrapped_view

