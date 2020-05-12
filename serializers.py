"""
pager/serializers.py
This file contains serializers for Плитки based on Django REST API
"""
__author__ = "shmakovpn <shmakovpn@yandex.ru>"
__date__ = "2020-05-08"

from rest_framework import serializers
from .models import *


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'


class LocalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalUser
        fields = '__all__'




