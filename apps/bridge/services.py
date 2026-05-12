# apps/bridge/services.py
"""Services for bridge operations including routing, storage, and external communication."""

import logging

import httpx

from apps.audit.services import create_log
from apps.control.models import (CommandMessage, EventMessage, StatusMessage,
                                 TelemetryMessage)

from .clients import ServiceClientPool
from .config import APIPaths, ServiceRegistry, VALID_DESTINATIONS
from .exceptions import ExternalServiceError, InvalidDestinationError
from .schemas import (CommandMessageSchema, EventMessageSchema,
                      StatusMessageSchema, TelemetryMessageSchema)

logger = logging.getLogger(__name__)


async def store_command_data(data: CommandMessageSchema) -> CommandMessage:
    """Store command data in the database.

    Args:
        data: Command message schema containing the command data.

    Returns:
        The created CommandMessage model instance.
    """
    command = await CommandMessage.objects.acreate(
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
    logger.info(f"Command stored: ID={command.id}, type={data.command_type}")
    return command


async def store_telemetry_data(data: TelemetryMessageSchema) -> TelemetryMessage:
    """Store telemetry data in the database.

    Args:
        data: Telemetry message schema containing the telemetry data.

    Returns:
        The created TelemetryMessage model instance.
    """
    telemetry = await TelemetryMessage.objects.acreate(
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
    logger.debug(f"Telemetry stored: ID={telemetry.id}, {data.subsystem}.{data.module}={data.value}")
    return telemetry


async def store_event_data(data: EventMessageSchema) -> EventMessage:
    """Store event data in the database.

    Args:
        data: Event message schema containing the event data.

    Returns:
        The created EventMessage model instance.
    """
    event = await EventMessage.objects.acreate(
        message_type=data.message_type,
        source=data.source,
        destination=data.destination,
        timestamp=data.timestamp,
        subsystem=data.subsystem,
        severity=data.severity,
        code=data.code,
        description=data.description
    )
    logger.info(f"Event stored: ID={event.id}, severity={data.severity}, code={data.code}")
    return event


async def store_status_data(data: StatusMessageSchema) -> StatusMessage:
    """Store status data in the database.

    Args:
        data: Status message schema containing the status data.

    Returns:
        The created StatusMessage model instance.
    """
    status = await StatusMessage.objects.acreate(
        message_type=data.message_type,
        source=data.source,
        destination=data.destination,
        timestamp=data.timestamp,
        subsystem=data.subsystem,
        state=data.state,
        mode=data.mode
    )
    logger.info(f"Status stored: ID={status.id}, subsystem={data.subsystem}, mode={data.mode}")
    return status


def _get_service_and_path(destination: str, api_path: str):
    """Return the service endpoint and API path for a destination.

    Args:
        destination: Destination service identifier.
        api_path: API path constant.

    Returns:
        Tuple of (service_endpoint, api_path).

    Raises:
        InvalidDestinationError: If the destination is invalid or not configured.
    """
    if destination not in VALID_DESTINATIONS:
        raise InvalidDestinationError(f"Invalid destination: {destination}")

    service = ServiceRegistry.get_service(destination)
    if not service:
        raise InvalidDestinationError(f"No service configured for: {destination}")

    return service, api_path


async def send_data(url: str, data: dict, timeout: int = 30) -> dict:
    """Send a POST request to an external service.

    Args:
        url: Full URL to send the request to.
        data: JSON data to send.
        timeout: Request timeout in seconds.

    Returns:
        Response JSON as a dictionary.

    Raises:
        ExternalServiceError: If the request fails.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            raise ExternalServiceError(f"Timeout connecting to {url}") from e
        except httpx.HTTPStatusError as e:
            raise ExternalServiceError(f"HTTP {e.response.status_code} from {url}: {e.response.text}") from e
        except Exception as e:
            raise ExternalServiceError(f"Failed to send data to {url}: {str(e)}") from e


async def get_data(url: str, params: dict, timeout: int = 30) -> dict:
    """Send a GET request to an external service.

    Args:
        url: Full URL to send the request to.
        params: Query parameters.
        timeout: Request timeout in seconds.

    Returns:
        Response JSON as a dictionary.

    Raises:
        ExternalServiceError: If the request fails.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            raise ExternalServiceError(f"Timeout connecting to {url}") from e
        except httpx.HTTPStatusError as e:
            raise ExternalServiceError(f"HTTP {e.response.status_code} from {url}: {e.response.text}") from e
        except Exception as e:
            raise ExternalServiceError(f"Failed to get data from {url}: {str(e)}") from e


async def route_command(destination: str, command_data: dict) -> dict:
    """Route a command to the appropriate external service.

    Args:
        destination: Target destination service.
        command_data: Command data dictionary.

    Returns:
        Response from the external service.
    """
    service, api_path = _get_service_and_path(destination, APIPaths.COMMANDS)
    client = ServiceClientPool.get_client(destination, service)
    return await client.post(api_path, command_data)


async def route_telemetry_request(destination: str, params: dict) -> dict:
    """Request telemetry data from an external service.

    Args:
        destination: Source destination service.
        params: Request parameters.

    Returns:
        Telemetry data from the external service.
    """
    service, api_path = _get_service_and_path(destination, APIPaths.TELEMETRY)
    client = ServiceClientPool.get_client(destination, service)
    return await client.get(api_path, params)


async def route_event_request(destination: str, params: dict) -> dict:
    """Request event data from an external service.

    Args:
        destination: Source destination service.
        params: Request parameters.

    Returns:
        Event data from the external service.
    """
    service, api_path = _get_service_and_path(destination, APIPaths.EVENTS)
    client = ServiceClientPool.get_client(destination, service)
    return await client.get(api_path, params)


async def route_status_request(destination: str, params: dict) -> dict:
    """Request status data from an external service.

    Args:
        destination: Source destination service.
        params: Request parameters.

    Returns:
        Status data from the external service.
    """
    service, api_path = _get_service_and_path(destination, APIPaths.STATUS)
    client = ServiceClientPool.get_client(destination, service)
    return await client.get(api_path, params)