# apps/audit/models.py
"""Logging and audit trail models for the satellite ground station."""

import json
import logging
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class LogLevel(models.TextChoices):
    """Standard log level enumeration."""
    DEBUG = 'DEBUG', 'Debug'
    INFO = 'INFO', 'Info'
    WARNING = 'WARNING', 'Warning'
    ERROR = 'ERROR', 'Error'
    CRITICAL = 'CRITICAL', 'Critical'


class LogQuerySet(models.QuerySet):
    """Custom queryset for LogEntry providing common filter methods."""

    def debug(self):
        """Filter logs at DEBUG level."""
        return self.filter(level=LogLevel.DEBUG)

    def info(self):
        """Filter logs at INFO level."""
        return self.filter(level=LogLevel.INFO)

    def warning(self):
        """Filter logs at WARNING level."""
        return self.filter(level=LogLevel.WARNING)

    def error(self):
        """Filter logs at ERROR level."""
        return self.filter(level=LogLevel.ERROR)

    def critical(self):
        """Filter logs at CRITICAL level."""
        return self.filter(level=LogLevel.CRITICAL)

    def errors_or_higher(self):
        """Filter logs at ERROR or CRITICAL level."""
        return self.filter(level__in=[LogLevel.ERROR, LogLevel.CRITICAL])

    def by_logger(self, logger_name: str):
        """Filter logs by logger name."""
        return self.filter(logger=logger_name)

    def by_module(self, module_name: str):
        """Filter logs by module name."""
        return self.filter(module=module_name)

    def last_hours(self, hours: int):
        """Filter logs from the last N hours."""
        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(timestamp__gte=cutoff)

    def last_days(self, days: int):
        """Filter logs from the last N days."""
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(timestamp__gte=cutoff)

    def with_exceptions(self):
        """Filter logs that contain exception information."""
        return self.filter(exception_type__isnull=False)

    def for_request(self, request_path: str):
        """Filter logs for a specific request path."""
        return self.filter(request_path=request_path)


class LogEntry(models.Model):
    """
    Centralized log entry model for the entire application.

    Provides comprehensive audit trail and debugging capabilities including
    request context, exception details, and structured extra data.
    """

    # Core log fields
    timestamp = models.DateTimeField(
        db_index=True,
        help_text="When the log entry was created"
    )
    level = models.CharField(
        max_length=10,
        choices=LogLevel.choices,
        db_index=True,
        help_text="Log severity level"
    )
    logger = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Logger name (e.g., 'ground-stations-central-server')"
    )
    module = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Source module/file name"
    )
    function = models.CharField(
        max_length=100,
        help_text="Function/method name"
    )
    message = models.TextField(
        help_text="Log message content"
    )

    # Request context (optional)
    request_method = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="HTTP method"
    )
    request_path = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Request URL path"
    )
    request_status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="HTTP response status code"
    )
    request_client_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address"
    )
    request_user = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Authenticated username"
    )

    # Exception context (optional)
    exception_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="Exception class name"
    )
    exception_message = models.TextField(
        null=True,
        blank=True,
        help_text="Exception message"
    )
    exception_stack_trace = models.TextField(
        null=True,
        blank=True,
        help_text="Full stack trace"
    )

    # Additional data
    extra_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Any additional structured data"
    )

    objects = LogQuerySet.as_manager()

    class Meta:
        """Meta configuration for LogEntry model."""
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['logger', 'timestamp']),
            models.Index(fields=['module', 'function']),
            models.Index(fields=['exception_type']),
            models.Index(fields=['request_path']),
        ]
        verbose_name = "Log Entry"
        verbose_name_plural = "Log Entries"

    def __str__(self) -> str:
        """Return string representation of the log entry."""
        return f"[{self.timestamp}] {self.level} - {self.message[:50]}"

    @property
    def is_error(self) -> bool:
        """Return True if this is an ERROR or CRITICAL level log."""
        return self.level in [LogLevel.ERROR, LogLevel.CRITICAL]

    @property
    def has_exception(self) -> bool:
        """Return True if this log contains exception information."""
        return bool(self.exception_type)

    @property
    def short_message(self) -> str:
        """Return truncated message (first 100 characters) for display."""
        return self.message[:100] + '...' if len(self.message) > 100 else self.message

    def get_extra_data(self) -> dict:
        """Return extra_data as dict, or empty dict if None."""
        return self.extra_data or {}