from ninja import FilterSchema, Field
from typing import Optional, Any
from datetime import datetime

class DataFilterSchema(FilterSchema):
    data_type: Optional[str] = None
    data_source: Optional[str] = None
    data_destination: Optional[str] = None
    content: Optional[dict[str, Any]] = None
    timestamp: Optional[datetime] = Field(None, q='timestamp__gte')
    category: Optional[str] = None


# Schema for live data sending
class LiveDataFilter(FilterSchema):
    data_type: str
    data_destination: str
    content: str