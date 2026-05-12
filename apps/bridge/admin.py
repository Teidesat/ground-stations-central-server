# apps/bridge/admin.py
"""Django admin configuration for bridge module.

Note: Models are registered in apps.control.admin. This app handles
data routing and external communication rather than direct model registration.
"""

from django.contrib import admin

# Configure admin site branding
admin.site.site_header = "Satellite Ground Station Admin"
admin.site.site_title = "Satellite Ground Station"
admin.site.index_title = "Mission Control Dashboard"