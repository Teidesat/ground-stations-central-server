# apps/imaging/models.py
"""Models for image analysis, storage, and metadata management."""

import json
import logging

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class ImageManager(models.Manager):
    """Custom manager for the Imagen model providing common query methods."""

    def get_by_format(self, format_type: str):
        """Return images filtered by format type (case-insensitive)."""
        return self.filter(format__iexact=format_type)

    def get_recent(self, limit: int = 10):
        """Return the most recent images by creation date."""
        return self.all().order_by('-created_at')[:limit]

    def get_by_date_range(self, start_date, end_date):
        """Return images with creation date within the given range."""
        return self.filter(created_at__date__range=[start_date, end_date])


class Imagen(models.Model):
    """Image model for storing satellite and ground station imagery.

    Supports metadata extraction, EXIF data, and file storage.
    """

    format = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Image format (PNG, JPEG, etc.)"
    )
    header = models.TextField(
        null=True,
        blank=True,
        help_text="Image header metadata"
    )
    exif = models.TextField(
        null=True,
        blank=True,
        help_text="EXIF data as JSON string"
    )
    fecha = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Original capture date/time"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Record creation timestamp"
    )
    raw_data = models.TextField(
        help_text="Raw image data or reference"
    )
    content = models.ImageField(
        upload_to='images/%Y/%m/%d/',
        blank=True,
        null=True,
        default=None,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'bmp'])],
        help_text="Uploaded image file"
    )

    objects = ImageManager()

    class Meta:
        """Meta configuration for Imagen model."""
        ordering = ['-created_at']
        verbose_name = "Image"
        verbose_name_plural = "Images"
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['format']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self) -> str:
        """Return string representation of the image."""
        return f'Image {self.pk} - {self.format or "unknown format"}'

    @property
    def header_dict(self) -> dict:
        """Return header metadata as a dictionary if valid JSON."""
        if self.header:
            try:
                return json.loads(self.header)
            except json.JSONDecodeError:
                return {}
        return {}

    @property
    def exif_dict(self) -> dict:
        """Return EXIF data as a dictionary if valid JSON."""
        if self.exif:
            try:
                return json.loads(self.exif)
            except json.JSONDecodeError:
                return {}
        return {}

    def save(self, *args, **kwargs):
        """Override save to log image creation events."""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            logger.info(f"New image created: ID={self.pk}, Format={self.format}")