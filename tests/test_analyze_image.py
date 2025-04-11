import pytest
from main.settings import API_TOKEN



@pytest.mark.django_db
def test_all_images_requires_authentication(client):
    response = client.get('/api/analyze-image', follow=True)
    assert response.status_code == 401

import pytest

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
        print(type(data))
        assert isinstance(data, list)


@pytest.mark.django_db
def test_all_images_with_filter_timestamp(client):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    response = client.get('/api/analyze-image?fecha=2024-01-01', **headers, follow=True)

    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'Error': 'No images available'}


@pytest.mark.django_db
def test_all_images_with_filter_format(client):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    response = client.get('/api/analyze-image?format=PNG', **headers, follow=True)

    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'Error': 'No images available'}