from django.db import models


class Imagen(models.Model):
    format = models.CharField(max_length=10, null=True)
    header = models.TextField(null=True, blank=True)
    exif = models.TextField(null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    raw_data = models.TextField()
    content = models.ImageField(upload_to='media', blank=True, null=True, default=None)

    def __str__(self):
        return f'Img {self.pk}'
