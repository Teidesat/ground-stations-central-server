from ninja import Router, Query
from .models import Imagen
from .serializer import ImageSerializer
from .schemas import ImageFilterSchema
from django.http import JsonResponse
from main.auth import SimpleTokenAuth
router = Router()

auth = SimpleTokenAuth()

@router.get('/', auth=auth) 
def all_images(request, filters:ImageFilterSchema = Query(...)):
    try:
        images = Imagen.objects.all()
        images = filters.filter(images)
        images_json = ImageSerializer(images, request=request)
        return images_json.json_response()
    except:
        return JsonResponse({'error': 'No images available'}, status=404)