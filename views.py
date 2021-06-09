"""
tile/pager/views.py
Views
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2019-12-26'

import json
import bcrypt  # needs to check password in LaravelUser model
from pager.ad.ad_tools import ldap_conn, user_dn, dn_groups
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, login
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.conf import settings
from .models import *
from .decorators import *
# for sphinx docs supporting
from django.core.handlers.wsgi import WSGIRequest


# Create your views here.
class AbstractBaseView(View):
    """
    Abstract parent class for Index views
    """
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


class IndexView(LoginRequiredMixin, AbstractBaseView):
    """
    Redirects to profile page or to login page
    2019-12-20
    """
    login_url = reverse_lazy(f'{__package__}:login')
    redirect_field_name = None

    def get(self, request, ):
        """
        Index view with gridstackjs
        :param request:
        :return: HttpResponse
        """
        return redirect(reverse(f'{__package__}:profile', kwargs={'username': request.user, 'tile_path': ''}))


# class LocalProfileView(AbstractBaseView):
#     """
#     User profile page for local usage
#     2020-04-09
#     """
#     def get(self, request: WSGIRequest, username: str, tile_path: str) -> HttpResponse:
#         print(f"request host={request.get_host()}:{request.get_port()}")
#         return HttpResponse("Hello from LocalProfileView")


