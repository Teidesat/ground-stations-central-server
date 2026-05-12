# apps/bridge/schemas.py
"""Pydantic/Ninja schemas for bridge request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List

from ninja import FilterSchema, Field, Schema
from pydantic import field_validator


VALID_DESTINATIONS = ["satellite", "radio_station", "optical_station", "fomalhaut"]
VALID_SUBSYSTEMS = ["EPS", "ADCS", "THERMAL", "COMMS", "PAYLOAD", "OBC", "GENERAL"]


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


class BaseRequestSchema(Schema):
    """Base request schema with common validation."""

    destination: str
    subsystem: str

    @field_validator('destination')
    @classmethod
    def validate_destination_field(cls, value: str) -> str:
        """Validate that the destination is in the allowed list."""
        if value not in VALID_DESTINATIONS:
            raise ValueError(f"Destination '{value}' is invalid. Valid destinations are {VALID_DESTINATIONS}")
        return value

    @field_validator('subsystem')
    @classmethod
    def validate_subsystem_field(cls, value: str) -> str:
        """Validate that the subsystem is in the allowed list."""
        if value not in VALID_SUBSYSTEMS:
            raise ValueError(f"Subsystem '{value}' is invalid. Valid subsystems are {VALID_SUBSYSTEMS}")
        return value


class TelemetryRequestSchema(BaseRequestSchema):
    """Request schema for live telemetry queries."""

    module: str

    @field_validator('module')
    @classmethod
    def validate_module_field(cls, value: str) -> str:
        """Validate that module is a non-empty string."""
        if not value:
            raise ValueError("Module must be a non-empty string")
        return value


class EventRequestSchema(BaseRequestSchema):
    """Request schema for live event queries."""


class StatusRequestSchema(BaseRequestSchema):
    """Request schema for live status queries."""


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