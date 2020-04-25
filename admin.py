"""
tile/pager/admin.py
Модели админки
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2019-12-26'

from django.contrib import admin
from .models import *


class TileAbstractBaseAdmin(admin.ModelAdmin):
    """
    Базовый класс для создания элементов управления в админке для плиток
    2019-12-24
    """
    list_display = ('user', 'title', 'path', 'data_gs_x', 'data_gs_y', 'data_gs_width', 'data_gs_height',)
    search_fields = ('title', 'user__username', )

    class Meta:
        abstract = True


class PageAdmin(TileAbstractBaseAdmin):
    """
    Элемент управления модели Page для админки
    2019-12-24
    """
    pass


class LinkAdmin(TileAbstractBaseAdmin):
    """
    Элемент управления модели Link для админки
    2019-12-24
    """
    list_display = TileAbstractBaseAdmin.list_display + ('url_pattern', )
    search_fields = TileAbstractBaseAdmin.search_fields + ('url_pattern', )


# Register your models here.
admin.site.register(Page, PageAdmin)
admin.site.register(Link, LinkAdmin)
