# core/services/image_service.py
"""Image service utilities for async existence checking."""

from apps.imaging.models import Imagen


async def filter_exists(imagen) -> bool:
    """Check if a image query set contains any results asynchronously.

    Args:
        imagen: A Django QuerySet or model instance to check for existence.

    Returns:
        True if the query set or instance exists, False otherwise.
    """
    return await imagen.exists()