from django.contrib import admin
from .models import LogEntry

@admin.register(LogEntry)
class LogEntry(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'level',
        'logger',
        'module',
        'function',
        'message',
        'request_method',
        'request_path',
        'request_status_code',
        'request_client_ip',
        'request_user',
        'exception_type',
        'exception_message',
        'exception_stack_trace'
    )

