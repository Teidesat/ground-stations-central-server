import pytest
from main.settings import API_TOKEN


def basic_satellite_test(client, query):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    response = client.get(f'/api/dataflow/satellite-data?{query}', **headers, follow=True)

    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'error': 'No data available'}
    else:
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.django_db
def test_satellite_data_requires_authentication(client):
    response = client.get('/api/dataflow/satellite-data', follow=True)
    assert response.status_code == 401


@pytest.mark.django_db
def test_satellite_data_returns_empty(client):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    response = client.get('/api/dataflow/satellite-data', **headers, follow=True)

    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'error': 'No data available'}
    else:
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.django_db
def test_satellite_data_with_filter_format(client):
    queries = ['format=bin', 'format=json', 'format=xml']
    for query in queries:
        basic_satellite_test(client, query)


@pytest.mark.django_db
def test_satellite_data_with_filter_header(client):
    queries = ['header=telemetry', 'header=communication', 'header=satellite']
    for query in queries:
        basic_satellite_test(client, query)


@pytest.mark.django_db
def test_satellite_data_with_filter_created_at(client):
    queries = [
        'created_at=2022-01-01',
        'created_at=2023-05-15',
        'created_at=2024-12-01',
        'created_at=2025-04-11',
    ]
    for query in queries:
        basic_satellite_test(client, query)


@pytest.mark.django_db
def test_satellite_data_with_combined_filters(client):
    queries = [
        'format=json&header=satellite',
        'format=xml&created_at=2023-05-10',
        'format=bin&header=telemetry&created_at=2024-01-01',
    ]
    for query in queries:
        basic_satellite_test(client, query)


@pytest.mark.django_db
def test_satellite_data_filter_case_insensitive(client):
    queries = [
        'format=JSON',
        'format=Json',
        'header=Satellite',
        'header=SATELLITE',
    ]
    for query in queries:
        basic_satellite_test(client, query)


@pytest.mark.django_db
def test_satellite_data_with_invalid_filters(client):
    queries = [
        'created_at=invalid-date',
        'format=<>',
        'header=',
        'created_at=2025-13-01' 
    ]
    for query in queries:
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
        }
        response = client.get(f'/api/dataflow/satellite-data?{query}', **headers, follow=True)
        assert response.status_code in [422, 404]
