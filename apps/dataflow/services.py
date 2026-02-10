import httpx
from apps.core.models import CommandMessage, EventMessage, EventMessage, StatusMessage, TelemetryMessage
# from django.utils import timezone

from apps.dataflow.schemas import CommandMessageSchema, TelemetryMessageSchema, EventMessageSchema, StatusMessageSchema


async def store_command_data(data: CommandMessageSchema):
    data = CommandMessage.objects.acreate(
        message_type=data.message_type,
        source=data.source,
        destination=data.destination,
        timestamp=data.timestamp,
        subsystem=data.subsystem,
        parameters=data.parameters,
        status=data.status,
        execution_time=data.execution_time,
        command_type=data.command_type
    )
    return data

async def store_telemetry_data(data: TelemetryMessageSchema):
    data = TelemetryMessage.objects.acreate(
        message_type=data.message_type,
        source=data.source,
        destination=data.destination,
        timestamp=data.timestamp,
        subsystem=data.subsystem,
        module=data.module,
        value=data.value,
        unit=data.unit,
        valid=data.valid
    )
    return data

async def store_event_data(data: EventMessageSchema):
    data = EventMessage.objects.acreate(
        message_type=data.message_type,
        source=data.source,
        destination=data.destination,
        timestamp=data.timestamp,
        subsystem=data.subsystem,
        severity=data.severity,
        code=data.code,
        description=data.description
    )
    return data

    
async def store_status_data(data: StatusMessageSchema):
    data = StatusMessage.objects.acreate(
        message_type=data.message_type,
        source=data.source,
        destination=data.destination,
        timestamp=data.timestamp,
        subsystem=data.subsystem,
        state=data.state,
        mode=data.mode
    )
    return data

async def send_data(url: str, data: dict):
    async with httpx.AsyncClient() as client: # possible timeout addition
        response = await client.post(url, json=data)
        response.raise_for_status()
    return response.json()


async def get_data(url: str, params: dict):
    async with httpx.AsyncClient() as client: # possible timeout addition
        response = await client.get(url, params=params)
        response.raise_for_status()
    return response.json()
        