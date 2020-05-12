"""
pager/apiviews.py
This file contains views for Плитки based on Django REST API
"""
__author__ = "shmakovpn <shmakovpn@yandex.ru>"
__date__ = "2020-05-08"

import os
import mimetypes
from django.urls import reverse_lazy

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.http import http_date
from django.views.static import was_modified_since
from django.http import HttpResponse, Http404, HttpResponseNotModified
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
