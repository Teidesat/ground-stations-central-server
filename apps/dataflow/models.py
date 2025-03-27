from django.db import models

class SatelliteData(models.Model):
    CATEGORY_CHOICES = [
        ("TEMP", "temperature"),
        ("POWR", "power"),
        ("HUMI", "humidity"),
        ("POSI", "position"),
        ("GENE", "general"),
    ] 

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES.GENE)
    content = models.JSONField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.timestamp} - {self.category} ({self.id})"
