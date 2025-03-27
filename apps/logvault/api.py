from ninja import Router
from .serializer import LogSerializer
from .models import LogEntry
from django.http import JsonResponse
from .schema import LogSchema
router = Router()


@router.get('/')
def all_logs(request):
    try:
        logs = LogEntry.objects.all()
        logs_json = LogSerializer(logs, request=request)
        return logs_json.json_response()
    except LogEntry.DoesNotExist:
        return JsonResponse({'error': 'No logs available'}, status=404)
    except:
        return JsonResponse({'error': 'Error interno'}, status=500)