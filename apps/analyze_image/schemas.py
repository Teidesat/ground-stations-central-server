from ninja import Schema, FilterSchema, Field
from typing import Optional
from datetime import datetime

class ImageSchema(Schema):
    id:int
    header:dict
    exif:dict


class ImageFilterSchema(FilterSchema):
    format: Optional[str] = None
    header: Optional[str] = Field(None, q='header__icontains')
    fecha: Optional[datetime] = Field(None, q='fecha__gte')
    created_at: Optional[datetime] = Field(None, q='created_at__gte')