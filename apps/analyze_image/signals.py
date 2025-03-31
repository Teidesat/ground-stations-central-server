from django.db.models.signals import post_save
from .models import Imagen
from apps.logvault.models import LogEntry
from django.dispatch import receiver
from django.utils import timezone

@receiver(post_save, sender=Imagen)
def log_object_create(sender, instance, created, **kwargs):
    LogEntry.objects.create(
        timestamp = timezone.now(),
        level = "INFO",
        logger = 'ground-stations-central-server',
        module = 'analyze_image.tasks',
        function = 'img_proccesing',
        message = 'Imagen is created',
    )
