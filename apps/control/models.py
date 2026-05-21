# apps/control/models.py
"""Control models for satellite telemetry, commands, events, and software updates."""

from django.db import models
from django.utils import timezone

from .managers import CommandManager, EventManager, TelemetryManager, SoftwareUpdateManager


class MessageType(models.TextChoices):
    """Standard message type identifiers."""

    TELEMETRY = 'TM', 'Telemetry'
    COMMAND = 'CM', 'Command'
    EVENT = 'EV', 'Event'
    STATUS = 'ST', 'Status'
    UPDATE = 'UP', 'Software Update'


class Endpoint(models.TextChoices):
    """Valid communication endpoints in the system."""

    SATELLITE = 'SATELLITE', 'Satellite'
    GROUND = 'GROUND', 'Ground Station'
    RADIO = 'RADIO', 'Radio Station'
    OPTICAL = 'OPTICAL', 'Optical Station'
    FOMALHAUT = 'FOMALHAUT', 'Central Panel'


class Subsystem(models.TextChoices):
    """Satellite subsystem identifiers."""

    EPS = 'EPS', 'Electrical Power System'
    ADCS = 'ADCS', 'Attitude Control'
    THERMAL = 'THERMAL', 'Thermal Control'
    COMMS = 'COMMS', 'Communications'
    PAYLOAD = 'PAYLOAD', 'Payload'
    OBC = 'OBC', 'On Board Computer'
    GENERAL = 'GENERAL', 'General'


class Message(models.Model):
    """Abstract base message model providing common fields for all message types."""

    message_type = models.CharField(max_length=2, choices=MessageType.choices)
    source = models.CharField(max_length=20, choices=Endpoint.choices)
    destination = models.CharField(max_length=20, choices=Endpoint.choices)
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        abstract = True
        ordering = ["-timestamp"]


class TelemetryMessage(Message):
    """Telemetry message model for sensor and system measurements."""

    subsystem = models.CharField(max_length=20, choices=Subsystem.choices, db_index=True)
    module = models.CharField(max_length=50, db_index=True)
    raw_data = models.TextField(blank=True)
    value = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    valid = models.BooleanField(default=True, db_index=True)

    objects = TelemetryManager()

    class Meta:
        indexes = [
            models.Index(fields=['subsystem', 'module']),
            models.Index(fields=['timestamp', 'subsystem']),
        ]

    def save(self, *args, **kwargs):
        """Set timestamp and message type before saving."""
        if not self.timestamp:
            self.timestamp = timezone.now()
        self.message_type = MessageType.TELEMETRY
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return string representation of the telemetry message."""
        return f"TM [{self.subsystem}] {self.module}: {self.value} {self.unit}"


class SystemMode(models.TextChoices):
    """Valid system operating modes."""

    TEST = 'TEST', 'Test'
    OFFLINE = 'OFFLINE', 'Offline'
    AWAIT_LAUNCH = 'AWAIT_LAUNCH', 'Await Launch'
    DEPLOYMENT = 'DEPLOYMENT', 'Deployment'
    INITIALIZATION = 'INITIALIZATION', 'Initialization'
    CHECKING = 'CHECKING', 'Checking'
    NOMINAL = 'NOMINAL', 'Nominal'
    DETUMBLING = 'DETUMBLING', 'Detumbling'
    SAFE = 'SAFE', 'Safe Mode'
    EMERGENCY = 'EMERGENCY', 'Emergency'
    OPERATIONAL = 'OPERATIONAL', 'Operational'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'


class StatusMessage(Message):
    """Status message model for system state reporting."""

    subsystem = models.CharField(max_length=20, choices=Subsystem.choices, db_index=True)
    state = models.JSONField(help_text="Current state as JSON")
    mode = models.CharField(max_length=20, choices=SystemMode.choices, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['subsystem', 'mode']),
        ]

    def save(self, *args, **kwargs):
        """Set timestamp and message type before saving."""
        if not self.timestamp:
            self.timestamp = timezone.now()
        self.message_type = MessageType.STATUS
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return string representation of the status message."""
        return f"STATUS [{self.subsystem}] Mode: {self.mode}"


