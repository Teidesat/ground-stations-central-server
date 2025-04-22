from ninja import Router, Query
from .serializer import LogSerializer
from .models import LogEntry
from django.http import JsonResponse
from .schemas import LogFilterSchema
router = Router()


@router.get('/')
def all_logs(request, filters:LogFilterSchema = Query(...)):
    try:
        logs = LogEntry.objects.all()
        logs = filters.filter(logs)
        if logs.exists():
            logs_json = LogSerializer(logs, request=request)
        else:
            return JsonResponse({'error': 'No logs available'}, status=404)
        return logs_json.json_response()
    except LogEntry.DoesNotExist:
        return JsonResponse({'error': 'No logs available'}, status=404)
    except:
        return JsonResponse({'error': 'Error interno'}, status=500)