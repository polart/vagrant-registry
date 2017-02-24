from django.apps import AppConfig


class BoxesConfig(AppConfig):
    name = 'apps.boxes'

    def ready(self):
        import apps.boxes.signals
