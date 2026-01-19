from django.contrib import admin
from .models import GeneralData, SatelliteData, RadioStationData, OpticalStationData, FomalhautData

@admin.register(GeneralData)
class GeneralDataAdmin(admin.ModelAdmin):
    list_display = (
        'data_type',
        'data_source',
        'data_destination',
        'content',
        'timestamp'
    )

@admin.register(SatelliteData)
class SatelliteDataAdmin(admin.ModelAdmin):
    list_display = (
        'data_type',
        'data_source',
        'data_destination',
        'category',
        'content',
        'timestamp'
    )

@admin.register(RadioStationData)
class RadioStationDataAdmin(admin.ModelAdmin):
    list_display = (
        'data_type',
        'data_source',
        'data_destination',
        'category',
        'content',
        'timestamp'
    )

@admin.register(OpticalStationData)
class OpticalStationDataAdmin(admin.ModelAdmin):
    list_display = (
        'data_type',
        'data_source',
        'data_destination',
        'category',
        'content',
        'timestamp'
    )

@admin.register(FomalhautData)
class FomalhautDataAdmin(admin.ModelAdmin):
    list_display = (
        'data_type',
        'data_source',
        'data_destination',
        'category',
        'content',
        'timestamp'
    )