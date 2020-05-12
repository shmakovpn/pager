"""
tile/pager/urls.py
Плиточный сервер - диспетчер url
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2019-12-19'


from django.urls import path, reverse_lazy
from django.conf import settings
from django.views.generic.base import RedirectView

from rest_framework.authtoken import views
from rest_framework_swagger.views import get_swagger_view

from django.urls.converters import register_converter
from .converters import *

# import views
from .views import *
# import api views
from .apiviews import *

register_converter(TilePathConverter, 'tile_path')
register_converter(DomainUserConverter, 'domain_user')

schema_view = get_swagger_view(title='Tiles Server API')
app_name = __package__

urlpatterns = [
    # index
    path('', IndexView.as_view(), name='index'),
    # login
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # profile
    path('profile/<tile_path:tile_path><domain_user:username>.html', ProfileView.as_view(), name='profile'),
    # api list of user pages
    path('api/pages/<int:userid>/', ListUserPages.as_view(), name='list_pages'),
    # api list of local user для которых включена локальная версия в Nextcloud
    path('api/users/', ListLocalUsers.as_view(), name='list_users'),
    # local view for particular page
    path('local/<tile_path:tile_path><domain_user:username>.html', LocalProfileView.as_view(), name='local'),
    # settings
    path('settings/', SettingsView.as_view(), name='settings'),
    # swagger
    path('swagger/', schema_view),
    # test laravel users
    path('test/', TestLaravelUser.as_view(), name='laravel'),
]

#urlpatterns += staticfiles_urlpatterns()