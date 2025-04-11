from django.apps import AppConfig


class Analyze_ImageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analyze_image'

    def ready(self):
        from . import signals