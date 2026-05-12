# apps/control/apps.py
"""Django app configuration for the control module."""

from django.apps import AppConfig


class ControlConfig(AppConfig):
    """Configuration class for the control application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.control'

    def ready(self):
        """Perform initialization when the app is ready."""
        pass