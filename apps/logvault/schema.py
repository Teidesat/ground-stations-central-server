from ninja import Schema
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