class CommandType(models.TextChoices):
    """Valid command types."""

    CHANGE_MODE = 'CHANGE_MODE', 'Change Mode'
    PAYLOAD_POWER = 'PAYLOAD_POWER', 'Payload Power'
    ADCS_CONTROL = 'ADCS_CONTROL', 'ADCS Control'
    TAKE_PICTURE = 'TAKE_PICTURE', 'Take Picture'
    THERMAL_CONTROL = 'THERMAL_CONTROL', 'Thermal Control'
    POWER_LINE = 'POWER_LINE', 'Power Line'
    DEPLOY_ANTENNA = 'DEPLOY_ANTENNA', 'Deploy Antenna'
    RECALIBRATE_SENSOR = 'RECALIBRATE_SENSOR', 'Recalibrate Sensor'
    SOFTWARE_UPDATE = 'SOFTWARE_UPDATE', 'Software Update'


class CommandStatus(models.TextChoices):
    """Valid command execution status values."""

    SENT = 'SENT', 'Sent'
    RECEIVED = 'RECEIVED', 'Received'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    EXECUTED = 'EXECUTED', 'Executed'
    FAILED = 'FAILED', 'Failed'


class CommandMessage(Message):
    """Command message model for sending instructions to subsystems."""

    subsystem = models.CharField(max_length=20, choices=Subsystem.choices, db_index=True)
    parameters = models.JSONField(help_text="Command parameters")
    status = models.CharField(
        max_length=20,
        choices=CommandStatus.choices,
        default=CommandStatus.SENT,
        db_index=True
    )
    execution_time = models.DateTimeField(null=True, blank=True)
    command_type = models.CharField(max_length=30, choices=CommandType.choices, db_index=True)

    objects = CommandManager()

    class Meta:
        indexes = [
            models.Index(fields=['status', 'command_type']),
            models.Index(fields=['subsystem', 'command_type']),
        ]

    def save(self, *args, **kwargs):
        """Set timestamp and message type before saving."""
        if not self.timestamp:
            self.timestamp = timezone.now()
        self.message_type = MessageType.COMMAND
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return string representation of the command message."""
        return f"CMD [{self.command_type}] -> {self.subsystem} - {self.status}"


class EventSeverity(models.TextChoices):
    """Event severity levels."""

    INFO = 'INFO', 'Info'
    WARNING = 'WARNING', 'Warning'
    CRITICAL = 'CRITICAL', 'Critical'


class EventMessage(Message):
    """Event message model for system notifications and alerts."""

    subsystem = models.CharField(max_length=20, choices=Subsystem.choices, db_index=True)
    severity = models.CharField(max_length=10, choices=EventSeverity.choices, db_index=True)
    code = models.CharField(max_length=50, db_index=True)
    description = models.TextField()

    objects = EventManager()

    class Meta:
        indexes = [
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['subsystem', 'severity']),
            models.Index(fields=['code']),
        ]

    def save(self, *args, **kwargs):
        """Set timestamp and message type before saving."""
        if not self.timestamp:
            self.timestamp = timezone.now()
        self.message_type = MessageType.EVENT
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return string representation of the event message."""
        return f"EVENT [{self.severity}] {self.code}: {self.description[:50]}"


class SoftwareUpdateMessage(Message):
    """Software update model for firmware and software distribution."""

    version = models.CharField(max_length=20)
    checksum = models.CharField(max_length=64)
    size_bytes = models.PositiveIntegerField()
    verified = models.BooleanField(default=False, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    data = models.BinaryField()

    objects = SoftwareUpdateManager()

    class Meta:
        indexes = [
            models.Index(fields=['verified', 'uploaded_at']),
        ]

    def save(self, *args, **kwargs):
        """Set timestamp, message type, and destination before saving."""
        if not self.timestamp:
            self.timestamp = timezone.now()
        self.message_type = MessageType.UPDATE
        self.destination = Endpoint.SATELLITE
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return string representation of the software update."""
        return f"UPDATE v{self.version} - {'Verified' if self.verified else 'Pending'}"