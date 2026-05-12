# apps/audit/serializers.py
"""Serializers for LogEntry model conversion to JSON."""

from typing import Optional
from django.http import HttpRequest

from core.serializers.base import BaseSerializer


class LogSerializer(BaseSerializer):
    """
    Serializer for LogEntry instances.

    Converts log entries to JSON format with computed fields.
    """

    def __init__(self, to_serialize, *, fields: list = [], request: Optional[HttpRequest] = None):
        """Initialize the LogSerializer.

        Args:
            to_serialize: The object(s) to serialize (single instance or iterable).
            fields: Optional list of field names to include in output.
            request: Optional HTTP request object for context.
        """
        super().__init__(to_serialize, fields=fields, request=request)

    def serialize_instance(self, instance) -> dict:
        """Convert a single LogEntry instance to a dictionary.

        Args:
            instance: The LogEntry model instance to serialize.

        Returns:
            Dictionary representation of the log entry.
        """
        result = {
            'id': instance.pk,
            'timestamp': instance.timestamp.isoformat(),
            'level': instance.level,
            'logger': instance.logger,
            'module': instance.module,
            'function': instance.function,
            'message': instance.message,
            'request_method': instance.request_method,
            'request_path': instance.request_path,
            'request_status_code': instance.request_status_code,
            'request_client_ip': instance.request_client_ip,
            'request_user': instance.request_user,
            'exception_type': instance.exception_type,
            'exception_message': instance.exception_message,
            'exception_stack_trace': instance.exception_stack_trace,
            'extra_data': instance.extra_data,
            'is_error': instance.is_error,
            'has_exception': instance.has_exception,
        }

        # Filter fields if specified
        if self.fields:
            return {k: v for k, v in result.items() if k in self.fields}

        return result


class LogDetailSerializer(BaseSerializer):
    """
    Detailed serializer for LogEntry with additional computed fields.

    Includes short_message field for truncated display.
    """

    def __init__(self, to_serialize, *, fields: list = [], request: Optional[HttpRequest] = None):
        """Initialize the LogDetailSerializer.

        Args:
            to_serialize: The object(s) to serialize (single instance or iterable).
            fields: Optional list of field names to include in output.
            request: Optional HTTP request object for context.
        """
        super().__init__(to_serialize, fields=fields, request=request)

    def serialize_instance(self, instance) -> dict:
        """Convert a single LogEntry instance to a detailed dictionary.

        Args:
            instance: The LogEntry model instance to serialize.

        Returns:
            Detailed dictionary representation including short_message.
        """
        result = {
            'id': instance.pk,
            'timestamp': instance.timestamp.isoformat(),
            'level': instance.level,
            'logger': instance.logger,
            'module': instance.module,
            'function': instance.function,
            'message': instance.message,
            'request_method': instance.request_method,
            'request_path': instance.request_path,
            'request_status_code': instance.request_status_code,
            'request_client_ip': instance.request_client_ip,
            'request_user': instance.request_user,
            'exception_type': instance.exception_type,
            'exception_message': instance.exception_message,
            'exception_stack_trace': instance.exception_stack_trace,
            'extra_data': instance.extra_data,
            'is_error': instance.is_error,
            'has_exception': instance.has_exception,
            'short_message': instance.short_message,
        }

        if self.fields:
            return {k: v for k, v in result.items() if k in self.fields}

        return result