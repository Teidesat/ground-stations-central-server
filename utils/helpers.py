from apps.logvault.models import LogEntry
from django.utils import timezone
async def create_log(*, level, logger, module, function, message):
    await LogEntry.objects.acreate(
        timestamp = timezone.now(),
        level = level,
        logger = logger,
        module = module,
        function = function,
        message = message
    ) 


