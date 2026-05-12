# apps/control/serializers.py
"""Serializers for control models (primarily for admin display)."""

from core.serializers.base import BaseSerializer


class TelemetrySerializer(BaseSerializer):
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
            'subsystem': instance.subsystem,
            'module': instance.module,
            'value': instance.value,
            'unit': instance.unit,
            'valid': instance.valid,
            'timestamp': instance.timestamp.isoformat(),
        }


class CommandSerializer(BaseSerializer):
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
            'command_type': instance.command_type,
            'subsystem': instance.subsystem,
            'parameters': instance.parameters,
            'status': instance.status,
            'timestamp': instance.timestamp.isoformat(),
        }