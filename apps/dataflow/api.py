from ninja import Router
from .models import SatelliteData
from .serializer import SatelliteDataSerializer
from django.http import JsonResponse
router = Router()

@router.get('/satellite-data')
def all_satellite_data(request):
    try:
        data = SatelliteData.objects.all()
        data_json = SatelliteDataSerializer(data, request=request)
        return data_json.json_response()
    except SatelliteData.DoesNotExist:
        return JsonResponse({'error': 'No data available'}, status=404)
    except:
        return JsonResponse({'error': 'Error interno'}, status=500)