# apps/bridge/apps.py
"""Django app configuration for the bridge module."""

from django.apps import AppConfig


class BridgeConfig(AppConfig):
    """Configuration class for the bridge application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bridge'