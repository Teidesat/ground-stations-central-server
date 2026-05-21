# apps/control/serializers.py
"""Serializers for control models (primarily for admin display)."""

import base64

from core.serializers.base import BaseSerializer


class TelemetrySerializer():
    """Serializer for telemetry messages."""

    def serialize_instance(self, instance) -> dict:
        """Convert a TelemetryMessage instance to a dictionary.

        Args:
            instance: The TelemetryMessage model instance.

        Returns:
            Dictionary representation of the telemetry message.
        """
        return {
            'id': instance.id,
            'message_type': instance.message_type,
            'source': instance.source,
            'destination': instance.destination,
            'subsystem': instance.subsystem,
            'module': instance.module,
            'value': instance.value,
            'unit': instance.unit,
            'valid': instance.valid,
            'timestamp': instance.timestamp.isoformat(),
        }


class CommandSerializer():
    """Serializer for command messages."""

    def serialize_instance(self, instance) -> dict:
        """Convert a CommandMessage instance to a dictionary.

        Args:
            instance: The CommandMessage model instance.

        Returns:
            Dictionary representation of the command message.
        """
        return {
            'id': instance.id,
            'message_type': instance.message_type,
            'source': instance.source,
            'destination': instance.destination,
            'command_type': instance.command_type,
            'subsystem': instance.subsystem,
            'parameters': instance.parameters,
            'status': instance.status,
            'execution_time': instance.execution_time,
            'timestamp': instance.timestamp.isoformat(),
        }
    
class EventSerializer():
    """Serializer for event messages."""

    def serialize_instance(self, instance) -> dict:
        """Convert a EventMessage instance to a dictionary.

        Args:
            instance: The EventMessage model instance.

        Returns:
            Dictionary representation of the event message.
        """
        return {
            'id': instance.id,
            'message_type': instance.message_type,
            'source': instance.source,
            'destination': instance.destination,
            'subsystem': instance.subsystem,
            'severity': instance.severity,
            'code': instance.code,
            'description': instance.description,
            'timestamp': instance.timestamp.isoformat(),
        }
    
class StatusSerializer():
    """Serializer for status messages."""

    def serialize_instance(self, instance) -> dict:
        """Convert a StatusMessage instance to a dictionary.

        Args:
            instance: The StatusMessage model instance.

        Returns:
            Dictionary representation of the status message.
        """
        return {
            'id': instance.id,
            'message_type': instance.message_type,
            'source': instance.source,
            'destination': instance.destination,
            'subsystem': instance.subsystem,
            'state': instance.state,
            'mode': instance.mode,
            'timestamp': instance.timestamp.isoformat(),
        }
    
class SoftwareUpdateSerializer():
    """Serializer for software update messages."""
    
    def serialize_instance(self, instance) -> dict:
        """Convert a SoftwareUpdateMessage instance to a dictionary.

        Args:
            instance: The SoftwareUpdateMessage model instance.
        
        Returns:
            Dictionary representation of the software update message.
        """

        data_value = None
        if instance.data:
            if isinstance(instance.data, memoryview):
                data_bytes = bytes(instance.data)
            else:
                data_bytes = instance.data
            data_value = base64.b64encode(data_bytes).decode('utf-8')
        
        return {
            'id': instance.id,
            'message_type': instance.message_type,
            'source': instance.source,
            'destination': instance.destination,
            'version': instance.version,
            'checksum': instance.checksum,
            'size_bytes': instance.size_bytes,
            'verified': instance.verified,
            'uploaded_at': instance.uploaded_at.isoformat(),
            'data':  data_value,
            'timestamp': instance.timestamp.isoformat(),
        }