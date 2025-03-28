from ninja import Schema, FilterSchema, Field
from typing import Optional
from datetime import datetime

class LogSchema(Schema):
    id: int
    timestamp: datetime
    level: str
    logger: str
    module: str
    function: str
    message: str
    request_method: str
    request_path: str
    request_status_code: int
    request_client_ip: str
    request_user: str
    exception_type: str
    exception_message: str
    exception_stack_trace: str
    extra_data: str



class LogFilterSchema(FilterSchema):
    timestamp: Optional[datetime] = Field(None, q='timestamp__gte')
    level: Optional[str] = None
    logger: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = Field(None, q='function__icontains')
    message: Optional[str] = Field(None, q='message__icontains')
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_client_ip: Optional[str] = None
    request_user: Optional[str] = None
    exception_type: Optional[str] = None
    exception_message: Optional[str] = Field(None, q='exception_message__icontains') 