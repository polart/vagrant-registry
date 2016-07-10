from django.apps import AppConfig


class BoxesConfig(AppConfig):
    name = 'boxes'

    def ready(self):
        from . import signals
