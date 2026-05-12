# apps/imaging/schemas.py
"""Pydantic/Ninja schemas for image request/response validation."""

from datetime import datetime
from typing import Optional, Dict, Any

from ninja import Schema, FilterSchema, Field


class ImageResponseSchema(Schema):
    """Response schema for image list views (lightweight)."""

    id: int
    format: Optional[str] = None
    created_at: datetime
    content: Optional[str] = None


class ImageDetailResponseSchema(Schema):
    """Response schema for image detail view (full metadata)."""

    id: int
    format: Optional[str] = None
    header: Dict[str, Any] = {}
    exif: Dict[str, Any] = {}
    fecha: Optional[datetime] = None
    created_at: datetime
    content: Optional[str] = None


class ImageCreateSchema(Schema):
    """Schema for creating new image records."""

    format: Optional[str] = None
    header: Optional[str] = None
    exif: Optional[str] = None
    fecha: Optional[datetime] = None
    raw_data: str


class ImageFilterSchema(FilterSchema):
    """Filter schema for listing images with query parameters."""

    format: Optional[str] = None
    header: Optional[str] = Field(None, q='header__icontains')
    fecha: Optional[datetime] = Field(None, q='fecha__gte')
    created_at: Optional[datetime] = Field(None, q='created_at__gte')
    created_at_lte: Optional[datetime] = Field(None, q='created_at__lte')


class ImageErrorSchema(Schema):
    """Error response schema for image operations."""

    error: str
    detail: Optional[str] = None