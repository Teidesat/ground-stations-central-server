# apps/imaging/apps.py
"""Django app configuration for the imaging module."""

from django.apps import AppConfig


class ImagingConfig(AppConfig):
    """Configuration class for the imaging application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.imaging'

    def ready(self):
        """Import signals when the app is ready."""
        from . import signals