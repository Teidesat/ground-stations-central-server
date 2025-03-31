from django.db.models.signals import post_save, post_delete
from .models import SatelliteData
from apps.logvault.models import LogEntry
from django.dispatch import receiver
from django.utils import timezone

LOGGER = 'ground-stations-central-server'
MODULE = 'dataflow.tasks'
FUNCTION = 'data_proccesing'



@receiver(post_save, sender=SatelliteData)
def log_object_create(sender, instance, created, **kwargs):
    LogEntry.objects.create(
        timestamp = timezone.now(),
        level = "INFO",
        logger = LOGGER,
        module = MODULE,
        function = FUNCTION,
        message = 'SatelliteData is created',
    )


@receiver(post_delete, sender=SatelliteData)
def log_delete_object(sender, instance, created, **kwargs):
    LogEntry.objects.create(
        timestamp = timezone.now(),
        level = 'WARNING',
        logger = LOGGER,
        module = MODULE,
        function = FUNCTION,
        message = 'SatelliteData is deleted',
    )