import pytest
from main.settings import API_TOKEN


def basic_test(client, query):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    response = client.get(f'/api/analyze-image?{query}', **headers, follow=True)

    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'Error': 'No images available'}
    else:
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.django_db
def test_imagen_str():
    from apps.analyze_image.models import Imagen

    imagen = Imagen.objects.create(format='jpeg', raw_data='binary')
    assert str(imagen) == f'Img {imagen.pk}'


@pytest.mark.django_db
def test_create_imagen_instance():
    from apps.analyze_image.models import Imagen
    from django.utils import timezone

    imagen = Imagen.objects.create(
        format='jpeg',
        header='Test Header',
        exif='Exif data',
        fecha=timezone.now(),
        raw_data='raw binary content',
    )

    assert imagen.pk is not None
    assert isinstance(imagen.created_at, timezone.datetime)



@pytest.mark.django_db
def test_image_field_optional(client, tmpdir):
    from apps.analyze_image.models import Imagen
    from django.core.files.uploadedfile import SimpleUploadedFile

    img = Imagen.objects.create(format='png', raw_data='data')
    assert img.content is None

    image_file = SimpleUploadedFile("test.png", b"file_content", content_type="image/png")
    img2 = Imagen.objects.create(format='png', raw_data='data', content=image_file)
    assert img2.content.name.startswith('media/test')



@pytest.mark.django_db
def test_all_images_requires_authentication(client):
    response = client.get('/api/analyze-image', follow=True)
    assert response.status_code == 401


@pytest.mark.django_db
def test_all_images_returns_empty(client):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    response = client.get('/api/analyze-image', **headers, follow=True)
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 404:
        assert response.json() == {'Error': 'No images available'}
    else:
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.django_db
def test_all_images_with_filter_timestamp(client):
    queries = ['fecha=2024-01-01', 'fecha=2025-04-11', 'fecha=2025-01-01', 'fecha=1990-01-01']
    for query in queries:
        basic_test(client, query)


@pytest.mark.django_db
def test_all_images_with_filter_format(client):
    queries = ['format=Pgn', 'format=png', 'format=jpeg', 'format=jpg']
    for query in queries:
        basic_test(client, query)

@pytest.mark.django_db
def test_all_images_with_filter_created_at(client):
    queries = [
        'created_at=2022-06-01',
        'created_at=2023-12-25',
        'created_at=2024-10-11',
        'created_at=2025-04-11'
    ]
    for query in queries:
        basic_test(client, query)

@pytest.mark.django_db
def test_all_images_with_combined_filters(client):
    queries = [
        'format=png&fecha=2024-01-01',
        'header=satellite&created_at=2023-01-01',
        'format=jpeg&header=test&fecha=2024-12-01',
        'format=jpg&header=telemetry&created_at=2025-01-01'
    ]
    for query in queries:
        basic_test(client, query)
