from django.db import models
import ast

# Create your models here.

class Imagen(models.Model):
    format = models.CharField(max_length=10, null=True)
    header = models.TextField(null= True, blank=True)
    exif = models.TextField(null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    content = models.ImageField(
        upload_to='media',
    )
    
'''
    def save(self, *args, **kwargs):
        exif = ast.literal_eval(self.exif)
        date = datetime.strptime(exif["DateTime"], "%Y:%m:%d %H:%M:%S")
        self.fecha = date
        super().save(*args, **kwargs)
'''   
    
   