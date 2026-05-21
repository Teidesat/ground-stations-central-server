# apps/bridge/api.py
"""API endpoints for dataflow operations including historical data and real-time streaming."""

import logging
from typing import List

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from ninja import Router, Query

from apps.audit.services import create_log
from apps.control.models import (CommandMessage, EventMessage, StatusMessage,
                                 TelemetryMessage, SoftwareUpdateMessage)
from apps.control.serializers import *

from .clients import ExternalServiceClient
from .config import APIPaths, ServiceRegistry, VALID_DESTINATIONS
from .exceptions import ExternalServiceError, InvalidDestinationError
from .schemas import (
    CommandFilterSchema,
    CommandMessageSchema,
    EventFilterSchema,
    EventMessageSchema,
    EventRequestSchema,
    StatusFilterSchema,
    StatusMessageSchema,
    StatusRequestSchema,
    TelemetryFilterSchema,
    TelemetryMessageSchema,
    TelemetryRequestSchema,
    SoftwareUpdateFilterSchema,
    SoftwareUpdateMessageSchema,
    SoftwareUpdateRequestSchema,
    SoftwareUpdateSendRequestSchema
)
from .services import (
    store_command_data,
    store_event_data,
    store_status_data,
    store_telemetry_data,
    store_software_update_data,
)

logger = logging.getLogger(__name__)
router = Router(tags=["Data Flow"])


def _get_service_client(destination: str) -> ExternalServiceClient:
    """Return the service client for a given destination.

    Args:
        destination: The target service destination name.

    Returns:
        ExternalServiceClient instance configured for the destination.

    Raises:
        InvalidDestinationError: If the destination is not registered.
    """
    service = ServiceRegistry.get_service(destination)
    if not service:
        raise InvalidDestinationError(f"Invalid destination: {destination}")
    return ExternalServiceClient(service)


@router.get("/historical/telemetry", response=List[TelemetryMessageSchema])
async def get_telemetry_data(request, filters: TelemetryFilterSchema = Query(...)):
    """Retrieve historical telemetry data from the database.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering telemetry records.

    Returns:
        List of telemetry message dictionaries.
    """
    qs = TelemetryMessage.objects.all()
    qs = filters.filter(qs)

    serializer = TelemetrySerializer()
    result = [serializer.serialize_instance(item) async for item in qs]

    await create_log(
        level='INFO',
        logger='bridge-api',
        module='bridge.api',
        function='get_telemetry_data',
        message=f'Retrieved {len(result)} telemetry records',
        request=request,
    )

    return result


@router.get("/historical/events", response=List[EventMessageSchema])
async def get_event_data(request, filters: EventFilterSchema = Query(...)):
    """Retrieve historical event data from the database.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering event records.

    Returns:
        List of event message dictionaries.
    """
    qs = EventMessage.objects.all()
    qs = filters.filter(qs)

    serializer = EventSerializer()
    result = [serializer.serialize_instance(item) async for item in qs]

    await create_log(
        level='INFO',
        logger='bridge-api',
        module='bridge.api',
        function='get_event_data',
        message=f'Retrieved {len(result)} event records',
        request=request,
    )

    return result


@router.get("/historical/status", response=List[StatusMessageSchema])
async def get_status_data(request, filters: StatusFilterSchema = Query(...)):
    """Retrieve historical system status data from the database.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering status records.

    Returns:
        List of status message dictionaries.
    """
    qs = StatusMessage.objects.all()
    qs = filters.filter(qs)

    serializer = StatusSerializer()
    result = [serializer.serialize_instance(item) async for item in qs]
    await create_log(
        level='INFO',
        logger='bridge-api',
        module='bridge.api',
        function='get_status_data',
        message=f'Retrieved {len(result)} status records',
        request=request,
    )

    return result


@router.get("/historical/commands", response=List[CommandMessageSchema])
async def get_command_data(request, filters: CommandFilterSchema = Query(...)):
    """Retrieve historical command data from the database.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering command records.

    Returns:
        List of command message dictionaries.
    """
    qs = CommandMessage.objects.all()
    qs = filters.filter(qs)

    serializer = CommandSerializer()
    result = [serializer.serialize_instance(item) async for item in qs]

    await create_log(
        level='INFO',
        logger='bridge-api',
        module='bridge.api',
        function='get_command_data',
        message=f'Retrieved {len(result)} command records',
        request=request,
    )

    return result

