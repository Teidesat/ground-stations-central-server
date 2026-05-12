# apps/imaging/signals.py
"""Django signals for image model lifecycle events."""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.audit.models import LogEntry

from .models import Imagen

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Imagen)
def log_image_created(sender, instance, created, **kwargs):
    """Log when an image is created or updated.

    Args:
        sender: The model class sending the signal.
        instance: The Imagen instance being saved.
        created: Boolean indicating if this is a new instance.
        **kwargs: Additional keyword arguments.
    """
    if created:
        level = "INFO"
        message = f'Image {instance.pk} created'
    else:
        level = "DEBUG"
        message = f'Image {instance.pk} updated'

    try:
        LogEntry.objects.create(
            timestamp=timezone.now(),
            level=level,
            logger='ground-stations-central-server',
            module='imaging.signals',
            function='log_image_created',
            message=message,
        )
        logger.debug(message)
    except Exception as e:
        logger.error(f"Failed to create log entry: {e}")


@receiver(post_delete, sender=Imagen)
def log_image_deleted(sender, instance, **kwargs):
    """Log when an image is deleted.

    Args:
        sender: The model class sending the signal.
        instance: The Imagen instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    try:
        LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger='ground-stations-central-server',
            module='imaging.signals',
            function='log_image_deleted',
            message=f'Image {instance.pk} deleted',
        )
        logger.info(f"Image {instance.pk} deleted")
    except Exception as e:
        logger.error(f"Failed to create deletion log: {e}")