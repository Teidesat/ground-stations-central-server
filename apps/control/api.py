# apps/control/api.py
"""API endpoints for mission control functionality."""

from typing import List

from asgiref.sync import sync_to_async
from ninja import Router, Query
from ninja.pagination import paginate

from .models import (CommandMessage, EventMessage, SoftwareUpdate, StatusMessage,
                     TelemetryMessage)
from .schemas import (
    CommandCreateSchema,
    CommandFilterSchema,
    CommandSchema,
    CommandUpdateSchema,
    EventCreateSchema,
    EventFilterSchema,
    EventSchema,
    SoftwareUpdateCreateSchema,
    SoftwareUpdateSchema,
    StatusCreateSchema,
    StatusSchema,
    SystemMetricsSchema,
    TelemetryCreateSchema,
    TelemetryFilterSchema,
    TelemetrySchema,
)
from .services import CommandService, EventService, SystemService, TelemetryService

router = Router(tags=["Mission Control"])


@router.get('/telemetry', response={200: List[TelemetrySchema]})
@paginate
async def get_telemetry(request, filters: TelemetryFilterSchema = Query(...)):
    """Retrieve telemetry data with optional filters.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering telemetry records.

    Returns:
        List of telemetry message dictionaries.
    """
    qs = TelemetryMessage.objects.all()
    qs = filters.filter(qs)
    return await sync_to_async(list)(qs)


@router.post('/telemetry', response={201: TelemetrySchema})
async def create_telemetry(request, data: TelemetryCreateSchema):
    """Create a new telemetry reading.

    Args:
        request: HTTP request object.
        data: Telemetry data for creation.

    Returns:
        Tuple of (HTTP status code, created telemetry object).
    """
    telemetry = await sync_to_async(TelemetryMessage.objects.create)(
        subsystem=data.subsystem,
        module=data.module,
        value=data.value,
        unit=data.unit,
        raw_data=data.raw_data,
        source=data.source,
        destination=data.destination
    )
    return 201, telemetry


@router.get('/telemetry/latest', response=List[TelemetrySchema])
async def latest_telemetry(request, subsystem: str = None, limit: int = 10):
    """Retrieve the latest telemetry readings.

    Args:
        request: HTTP request object.
        subsystem: Optional subsystem filter.
        limit: Maximum number of records to return.

    Returns:
        List of latest telemetry readings.
    """
    data = await sync_to_async(TelemetryService.get_latest_telemetry)(subsystem, limit)
    return data


@router.get('/telemetry/health', response=dict)
async def subsystem_health(request):
    """Retrieve health status for all subsystems.

    Args:
        request: HTTP request object.

    Returns:
        Dictionary mapping subsystem names to health status.
    """
    return await sync_to_async(TelemetryService.get_subsystem_health)()


@router.get('/status', response=List[StatusSchema])
@paginate
async def get_status(request):
    """Retrieve all status messages.

    Args:
        request: HTTP request object.

    Returns:
        List of status message dictionaries.
    """
    return await sync_to_async(list)(StatusMessage.objects.all())


@router.post('/status', response={201: StatusSchema})
async def create_status(request, data: StatusCreateSchema):
    """Create a new status message.

    Args:
        request: HTTP request object.
        data: Status data for creation.

    Returns:
        Tuple of (HTTP status code, created status object).
    """
    status = await sync_to_async(StatusMessage.objects.create)(
        subsystem=data.subsystem,
        state=data.state,
        mode=data.mode,
        source=data.source,
        destination=data.destination
    )
    return 201, status


@router.get('/commands', response=List[CommandSchema])
@paginate
async def get_commands(request, filters: CommandFilterSchema = Query(...)):
    """Retrieve commands with optional filters.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering command records.

    Returns:
        List of command message dictionaries.
    """
    qs = CommandMessage.objects.all()
    qs = filters.filter(qs)
    return await sync_to_async(list)(qs)


