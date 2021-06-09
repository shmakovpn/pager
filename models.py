"""
tile/pager/models.py
Модели
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2019-12-26'

from django.db import models
from django.contrib.auth.models import User
from .validators import validate_tile_path, validate_color


# Create your models here.
class TileAbstractBase(models.Model):
    """
    Базовый для всех моделей "плиток"
    2019-12-24
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=False)
    data_gs_x = models.IntegerField(default=0)
    data_gs_y = models.IntegerField(default=0)
    data_gs_width = models.IntegerField(default=2)
    data_gs_height = models.IntegerField(default=2)
    # путь к странице с элементом, по умолчанию '' - главная страница
    path = models.CharField(validators=[validate_tile_path], null=False, max_length=100, default='', blank=True)
    description = models.TextField(null=True, default='')
    # цвет фона плитки
    bgcolor = models.CharField(validators=[validate_color], max_length=6, null=False, default='', blank=True)
    # рамка
    border_right_width = models.IntegerField(null=False, default=1)
    border_left_width = models.IntegerField(null=False, default=1)
    border_top_width = models.IntegerField(null=False, default=1)
    border_bottom_width = models.IntegerField(null=False, default=1)
    border_right_color = models.CharField(validators=[validate_color], max_length=6, null=False, default='', blank=True)
    border_left_color = models.CharField(validators=[validate_color], max_length=6, null=False, default='', blank=True)
    border_top_color = models.CharField(validators=[validate_color], max_length=6, null=False, default='', blank=True)
    border_bottom_color = models.CharField(validators=[validate_color], max_length=6, null=False, default='',
                                           blank=True)

    @property
    def style_bgcolor(self):
        """
        Возвращает css стиль для поля bgcolor
        2020-02-06
        :return: string, the css style for bgcolor or empty string (if bgcolor is empty or None)
        """
        if not self.bgcolor or self.bgcolor == '':
            return ""
        return f"background-color: #{self.bgcolor};"

    @property
    def style_border_right_width(self):
        """
        Возвращает css стиль для поля border_right_width
        2020-02-10
        :return: string, the css style for border_right_width or empty string (if border_right_width is empty or None)
        """
        if self.border_right_width is None or self.border_right_width == '':
            return ''
        return f"border-right-width: {self.border_right_width}px;"

    @property
    def style_border_left_width(self):
        """
        Возвращает css стиль для поля border_left_width
        2020-02-10
        :return: string, the css style for border_left_width or empty string (if border_left_width is empty or None)
        """
        if self.border_left_width is None or self.border_left_width == '':
            return ''
        return f"border-left-width: {self.border_left_width}px;"

    @property
    def style_border_top_width(self):
        """
        Возвращает css стиль для поля border_top_width
        2020-02-10
        :return: string, the css style for border_top_width or empty string (if border_top_width is empty or None)
        """
        if self.border_top_width is None or self.border_top_width == '':
            return ''
        return f"border-top-width: {self.border_top_width}px;"

    @property
    def style_border_bottom_width(self):
        """
        Возвращает css стиль для поля border_bottom_width
        2020-02-10
        :return: string, the css style for border_bottom_width or empty string (if border_bottom_width is empty or None)
        """
        if self.border_bottom_width is None or self.border_bottom_width == '':
            return ''
        return f"border-bottom-width: {self.border_bottom_width}px;"

    @property
    def style_border_right_color(self):
        """
        Возвращает css стиль для поля border_right_color
        2020-02-10
        :return: string, the css style for border_right_color or empty string (if border_right_color is empty or None)
        """
        if not self.border_right_color or self.border_right_color == '':
            return ''
        return f"border-right-color: #{self.border_right_color};"

    @property
    def style_border_left_color(self):
        """
        Возвращает css стиль для поля border_left_color
        2020-02-10
        :return: string, the css style for border_left_color or empty string (if border_left_color is empty or None)
        """
        if not self.border_left_color or self.border_left_color == '':
            return ''
        return f"border-left-color: #{self.border_left_color};"

    @property
    def style_border_top_color(self):
        """
        Возвращает css стиль для поля border_top_color
        2020-02-10
        :return: string, the css style for border_top_color or empty string (if border_top_color is empty or None)
        """
        if not self.border_top_color or self.border_top_color == '':
            return ''
        return f"border-top-color: #{self.border_top_color};"

    @property
    def style_border_bottom_color(self):
        """
        Возвращает css стиль для поля border_bottom_color
        2020-02-10
        :return: string, the css style for border_bottom_color or empty string (if border_bottom_color is empty or None)
        """
        if not self.border_bottom_color or self.border_bottom_color == '':
            return ''
        return f"border-bottom-color: #{self.border_bottom_color};"

    class Meta:
        abstract = True


