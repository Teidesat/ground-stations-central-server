# apps/imaging/api.py
"""API endpoints for image management, upload, and retrieval."""

from datetime import datetime
from typing import List

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from ninja import File, Query, Router, UploadedFile
from ninja.pagination import paginate

from apps.audit.services import create_log

from .models import Imagen
from .schemas import ImageDetailResponseSchema, ImageFilterSchema, ImageResponseSchema
from .services import ImageProcessingService
from .tasks import run_tasks

router = Router(tags=["Image Analysis"])


@router.get("/", response={200: List[ImageResponseSchema]})
@paginate
async def all_images(request, filters: ImageFilterSchema = Query(...)):
    """Retrieve all images with optional filtering.

    Args:
        request: HTTP request object.
        filters: Query parameters for filtering images.

    Returns:
        List of image response schemas.
    """
    qs = Imagen.objects.all()
    qs = filters.filter(qs)
    return await sync_to_async(list)(qs)


@router.get("/{image_id}", response={200: ImageDetailResponseSchema, 404: dict})
async def image_detail(request, image_id: int):
    """Retrieve detailed information for a specific image by ID.

    Args:
        request: HTTP request object.
        image_id: Primary key of the image.

    Returns:
        Tuple of (HTTP status code, response data or error dict).
    """
    try:
        image = await sync_to_async(Imagen.objects.get)(id=image_id)

        response = {
            'id': image.pk,
            'format': image.format,
            'header': image.header_dict,
            'exif': image.exif_dict,
            'fecha': image.fecha,
            'created_at': image.created_at,
            'content': request.build_absolute_uri(image.content.url) if image.content else None,
        }

        await create_log(
            level='INFO',
            logger='imaging-api',
            module='imaging.api',
            function='image_detail',
            message=f'Image {image_id} retrieved',
            request=request,
        )

        return 200, response

    except Imagen.DoesNotExist:
        return 404, {'error': f'Image {image_id} not found'}

    except Exception as e:
        await create_log(
            level='ERROR',
            logger='imaging-api',
            module='imaging.api',
            function='image_detail',
            message=f'Error: {e}',
            request=request,
            exception=e,
        )
        return 404, {'error': str(e)}


@router.get("/by-date/{date_str}", response={200: List[ImageResponseSchema], 400: dict})
async def images_by_date(request, date_str: str):
    """Retrieve images captured on a specific date.

    Args:
        request: HTTP request object.
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        Tuple of (HTTP status code, list of images or error dict).
    """
    try:
        fecha_obj = datetime.strptime(date_str, '%Y-%m-%d')
        images = Imagen.objects.filter(created_at__date=fecha_obj.date())

        serialized = []
        async for image in images:
            serialized.append({
                'id': image.pk,
                'format': image.format,
                'created_at': image.created_at,
                'content': request.build_absolute_uri(image.content.url) if image.content else None,
            })

        await create_log(
            level='INFO',
            logger='imaging-api',
            module='imaging.api',
            function='images_by_date',
            message=f'Retrieved {len(serialized)} images for date {date_str}',
            request=request,
        )

        return 200, serialized

    except ValueError:
        return 400, {'error': 'Invalid date format. Use YYYY-MM-DD'}


@router.post("/upload/", response={200: dict, 400: dict})
async def upload_image(request, file: UploadedFile = File(...)):
    """Upload and process a new image file.

    Args:
        request: HTTP request object.
        file: The uploaded image file.

    Returns:
        Tuple of (HTTP status code, response dict with success/error info).
    """
    try:
        await create_log(
            level='INFO',
            logger='imaging-api',
            module='imaging.api',
            function='upload_image',
            message=f'Uploading file: {file.name}',
            request=request,
        )

        is_valid, error = ImageProcessingService.validate_image(file.file)
        if not is_valid:
            return 400, {'error': f'Invalid image: {error}'}

        metadata = ImageProcessingService.extract_metadata(file.file)

        file.file.seek(0)

        image = await sync_to_async(Imagen.objects.create)(
            format=metadata.get('format'),
            header=metadata,
            content=file,
            raw_data=f"images/{file.name}",
        )

        await run_tasks(image)

        await create_log(
            level='INFO',
            logger='imaging-api',
            module='imaging.api',
            function='upload_image',
            message=f'Image {image.pk} uploaded and processing started',
            request=request,
        )

        return 200, {
            'success': True,
            'image_id': image.pk,
            'message': 'Image uploaded successfully, processing in background'
        }

    except Exception as e:
        await create_log(
            level='ERROR',
            logger='imaging-api',
            module='imaging.api',
            function='upload_image',
            message=f'Upload failed: {e}',
            request=request,
            exception=e,
        )
        return 400, {'error': str(e)}