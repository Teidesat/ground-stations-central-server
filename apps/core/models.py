from django.db import models


# =========================================================
# GLOBAL ENUMS
# =========================================================

class MessageType(models.TextChoices):
    TELEMETRY = 'TM', 'Telemetry'
    COMMAND = 'CM', 'Command'
    EVENT = 'EV', 'Event'
    STATUS = 'ST', 'Status'
    UPDATE = 'UP', 'Software Update'


class Endpoint(models.TextChoices):
    SATELLITE = 'SATELLITE', 'Satellite'
    GROUND = 'GROUND', 'Ground Station'
    RADIO = 'RADIO', 'Radio Station'
    OPTICAL = 'OPTICAL', 'Optical Station'
    FOMALHAUT = 'FOMALHAUT', 'Central Panel'


class Subsystem(models.TextChoices):
    EPS = 'EPS', 'Electrical Power System'
    ADCS = 'ADCS', 'Attitude Control'
    THERMAL = 'THERMAL', 'Thermal Control'
    COMMS = 'COMMS', 'Communications'
    PAYLOAD = 'PAYLOAD', 'Payload'
    OBC = 'OBC', 'On Board Computer'
    GENERAL = 'GENERAL', 'General'


# =========================================================
# BASE MESSAGE MODEL
# =========================================================

class Message(models.Model):
    """
    Base message of the system.
    """

    message_type = models.CharField(max_length=2, choices=MessageType.choices)
    source = models.CharField(max_length=20, choices=Endpoint.choices)
    destination = models.CharField(max_length=20, choices=Endpoint.choices)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-timestamp"]


# =========================================================
# TELEMETRY
# =========================================================

class TelemetryMessage(Message):
    subsystem = models.CharField(max_length=10, choices=Subsystem.choices)
    module = models.CharField(max_length=50)
    raw_data = models.TextField(blank=True)
    value = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    valid = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.message_type = MessageType.TELEMETRY
        super().save(*args, **kwargs)


# =========================================================
# STATUS
# =========================================================

class SystemMode(models.TextChoices):
    TEST = 'TEST'
    OFFLINE = 'OFFLINE'
    AWAIT_LAUNCH = 'AWAIT_LAUNCH'
    DEPLOYMENT = 'DEPLOYMENT'
    INITIALIZATION = 'INITIALIZATION'
    CHECKING = 'CHECKING'
    NOMINAL = 'NOMINAL'
    DETUMBLING = 'DETUMBLING'
    SAFE = 'SAFE'
    EMERGENCY = 'EMERGENCY'
    OPERATIONAL = 'OPERATIONAL'
    MAINTENANCE = 'MAINTENANCE'  


class StatusMessage(Message):
    subsystem = models.CharField(max_length=10, choices=Subsystem.choices)
    state = models.JSONField()
    mode = models.CharField(max_length=20, choices=SystemMode.choices)

    def save(self, *args, **kwargs):
        self.message_type = MessageType.STATUS
        super().save(*args, **kwargs)



# =========================================================
# COMMANDS
# =========================================================

class CommandType(models.TextChoices):
    CHANGE_MODE = 'CHANGE_MODE'
    PAYLOAD_POWER = 'PAYLOAD_POWER'
    ADCS_CONTROL = 'ADCS_CONTROL'
    TAKE_PICTURE = 'TAKE_PICTURE'
    THERMAL_CONTROL = 'THERMAL_CONTROL'
    POWER_LINE = 'POWER_LINE'
    DEPLOY_ANTENNA = 'DEPLOY_ANTENNA'
    RECALIBRATE_SENSOR = 'RECALIBRATE_SENSOR'
    SOFTWARE_UPDATE = 'SOFTWARE_UPDATE'

class CommandStatus(models.TextChoices):
    SENT = 'SENT'
    RECEIVED = 'RECEIVED'
    ACCEPTED = 'ACCEPTED'
    EXECUTED = 'EXECUTED'
    FAILED = 'FAILED'


class CommandMessage(Message):
    subsystem = models.CharField(max_length=10, choices=Subsystem.choices)
    parameters = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=CommandStatus.choices,
        default=CommandStatus.SENT
    )
    
    execution_time = models.DateTimeField(null=True, blank=True)
    command_type = models.CharField(max_length=30, choices=CommandType.choices)

    def save(self, *args, **kwargs):
        self.message_type = MessageType.COMMAND
        super().save(*args, **kwargs)


# =========================================================
# EVENTS
# =========================================================

class EventSeverity(models.TextChoices):
    INFO = 'INFO'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'


class EventMessage(Message):
    subsystem = models.CharField(max_length=10, choices=Subsystem.choices)
    severity = models.CharField(max_length=10, choices=EventSeverity.choices)
    code = models.CharField(max_length=50)
    description = models.TextField()

    def save(self, *args, **kwargs):
        self.message_type = MessageType.EVENT
        super().save(*args, **kwargs)


# =========================================================
# SOFTWARE UPDATE
# =========================================================

class SoftwareUpdate(Message):
    versión = models.CharField(max_length=20)
    checksum = models.CharField(max_length=64)
    size_bytes = models.PositiveIntegerField()
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    data = models.BinaryField()

    def save(self, *args, **kwargs):
        self.message_type = MessageType.UPDATE
        self.destination = Endpoint.SATELLITE
        super().save(*args, **kwargs)