class PageLinkAbstractBase(TileAbstractBase):
    """
    Родительская модель для моделей Page и Link
    2020-02-11
    """
    title = models.CharField(max_length=100, null=False, default='')
    title_font_size = models.IntegerField(null=False, default=12)
    title_font_color = models.CharField(validators=[validate_color], max_length=6, null=False, default='', blank=True)

    @property
    def style_title_font_size(self):
        """
        Возвращает css стиль для поля title_font_size
        2020-02-11
        :return: string, the css style for title_font_size or empty string (if title_font_size is empty or None)
        """
        if self.title_font_size is None or self.title_font_size == '':
            return ''
        return f'font-size: {self.title_font_size}px;'

    @property
    def style_title_font_color(self):
        """
        Возвращает css стиль для поля title_font_color
        2020-02-11
        :return: string, the css style for title_font_color or empty string (if title_font_color is empty or None)
        """
        if not self.title_font_color or self.title_font_color == '':
            return ''
        return f'color: #{self.title_font_color};'

    class Meta:
        abstract = True


class Page(PageLinkAbstractBase):
    """
    Плитка октрывающая страницу с другими плитками
    2019-12-23
    """
    def get_full_path(self):
        """
        Возвращает полный путь к странице. {self.path}/{self.id}
        2019-12-27
        :return: string полный путь к странице
        """
        if self.path == '':
            return self.id
        return f"{self.path}/{self.id}"

    def __str__(self):
        return f"Page(id={self.id}, title='{self.title}', user={self.user}, path='{self.path}')"
    


class Link(PageLinkAbstractBase):
    """
    Плитка открывающая ссылку на внешний ресурс
    2019-12-23
    """
    url_pattern = models.CharField(max_length=500, null=False, default='')
    owner = models.CharField(max_length=100, null=True, default='')

    def __str__(self):
        return f"Link(id={self.id}, title='{self.title}', user={self.user}, path='{self.path}', url_pattern='{self.url_pattern}')"
    


class LaravelUser(models.Model):
    """
    This model
    """
    name = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255, null=True)
    active = models.CharField(max_length=255, null=False, default='1')
    password = models.CharField(max_length=60, null=False)
    fio = models.CharField(max_length=64, null=True)
    job_title = models.CharField(max_length=64, null=True)
    phone = models.CharField(max_length=64, null=True)
    remember_token = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(null=False, default='0000-00-00 00:00:00')
    updated_at = models.DateTimeField(null=False, default='0000-00-00 00:00:00')

    class Meta:
        db_table = 'users'


class Stub(TileAbstractBase):
    """
    Плитка заглушка
    2020-02-10
    """
    def __str__(self):
        return f"Stub(id={self.id}, user={self.user}, path='{self.path}')"


class DomainController(models.Model):
    """
    Модель для хранения ip адреса доступного контроллера домена
    2020-04-14
    """
    ip = models.CharField(max_length=15, null=False)

    @classmethod
    def get(cls) -> str:
        """
        Returns an ip address of Domain Controller or '' if it does not exist
        :return: an ip address of Domain Controller
        :rtype: str
        """
        try:
            return cls.objects.all()[0].ip
        except DomainController.DoesNotExist:
            return ''
        except IndexError:
            return ''

    @classmethod
    def set(cls, ip: str) -> None:
        """
        Sets the ip address of domain controller
        :param ip: an ip address of domain controller
        :return: None
        """
        cls.objects.all().delete()
        dc: DomainController = cls()
        dc.ip = ip
        dc.save()


class LocalUser(models.Model):
    """
    Пользователи, для которых включена локальная версия Плиток через Nextcloud
    2020-05-08
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, null=False)
    nextcloud_user = models.CharField(max_length=255, null=False, unique=True)
    enabled = models.BooleanField(null=False, default=True)

    def __str__(self):
        return f'{self.user.username} -> {self.nextcloud_user} {"Enabled" if self.enabled else "disabled"}'
