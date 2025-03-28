from ninja import FilterSchema, Field
from typing import Optional
from datetime import datetime

class SatelliteDataFilterSchema(FilterSchema):
    category: Optional[str] = None
    content: Optional[str] = Field(None, q='content__icontains')
    timestamp: Optional[datetime] = Field(None, q='timestamp__gte')