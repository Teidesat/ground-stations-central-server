# apps/imaging/tasks.py
"""Asynchronous tasks for image processing."""

import asyncio
import base64
import io
import logging

from asgiref.sync import sync_to_async

from apps.audit.services import create_log
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


async def image_processing(img_object) -> bool:
    """Process an image by handling raw payload or existing content,

    converting it to JPEG and saving to the model while cleaning raw_data.

    Args:
        img_object: Imagen model instance to process.

    Returns:
        True if processing succeeded, False otherwise.
    """
    try:
        image_bytes_io = None

        # 1. Caso trama cruda: Satélite envía Hex o Base64 en raw_data
        if img_object.raw_data:
            raw = img_object.raw_data
            if isinstance(raw, str):
                try:
                    raw_bytes = base64.b64decode(raw)
                except Exception:
                    raw_bytes = bytes.fromhex(raw)
            else:
                raw_bytes = raw

            image_bytes_io = io.BytesIO(raw_bytes)

        # 2. Caso archivo existente: Se subió un archivo físico directamente a content
        elif img_object.content:
            img_bytes = await sync_to_async(img_object.content.read)()
            image_bytes_io = io.BytesIO(img_bytes)

        else:
            raise ValueError("No content or raw_data available for processing")

        # Validación con el servicio nativo de dev
        is_valid, error = ImageProcessingService.validate_image(image_bytes_io)
        if not is_valid:
            raise ValueError(f"Invalid image: {error}")

        image_bytes_io.seek(0)

        # Conversión a JPEG estandarizada
        jpeg_file = ImageProcessingService.convert_to_jpeg(image_bytes_io)

        # Asignación del archivo al ImageField y vaciado de raw_data
        img_object.content = jpeg_file
        img_object.raw_data = None
        img_object.format = 'JPEG'

        await sync_to_async(img_object.save)()

        await create_log(
            level='INFO',
            logger='image-processor',
            module='imaging.tasks',
            function='image_processing',
            message=f'Image {img_object.pk} processed successfully',
        )

        logger.info(f"Image {img_object.pk} processed successfully")
        return True

    except Exception as e:
        error_msg = f"Error processing image {getattr(img_object, 'pk', 'unknown')}: {e}"
        logger.error(error_msg, exc_info=True)

        await create_log(
            level='ERROR',
            logger='image-processor',
            module='imaging.tasks',
            function='image_processing',
            message=error_msg,
            exception=e,
        )
        return False


async def run_tasks(img_object):
    """Run the image processing task for a given image.

    Args:
        img_object: Imagen model instance to process.

    Returns:
        The result of the image_processing task.
    """
    task = asyncio.create_task(image_processing(img_object))
    return await task