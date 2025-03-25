from django.contrib import admin
from .models import Imagen
# Register your models here.

@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'format',
        'created_at',
    )