@router.get("/historical/software_updates")
async def get_historical_software_updates(request, filters: SoftwareUpdateFilterSchema = Query(...)):
    """Retrieve historical software update data from the database."""
    from apps.control.models import SoftwareUpdateMessage
    
    qs = SoftwareUpdateMessage.objects.all()
    qs = filters.filter(qs)
    
    serializer = SoftwareUpdateSerializer()
    result = [serializer.serialize_instance(item) async for item in qs]
    
    await create_log(
        level='INFO',
        logger='bridge-api',
        module='bridge.api.software_updates',
        function='get_historical_software_updates',
        message=f'Retrieved {len(result)} software update records',
        request=request
    )
    
    return result


@router.post("/stream/commands")
async def send_command_data(request, data: CommandMessageSchema):
    """Send a command to an external service in real-time.

    Args:
        request: HTTP request object.
        data: Command message schema containing the command data.

    Returns:
        JSON response with status and message.
    """
    try:
        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api',
            function='send_command_data',
            message=f'Sending command to {data.destination}',
            request=request
        )

        command_dict = data.dict()
        if command_dict.get('timestamp'):
            command_dict['timestamp'] = command_dict['timestamp'].isoformat()
        if command_dict.get('execution_time'):
            command_dict['execution_time'] = command_dict['execution_time'].isoformat() if command_dict['execution_time'] else None

        client = _get_service_client(data.destination)
        response = await client.post(APIPaths.COMMANDS, command_dict)

        await store_command_data(data)

        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api',
            function='send_command_data',
            message=f'Command sent successfully to {data.destination}',
            request=request
        )

        return {'status': 'success', 'message': response, 'destination': data.destination}

    except InvalidDestinationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except ExternalServiceError as e:
        return JsonResponse({'error': 'Failed to send command', 'detail': str(e)}, status=502)
    except Exception as e:
        await create_log(
            level='ERROR',
            logger='bridge-api',
            module='bridge.api',
            function='send_command_data',
            message=f'Unexpected error: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Internal server error'}, status=500)


@router.get("/stream/telemetry")
async def get_live_telemetry(request, params: TelemetryRequestSchema = Query(...)):
    """Retrieve live telemetry data from an external service.

    Args:
        request: HTTP request object.
        params: Request parameters including destination and subsystem.

    Returns:
        JSON response with telemetry data.
    """
    try:
        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api',
            function='get_live_telemetry',
            message=f'Fetching live telemetry from {params.destination}',
            request=request
        )

        client = _get_service_client(params.destination)
        response = await client.get(APIPaths.TELEMETRY, params.dict())

        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api',
            function='get_live_telemetry',
            message='Live telemetry retrieved successfully',
            request=request
        )

        telemetry_data = TelemetryMessageSchema(**response)
        await store_telemetry_data(telemetry_data)

        return {'status': 'success', 'message': response}

    except InvalidDestinationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except ExternalServiceError as e:
        return JsonResponse({'error': 'Failed to fetch telemetry', 'detail': str(e)}, status=502)
    except Exception as e:
        await create_log(
            level='ERROR',
            logger='bridge-api',
            module='bridge.api',
            function='get_live_telemetry',
            message=f'Error: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Internal server error'}, status=500)


@router.get("/stream/events")
async def get_live_events(request, params: EventRequestSchema = Query(...)):
    """Retrieve live event data from an external service.

    Args:
        request: HTTP request object.
        params: Request parameters including destination and subsystem.

    Returns:
        JSON response with event data.
    """
    try:
        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api',
            function='get_live_events',
            message=f'Fetching live events from {params.destination}',
            request=request
        )

        client = _get_service_client(params.destination)
        response = await client.get(APIPaths.EVENTS, params.dict())

        event_data = EventMessageSchema(**response)
        await store_event_data(event_data)

        return {'status': 'success', 'message': response}

    except InvalidDestinationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except ExternalServiceError as e:
        return JsonResponse({'error': 'Failed to fetch events', 'detail': str(e)}, status=502)
    except Exception as e:
        await create_log(
            level='ERROR',
            logger='bridge-api',
            module='bridge.api',
            function='get_live_events',
            message=f'Error: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Internal server error'}, status=500)


