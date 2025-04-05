from ninja import Router, Query
from .models import SatelliteData
from .serializer import SatelliteDataSerializer
from django.http import JsonResponse
from .schemas import SatelliteDataFilterSchema
from utils.helpers import create_log


router = Router()

@router.get('/satellite-data')
async def all_satellite_data(request, filters: SatelliteDataFilterSchema = Query(...)):
    try:
        data = SatelliteData.objects.all()
        data = filters.filter(data)
        data_json = SatelliteDataSerializer(data, request=request)
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='all_satellite_data',
            message= f'Petición realizada',
            request=request
        )



        return data_json.json_response()
    except SatelliteData.DoesNotExist as e :
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='all_satellite_data',
            message= f'ERROR en el procesamiento del dato: {e}',
            request=request
        )

        return JsonResponse({'error': 'No data available'}, status=404)
    except:
        return JsonResponse({'error': 'Error interno'}, status=500)