# apps/audit/apps.py
"""Django app configuration for the audit module."""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Configuration class for the audit application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'