class ProfileView(LoginRequiredMixin, AbstractBaseView):
    """
    User profile page
    Opens default user tiles page
    2019-12-23
    """
    login_url = reverse_lazy(f'{__package__}:login')
    redirect_field_name = None

    @check_profile_exists
    @check_profile_access
    def get(self, request, username, tile_path):
        """
        User profile page
        2019-12-25
        :param request:
        :param username: имя пользователя чей профиль будет отображен
        :param tile_path: путь к отображаемой странице
        :return: HttpResponse
        """
        self.context['username'] = username
        if tile_path != '':
            self.context['breadcrumbs'] = {}  # показывать хлебные крошки
            tile_path = tile_path.strip('/')  # отрезаем / от конца строки tile_path
            tile_path_ar = tile_path.split('/')  # разбиваем tile_path разделителем /
            parent_pages = []
            for parent_page_id in tile_path_ar:
                try:
                    parent_page = Page.objects.get(id=int(parent_page_id))
                    if username != parent_page.user.username:
                        response = {
                            'success': False,
                            'error': f'Request error, parent object Page with id="{parent_page.id}" belongs to another user',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
                    parent_pages.append(parent_page)
                except Page.DoesNotExist:
                    raise Http404(f'Request error. Parent Page for path="{tile_path}" with id="{parent_page.id}" does not exist')
            self.context['breadcrumbs']['last'] = parent_pages.pop().title
            self.context['breadcrumbs']['items'] = []
            for parent_page in parent_pages:
                self.context['breadcrumbs']['items'].append({
                    'title': parent_page.title,
                    'url': reverse(f'{__package__}:profile', kwargs={
                        'username': username,
                        'tile_path': f'{parent_page.get_full_path()}/',
                    }),
                })
        user = User.objects.get(username=username)  # пользователь, чья страница открывается
        pages = Page.objects.filter(user=user, path=tile_path)  # получаем все страницы для панели по умолчанию
        links = Link.objects.filter(user=user, path=tile_path)  # получаем все ссылки для панели по умолчанию
        stubs = Stub.objects.filter(user=user, path=tile_path)  # получаем все заглушки для панели по умолчанию
        self.context['pages'] = pages  # помещаем полученные страницы в контекст шаблона
        self.context['links'] = links  # помещаем полученные ссылки в контекст шаблона
        self.context['stubs'] = stubs  # помещаем полученные заглушки в контекст шаблона
        return self._render_template(request=request, template_name='profile.html')

    @check_profile_exists
    @check_profile_access
    def post(self, request, username, tile_path):
        """
        User profile page and save changes
        2019-12-25
        :param request:
        :param username:
        :return: HttpResponse
        """
        if tile_path != '':
            tile_path = tile_path.strip('/')  # отрезаем / от конца строки tile_path
            tile_path_ar = tile_path.split('/')  # разбиваем tile_path разделителем /
            try:
                parent_page = Page.objects.get(id=int(tile_path_ar.pop()), path='/'.join(tile_path_ar))
                if username != parent_page.user.username:
                    response = {
                        'success': False,
                        'error': f'Request error, parent object Page with path="{parent_page.path}" and id="{parent_page.id}" belongs to another user',
                    }
                    return HttpResponseBadRequest(json.dumps(response))
            except Page.DoesNotExist:
                raise Http404(f'Request error. Parent Page for path="{tile_path}" does not exist')
        user = User.objects.get(username=username)  # пользователь, чья страница открывается
        body_str = request.body.decode('utf8')
        try:
            body = json.loads(body_str)
        except json.decoder.JSONDecodeError as e:
            response = {
                'success': False,
                'error': f'Request body JSON decode error: "{str(e)}"',
            }
            return HttpResponseBadRequest(json.dumps(response))
        try:
            # проверка на наличие только поддерживаемых типов плиток page и link, до выполнения транзакций
            for tile in body['insert']+body['update']+body['delete']:
                if tile['type'] != 'page' and tile['type'] != 'link' and tile['type'] != 'stub':
                    response = {
                        'success': False,
                        'error': f'Request body error: unsupported type "{tile["type"]}" of tile',
                    }
                    return HttpResponseBadRequest(json.dumps(response))
            # добавление плиток
            for tile in body['insert']:
                if tile['type'] == 'page':
                    page = Page(user=user,
                                data_gs_x=tile['x'],
                                data_gs_y=tile['y'],
                                data_gs_width=tile['width'],
                                data_gs_height=tile['height'],
                                title=tile['title'],
                                path=tile_path,
                                description=tile['description'],
                                bgcolor=tile['bgcolor'],
                                border_right_width=tile['border_right_width'],
                                border_left_width=tile['border_left_width'],
                                border_top_width=tile['border_top_width'],
                                border_bottom_width=tile['border_bottom_width'],
                                border_right_color=tile['border_right_color'],
                                border_left_color=tile['border_left_color'],
                                border_top_color=tile['border_top_color'],
                                border_bottom_color=tile['border_bottom_color'],
                                title_font_size=tile['title_font_size'],
                                title_font_color=tile['title_font_color'],
                    )
                    page.save()
                elif tile['type'] == 'link':
                    link = Link(user=user,
                                data_gs_x=tile['x'],
                                data_gs_y=tile['y'],
                                data_gs_width=tile['width'],
                                data_gs_height=tile['height'],
                                title=tile['title'],
                                url_pattern=tile['url_pattern'],
                                path=tile_path,
                                description=tile['description'],
                                bgcolor=tile['bgcolor'],
                                border_right_width=tile['border_right_width'],
                                border_left_width=tile['border_left_width'],
                                border_top_width=tile['border_top_width'],
                                border_bottom_width=tile['border_bottom_width'],
                                border_right_color=tile['border_right_color'],
                                border_left_color=tile['border_left_color'],
                                border_top_color=tile['border_top_color'],
                                border_bottom_color=tile['border_bottom_color'],
                                title_font_size=tile['title_font_size'],
                                title_font_color=tile['title_font_color'],
                                owner=tile['owner'],
                    )
                    link.save()
                elif tile['type'] == 'stub':
                    stub = Stub(user=user,
                                data_gs_x=tile['x'],
                                data_gs_y=tile['y'],
                                data_gs_width=tile['width'],
                                data_gs_height=tile['height'],
                                path=tile_path,
                                description=tile['description'],
                                bgcolor=tile['bgcolor'],
                                border_right_width=tile['border_right_width'],
                                border_left_width=tile['border_left_width'],
                                border_top_width=tile['border_top_width'],
                                border_bottom_width=tile['border_bottom_width'],
                                border_right_color=tile['border_right_color'],
                                border_left_color=tile['border_left_color'],
                                border_top_color=tile['border_top_color'],
                                border_bottom_color=tile['border_bottom_color'], )
                    stub.save()
            # обновление плиток
            for tile in body['update']:
                if tile['type'] == 'page':
                    try:
                        page = Page.objects.get(id=tile['id'])
                        if page.path != tile_path:
                            response = {
                                'success': False,
                                'error': f'Request error, object Page with id="{tile["id"]}" has path="{page.path}" differ than "{tile["path"]}"'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        if page.user.username != username:
                            response = {
                                'success': False,
                                'error': f'Request error, object Page with id="{tile["id"]}" belongs to another user'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        page.data_gs_x = tile['x']
                        page.data_gs_y = tile['y']
                        page.data_gs_width = tile['width']
                        page.data_gs_height = tile['height']
                        page.title = tile['title']
                        page.description = tile['description']
                        page.bgcolor = tile['bgcolor']
                        page.border_right_width = tile['border_right_width']
                        page.border_left_width = tile['border_left_width']
                        page.border_top_width = tile['border_top_width']
                        page.border_bottom_width = tile['border_bottom_width']
                        page.border_right_color = tile['border_right_color']
                        page.border_left_color = tile['border_left_color']
                        page.border_top_color = tile['border_top_color']
                        page.border_bottom_color = tile['border_bottom_color']
                        page.title_font_size = tile['title_font_size']
                        page.title_font_color = tile['title_font_color']
                        page.save()
                    except Page.DoesNotExist as e:
                        response = {
                            'success': False,
                            'error': f'Request error, object Page with id="{tile["id"]}" does not exist in database: {str(e)}',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
                elif tile['type'] == 'link':
                    try:
                        link = Link.objects.get(id=tile['id'])
                        if link.path != tile_path:
                            response = {
                                'success': False,
                                'error': f'Request error, object Link with id="{tile["id"]}" has path="{link.path}" differ than "{tile["path"]}"'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        if link.user.username != username:
                            response = {
                                'success': False,
                                'error': f'Request error, object Link with id="{tile["id"]}" belongs to another user'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        link.data_gs_x = tile['x']
                        link.data_gs_y = tile['y']
                        link.data_gs_width = tile['width']
                        link.data_gs_height = tile['height']
                        link.title = tile['title']
                        link.url_pattern = tile['url_pattern']
                        link.description = tile['description']
                        link.bgcolor = tile['bgcolor']
                        link.border_right_width = tile['border_right_width']
                        link.border_left_width = tile['border_left_width']
                        link.border_top_width = tile['border_top_width']
                        link.border_bottom_width = tile['border_bottom_width']
                        link.border_right_color = tile['border_right_color']
                        link.border_left_color = tile['border_left_color']
                        link.border_top_color = tile['border_top_color']
                        link.border_bottom_color = tile['border_bottom_color']
                        link.title_font_size = tile['title_font_size']
                        link.title_font_color = tile['title_font_color']
                        link.owner = tile['owner']
                        link.save()
                    except Page.DoesNotExist as e:
                        response = {
                            'success': False,
                            'error': f'Request error, object Link with id="{tile["id"]}" does not exist in database: {str(e)}',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
                elif tile['type'] == 'stub':
                    try:
                        stub = Stub.objects.get(id=tile['id'])
                        if stub.path != tile_path:
                            response = {
                                'success': False,
                                'error': f'Request error, object Stub with id="{tile["id"]}" has path="{stub.path}" differ than "{tile["path"]}"'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        if stub.user.username != username:
                            response = {
                                'success': False,
                                'error': f'Request error, object Stub with id="{tile["id"]}" belongs to another user'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        stub.data_gs_x = tile['x']
                        stub.data_gs_y = tile['y']
                        stub.data_gs_width = tile['width']
                        stub.data_gs_height = tile['height']
                        stub.description = tile['description']
                        stub.bgcolor = tile['bgcolor']
                        stub.border_right_width = tile['border_right_width']
                        stub.border_left_width = tile['border_left_width']
                        stub.border_top_width = tile['border_top_width']
                        stub.border_bottom_width = tile['border_bottom_width']
                        stub.border_right_color = tile['border_right_color']
                        stub.border_left_color = tile['border_left_color']
                        stub.border_top_color = tile['border_top_color']
                        stub.border_bottom_color = tile['border_bottom_color']
                        stub.save()
                    except Page.DoesNotExist as e:
                        response = {
                            'success': False,
                            'error': f'Request error, object Stub with id="{tile["id"]}" does not exist in database: {str(e)}',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
            # удаление плиток
            for tile in body['delete']:
                if tile['type'] == 'page':
                    try:
                        page = Page.objects.get(id=tile['id'])
                        if page.path != tile_path:
                            response = {
                                'success': False,
                                'error': f'Request error, object Page with id="{tile["id"]}" has path="{page.path}" deffer than "{tile["path"]}"'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        if page.user.username != username:
                            response = {
                                'success': False,
                                'error': f'Request error, object Page with id="{tile["id"]}" belongs to another user',
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        if tile['path'] == '':
                            Page.objects.filter(user=user, path__startswith=f"{tile['id']}").delete()
                            Link.objects.filter(user=user, path__startswith=f"{tile['id']}").delete()
                            Stub.objects.filter(user=user, path__startswith=f"{tile['id']}").delete()
                        else:
                            Page.objects.filter(user=user, path__startswith=f"{tile['path']}/{tile['id']}").delete()
                            Link.objects.filter(user=user, path__startswith=f"{tile['path']}/{tile['id']}").delete()
                            Stub.objects.filter(user=user, path__startswith=f"{tile['path']}/{tile['id']}").delete()
                        page.delete()
                    except Page.DoesNotExist as e:
                        response = {
                            'success': False,
                            'error': f'Request error, object Page with id="{tile["id"]}" does not exist in database: {str(e)}',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
                elif tile['type'] == 'link':
                    try:
                        link = Link.objects.get(id=tile['id'])
                        if link.path != tile_path:
                            response = {
                                'success': False,
                                'error': f'Request error, object Link with id="{tile["id"]}" has path="{link.path}" deffer than "{tile["path"]}"'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        if link.user.username != username:
                            response = {
                                'success': False,
                                'error': f'Request error, object Link with id="{tile["id"]}" belongs to another user',
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        link.delete()
                    except Page.DoesNotExist as e:
                        response = {
                            'success': False,
                            'error': f'Request error, object Link with id="{tile["id"]}" does not exist in database: {str(e)}',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
                elif tile['type'] == 'stub':
                    try:
                        stub = Stub.objects.get(id=tile['id'])
                        if stub.path != tile_path:
                            response = {
                                'success': False,
                                'error': f'Request error, object Stub with id="{tile["id"]}" has path="{stub.path}" differ than "{tile["path"]}"'
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        if stub.user.username != username:
                            response = {
                                'success': False,
                                'error': f'Request error, object Stub with id="{tile["id"]}" belongs to another user',
                            }
                            return HttpResponseBadRequest(json.dumps(response))
                        stub.delete()
                    except Page.DoesNotExist as e:
                        response = {
                            'success': False,
                            'error': f'Request error, object Stub with id="{tile["id"]}" does not exist in database: {str(e)}',
                        }
                        return HttpResponseBadRequest(json.dumps(response))
        except KeyError as e:
            response = {
                'success': False,
                'error': f'Request body format error, key does not exist: "{str(e)}"',
            }
            return HttpResponseBadRequest(json.dumps(response))
        return HttpResponse(json.dumps({'success': True}))


class SettingsView(LoginRequiredMixin, AbstractBaseView):
    """
    Страница настроек пользователя
    2019-12-27
    """
    def get(self, request, ):
        """
        Страница настроек пльзователя
        :param request: HttpRequest
        :return: HttpResponse
        """
        self.context['users'] = []
        users = User.objects.all()
        for user in users:
            if user.username == request.user.username:
                continue
            self.context['users'].append(user)
        return self._render_template(request=request, template_name='settings.html')


class LoginView(AbstractBaseView):
    """
    Login page
    2019-12-23
    """
    def get(self, request, ):
        """
        Show login page
        :param request:
        :return: HttpResponse
        """
        return self._render_template(request=request, template_name='login.html')

    def post(self, request, ):
        if 'username' in request.POST and 'password' in request.POST:
            msg = f'username={request.POST["username"]} password={request.POST["password"]}'
            user = authenticate(request=request, username=request.POST['username'], password=request.POST['password'])
            if user:
                print(f'local auth {msg}')
                login(request=request, user=user)
                return redirect(reverse(f'{__package__}:index'))
            else:
                try:
                    laravel_user = LaravelUser.objects.get(name=request.POST['username'])
                    laravel_password = laravel_user.password.encode()
                    if bcrypt.checkpw(request.POST['password'].encode(), laravel_password):
                        print(f'laravel auth {msg}')
                        user, created = User.objects.get_or_create(username=request.POST['username'])
                        user.set_password(request.POST['password'])
                        user.email = laravel_user.email
                        user.save()
                        login(request=request, user=user)
                        return redirect(reverse(f'{__package__}:index'))
                except LaravelUser.DoesNotExist:
                    if '@' in request.POST['username']:
                        dc: str = DomainController.get()
                        if dc:
                            msg = f'{msg} dc={dc}'
                            conn = ldap_conn(dc, request.POST['username'], request.POST['password'])
                            if conn:
                                domain: str = getattr(settings, 'DC_DOMAIN', '')
                                if domain:
                                    msg = f'{msg} domain={domain}'
                                    valid_group: str = getattr(settings, 'DC_GROUP', '')
                                    if valid_group:
                                        msg = f'{msg} valid_group={valid_group}'
                                        dn: str = user_dn(conn, request.POST['username'], domain)
                                        if dn:
                                            msg = f'{msg} dn={dn}'
                                            if valid_group in dn_groups(conn, dn, domain):
                                                user, created = User.objects.get_or_create(
                                                    username=request.POST['username'])
                                                user.set_password(request.POST['password'])
                                                user.save()
                                                login(request=request, user=user)
                                                return redirect(reverse(f'{__package__}:index'))
                                            else:
                                                print(f'AD auth failed. Valid_group is not in dn_groups: {dn_groups(conn, dn, domain)}; {msg}')
                                        else:
                                            print(f'AD auth failed. DN retrieving failed {msg}')
                                    else:
                                        print(f'AD auth failed, DC_GROUP setting not set. {msg}')
                                else:
                                    print(f'AD auth failed, DC_DOMAIN setting not set. {msg}')
                            else:
                                print(f'AD auth failed, ldap_conn failed {msg}')
                        else:
                            print(f'AD auth failed, DomainController.get() failed {msg}')
                    else:
                        print(f'local and laravel and AD auths failed {msg}')
        self.context['login_failed'] = True
        return self._render_template(request=request, template_name='login.html')


class LogoutView(AbstractBaseView):
    """
    Logout page
    2019-12-23
    """
    def get(self, request, ):
        """
        Performs logout
        :param request:
        :return: HttpResponse
        """
        logout(request)  # выполняем выход пользователя
        return redirect(reverse(f'{__package__}:index'))


class TestLaravelUser(View):
    def get(self, request, ):
        laravel_users = LaravelUser.objects.all()
        out = "<table>"
        for laravel_user in laravel_users:
            out += "<tr>"
            out += f"<td>{laravel_user.id}</td>"
            out += f"<td>{laravel_user.name}</td>"
            out += f"<td>{laravel_user.email}</td>"
            out += f"<td>{laravel_user.active}</td>"
            out += f"<td>{laravel_user.password}</td>"
            out += f"<td>{laravel_user.fio}</td>"
            out += f"<td>{laravel_user.job_title}</td>"
            out += f"<td>{laravel_user.phone}</td>"
            out += f"<td>{laravel_user.remember_token}</td>"
            out += f"<td>{laravel_user.created_at}</td>"
            out += f"<td>{laravel_user.updated_at}</td>"
            out += "</tr>"
        out += "</table>"
        return HttpResponse(out)

