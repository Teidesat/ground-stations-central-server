from ninja import Router, Query
from .serializer import LogSerializer
from .models import LogEntry
from django.http import JsonResponse
from .schemas import LogFilterSchema
router = Router()

@router.get('/')
def get_all_logs(request, filters:LogFilterSchema = Query(...)):
    try:
        logs = LogEntry.objects.all()
        logs_serializer = LogSerializer(logs, request=request)
        return logs_serializer.json_response()
    except:
        return JsonResponse({'error': 'Error while retrieving logs'}, status=500)

@router.get('/filter')
def get_filtered_logs(request, filters:LogFilterSchema = Query(...)):
    try:
        logs = LogEntry.objects.all()
        logs = filters.filter(logs)
        logs_serializer = LogSerializer(logs, request=request)
        return logs_serializer.json_response()
    except:
        return JsonResponse({'error': 'Error interno'}, status=500)