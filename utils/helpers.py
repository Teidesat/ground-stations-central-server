from apps.logvault.models import LogEntry
from django.utils import timezone
import traceback


async def create_log(
    *, level, logger, module, function, message, request=None, exception=None, extra_data=None
):
    await LogEntry.objects.acreate(
        timestamp=timezone.now(),
        level=level,
        logger=logger,
        module=module,
        function=function,
        message=message,
        request_method=getattr(request, 'method', None),
        request_path=getattr(request, 'path', None),
        request_status_code=getattr(request, 'status_code', None),
        request_client_ip=_get_client_ip(request) if request else None,
        request_user=None,
        exception_type=type(exception).__name__ if exception else None,
        exception_message=str(exception) if exception else None,
        exception_stack_trace=traceback.format_exc() if exception else None,
        extra_data=extra_data,
    )
    

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


