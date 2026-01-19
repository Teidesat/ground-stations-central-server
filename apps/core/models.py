from django.db import models

class GeneralData(models.Model):
    class DATA_TYPE_CHOICES(models.TextChoices):
        TELEMETRY = 'TELEMETRY', 'telemetry'
        COMMAND = 'COMMAND', 'command'
        EVENT = 'EVENT', 'event'
        STATUS = 'STATUS', 'status'
        OTHER = 'OTHER', 'other'
    
    class DATA_SOURCE_CHOICES(models.TextChoices):
        GROUND_STATION = 'GROUND_STATION', 'ground_station'
        SATELLITE = 'SATELLITE', 'satellite'
        RADIO_STATION = 'RADIO_STATION', 'radio_station'
        OPTICAL_STATION = 'OPTICAL_STATION', 'optical_station'
        FOMALHAUT = 'FOMALHAUT', 'fomalhaut'
        OTHER = 'OTHER', 'other'
    
    class DATA_DESTINATION_CHOICES(models.TextChoices):
        GROUND_STATION = 'GROUND_STATION', 'ground_station'
        SATELLITE = 'SATELLITE', 'satellite'
        RADIO_STATION = 'RADIO_STATION', 'radio_station'
        OPTICAL_STATION = 'OPTICAL_STATION', 'optical_station'
        FOMALHAUT = 'FOMALHAUT', 'fomalhaut'
        OTHER = 'OTHER', 'other'

    data_type = models.CharField(
        max_length=50, choices=DATA_TYPE_CHOICES, default=DATA_TYPE_CHOICES.OTHER
    )
    data_source = models.CharField(
        max_length=50, choices=DATA_SOURCE_CHOICES, default=DATA_SOURCE_CHOICES.OTHER
    )
    data_destination = models.CharField(
        max_length=50, choices=DATA_DESTINATION_CHOICES, default=DATA_DESTINATION_CHOICES.OTHER
    )
    content = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    raw_data = models.TextField(default='')

class SatelliteData(GeneralData):
    class CATEGORY_CHOICES(models.TextChoices):
        TEMPERATURE = 'TEMP', 'temperature'
        POWER = 'POWR', 'power'
        HUMIDITY = 'HUMI', 'humidity'
        POSITION = 'POSI', 'position'
        GENERAL = 'GENE', 'general'

    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES.GENERAL
    )

class RadioStationData(GeneralData):
    class CATEGORY_CHOICES(models.TextChoices):
        SIGNAL_STRENGTH = 'SIGNAL', 'signal_strength'
        NOISE_LEVEL = 'NOISE', 'noise_level'
        FREQUENCY = 'FREQ', 'frequency'
        GENERAL = 'GENE', 'general'

    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES.GENERAL
    )

class OpticalStationData(GeneralData):
    class CATEGORY_CHOICES(models.TextChoices):
        LIGHT_INTENSITY = 'LIGHT', 'light_intensity'
        GENERAL = 'GENE', 'general'

    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES.GENERAL
    )

class FomalhautData(GeneralData):
    class CATEGORY_CHOICES(models.TextChoices): # Needs more specific categories
        IMAGE_DATA = 'IMAGE', 'image_data'
        SPECTRAL_DATA = 'SPECTRAL', 'spectral_data'
        GENERAL = 'GENE', 'general'

    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES.GENERAL
    )
    
