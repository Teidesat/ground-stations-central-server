# apps/control/schemas.py
"""Pydantic/Ninja schemas for control message validation and serialization."""

from datetime import datetime
from typing import Optional, Dict, Any

from ninja import Schema, FilterSchema, Field


class TelemetrySchema(Schema):
    """Telemetry message response schema."""

    id: int
    subsystem: str
    module: str
    value: Optional[float] = None
    unit: str = ""
    valid: bool = True
    timestamp: datetime


class TelemetryCreateSchema(Schema):
    """Schema for creating telemetry messages."""

    subsystem: str
    module: str
    value: Optional[float] = None
    unit: str = ""
    raw_data: str = ""
    source: str = "GROUND"
    destination: str = "FOMALHAUT"


class TelemetryFilterSchema(FilterSchema):
    """Filter schema for telemetry queries."""

    subsystem: Optional[str] = None
    module: Optional[str] = None
    valid: Optional[bool] = None
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    timestamp_lte: Optional[datetime] = Field(None, q='timestamp__lte')
    value_min: Optional[float] = Field(None, q='value__gte')
    value_max: Optional[float] = Field(None, q='value__lte')


class StatusSchema(Schema):
    """Status message response schema."""

    id: int
    subsystem: str
    state: Dict[str, Any]
    mode: str
    timestamp: datetime


class StatusCreateSchema(Schema):
    """Schema for creating status messages."""

    subsystem: str
    state: Dict[str, Any]
    mode: str
    source: str = "SATELLITE"
    destination: str = "FOMALHAUT"


class CommandSchema(Schema):
    """Command message response schema."""

    id: int
    command_type: str
    subsystem: str
    parameters: Dict[str, Any]
    status: str
    execution_time: Optional[datetime] = None
    timestamp: datetime


class CommandCreateSchema(Schema):
    """Schema for creating commands."""

    command_type: str
    subsystem: str
    parameters: Dict[str, Any]
    source: str = "FOMALHAUT"
    destination: str = "SATELLITE"


class CommandUpdateSchema(Schema):
    """Schema for updating command status."""

    status: str
    execution_time: Optional[datetime] = None
    error_message: Optional[str] = None


class CommandFilterSchema(FilterSchema):
    """Filter schema for command queries."""

    command_type: Optional[str] = None
    subsystem: Optional[str] = None
    status: Optional[str] = None
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')


class EventSchema(Schema):
    """Event message response schema."""

    id: int
    subsystem: str
    severity: str
    code: str
    description: str
    timestamp: datetime


class EventCreateSchema(Schema):
    """Schema for creating events."""

    subsystem: str
    severity: str
    code: str
    description: str
    source: str = "SATELLITE"
    destination: str = "FOMALHAUT"


class EventFilterSchema(FilterSchema):
    """Filter schema for event queries."""

    subsystem: Optional[str] = None
    severity: Optional[str] = None
    code: Optional[str] = None
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    timestamp_lte: Optional[datetime] = Field(None, q='timestamp__lte')


class SoftwareUpdateSchema(Schema):
    """Software update response schema."""

    id: int
    version: str
    checksum: str
    size_bytes: int
    verified: bool
    uploaded_at: datetime


class SoftwareUpdateCreateSchema(Schema):
    """Schema for uploading software updates (Base64-encoded data)."""

    version: str
    checksum: str
    data: str


class SystemMetricsSchema(Schema):
    """System metrics response schema."""

    telemetry_count: int
    active_alerts: int
    pending_commands: int
    command_success_rate: float
    last_contact: Optional[datetime]
    system_mode: str