"""
tile/pager/db_routers.py
https://docs.djangoproject.com/en/dev/topics/db/multi-db/
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-02-14'


class LaravelAuthRouter:
    """
    A router to control all database operations on models in the
    LaravelAuth model.
    """
    model_names = ('laraveluser',)

    def db_for_read(self, model, **hints):
        """
        Attempts to read LaravelUser model go to laravel1 database.
        :param model:
        :param hints:
        :return:
        """
        if model._meta.model_name in self.model_names:
            return "laravel1"

    def db_for_write(self, model, **hints):
        """
        Attempts to write LaravelUser model go to laravel1 database.
        :param model:
        :param hints:
        :return:
        """
        if model._meta.model_name in self.model_names:
            return "laravel1"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model is LaravelAuth.
        :param model:
        :param hints:
        :return:
        """
        if (
                obj1._meta.model_name in self.model_names or
                obj2._meta.model_name in self.model_names
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Disallow migrations for LaravelUser model
        :param db:
        :param app_label:
        :param model_name:
        :param hints:
        :return:
        """
        if model_name in self.model_names:
            return False  # disallow migrations
        return None
