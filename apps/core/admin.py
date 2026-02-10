from django.contrib import admin
from .models import TelemetryMessage, StatusMessage, CommandMessage, EventMessage, SoftwareUpdate

@admin.register(TelemetryMessage)
class TelemetryMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message_type',
        'source',
        'destination',
        'timestamp',
        'raw_data',
        'subsystem',
        'module',
        'value',
        'unit',
        'valid'
    )

@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message_type',
        'source',
        'destination',
        'timestamp',
        'state',
        'mode'
    )

@admin.register(CommandMessage)
class CommandMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message_type',
        'source',
        'destination',
        'timestamp',
        'subsystem',
        'parameters',
        'status',
        'execution_time',
        'command_type'
    )

@admin.register(EventMessage)
class EventMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message_type',
        'source',
        'destination',
        'timestamp',
        'subsystem',
        'severity',
        'code',
        'description'
    )

@admin.register(SoftwareUpdate)
class SoftwareUpdateAdmin(admin.ModelAdmin):
    list_display = (
       'id',
        'message_type',
        'source',
        'destination',
        'timestamp',
        'versión',
        'checksum',
        'size_bytes',
        'verified',
        'uploaded_at',
        'data' 
    )