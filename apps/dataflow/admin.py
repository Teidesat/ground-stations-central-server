from django.contrib import admin
from .models import SatelliteData

@admin.register(SatelliteData)
class SatelliteDataAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'content',
        'timestamp'
    )