# apps/control/managers.py
"""Custom managers and querysets for core control models."""

from datetime import timedelta
from typing import Optional, List

from django.db import models
from django.db.models import Q
from django.utils import timezone


class TelemetryQuerySet(models.QuerySet):
    """QuerySet for TelemetryMessage with common filter methods."""

    def valid(self):
        """Filter only valid telemetry readings."""
        return self.filter(valid=True)

    def invalid(self):
        """Filter invalid telemetry readings."""
        return self.filter(valid=False)

    def by_subsystem(self, subsystem: str):
        """Filter by subsystem name."""
        return self.filter(subsystem=subsystem)

    def by_module(self, module: str):
        """Filter by module name (case-insensitive exact match)."""
        return self.filter(module__iexact=module)

    def last_hours(self, hours: int):
        """Filter telemetry records from the last N hours."""
        cutoff = timezone.now() - timedelta(hours=hours)
        return self.filter(timestamp__gte=cutoff)

    def value_range(self, min_val: float, max_val: float):
        """Filter telemetry records within a value range."""
        return self.filter(value__gte=min_val, value__lte=max_val)


class TelemetryManager(models.Manager):
    """Manager for TelemetryMessage providing extended query methods."""

    def get_queryset(self):
        """Return the custom TelemetryQuerySet."""
        return TelemetryQuerySet(self.model, using=self._db)

    def valid(self):
        """Return only valid telemetry readings."""
        return self.get_queryset().valid()

    def by_subsystem(self, subsystem: str):
        """Filter by subsystem name."""
        return self.get_queryset().by_subsystem(subsystem)

    def last_hours(self, hours: int):
        """Return telemetry records from the last N hours."""
        return self.get_queryset().last_hours(hours)

    def last_telemetry(self, subsystem: Optional[str] = None, limit: int = 10):
        """Return the latest valid telemetry readings."""
        qs = self.get_queryset().valid()
        if subsystem:
            qs = qs.by_subsystem(subsystem)
        return qs[:limit]

    def average_value(self, subsystem: str, module: str, hours: int = 24) -> Optional[float]:
        """Calculate the average value for a specific metric over time.

        Args:
            subsystem: The subsystem name.
            module: The module/metric name.
            hours: Time window in hours.

        Returns:
            Average value as float, or None if no data found.
        """
        qs = self.get_queryset().valid().by_subsystem(subsystem).by_module(module)
        qs = qs.last_hours(hours)
        return qs.aggregate(models.Avg('value'))['value__avg']


class CommandQuerySet(models.QuerySet):
    """QuerySet for CommandMessage with common filter methods."""

    def pending(self):
        """Return commands that have not yet been executed."""
        from .models import CommandStatus
        return self.filter(status__in=[CommandStatus.SENT, CommandStatus.RECEIVED, CommandStatus.ACCEPTED])

    def executed(self):
        """Return successfully executed commands."""
        from .models import CommandStatus
        return self.filter(status=CommandStatus.EXECUTED)

    def failed(self):
        """Return failed commands."""
        from .models import CommandStatus
        return self.filter(status=CommandStatus.FAILED)

    def by_type(self, command_type: str):
        """Filter by command type."""
        return self.filter(command_type=command_type)


class CommandManager(models.Manager):
    """Manager for CommandMessage providing extended query methods."""

    def get_queryset(self):
        """Return the custom CommandQuerySet."""
        return CommandQuerySet(self.model, using=self._db)

    def pending(self):
        """Return all pending commands."""
        return self.get_queryset().pending()

    def get_statistics(self) -> dict:
        """Return command execution statistics.

        Returns:
            Dictionary with total, executed, failed, pending counts and success rate.
        """
        total = self.count()
        executed = self.get_queryset().executed().count()
        failed = self.get_queryset().failed().count()
        pending = self.get_queryset().pending().count()

        return {
            'total': total,
            'executed': executed,
            'failed': failed,
            'pending': pending,
            'success_rate': (executed / total * 100) if total > 0 else 0
        }


class EventQuerySet(models.QuerySet):
    """QuerySet for EventMessage with common filter methods."""

    def critical(self):
        """Filter critical severity events."""
        from .models import EventSeverity
        return self.filter(severity=EventSeverity.CRITICAL)

    def warnings(self):
        """Filter warning severity events."""
        from .models import EventSeverity
        return self.filter(severity=EventSeverity.WARNING)

    def info(self):
        """Filter info severity events."""
        from .models import EventSeverity
        return self.filter(severity=EventSeverity.INFO)

    def by_subsystem(self, subsystem: str):
        """Filter by subsystem name."""
        return self.filter(subsystem=subsystem)

    def last_hours(self, hours: int):
        """Filter events from the last N hours."""
        cutoff = timezone.now() - timedelta(hours=hours)
        return self.filter(timestamp__gte=cutoff)


class EventManager(models.Manager):
    """Manager for EventMessage providing extended query methods."""

    def get_queryset(self):
        """Return the custom EventQuerySet."""
        return EventQuerySet(self.model, using=self._db)

    def critical(self):
        """Return critical severity events."""
        return self.get_queryset().critical()

    def get_recent_alerts(self, limit: int = 50):
        """Return recent critical and warning events.

        Args:
            limit: Maximum number of alerts to return.

        Returns:
            QuerySet of recent alerts limited to the specified count.
        """
        from .models import EventSeverity

        return self.get_queryset().filter(
            Q(severity=EventSeverity.CRITICAL) | Q(severity=EventSeverity.WARNING)
        )[:limit]