from ninja import FilterSchema, Field, Schema
from typing import Optional, Any
from datetime import datetime

# Filters

class TelemetryFilterSchema(FilterSchema):
    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp: Optional[datetime] = Field(None, q='timestamp__gte')
    subsystem: Optional[str] = None
    module: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    valid: Optional[bool] = None

class EventFilterSchema(FilterSchema):
    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp: Optional[datetime] = Field(None, q='timestamp__gte')
    subsystem: Optional[str] = None
    severity: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class StatusFilterSchema(FilterSchema):
    source: Optional[str] = None
    destination: Optional[str] = None
    subsystem: Optional[str] = None
    state: Optional[dict[str, Any]] = None
    mode: Optional[str] = None

class CommandFilterSchema(FilterSchema):
    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp: Optional[datetime] = Field(None, q='timestamp__gte')
    subsystem: Optional[str] = None
    parameters: Optional[str] = None
    status: Optional[str] = None
    execution_time: Optional[datetime] = None
    command_type: Optional[str] = None


# Schemas
class CommandMessageSchema(Schema):
    message_type: str = "CM"
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    parameters: dict[str, Any]
    status: str
    execution_time: datetime
    command_type: str

class TelemetryMessageSchema(Schema):
    message_type: str = "TM"
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    module: str
    value: Optional[float] = None
    unit: Optional[str] = None
    valid: bool

class EventMessageSchema(Schema):
    message_type: str = "EV"
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    severity: str
    code: str
    description: str

class StatusMessageSchema(Schema):
    message_type: str = "SM"
    source: str
    destination: str
    timestamp: datetime
    subsystem: str
    state: dict[str, Any]
    mode: str


# Request

class TelemetryRequestSchema(Schema):
    destination: str
    subsystem: str
    module: str

class EventRequestSchema(Schema):
    destination: str
    subsystem: str


class StatusRequestSchema(Schema):
    destination: str
    subsystem: str
