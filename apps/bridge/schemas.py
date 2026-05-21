# apps/bridge/schemas.py
"""Pydantic/Ninja schemas for bridge request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List
import base64

from ninja import FilterSchema, Field, Schema
from pydantic import field_validator


VALID_DESTINATIONS = ["satellite", "radio_station", "optical_station", "fomalhaut"]
VALID_SUBSYSTEMS = ["EPS", "ADCS", "THERMAL", "COMMS", "PAYLOAD", "OBC", "GENERAL"]

VALID_VERSION_PATTERNS = ['dev', 'test', 'prod']
MAX_VERSION_LENGTH = 20
VALID_CHECKSUM_LENGTHS = [64]  # SHA256


class MessageType(str, Enum):
    """Standard message type identifiers."""

    COMMAND = "CM"
    TELEMETRY = "TM"
    EVENT = "EV"
    STATUS = "SM"


class TelemetryFilterSchema(FilterSchema):
    """Filter schema for telemetry data queries."""

    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    timestamp_lte: Optional[datetime] = Field(None, q='timestamp__lte')
    subsystem: Optional[str] = None
    module: Optional[str] = None
    module_contains: Optional[str] = Field(None, q='module__icontains')
    value_min: Optional[float] = Field(None, q='value__gte')
    value_max: Optional[float] = Field(None, q='value__lte')
    unit: Optional[str] = None
    valid: Optional[bool] = None


class EventFilterSchema(FilterSchema):
    """Filter schema for event data queries."""

    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    timestamp_lte: Optional[datetime] = Field(None, q='timestamp__lte')
    subsystem: Optional[str] = None
    severity: Optional[str] = None
    severity_in: Optional[List[str]] = Field(None, q='severity__in')
    code: Optional[str] = None
    code_contains: Optional[str] = Field(None, q='code__icontains')
    description: Optional[str] = Field(None, q='description__icontains')


class StatusFilterSchema(FilterSchema):
    """Filter schema for status data queries."""

    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    subsystem: Optional[str] = None
    mode: Optional[str] = None
    mode_in: Optional[List[str]] = Field(None, q='mode__in')

class SoftwareUpdateFilterSchema(FilterSchema):
    """Filter schema for software update data queries."""
    
    version: Optional[str] = None
    version_in: Optional[List[str]] = Field(None, q='version__in')
    version_contains: Optional[str] = Field(None, q='version__icontains')
    checksum: Optional[str] = None
    size_bytes_gte: Optional[int] = Field(None, q='size_bytes__gte')
    size_bytes_lte: Optional[int] = Field(None, q='size_bytes__lte')
    verified: Optional[bool] = None
    uploaded_at_gte: Optional[datetime] = Field(None, q='uploaded_at__gte')
    uploaded_at_lte: Optional[datetime] = Field(None, q='uploaded_at__lte')
    uploaded_at_date: Optional[str] = Field(None, q='uploaded_at__date')
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    timestamp_lte: Optional[datetime] = Field(None, q='timestamp__lte')
    source: Optional[str] = None
    destination: Optional[str] = None

class CommandFilterSchema(FilterSchema):
    """Filter schema for command data queries."""

    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    timestamp_lte: Optional[datetime] = Field(None, q='timestamp__lte')
    subsystem: Optional[str] = None
    status: Optional[str] = None
    status_in: Optional[List[str]] = Field(None, q='status__in')
    command_type: Optional[str] = None
    command_type_in: Optional[List[str]] = Field(None, q='command_type__in')

class CommandMessageSchema(Schema):
    """Schema for command message validation."""

    message_type: str = MessageType.COMMAND
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    parameters: Dict[str, Any]
    status: str
    execution_time: Optional[datetime] = None
    command_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "message_type": "CM",
                "source": "fomalhaut",
                "destination": "satellite",
                "timestamp": "2024-01-01T12:00:00Z",
                "subsystem": "ADCS",
                "parameters": {"mode": "nominal"},
                "status": "SENT",
                "command_type": "CHANGE_MODE"
            }
        }


class TelemetryMessageSchema(Schema):
    """Schema for telemetry message validation."""

    message_type: str = MessageType.TELEMETRY
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    module: str
    value: Optional[float] = None
    unit: Optional[str] = None
    valid: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "message_type": "TM",
                "source": "satellite",
                "destination": "fomalhaut",
                "timestamp": "2024-01-01T12:00:00Z",
                "subsystem": "EPS",
                "module": "battery_voltage",
                "value": 28.5,
                "unit": "V",
                "valid": True
            }
        }


class EventMessageSchema(Schema):
    """Schema for event message validation."""

    message_type: str = MessageType.EVENT
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    severity: str
    code: str
    description: str

    class Config:
        json_schema_extra = {
            "example": {
                "message_type": "EV",
                "source": "satellite",
                "destination": "fomalhaut",
                "timestamp": "2024-01-01T12:00:00Z",
                "subsystem": "OBC",
                "severity": "WARNING",
                "code": "WATCHDOG_RESET",
                "description": "Watchdog timer triggered reset"
            }
        }


class StatusMessageSchema(Schema):
    """Schema for status message validation."""

    message_type: str = MessageType.STATUS
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    state: Dict[str, Any]
    mode: str

    class Config:
        json_schema_extra = {
            "example": {
                "message_type": "SM",
                "source": "satellite",
                "destination": "fomalhaut",
                "timestamp": "2024-01-01T12:00:00Z",
                "subsystem": "GENERAL",
                "state": {"battery": 95, "temperature": 22},
                "mode": "NOMINAL"
            }
        }

class SoftwareUpdateMessageSchema(Schema):
    """Schema for software update message validation."""
    
    message_type: str
    source: str
    destination: str
    timestamp: datetime
    
    version: str
    checksum: str
    size_bytes: int
    verified: bool = False
    uploaded_at: datetime
    data: Optional[bytes] = None
    
    @field_validator('data', mode='before')
    @classmethod
    def decode_data_from_base64(cls, v):
        """Convert bytes/memoryview to base64 string."""
        if v is None:
            return None
        if isinstance(v, str):
            # Decodificar de base64 a bytes
            return base64.b64decode(v)
        if isinstance(v, memoryview):
            return bytes(v)
        if isinstance(v, bytes):
            return v
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "message_type": "UPDATE",
                "source": "fomalhaut",
                "destination": "satellite",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "1.2.3",
                "checksum": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678",
                "size_bytes": 1048576,
                "verified": True,
                "uploaded_at": "2024-01-01T12:00:00Z",
                "data": "dGVzdF9maXJtd2FyZV9kYXRh"
            }
        }


class BaseRequestSchema(Schema):
    """Base request schema with common validation."""

    destination: str

    @field_validator('destination')
    @classmethod
    def validate_destination_field(cls, value: str) -> str:
        """Validate that the destination is in the allowed list."""
        if value not in VALID_DESTINATIONS:
            raise ValueError(f"Destination '{value}' is invalid. Valid destinations are {VALID_DESTINATIONS}")
        return value


class TelemetryRequestSchema(BaseRequestSchema):
    """Request schema for live telemetry queries."""

    module: str
    subsystem: str

    @field_validator('subsystem')
    @classmethod
    def validate_subsystem_field(cls, value: str) -> str:
        """Validate that the subsystem is in the allowed list."""
        if value not in VALID_SUBSYSTEMS:
            raise ValueError(f"Subsystem '{value}' is invalid. Valid subsystems are {VALID_SUBSYSTEMS}")
        return value

    @field_validator('module')
    @classmethod
    def validate_module_field(cls, value: str) -> str:
        """Validate that module is a non-empty string."""
        if not value:
            raise ValueError("Module must be a non-empty string")
        return value


class EventRequestSchema(BaseRequestSchema):
    """Request schema for live event queries."""

    subsystem: str

    @field_validator('subsystem')
    @classmethod
    def validate_subsystem_field(cls, value: str) -> str:
        """Validate that the subsystem is in the allowed list."""
        if value not in VALID_SUBSYSTEMS:
            raise ValueError(f"Subsystem '{value}' is invalid. Valid subsystems are {VALID_SUBSYSTEMS}")
        return value


class StatusRequestSchema(BaseRequestSchema):
    """Request schema for live status queries."""

    subsystem: str

    @field_validator('subsystem')
    @classmethod
    def validate_subsystem_field(cls, value: str) -> str:
        """Validate that the subsystem is in the allowed list."""
        if value not in VALID_SUBSYSTEMS:
            raise ValueError(f"Subsystem '{value}' is invalid. Valid subsystems are {VALID_SUBSYSTEMS}")
        return value


class SoftwareUpdateRequestSchema(BaseRequestSchema):
    """Request schema for software update operations."""


class SoftwareUpdateSendRequestSchema(BaseRequestSchema):
    """Request schema for verifying software updates."""
    
    version: str
    checksum: str
    data: str
    
    @field_validator('version')
    @classmethod
    def validate_version_format(cls, value: str) -> str:
        """Validate version format."""
        if not value or len(value) > MAX_VERSION_LENGTH:
            raise ValueError(f"Version must be between 1 and {MAX_VERSION_LENGTH} characters")
        return value
    
    @field_validator('checksum')
    @classmethod
    def validate_checksum(cls, value: str) -> str:
        """Validate checksum format."""
        if len(value) != 64:
            raise ValueError("Checksum must be 64 characters for SHA256")
        if not all(c in '0123456789abcdef' for c in value.lower()):
            raise ValueError("Checksum must be hexadecimal")
        return value


class BridgeResponseSchema(Schema):
    """Standard response schema for bridge operations."""

    status: str
    message: Any
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponseSchema(Schema):
    """Error response schema for API error responses."""

    error: str
    detail: Optional[str] = None
    destination: Optional[str] = None