@router.get("/stream/status")
async def get_live_status(request, params: StatusRequestSchema = Query(...)):
    """Retrieve live system status from an external service.

    Args:
        request: HTTP request object.
        params: Request parameters including destination and subsystem.

    Returns:
        JSON response with status data.
    """
    try:
        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api',
            function='get_live_status',
            message=f'Fetching live status from {params.destination}',
            request=request
        )

        client = _get_service_client(params.destination)
        response = await client.get(APIPaths.STATUS, params.dict())

        status_data = StatusMessageSchema(**response)
        await store_status_data(status_data)

        return {'status': 'success', 'message': response}

    except InvalidDestinationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except ExternalServiceError as e:
        return JsonResponse({'error': 'Failed to fetch status', 'detail': str(e)}, status=502)
    except Exception as e:
        await create_log(
            level='ERROR',
            logger='bridge-api',
            module='bridge.api',
            function='get_live_status',
            message=f'Error: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Internal server error'}, status=500)
    
@router.get("/stream/software_update")
async def get_live_software_update(request, params: SoftwareUpdateRequestSchema = Query(...)):
    """Retrieve live software update from an external service.
    
    Args:
        request: HTTP request object.
        destination: Target destination service.
        version: Specific version to fetch (optional).
        
    Returns:
        JSON response with software update data.
    """
    try:
        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api.software_updates',
            function='get_live_software_update',
            message=f'Fetching live software update from {params.destination}',
            request=request
        )
        
        client = _get_service_client(params.destination)
        response = await client.get(APIPaths.SOFTWARE_UPDATE, params.dict())

        if 'checksum' in response and len(response['checksum']) > 64:
            await create_log(
                level='WARNING',
                logger='bridge-api',
                module='bridge.api.software_updates',
                function='get_live_software_update',
                message=f'Checksum too long ({len(response["checksum"])} chars), truncating to 64',
                request=request
            )
            response['checksum'] = response['checksum'][:64]
        
        update_data = SoftwareUpdateMessageSchema(**response)
        await store_software_update_data(update_data)
        
        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api.software_updates',
            function='get_live_software_update',
            message=f'Successfully stored software update version {update_data.version}',
            request=request
        )
        
        return {
            'status': 'success',
            'data': response,
            'stored': True
        }
        
    except InvalidDestinationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except ExternalServiceError as e:
        return JsonResponse(
            {'error': 'Failed to fetch software update', 'detail': str(e)}, 
            status=502
        )
    except ValueError as e:
        return JsonResponse(
            {'error': 'Invalid response format', 'detail': str(e)}, 
            status=500
        )
    except Exception as e:
        await create_log(
            level='ERROR',
            logger='bridge-api',
            module='bridge.api.software_updates',
            function='get_live_software_update',
            message=f'Error: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Internal server error'}, status=500)


@router.post("/stream/software_update")
async def send_software_update(request, data: SoftwareUpdateSendRequestSchema):
    """Send a software update.
    
    Args:
        request: HTTP request object.
        params: Data parameters including version and checksum for do the update.
        
    Returns:
        Verification the update result.
    """
    try:
        await create_log(
            level='INFO',
            logger='bridge-api',
            module='bridge.api.software_updates',
            function='send_software_update',
            message=f'Sending software update version {data.version}',
            request=request
        )

        client = _get_service_client(data.destination)
        response = await client.post(APIPaths.SOFTWARE_UPDATE, data.dict())

        if response['verified'] == True:
            update_data = SoftwareUpdateMessageSchema(**response)
            await store_software_update_data(update_data)

            await create_log(
                level='INFO',
                logger='bridge-api',
                module='bridge.api.software_updates',
                function='send_software_update',
                message=f'Software update {data.version} {"verified" if response["verified"] else "unverified"} successfully',
                request=request
            )

            return {'status': 'success', 'message': response, 'destination': data.destination}
        
        await create_log(
            level='ERROR',
            logger='bridge-api',
            module='bridge.api.software_updates',
            function='send_software_update',
            message=f'Error produced sending software update {data.version} to {data.destination} ',
            request=request
        )

        return JsonResponse({'error': 'Failed to send software update'}, status=502)
        
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        await create_log(
            level='ERROR',
            logger='bridge-api',
            module='bridge.api.software_updates',
            function='send_software_update',
            message=f'Error: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Internal server error'}, status=500)


@router.get("/destinations", response=List[str])
async def get_available_destinations(request):
    """Return the list of available destinations for data routing.

    Args:
        request: HTTP request object.

    Returns:
        List of destination name strings.
    """
    return VALID_DESTINATIONS