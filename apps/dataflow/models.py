from django.db import models

class SatelliteData(models.Model):
    class CATEGORY_CHOICES(models.TextChoices):
        TEMPERATURE = "TEMP", "temperature"
        POWER = "POWR", "power"
        HUMIDITY = "HUMI", "humidity"
        POSITION = "POSI", "position"
        GENERAL = "GENE", "general"

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES.GENERAL)
    content = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    raw_data = models.TextField(default='')

    def __str__(self):
        return f"{self.timestamp} - {self.category} ({self.id})"
