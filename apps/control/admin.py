# apps/control/admin.py
"""Django admin configuration for control models."""

from django.contrib import admin
from django.utils.html import format_html

from .models import (CommandMessage, EventMessage, SoftwareUpdateMessage, StatusMessage,
                     TelemetryMessage)


@admin.register(TelemetryMessage)
class TelemetryMessageAdmin(admin.ModelAdmin):
    """Admin interface for TelemetryMessage model."""

    list_display = ('id', 'subsystem', 'module', 'value', 'unit', 'valid', 'timestamp')
    list_filter = ('subsystem', 'module', 'valid', 'timestamp')
    search_fields = ('subsystem', 'module', 'value')
    readonly_fields = ('timestamp', 'message_type')
    fieldsets = (
        ('Basic Info', {
            'fields': ('subsystem', 'module', 'value', 'unit', 'valid')
        }),
        ('Metadata', {
            'fields': ('source', 'destination', 'raw_data', 'timestamp'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    """Admin interface for StatusMessage model."""

    list_display = ('id', 'subsystem', 'mode', 'timestamp')
    list_filter = ('subsystem', 'mode', 'timestamp')
    search_fields = ('subsystem',)
    readonly_fields = ('timestamp', 'message_type')


@admin.register(CommandMessage)
class CommandMessageAdmin(admin.ModelAdmin):
    """Admin interface for CommandMessage model."""

    list_display = ('id', 'command_type', 'subsystem', 'status', 'timestamp')
    list_filter = ('command_type', 'subsystem', 'status', 'timestamp')
    search_fields = ('command_type', 'subsystem')
    readonly_fields = ('timestamp', 'message_type')
    fieldsets = (
        ('Command Info', {
            'fields': ('command_type', 'subsystem', 'parameters', 'status')
        }),
        ('Execution', {
            'fields': ('execution_time', 'timestamp'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventMessage)
class EventMessageAdmin(admin.ModelAdmin):
    """Admin interface for EventMessage model."""

    list_display = ('id', 'severity', 'subsystem', 'code', 'short_description', 'timestamp')
    list_filter = ('severity', 'subsystem', 'code', 'timestamp')
    search_fields = ('code', 'description')
    readonly_fields = ('timestamp', 'message_type')

    def short_description(self, obj) -> str:
        """Return truncated description for list display."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    short_description.short_description = 'Description'


@admin.register(SoftwareUpdateMessage)
class SoftwareUpdateAdmin(admin.ModelAdmin):
    """Admin interface for SoftwareUpdateMessage model."""

    list_display = ('id', 'version', 'size_bytes', 'verified', 'uploaded_at')
    list_filter = ('verified', 'uploaded_at')
    search_fields = ('version', 'checksum')
    readonly_fields = ('uploaded_at', 'message_type')