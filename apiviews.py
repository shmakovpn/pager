"""
pager/apiviews.py
This file contains views for Плитки based on Django REST API
"""
__author__ = "shmakovpn <shmakovpn@yandex.ru>"
__date__ = "2020-05-08"

import os
import json
import mimetypes
from django.urls import reverse, reverse_lazy
from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.http import http_date
from django.views.static import was_modified_since
from django.http import HttpResponse, Http404, HttpResponseNotModified, HttpResponseBadRequest
from django.db.models import Q
from .models import *
from django.conf import settings
from .serializers import *


class TileApiView(APIView):
    """
    Parent view class for all Tile Api Views API views 2020-05-08
    """
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)


class ListUserPages(TileApiView):
    """
    Returns a list of all Pages of a User in JSON format 2020-05-08
    """
    def get(self, request, userid, *args, **kwargs):
        """
        Returns a list of all Pages of a User in JSON format 2020-05-08
        :param request: rest framework request
        :return: rest framework response
        """
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            raise Http404(f'Request error. Profile id="{userid}" does not exist')
        pages = Page.objects.filter(user=user)
        data = PageSerializer(pages, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class ListLocalUsers(TileApiView):
    """
    Список пользователей для которых включена локальная версия в Nextcloud
    """
    def get(self, request, *args, **kwargs):
        """
        Возвращаяе список пользователей для которых включена локальная версия в Nextcloud
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        local_users = LocalUser.objects.filter(enabled=True)
        data = LocalUserSerializer(local_users, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class LocalPage(TileApiView):
    @staticmethod
    def _get_template(template_name):
        """
        Returns template name with package
        2019-12-20
        :param template_name: string, template_name without package name
        :return: full template name with package
        """
        return f'{__package__}/{template_name}'

    def _render_template(self, request, template_name) -> HttpResponse:
        """
        Returns HttpResponse by rendering django template
        :param request: http request
        :param template_name: string, template_name withot package name
        :return: HttpResponse
        """
        response: HttpResponse = render(request, self._get_template(template_name=template_name), self.context)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = {'package': __package__}

    def get(self, request, userid, tile_path):
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist as e:
            raise Http404(f'Request error. Profile id="{userid}" does not exist')
        self.context['username'] = user.username
        self.context['root_level'] = ''  # уровень относительно корня
        if tile_path != '':
            self.context['breadcrumbs'] = {}  # показывать хлебные крошки
            tile_path = tile_path.strip('/')  # отрезаем / от конца строки tile_path
            tile_path_ar = tile_path.split('/')  # разбиваем tile_path разделителем /
            parent_pages = []
            for parent_page_id in tile_path_ar:
                self.context['root_level'] += '../'
                try:
                    parent_page = Page.objects.get(id=int(parent_page_id))
                    if user.username != parent_page.user.username:
                        response = {
                            'success': False,
                            'error': f'Request error, parent object Page with id="{parent_page_id}" belongs to another user',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
                    parent_pages.append(parent_page)
                except Page.DoesNotExist:
                    raise Http404(
                        f'Request error. Parent Page for path="{tile_path}" with id="{parent_page_id}" does not exist')
            self.context['breadcrumbs']['last'] = parent_pages.pop().title
            self.context['breadcrumbs']['items'] = []
            len_broadcrumbs = len(parent_pages)
            i = 0
            for parent_page in parent_pages:
                self.context['breadcrumbs']['items'].append({
                    'title': parent_page.title,
                    'url': '../'*(len_broadcrumbs-i)+'index.html',
                })
                i += 1
        pages = Page.objects.filter(user=user, path=tile_path)  # получаем все страницы для панели по умолчанию
        links = Link.objects.filter(user=user, path=tile_path)  # получаем все ссылки для панели по умолчанию
        stubs = Stub.objects.filter(user=user, path=tile_path)  # получаем все заглушки для панели по умолчанию
        self.context['pages'] = pages  # помещаем полученные страницы в контекст шаблона
        self.context['links'] = links  # помещаем полученные ссылки в контекст шаблона
        self.context['stubs'] = stubs  # помещаем полученные заглушки в контекст шаблона
        return self._render_template(request=request, template_name='local.html')
