# apps/imaging/serializers.py
"""Serializers for Image model conversion to JSON."""

from typing import Optional

from django.http import HttpRequest

from core.serializers.base import BaseSerializer


class ImageSerializer(BaseSerializer):
    """Serializer for list views - lightweight representation of images."""

    def __init__(self, to_serialize, *, fields: list = [], request: Optional[HttpRequest] = None):
        """Initialize the ImageSerializer.

        Args:
            to_serialize: The object(s) to serialize.
            fields: Optional list of field names to include.
            request: Optional HTTP request for URL building.
        """
        super().__init__(to_serialize, fields=fields, request=request)

    def serialize_instance(self, instance) -> dict:
        """Convert a single Imagen instance to a lightweight dictionary.

        Args:
            instance: The Imagen model instance.

        Returns:
            Dictionary with id, format, created_at, and content URL.
        """
        result = {
            'id': instance.pk,
            'format': instance.format,
            'created_at': instance.created_at.isoformat() if instance.created_at else None,
        }

        if instance.content and hasattr(instance.content, 'url'):
            result['content'] = self.build_url(instance.content.url)
        else:
            result['content'] = None

        if self.fields:
            return {k: v for k, v in result.items() if k in self.fields}

        return result


class ImageDetailSerializer(BaseSerializer):
    """Serializer for detail views - full representation with metadata."""

    def __init__(self, to_serialize, *, fields: list = [], request: Optional[HttpRequest] = None):
        """Initialize the ImageDetailSerializer.

        Args:
            to_serialize: The object(s) to serialize.
            fields: Optional list of field names to include.
            request: Optional HTTP request for URL building.
        """
        super().__init__(to_serialize, fields=fields, request=request)

    def serialize_instance(self, instance) -> dict:
        """Convert a single Imagen instance to a detailed dictionary.

        Args:
            instance: The Imagen model instance.

        Returns:
            Dictionary with full image metadata and content URL.
        """
        result = {
            'id': instance.pk,
            'format': instance.format,
            'header': instance.header_dict,
            'exif': instance.exif_dict,
            'fecha': instance.fecha.isoformat() if instance.fecha else None,
            'created_at': instance.created_at.isoformat() if instance.created_at else None,
        }

        if instance.content and hasattr(instance.content, 'url'):
            result['content'] = self.build_url(instance.content.url)
        else:
            result['content'] = None

        if self.fields:
            return {k: v for k, v in result.items() if k in self.fields}

        return result