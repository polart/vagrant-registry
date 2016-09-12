from django.apps import AppConfig


class BoxesConfig(AppConfig):
    name = 'boxes'

    def ready(self):
        import apps.boxes.signals
