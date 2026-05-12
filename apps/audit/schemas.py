# apps/audit/schemas.py
"""Pydantic/Ninja schemas for log entry validation and serialization."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from ninja import Schema, FilterSchema, Field


class LogSchema(Schema):
    """Base log entry schema for API responses."""
    id: int
    timestamp: datetime
    level: str
    logger: str
    module: str
    function: str
    message: str
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_status_code: Optional[int] = None
    request_client_ip: Optional[str] = None
    request_user: Optional[str] = None
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    exception_stack_trace: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class LogDetailSchema(LogSchema):
    """Detailed log entry schema with computed fields."""
    is_error: bool
    has_exception: bool
    short_message: str


class LogCreateSchema(Schema):
    """Schema for creating new log entries via API."""
    level: str
    logger: str
    module: str
    function: str
    message: str
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_status_code: Optional[int] = None
    request_client_ip: Optional[str] = None
    request_user: Optional[str] = None
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    exception_stack_trace: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class LogFilterSchema(FilterSchema):
    """Filter schema for log entry query operations."""

    # Time filters
    timestamp_gte: Optional[datetime] = Field(None, q='timestamp__gte')
    timestamp_lte: Optional[datetime] = Field(None, q='timestamp__lte')

    # Level filters
    level: Optional[str] = None
    level_in: Optional[List[str]] = Field(None, q='level__in')

    # Source filters
    logger: Optional[str] = None
    logger_contains: Optional[str] = Field(None, q='logger__icontains')
    module: Optional[str] = None
    module_contains: Optional[str] = Field(None, q='module__icontains')
    function: Optional[str] = Field(None, q='function__icontains')
    message: Optional[str] = Field(None, q='message__icontains')

    # Request filters
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_path_contains: Optional[str] = Field(None, q='request_path__icontains')
    request_status_code: Optional[int] = None
    request_client_ip: Optional[str] = None
    request_user: Optional[str] = None
    request_user_contains: Optional[str] = Field(None, q='request_user__icontains')

    # Exception filters
    exception_type: Optional[str] = None
    exception_type_contains: Optional[str] = Field(None, q='exception_type__icontains')
    exception_message: Optional[str] = Field(None, q='exception_message__icontains')
    has_exception: Optional[bool] = None

    # Custom filters
    is_error: Optional[bool] = None

    def filter(self, queryset):
        """Apply custom filters (is_error, has_exception) that need special handling."""
        queryset = super().filter(queryset)

        # Filter for ERROR and CRITICAL levels
        if self.is_error is True:
            queryset = queryset.filter(level__in=['ERROR', 'CRITICAL'])
        elif self.is_error is False:
            queryset = queryset.exclude(level__in=['ERROR', 'CRITICAL'])

        # Filter for entries with/without exception data
        if self.has_exception is True:
            queryset = queryset.filter(exception_type__isnull=False)
        elif self.has_exception is False:
            queryset = queryset.filter(exception_type__isnull=True)

        return queryset


class LogStatisticsSchema(Schema):
    """Schema for log statistics aggregation response."""
    total_count: int
    by_level: Dict[str, int]
    by_logger: Dict[str, int]
    by_module: Dict[str, int]
    error_rate: float
    time_range: Dict[str, Optional[datetime]]