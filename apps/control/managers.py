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
    
class SoftwareUpdateQuerySet(models.QuerySet):
    """QuerySet for SoftwareUpdate with common filter methods."""
    
    def by_version(self, version: str):
        """Filter by version."""
        return self.filter(version=version)
    
    def by_date(self, date):
        """Filter by uploaded date (date object or string YYYY-MM-DD)."""
        if isinstance(date, str):
            from datetime import datetime
            date = datetime.strptime(date, '%Y-%m-%d').date()
        return self.filter(uploaded_at__date=date)
    
    def by_status(self, verified: bool):
        """Filter by verification status."""
        return self.filter(verified=verified)
    
    def verified(self):
        """Return only verified updates."""
        return self.filter(verified=True)
    
    def pending(self):
        """Return only pending (unverified) updates."""
        return self.filter(verified=False)
    
    def last(self):
        """Return the most recent update."""
        return self.order_by('-uploaded_at').first()
    
    def last_verified(self):
        """Return the most recent verified update."""
        return self.filter(verified=True).order_by('-uploaded_at').first()

class SoftwareUpdateManager(models.Manager):
    """Manager for SoftwareUpdate providing extended query methods."""
    
    def get_queryset(self):
        """Return the custom SoftwareUpdateQuerySet."""
        return SoftwareUpdateQuerySet(self.model, using=self._db)
    
    def get_last_update(self) -> Optional[object]:
        """Return the last update (most recent by uploaded_at)."""
        return self.get_queryset().order_by('-uploaded_at').first()
    
    def get_last_verified_update(self) -> Optional[object]:
        """Return the last verified update (most recent verified by uploaded_at)."""
        return self.get_queryset().filter(verified=True).order_by('-uploaded_at').first()
    
    def get_last_pending_update(self) -> Optional[object]:
        """Return the last pending update (most recent unverified by uploaded_at)."""
        return self.get_queryset().filter(verified=False).order_by('-uploaded_at').first()
    
    def get_version_history(self, version: str) -> List[object]:
        """Return all updates for a specific version ordered by date."""
        return self.get_queryset().by_version(version).order_by('-uploaded_at')
    
    def get_verified_updates(self) -> SoftwareUpdateQuerySet:
        """Return all verified updates."""
        return self.get_queryset().verified()
    
    def get_pending_updates(self) -> SoftwareUpdateQuerySet:
        """Return all pending (unverified) updates."""
        return self.get_queryset().pending()
    
    def get_updates_since(self, since_date):
        """Return updates uploaded since a specific date."""
        return self.get_queryset().filter(uploaded_at__gte=since_date)
    
    def verify_update(self, update_id: int) -> bool:
        """Mark an update as verified and return success status."""
        updated = self.filter(id=update_id).update(verified=True)
        return updated > 0
    
    def exists_version(self, version: str) -> bool:
        """Check if an update with given version exists."""
        return self.filter(version=version).exists()
    
    def get_statistics(self) -> dict:
        """Return statistics about software updates."""
        total = self.count()
        verified_count = self.filter(verified=True).count()
        pending_count = self.filter(verified=False).count()
        
        total_size = self.aggregate(total=models.Sum('size_bytes'))['total'] or 0
        
        latest = self.get_last_update()
        latest_verified = self.get_last_verified_update()
        
        return {
            'total_updates': total,
            'verified_updates': verified_count,
            'pending_updates': pending_count,
            'verification_rate': (verified_count / total * 100) if total > 0 else 0,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest_update_version': latest.version if latest else None,
            'latest_update_date': latest.uploaded_at if latest else None,
            'latest_verified_version': latest_verified.version if latest_verified else None,
            'latest_verified_date': latest_verified.uploaded_at if latest_verified else None,
        }