# apps/imaging/admin.py
"""Django admin configuration for the Image model."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Imagen


@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    """Admin interface for the Imagen model."""

    list_display = ('pk', 'format', 'created_at', 'preview_image')
    list_filter = ('format', 'created_at')
    search_fields = ('pk', 'header')
    readonly_fields = ('created_at', 'preview_image')
    fieldsets = (
        ('Basic Information', {
            'fields': ('format', 'header', 'exif')
        }),
        ('Dates', {
            'fields': ('fecha', 'created_at')
        }),
        ('Files', {
            'fields': ('raw_data', 'content')
        }),
    )

    def preview_image(self, obj) -> str:
        """Display an image preview thumbnail in the admin interface.

        Args:
            obj: The Imagen instance.

        Returns:
            HTML img tag for preview, or "No image" text if none exists.
        """
        if obj.content and obj.content.url:
            return format_html('<img src="{}" width="100" height="100" />', obj.content.url)
        return "No image"
    preview_image.short_description = "Preview"

    def get_readonly_fields(self, request, obj=None):
        """Return readonly fields, making raw_data readonly for existing objects.

        Args:
            request: The HTTP request object.
            obj: The Imagen instance being edited, or None for creation.

        Returns:
            Tuple of readonly field names.
        """
        if obj:
            return self.readonly_fields + ('raw_data',)
        return self.readonly_fields