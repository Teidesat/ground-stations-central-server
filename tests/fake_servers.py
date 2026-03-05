from fastapi import FastAPI

from apps.dataflow.schemas import EventMessageSchema, StatusMessageSchema, TelemetryMessageSchema

def create_fake_server():
    app = FastAPI()

    @app.get("/stream/telemetry")
    async def telemetry(destination: str = None, **kwargs) -> TelemetryMessageSchema:
        telemetry_message = TelemetryMessageSchema(
            message_type="TM",
            source="TEST-SAT-1",
            destination=destination,
            timestamp="2026-01-01T00:00:00Z",
            subsystem="TEST_SUBSYSTEM",
            module="TEST_MODULE",
            value=42.0,
            unit="units",
            valid=True
        )
        return telemetry_message
    
    @app.get("/events")
    async def events(destination: str = None, **kwargs) -> EventMessageSchema:
        event_message = EventMessageSchema(
            message_type="EV",
            source="TEST-SAT-1",
            destination=destination,
            timestamp="2026-01-01T00:00:00Z",
            subsystem="TEST_SUBSYSTEM",
            severity="INFO",
            code="TEST_EVENT",
            description="This is a test event"
        )
        return event_message


    @app.get("/status")
    async def status(destination: str = None, **kwargs) -> StatusMessageSchema:
        status_message = StatusMessageSchema(
            message_type="SM",
            source="TEST-SAT-1",
            destination=destination,
            timestamp="2026-01-01T00:00:00Z",
            subsystem="TEST_SUBSYSTEM",
            state={"key": "value"},
            mode="NOMINAL"
        )
        return status_message

    return app