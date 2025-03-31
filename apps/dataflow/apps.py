from django.apps import AppConfig


class DataflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dataflow'

    def ready(self):
        from . import signals