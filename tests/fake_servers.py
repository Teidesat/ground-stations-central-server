"""
Fake server for testing external service integration.
"""

from fastapi import FastAPI, Query
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import base64


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


class SoftwareUpdateResponse(BaseModel):
    message_type: str = "UP"
    source: str = "satellite"
    destination: Optional[str] = None
    timestamp: str = "2024-01-01T12:00:00Z"
    version: str = "3.0.0"
    checksum: str = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678"
    size_bytes: int = 3145728
    verified: bool = True
    uploaded_at: str = "2024-01-01T12:00:00Z"
    data: str = base64.b64encode(b"test_firmware_data").decode()

class SoftwareUpdateRequest(BaseModel):
    destination: str
    version: str
    data: str
    checksum: str


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

    @app.get("/software_update", response_model=SoftwareUpdateResponse)
    async def get_software_update(
        destination: Optional[str] = Query(None),
        version: Optional[str] = Query(None)
    ):
        """Fake software update endpoint."""
        import hashlib
        response = SoftwareUpdateResponse(destination=destination)
        if version and version != "latest":
            response.version = version
            checksum_input = f"fake_software_{version}_{destination}".encode()
            response.checksum = hashlib.sha256(checksum_input).hexdigest()
            response.size_bytes = 1024 * 1024
            response.data = base64.b64encode(f"firmware_data_for_{version}".encode()).decode()
            firmware_data = f"firmware_data_for_{version}".encode()
            response.data = base64.b64encode(firmware_data).decode()
            
        else:
            response.data = base64.b64encode(b"test_firmware_data").decode()
        return response
    
    @app.post("/software_update", response_model=SoftwareUpdateResponse)
    async def post_software_update(request_data: SoftwareUpdateRequest):
        """Fake software update send endpoint."""
        import hashlib
        import base64
        from datetime import datetime

        decoded_data = base64.b64decode(request_data.data)
        calculated_checksum = hashlib.sha256(decoded_data).hexdigest()
        is_verified = (calculated_checksum == request_data.checksum)
        size_bytes = len(decoded_data)
        
        current_time = datetime.now().isoformat()
        
        response = SoftwareUpdateResponse(
            message_type="UP",
            source="GROUND",
            destination=request_data.destination,
            version=request_data.version,
            checksum=request_data.checksum,
            data=request_data.data,
            size_bytes=size_bytes,
            verified=is_verified,
            timestamp=current_time,
            uploaded_at=current_time
        )
        
        return response

    return app