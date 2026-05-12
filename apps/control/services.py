# apps/control/services.py
"""Business logic services for control functionality."""

import logging
from datetime import timedelta
from typing import Dict, Any, Optional, List

from django.utils import timezone

from .models import (CommandMessage, CommandStatus, EventMessage, EventSeverity,
                     StatusMessage, SystemMode, TelemetryMessage)

logger = logging.getLogger(__name__)


class TelemetryService:
    """Service class for telemetry data operations."""

    @staticmethod
    def get_latest_telemetry(subsystem: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Return the latest valid telemetry readings.

        Args:
            subsystem: Optional subsystem name to filter by.
            limit: Maximum number of records to return.

        Returns:
            List of dictionaries containing telemetry data.
        """
        qs = TelemetryMessage.objects.valid()
        if subsystem:
            qs = qs.by_subsystem(subsystem)
        return list(qs[:limit].values('subsystem', 'module', 'value', 'unit', 'timestamp'))

    @staticmethod
    def get_subsystem_health() -> Dict[str, Any]:
        """Return health status for each subsystem.

        Returns:
            Dictionary mapping subsystem names to health status objects.
        """
        from .models import Subsystem

        health = {}
        for subsystem in Subsystem.values:
            latest = TelemetryMessage.objects.valid().by_subsystem(subsystem).first()
            health[subsystem] = {
                'status': 'OK' if latest and latest.valid else 'UNKNOWN',
                'last_update': latest.timestamp if latest else None,
                'value': latest.value if latest else None
            }
        return health


class CommandService:
    """Service class for command operations."""

    @staticmethod
    def send_command(command_type: str, subsystem: str, parameters: Dict) -> CommandMessage:
        """Create and send a new command.

        Args:
            command_type: Type of command to send.
            subsystem: Target subsystem.
            parameters: Command parameters as a dictionary.

        Returns:
            The created CommandMessage instance.
        """
        command = CommandMessage.objects.create(
            command_type=command_type,
            subsystem=subsystem,
            parameters=parameters,
            status=CommandStatus.SENT
        )
        logger.info(f"Command {command.id} sent: {command_type} to {subsystem}")
        return command

    @staticmethod
    def update_command_status(command_id: int, status: str, execution_time=None) -> Optional[CommandMessage]:
        """Update the execution status of a command.

        Args:
            command_id: Primary key of the command to update.
            status: New command status.
            execution_time: Optional timestamp of execution.

        Returns:
            The updated CommandMessage instance, or None if not found.
        """
        try:
            command = CommandMessage.objects.get(id=command_id)
            command.status = status
            if execution_time:
                command.execution_time = execution_time
            command.save()
            logger.info(f"Command {command_id} status updated to {status}")
            return command
        except CommandMessage.DoesNotExist:
            logger.error(f"Command {command_id} not found")
            return None

    @staticmethod
    def get_pending_commands() -> List[CommandMessage]:
        """Return all pending (not yet executed) commands."""
        return list(CommandMessage.objects.pending())


class EventService:
    """Service class for event management."""

    @staticmethod
    def create_event(subsystem: str, severity: str, code: str, description: str) -> EventMessage:
        """Create a new event.

        Args:
            subsystem: Subsystem that generated the event.
            severity: Event severity (INFO, WARNING, CRITICAL).
            code: Event code identifier.
            description: Human-readable event description.

        Returns:
            The created EventMessage instance.
        """
        event = EventMessage.objects.create(
            subsystem=subsystem,
            severity=severity,
            code=code,
            description=description
        )

        # Log critical and warning events immediately
        if severity == EventSeverity.CRITICAL:
            logger.critical(f"CRITICAL EVENT [{subsystem}] {code}: {description}")
        elif severity == EventSeverity.WARNING:
            logger.warning(f"WARNING [{subsystem}] {code}: {description}")

        return event

    @staticmethod
    def get_active_alerts() -> List[EventMessage]:
        """Return unresolved critical events and warnings from the last hour."""
        return list(EventMessage.objects.get_recent_alerts(limit=50))


class SystemService:
    """Service class for overall system status and metrics."""

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Return comprehensive system metrics.

        Returns:
            Dictionary containing telemetry count, active alerts,
            pending commands, success rate, last contact, and system mode.
        """
        now = timezone.now()
        hour_ago = now - timedelta(hours=1)

        # Count telemetry in the last hour
        telemetry_count = TelemetryMessage.objects.filter(timestamp__gte=hour_ago).count()

        # Count active alerts in the last hour
        active_alerts = EventMessage.objects.filter(
            timestamp__gte=hour_ago,
            severity__in=[EventSeverity.CRITICAL, EventSeverity.WARNING]
        ).count()

        # Count pending commands
        pending_commands = CommandMessage.objects.pending().count()

        # Calculate command success rate from last 100 commands
        recent_commands = CommandMessage.objects.all()[:100]
        total = recent_commands.count()
        executed = recent_commands.filter(status=CommandStatus.EXECUTED).count()
        success_rate = (executed / total * 100) if total > 0 else 0

        # Get last contact timestamp from latest telemetry
        last_telemetry = TelemetryMessage.objects.first()

        # Get current system mode from latest status
        latest_status = StatusMessage.objects.first()

        return {
            'telemetry_count': telemetry_count,
            'active_alerts': active_alerts,
            'pending_commands': pending_commands,
            'command_success_rate': round(success_rate, 2),
            'last_contact': last_telemetry.timestamp if last_telemetry else None,
            'system_mode': latest_status.mode if latest_status else SystemMode.OFFLINE,
        }