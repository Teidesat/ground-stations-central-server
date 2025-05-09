from datetime import datetime

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from ninja import Query, Router

from utils.helpers import create_log

from .models import Imagen
from .schemas import ImageFilterSchema
from .serializer import ImageDetailSerializer, ImageSerializer

router = Router()


@router.get('/')
async def all_images(request, filters: ImageFilterSchema = Query(...)):
    try:
        images = Imagen.objects.all()
        images = filters.filter(images)
        if await sync_to_async(images.exists)():
            images_json = ImageSerializer(images, request=request)
        else:
            return JsonResponse({'Error': 'No images available'}, status=404)

        await create_log(
            level='INFO',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='all_images',
            message='Petición realizada',
            request=request,
        )

        return await sync_to_async(images_json.json_response)()

    except Exception as e:
        await create_log(
            level='ERROR',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='all_images',
            message=f'ERROR en el procesamiento de la imagen: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'Message': 'No images available'})


@router.get('/by-date/')
async def images_by_date(request, date: str):
    try:
        fecha_obj = datetime.strptime(date, '%d-%m-%Y')

        images = Imagen.objects.filter(created_at__date=fecha_obj.date())

        if await sync_to_async(images.exists)():
            images_json = ImageSerializer(images, request=request)
        else:
            return JsonResponse({'Error': 'No images found for this date'}, status=404)

        await create_log(
            level='INFO',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='images_by_date',
            message=f'Images retrieved for date {date}',
            request=request,
        )

        return await sync_to_async(images_json.json_response)()

    except ValueError:
        return JsonResponse({'Error': 'Invalid date format, use %d-%m-%Y'}, status=400)
    except Exception as e:
        await create_log(
            level='ERROR',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='images_by_date',
            message=f'ERROR retrieving images by date: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'Error': 'Internal server error'}, status=500)


@router.get('/{image_id}')
async def image_detail(request, image_id: int):
    try:
        image = await sync_to_async(Imagen.objects.get)(id=image_id)

        image_json = ImageDetailSerializer(image, request=request)

        await create_log(
            level='INFO',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='image_detail',
            message=f'Imagen {image_id} obtenida',
            request=request,
        )

        return await sync_to_async(image_json.json_response)()

    except Imagen.DoesNotExist:
        await create_log(
            level='ERROR',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='image_detail',
            message=f'Imagen {image_id} no encontrada',
            request=request,
        )
        return JsonResponse({'Error': 'Image not found'}, status=404)

    except Exception as e:
        await create_log(
            level='ERROR',
            logger='ground-stations-central-server',
            module='analyze_image.api',
            function='image_detail',
            message=f'ERROR obteniendo imagen: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'Error': 'Internal server error'}, status=500)
