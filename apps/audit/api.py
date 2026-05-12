# apps/audit/api.py
"""API endpoints for log management using Django Ninja."""

from typing import List
from ninja import Router, Query
from asgiref.sync import sync_to_async

from .models import LogEntry
from .serializers import LogSerializer, LogDetailSerializer
from .schemas import LogFilterSchema, LogSchema, LogDetailSchema, LogStatisticsSchema
from .services import LogService, create_log

# Router instance for log management endpoints
router = Router(tags=["Log Management"])


@router.get('/', response={200: List[LogSchema], 500: dict})
async def get_all_logs(request, filters: LogFilterSchema = Query(...)):
    """
    Retrieve all log entries with optional filtering.

    Available filters:
        - timestamp_gte: Start date for log timestamp range
        - timestamp_lte: End date for log timestamp range
        - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - logger: Name of the logger that created the entry
        - module: Module name where the log originated
        - function: Function name (performs contains search)
        - message: Message text (performs contains search)
        - request_path: Request path (performs contains search)
        - has_exception: Filter entries that contain exception data
        - is_error: Filter entries at ERROR or CRITICAL level

    Args:
        request: The HTTP request object.
        filters: Query parameters for filtering log entries.

    Returns:
        Tuple of (HTTP status code, response data).
    """
    try:
        logs = LogEntry.objects.all()
        logs = filters.filter(logs)

        # Convert async queryset to list
        logs_list = await sync_to_async(list)(logs)
        serializer = LogSerializer(logs_list, request=request)

        await create_log(
            level='INFO',
            logger='audit-api',
            module='audit.api',
            function='get_all_logs',
            message=f'Retrieved {len(logs_list)} log entries',
            request=request,
        )

        return 200, serializer.serialize()

    except Exception as e:
        await create_log(
            level='ERROR',
            logger='audit-api',
            module='audit.api',
            function='get_all_logs',
            message=f'Error retrieving logs: {e}',
            request=request,
            exception=e,
        )
        return 500, {'error': 'Error while retrieving logs', 'detail': str(e)}


@router.get('/filter', response={200: List[LogSchema], 500: dict})
async def get_filtered_logs(request, filters: LogFilterSchema = Query(...)):
    """
    Retrieve filtered log entries.

    Compatibility wrapper around get_all_logs endpoint.

    Args:
        request: The HTTP request object.
        filters: Query parameters for filtering log entries.

    Returns:
        Tuple of (HTTP status code, response data).
    """
    return await get_all_logs(request, filters)


@router.get('/errors', response={200: List[LogSchema]})
async def get_errors(request, limit: int = 100):
    """
    Retrieve error and critical level log entries.

    Args:
        request: The HTTP request object.
        limit: Maximum number of entries to return (default: 100).

    Returns:
        Tuple of (HTTP status code, response data).
    """
    logs = await sync_to_async(list)(
        LogEntry.objects.errors_or_higher()[:limit]
    )
    serializer = LogSerializer(logs, request=request)
    return 200, serializer.serialize()


@router.get('/exceptions', response={200: List[LogSchema]})
async def get_exceptions(request, limit: int = 100):
    """
    Retrieve log entries that contain exception information.

    Args:
        request: The HTTP request object.
        limit: Maximum number of entries to return (default: 100).

    Returns:
        Tuple of (HTTP status code, response data).
    """
    logs = await sync_to_async(list)(
        LogEntry.objects.with_exceptions()[:limit]
    )
    serializer = LogSerializer(logs, request=request)
    return 200, serializer.serialize()


@router.get('/statistics', response={200: LogStatisticsSchema})
async def get_statistics(request, hours: int = 24):
    """
    Retrieve log statistics for the last N hours.

    Args:
        request: The HTTP request object.
        hours: Number of hours to analyze (default: 24).

    Returns:
        Tuple of (HTTP status code, statistics data).
    """
    stats = await LogService.get_statistics(hours)

    await create_log(
        level='DEBUG',
        logger='audit-api',
        module='audit.api',
        function='get_statistics',
        message=f'Statistics retrieved for last {hours} hours',
        request=request,
    )

    return 200, stats


@router.delete('/cleanup', response={200: dict})
async def cleanup_old_logs(request, days: int = 30):
    """
    Delete log entries older than the specified number of days.

    Args:
        request: The HTTP request object.
        days: Age threshold in days (entries older than this are deleted).

    Returns:
        Tuple of (HTTP status code, dict with deletion count and days).
    """
    deleted = await LogService.cleanup_old_logs(days)

    await create_log(
        level='INFO',
        logger='audit-api',
        module='audit.api',
        function='cleanup_old_logs',
        message=f'Deleted {deleted} log entries older than {days} days',
        request=request,
    )

    return 200, {'deleted': deleted, 'days': days}


@router.get('/{log_id}', response={200: LogDetailSchema, 404: dict})
async def get_log_detail(request, log_id: int):
    """
    Retrieve detailed information for a specific log entry by ID.

    Args:
        request: The HTTP request object.
        log_id: Primary key of the log entry.

    Returns:
        Tuple of (HTTP status code, response data or error dict).
    """
    try:
        log = await sync_to_async(LogEntry.objects.get)(id=log_id)
        serializer = LogDetailSerializer(log, request=request)
        return 200, serializer.serialize()

    except LogEntry.DoesNotExist:
        return 404, {'error': f'Log entry {log_id} not found'}