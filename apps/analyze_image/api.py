from ninja import Router, Query
from .models import Imagen
from .serializer import ImageSerializer
from .schemas import ImageFilterSchema
from django.http import JsonResponse
from utils.helpers import create_log
from asgiref.sync import sync_to_async
router = Router()


@router.get('/') 
async def all_images(request, filters:ImageFilterSchema = Query(...)):
    try:
        images = Imagen.objects.all()
        images = filters.filter(images)
        images_json = ImageSerializer(images, request=request)

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='all_images',
            message= f'Petición realizada',
            request=request
        )

        return sync_to_async(images_json.json_response)()
    
    except Exception as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='all_images',
            message= f'ERROR en el procesamiento de la imagen: {e}',
            request=request, 
            exception=e,
        )
        return JsonResponse({'error': 'No images available'}, status=404)