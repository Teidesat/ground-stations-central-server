# apps/audit/admin.py
"""Django admin configuration for the audit LogEntry model."""

from django.contrib import admin
from django.utils.html import format_html

from .models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the LogEntry model.

    Provides customized list display, filters, search fields, and
    organized field sections for viewing audit log entries in the Django admin.
    """

    # Displayed columns in the changelist view
    list_display = (
        'timestamp',
        'colored_level',
        'logger',
        'module',
        'short_message',
        'request_method',
        'request_status_code',
    )

    # Sidebar filter options
    list_filter = (
        'level',
        'logger',
        'module',
        'request_method',
        'exception_type',
        'timestamp',
    )

    # Searchable fields
    search_fields = (
        'message',
        'logger',
        'module',
        'function',
        'exception_type',
        'exception_message',
    )

    # Non-editable fields (read-only)
    readonly_fields = ('timestamp',)

    # Date-based drill-down navigation
    date_hierarchy = 'timestamp'

    # Field grouping for the detail/edit form
    fieldsets = (
        ('Core Information', {
            'fields': ('timestamp', 'level', 'logger', 'module', 'function', 'message')
        }),
        ('Request Context', {
            'fields': ('request_method', 'request_path', 'request_status_code', 'request_client_ip', 'request_user'),
            'classes': ('collapse',)
        }),
        ('Exception Information', {
            'fields': ('exception_type', 'exception_message', 'exception_stack_trace'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
    )

    def colored_level(self, obj: LogEntry) -> str:
        """
        Return an HTML span with color-coded log level text.

        Args:
            obj: The LogEntry instance.

        Returns:
            HTML formatted string with colored level text.
        """
        colors = {
            'DEBUG': 'gray',
            'INFO': 'green',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'darkred',
        }
        color = colors.get(obj.level, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.level
        )
    colored_level.short_description = 'Level'
    colored_level.admin_order_field = 'level'

    def short_message(self, obj: LogEntry) -> str:
        """
        Return a truncated version of the log message.

        Args:
            obj: The LogEntry instance.

        Returns:
            First 100 characters of the message, followed by '...' if longer.
        """
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    short_message.short_description = 'Message'

    def get_queryset(self, request):
        """
        Return an optimized queryset for the changelist view.

        Args:
            request: The HTTP request object.

        Returns:
            Optimized QuerySet with optional select_related prefetching.
        """
        return super().get_queryset(request)