"""
Fake server for testing external service integration.
"""

from fastapi import FastAPI, Query
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# Response Models
class TelemetryResponse(BaseModel):
    message_type: str = "TM"
    source: str = "TEST-SAT-1"
    destination: Optional[str] = None
    timestamp: str = "2026-01-01T00:00:00Z"
    subsystem: str = "EPS"
    module: str = "battery_voltage"
    value: float = 28.5
    unit: str = "V"
    valid: bool = True


class EventResponse(BaseModel):
    message_type: str = "EV"
    source: str = "TEST-SAT-1"
    destination: Optional[str] = None
    timestamp: str = "2026-01-01T00:00:00Z"
    subsystem: str = "OBC"
    severity: str = "INFO"
    code: str = "STARTUP"
    description: str = "System startup completed"


class StatusResponse(BaseModel):
    message_type: str = "SM"
    source: str = "TEST-SAT-1"
    destination: Optional[str] = None
    timestamp: str = "2026-01-01T00:00:00Z"
    subsystem: str = "GENERAL"
    state: dict = {"status": "operational"}
    mode: str = "NOMINAL"


class CommandResponse(BaseModel):
    status: str = "success"
    command_id: str = "cmd-123"
    message: str = "Command accepted"


def create_fake_server() -> FastAPI:
    """Create a fake server for testing external service communication."""
    app = FastAPI(title="Fake External Service")

    @app.get("/telemetry", response_model=TelemetryResponse)
    async def get_telemetry(
        destination: Optional[str] = Query(None),
        subsystem: Optional[str] = Query(None),
        module: Optional[str] = Query(None)
    ):
        """Fake telemetry endpoint."""
        return TelemetryResponse(
            destination=destination,
            subsystem=subsystem or "EPS",
            module=module or "battery_voltage"
        )

    @app.get("/events", response_model=EventResponse)
    async def get_events(
        destination: Optional[str] = Query(None),
        subsystem: Optional[str] = Query(None)
    ):
        """Fake events endpoint."""
        return EventResponse(
            destination=destination,
            subsystem=subsystem or "OBC"
        )

    @app.get("/status", response_model=StatusResponse)
    async def get_status(
        destination: Optional[str] = Query(None),
        subsystem: Optional[str] = Query(None)
    ):
        """Fake status endpoint."""
        return StatusResponse(
            destination=destination,
            subsystem=subsystem or "GENERAL"
        )

    @app.post("/commands", response_model=CommandResponse)
    async def post_commands(data: dict):
        """Fake command endpoint."""
        return CommandResponse()

    return app