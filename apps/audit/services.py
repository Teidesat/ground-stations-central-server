# apps/audit/services.py
"""Services for log management and asynchronous log entry creation."""

import logging
import traceback
from typing import Optional, Dict, Any

from asgiref.sync import sync_to_async
from django.db.models import Count
from django.utils import timezone

from .models import LogEntry, LogLevel

_internal_logger = logging.getLogger(__name__)


def _get_client_ip(request) -> Optional[str]:
    """Extract client IP address from HTTP request.

    Handles proxy headers like X-Forwarded-For.

    Args:
        request: The HTTP request object.

    Returns:
        Client IP address string, or None if not available.
    """
    if not request:
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


async def create_log(
    *,
    level: str,
    logger: str,
    module: str,
    function: str,
    message: str,
    request=None,
    exception: Optional[Exception] = None,
    extra_data: Optional[Dict[str, Any]] = None,
    request_status_code: Optional[int] = None,
) -> LogEntry:
    """Create a log entry asynchronously.

    Args:
        level: Log severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        logger: Name of the logger.
        module: Source module name.
        function: Function/method name.
        message: Log message content.
        request: Optional HTTP request for context extraction.
        exception: Optional exception to capture traceback.
        extra_data: Optional additional structured data.
        request_status_code: Optional HTTP status code.

    Returns:
        The created LogEntry instance.
    """
    # Validate and normalize log level
    if level not in [l.value for l in LogLevel]:
        level = LogLevel.INFO

    # Extract exception information if provided
    exception_type = None
    exception_message = None
    exception_stack_trace = None

    if exception:
        exception_type = type(exception).__name__
        exception_message = str(exception)
        exception_stack_trace = traceback.format_exc()

    # Extract request context if available
    request_method = None
    request_path = None
    request_client_ip = None
    request_user = None

    if request:
        request_method = getattr(request, 'method', None)
        request_path = getattr(request, 'path', None)
        request_client_ip = _get_client_ip(request)
        if hasattr(request, 'user') and hasattr(request.user, 'username'):
            request_user = request.user.username

    # Create the log entry asynchronously
    log_entry = await LogEntry.objects.acreate(
        timestamp=timezone.now(),
        level=level,
        logger=logger,
        module=module,
        function=function,
        message=message,
        request_method=request_method,
        request_path=request_path,
        request_status_code=request_status_code,
        request_client_ip=request_client_ip,
        request_user=request_user,
        exception_type=exception_type,
        exception_message=exception_message,
        exception_stack_trace=exception_stack_trace,
        extra_data=extra_data,
    )

    # Also log to Python's standard logging system
    log_func = getattr(_internal_logger, level.lower(), _internal_logger.info)
    log_func(f"[{module}.{function}] {message}")

    return log_entry


class LogService:
    """Service class for log operations including statistics and cleanup."""

    @staticmethod
    async def get_statistics(hours: int = 24) -> Dict[str, Any]:
        """Get log statistics for the last N hours.

        Args:
            hours: Number of hours to analyze (default: 24).

        Returns:
            Dictionary containing:
            - total_count: Total number of logs in time range
            - by_level: Counts per log level
            - by_logger: Top 10 logger counts
            - by_module: Top 10 module counts
            - error_rate: Percentage of ERROR/CRITICAL logs
            - time_range: First and last log timestamps
        """
        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        queryset = LogEntry.objects.filter(timestamp__gte=cutoff)

        # Count logs by level
        by_level = {}
        for level in LogLevel.values:
            count = await sync_to_async(queryset.filter(level=level).count)()
            if count > 0:
                by_level[level] = count

        # Count logs by logger (top 10)
        by_logger = {}
        logger_counts = await sync_to_async(
            lambda: list(queryset.values('logger').annotate(
                count=Count('id')
            ).order_by('-count')[:10])
        )()
        for item in logger_counts:
            by_logger[item['logger']] = item['count']

        # Count logs by module (top 10)
        by_module = {}
        module_counts = await sync_to_async(
            lambda: list(queryset.values('module').annotate(
                count=Count('id')
            ).order_by('-count')[:10])
        )()
        for item in module_counts:
            by_module[item['module']] = item['count']

        # Calculate totals and error rate
        total = await sync_to_async(queryset.count)()
        errors = await sync_to_async(queryset.filter(level__in=['ERROR', 'CRITICAL']).count)()
        error_rate = (errors / total * 100) if total > 0 else 0

        # Get time range
        first_log = await sync_to_async(lambda: queryset.order_by('timestamp').first())()
        last_log = await sync_to_async(lambda: queryset.order_by('-timestamp').first())()

        return {
            'total_count': total,
            'by_level': by_level,
            'by_logger': by_logger,
            'by_module': by_module,
            'error_rate': round(error_rate, 2),
            'time_range': {
                'from': first_log.timestamp.isoformat() if first_log else None,
                'to': last_log.timestamp.isoformat() if last_log else None,
            }
        }

    @staticmethod
    async def cleanup_old_logs(days: int) -> int:
        """Delete log entries older than the specified number of days.

        Args:
            days: Age threshold in days. If <= 0, deletes all logs.

        Returns:
            Number of deleted log entries.
        """
        from asgiref.sync import sync_to_async

        if days <= 0:
            # Delete all logs
            @sync_to_async
            def delete_all():
                result = LogEntry.objects.all().delete()
                return result[0] if isinstance(result, tuple) else result

            return await delete_all()
        else:
            cutoff = timezone.now() - timezone.timedelta(days=days)

            @sync_to_async
            def delete_old():
                result = LogEntry.objects.filter(timestamp__lt=cutoff).delete()
                return result[0] if isinstance(result, tuple) else result

            return await delete_old()