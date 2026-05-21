"""
Tests for the mission app (telemetry, commands, events, status).
"""

import pytest

pytestmark = pytest.mark.django_db


class TestTelemetryModel:
    """Tests for TelemetryMessage model."""

    def test_create_telemetry(self):
        from apps.control.models import TelemetryMessage
        
        telemetry = TelemetryMessage.objects.create(
            subsystem="EPS",
            module="battery_voltage",
            value=28.5,
            unit="V",
            source="SATELLITE",
            destination="GROUND"
        )
        
        assert telemetry.pk is not None
        assert telemetry.message_type == "TM"
        assert telemetry.valid is True

    def test_telemetry_manager_valid(self):
        from apps.control.models import TelemetryMessage
        
        TelemetryMessage.objects.create(subsystem="EPS", module="test", value=10, valid=True)
        TelemetryMessage.objects.create(subsystem="EPS", module="test", value=20, valid=False)
        
        valid = TelemetryMessage.objects.valid()
        assert valid.count() == 1

    def test_telemetry_manager_by_subsystem(self):
        from apps.control.models import TelemetryMessage
        
        TelemetryMessage.objects.create(subsystem="EPS", module="test1", value=10)
        TelemetryMessage.objects.create(subsystem="ADCS", module="test2", value=20)
        
        eps = TelemetryMessage.objects.by_subsystem("EPS")
        assert eps.count() == 1

    def test_telemetry_manager_last_hours(self):
        from apps.control.models import TelemetryMessage
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        old = now - timedelta(hours=48)
        
        TelemetryMessage.objects.create(subsystem="EPS", module="test", value=10, timestamp=now)
        TelemetryMessage.objects.create(subsystem="EPS", module="test", value=20, timestamp=old)
        
        recent = TelemetryMessage.objects.last_hours(24)
        
        
        assert recent.count() == 1


class TestCommandModel:
    """Tests for CommandMessage model."""

    def test_create_command(self):
        from apps.control.models import CommandMessage, CommandStatus, CommandType
        
        command = CommandMessage.objects.create(
            command_type=CommandType.CHANGE_MODE,
            subsystem="ADCS",
            parameters={"mode": "nominal"},
            source="GROUND",
            destination="SATELLITE"
        )
        
        assert command.pk is not None
        assert command.status == CommandStatus.SENT

    def test_command_manager_pending(self):
        from apps.control.models import CommandMessage, CommandStatus
        
        CommandMessage.objects.create(
            command_type="CHANGE_MODE",
            subsystem="ADCS",
            parameters={},
            status=CommandStatus.SENT
        )
        CommandMessage.objects.create(
            command_type="CHANGE_MODE",
            subsystem="ADCS",
            parameters={},
            status=CommandStatus.EXECUTED
        )
        
        pending = CommandMessage.objects.pending()
        assert pending.count() == 1

    def test_command_statistics(self):
        from apps.control.models import CommandMessage, CommandStatus
        
        for i in range(5):
            CommandMessage.objects.create(
                command_type="TEST",
                subsystem="OBC",
                parameters={},
                status=CommandStatus.EXECUTED
            )
        for i in range(3):
            CommandMessage.objects.create(
                command_type="TEST",
                subsystem="OBC",
                parameters={},
                status=CommandStatus.FAILED
            )
        
        stats = CommandMessage.objects.get_statistics()
        assert stats['total'] == 8
        assert stats['executed'] == 5
        assert stats['failed'] == 3
        assert stats['success_rate'] == 62.5


class TestEventModel:
    """Tests for EventMessage model."""

    def test_create_event(self):
        from apps.control.models import EventMessage, EventSeverity
        
        event = EventMessage.objects.create(
            subsystem="OBC",
            severity=EventSeverity.CRITICAL,
            code="WATCHDOG_RESET",
            description="Watchdog triggered reset",
            source="SATELLITE",
            destination="GROUND"
        )
        
        assert event.pk is not None
        assert event.severity == "CRITICAL"

    def test_event_manager_critical(self):
        from apps.control.models import EventMessage, EventSeverity
        
        EventMessage.objects.create(
            subsystem="OBC",
            severity=EventSeverity.CRITICAL,
            code="ERROR1",
            description="Critical error"
        )
        EventMessage.objects.create(
            subsystem="OBC",
            severity=EventSeverity.INFO,
            code="INFO1",
            description="Information"
        )
        
        critical = EventMessage.objects.critical()
        assert critical.count() == 1

    def test_event_manager_get_recent_alerts(self):
        from apps.control.models import EventMessage, EventSeverity
        
        EventMessage.objects.create(
            subsystem="OBC",
            severity=EventSeverity.CRITICAL,
            code="CRIT1",
            description="Critical"
        )
        EventMessage.objects.create(
            subsystem="OBC",
            severity=EventSeverity.WARNING,
            code="WARN1",
            description="Warning"
        )
        EventMessage.objects.create(
            subsystem="OBC",
            severity=EventSeverity.INFO,
            code="INFO1",
            description="Info"
        )
        
        alerts = EventMessage.objects.get_recent_alerts(10)
        assert alerts.count() == 2


class TestStatusModel:
    """Tests for StatusMessage model."""

    def test_create_status(self):
        from apps.control.models import StatusMessage, SystemMode
        
        status = StatusMessage.objects.create(
            subsystem="GENERAL",
            state={"battery": 95, "temperature": 22},
            mode=SystemMode.NOMINAL,
            source="SATELLITE",
            destination="GROUND"
        )
        
        assert status.pk is not None
        assert status.mode == "NOMINAL"

class TestSoftwareUpdateModel:
    """Tests for SoftwareUpdateMessage model."""

    def test_create_software_update(self):
        """Test creating a software update instance."""
        import hashlib
        from apps.control.models import SoftwareUpdateMessage

        test_data = b"test_firmware_data"
        valid_checksum = hashlib.sha256(test_data).hexdigest()
        
        software_update = SoftwareUpdateMessage.objects.create(
            version="1.2.3",
            checksum=valid_checksum,
            size_bytes=len(test_data),
            verified=False,
            data=test_data,
            source="GROUND",
            destination="SATELLITE"
        )
        
        assert software_update.pk is not None
        assert software_update.version == "1.2.3"
        assert software_update.verified is False
        assert software_update.size_bytes == len(test_data)
        assert software_update.message_type == "UP"
        assert software_update.timestamp is not None
        assert software_update.uploaded_at is not None

    def test_software_update_str(self):
        """Test string representation."""
        import hashlib
        from apps.control.models import SoftwareUpdateMessage
        test_data = b"test_data"
        valid_checksum = hashlib.sha256(test_data).hexdigest()
        
        software_update = SoftwareUpdateMessage.objects.create(
            version="2.0.0",
            checksum=valid_checksum,
            size_bytes=len(test_data),
            verified=True,
            data=test_data
        )
        
        assert str(software_update) == "UPDATE v2.0.0 - Verified"
        
        software_update.verified = False
        software_update.save()
        assert str(software_update) == "UPDATE v2.0.0 - Pending"

    def test_software_update_auto_fields(self):
        """Test auto-populated fields."""
        import hashlib
        from apps.control.models import SoftwareUpdateMessage
        test_data = b"test_data"
        valid_checksum = hashlib.sha256(test_data).hexdigest()
        
        software_update = SoftwareUpdateMessage.objects.create(
            version="1.0.0",
            checksum=valid_checksum,
            size_bytes=len(test_data),
            data=test_data
        )
        
        assert software_update.message_type == "UP"
        assert software_update.destination == "SATELLITE"
        assert software_update.timestamp is not None
        assert software_update.uploaded_at is not None