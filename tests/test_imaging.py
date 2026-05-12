"""
Tests for the imaging app (image analysis and storage).
"""

import pytest
from datetime import datetime, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
import io

pytestmark = pytest.mark.django_db

@pytest.fixture(autouse=True)
def clean_images():
    """Clean images before each test."""
    from apps.imaging.models import Imagen
    Imagen.objects.all().delete()
    yield
    Imagen.objects.all().delete()

class TestImageModel:
    """Tests for the Image model."""

    def test_image_str(self):
        from apps.imaging.models import Imagen
        
        image = Imagen.objects.create(format='jpeg', raw_data='binary')
        assert str(image) == f'Image {image.pk} - jpeg'

    def test_create_image_instance(self):
        from apps.imaging.models import Imagen
        
        image = Imagen.objects.create(
            format='jpeg',
            header='{"test": "header"}',
            exif='{"camera": "test"}',
            fecha=timezone.now(),
            raw_data='raw binary content',
        )
        
        assert image.pk is not None
        assert isinstance(image.created_at, datetime)
        assert image.header_dict == {"test": "header"}
        assert image.exif_dict == {"camera": "test"}

    def test_image_manager_get_by_format(self):
        from apps.imaging.models import Imagen
        
        Imagen.objects.create(format='jpeg', raw_data='data1')
        Imagen.objects.create(format='png', raw_data='data2')
        Imagen.objects.create(format='jpeg', raw_data='data3')
        
        jpegs = Imagen.objects.get_by_format('jpeg')
        assert jpegs.count() == 2

    def test_image_manager_get_recent(self):
        from apps.imaging.models import Imagen
        
        for i in range(15):
            Imagen.objects.create(format='jpeg', raw_data=f'data{i}')
        
        recent = Imagen.objects.get_recent(10)
        assert recent.count() == 10

    def test_image_header_dict_property(self):
        from apps.imaging.models import Imagen
        
        image = Imagen.objects.create(
            format='jpeg',
            header='{"width": 1920, "height": 1080}',
            raw_data='data'
        )
        
        assert image.header_dict == {"width": 1920, "height": 1080}
    
    def test_image_header_dict_invalid_json(self):
        from apps.imaging.models import Imagen
        
        image = Imagen.objects.create(
            format='jpeg',
            header='invalid json',
            raw_data='data'
        )
        
        assert image.header_dict == {}


class TestImageAPI:
    """Tests for the Image API endpoints."""

    def test_all_images_requires_authentication(self, client):
        response = client.get('/api/imaging/', follow=True)
        assert response.status_code == 401

    def test_all_images_empty(self, api_client):
        response = api_client.get('/api/imaging/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['items'] == []
        assert data['count'] == 0

    def test_all_images_with_data(self, api_client):
        from apps.imaging.models import Imagen
        
        Imagen.objects.create(format='jpeg', raw_data='data1')
        Imagen.objects.create(format='png', raw_data='data2')
        
        response = api_client.get('/api/imaging/')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data['items'][0]['id'] == 24
        Imagen.objects.create(format='png', raw_data='data2')
        
        response = api_client.get('/api/imaging/')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data['items'][0]['format'] in ['jpeg', 'png']

    def test_image_detail(self, api_client):
        from apps.imaging.models import Imagen
        
        image = Imagen.objects.create(
            format='jpeg',
            header='{"test": "header"}',
            exif='{"test": "exif"}',
            raw_data='data'
        )
        
        response = api_client.get(f'/api/imaging/{image.pk}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == image.pk
        assert data['format'] == 'jpeg'

    def test_image_detail_not_found(self, api_client):
        response = api_client.get('/api/imaging/99999')
        
        assert response.status_code == 404
        assert 'error' in response.json()

    def test_images_by_date(self, api_client):
        from apps.imaging.models import Imagen
        
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        
        Imagen.objects.create(format='jpeg', raw_data='today', created_at=today)
        Imagen.objects.create(format='png', raw_data='yesterday', created_at=yesterday)
        
        date_str = yesterday.strftime('%Y-%m-%d')

        print(date_str)
        response = api_client.get(f'/api/imaging/by-date/{date_str}')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_images_by_date_invalid_format(self, api_client):
        response = api_client.get('/api/imaging/by-date/04-01-2001')
        
        assert response.status_code == 400
        assert 'error' in response.json()

    def test_upload_image(self, api_client):
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        image_file = SimpleUploadedFile(
            'test.png',
            img_bytes.read(),
            content_type='image/png'
        )
        
        response = api_client.post(
            '/api/imaging/upload/',
            {'file': image_file},
            format='multipart'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'image_id' in data

    def test_upload_invalid_image(self, api_client):
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'not an image',
            content_type='text/plain'
        )
        
        response = api_client.post(
            '/api/imaging/upload/',
            {'file': invalid_file},
            format='multipart'
        )
        
        assert response.status_code == 400
        assert 'error' in response.json()