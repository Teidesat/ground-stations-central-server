from django.db import models


class LogEntry(models.Model):
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    timestamp = models.DateTimeField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    logger = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    function = models.CharField(max_length=100)
    message = models.TextField()

    request_method = models.CharField(max_length=10, null=True, blank=True)
    request_path = models.CharField(max_length=255, null=True, blank=True)
    request_status_code = models.IntegerField(null=True, blank=True)
    request_client_ip = models.GenericIPAddressField(null=True, blank=True)
    request_user = models.CharField(max_length=100, null=True, blank=True)

    exception_type = models.CharField(max_length=100, null=True, blank=True)
    exception_message = models.TextField(null=True, blank=True)
    exception_stack_trace = models.TextField(null=True, blank=True)

    extra_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'[{self.timestamp}] {self.level} - {self.message[:50]}'
