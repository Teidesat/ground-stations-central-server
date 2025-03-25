from django.db import models
import ast

# Create your models here.

class Imagen(models.Model):
    format = models.CharField(max_length=10, null=True)
    header = models.TextField(null= True, blank=True)
    exif = models.TextField(null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    raw_data = models.TextField()
    content = models.ImageField(
        upload_to='media',
        blank=True,
        null=True, 
    )
    
    
    def __str__(self):
       return f'Img {self.pk}'
    