@router.post('/commands', response={201: CommandSchema})
async def create_command(request, data: CommandCreateSchema):
    """Send a new command.

    Args:
        request: HTTP request object.
        data: Command data for creation.

    Returns:
        Tuple of (HTTP status code, created command object).
    """
    command = await sync_to_async(CommandService.send_command)(
        command_type=data.command_type,
        subsystem=data.subsystem,
        parameters=data.parameters
    )
    return 201, command


@router.put('/commands/{command_id}/status', response={200: CommandSchema})
async def update_command_status(request, command_id: int, data: CommandUpdateSchema):
    """Update command execution status.

    Args:
        request: HTTP request object.
        command_id: Primary key of the command to update.
        data: Status update data.

    Returns:
        Tuple of (HTTP status code, updated command or error dict).
    """
    command = await sync_to_async(CommandService.update_command_status)(
        command_id, data.status, data.execution_time
    )
    if command:
        return 200, command
    return 404, {"error": "Command not found"}


@router.get('/commands/pending', response=List[CommandSchema])
async def pending_commands(request):
    """Retrieve all pending commands.

    Args:
        request: HTTP request object.

    Returns:
        List of pending command messages.
    """
    return await sync_to_async(CommandService.get_pending_commands)()


@router.get('/commands/statistics', response=dict)
async def command_statistics(request):
    """Retrieve command execution statistics.

    Args:
        request: HTTP request object.

    Returns:
        Dictionary with command statistics (total, executed, failed, pending, success_rate).
    """
    return await sync_to_async(CommandMessage.objects.get_statistics)()


@router.get('/events', response=List[EventSchema])
@paginate
async def get_events(request, filters: EventFilterSchema = Query(...)):
    """Retrieve events with optional filters.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering event records.

    Returns:
        List of event message dictionaries.
    """
    qs = EventMessage.objects.all()
    qs = filters.filter(qs)
    return await sync_to_async(list)(qs)


@router.post('/events', response={201: EventSchema})
async def create_event(request, data: EventCreateSchema):
    """Create a new event.

    Args:
        request: HTTP request object.
        data: Event data for creation.

    Returns:
        Tuple of (HTTP status code, created event object).
    """
    event = await sync_to_async(EventService.create_event)(
        subsystem=data.subsystem,
        severity=data.severity,
        code=data.code,
        description=data.description
    )
    return 201, event


@router.get('/events/alerts', response=List[EventSchema])
async def active_alerts(request):
    """Retrieve active alerts (critical events and warnings from the last hour).

    Args:
        request: HTTP request object.

    Returns:
        List of recent critical and warning events.
    """
    return await sync_to_async(EventService.get_active_alerts)()


@router.get('/metrics', response=SystemMetricsSchema)
async def system_metrics(request):
    """Retrieve comprehensive system metrics.

    Args:
        request: HTTP request object.

    Returns:
        SystemMetricsSchema with telemetry count, alerts, pending commands, etc.
    """
    return await sync_to_async(SystemService.get_system_metrics)()


@router.get('/updates', response=List[SoftwareUpdateSchema])
@paginate
async def get_updates(request):
    """Retrieve all software updates.

    Args:
        request: HTTP request object.

    Returns:
        List of software update schemas.
    """
    return await sync_to_async(list)(SoftwareUpdate.objects.all())


@router.post('/updates', response={201: SoftwareUpdateSchema})
async def upload_update(request, data: SoftwareUpdateCreateSchema):
    """Upload a new software update.

    Args:
        request: HTTP request object.
        data: Software update data with Base64-encoded content.

    Returns:
        Tuple of (HTTP status code, created software update object).
    """
    import base64
    binary_data = base64.b64decode(data.data)

    update = await sync_to_async(SoftwareUpdate.objects.create)(
        version=data.version,
        checksum=data.checksum,
        size_bytes=len(binary_data),
        data=binary_data
    )
    return 201, update