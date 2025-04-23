import pytest

from main.settings import API_TOKEN


def basic_log_test(client, query):
    headers = {'HTTP_AUTHORIZATION': f'Bearer {API_TOKEN}'}
    response = client.get(f'/api/logvault?{query}', **headers, follow=True)

    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'error': 'No logs available'}
    else:
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.django_db
def test_logs_filter_timestamp(client):
    queries = ['timestamp=2024-01-01', 'timestamp=2025-04-11', 'timestamp=2030-01-01']
    for query in queries:
        basic_log_test(client, query)


@pytest.mark.django_db
def test_logs_filter_basic_fields(client):
    queries = [
        'level=INFO',
        'level=ERROR',
        'logger=ground-stations-central-server',
        'module=dataflow.api',
        'function=all_satellite_data',
    ]
    for query in queries:
        basic_log_test(client, query)


@pytest.mark.django_db
def test_logs_filter_message_and_function_contains(client):
    queries = [
        'message=Petición',
        'message=ERROR',
        'function=satellite',
        'function=log',
    ]
    for query in queries:
        basic_log_test(client, query)


@pytest.mark.django_db
def test_logs_filter_request_fields(client):
    queries = [
        'request_method=GET',
        'request_method=POST',
        'request_path=/api/satellite-data',
        'request_client_ip=127.0.0.1',
        'request_user=admin',
    ]
    for query in queries:
        basic_log_test(client, query)


@pytest.mark.django_db
def test_logs_filter_exception_fields(client):
    queries = [
        'exception_type=ValueError',
        'exception_type=ValidationError',
        'exception_message=invalid',
        'exception_message=formato',
    ]
    for query in queries:
        basic_log_test(client, query)


@pytest.mark.django_db
def test_logs_with_invalid_filters(client):
    queries = [
        'timestamp=invalid-date',
        'level=<>',
        'function=',
        'exception_type=12345',
    ]
    for query in queries:
        headers = {'HTTP_AUTHORIZATION': f'Bearer {API_TOKEN}'}
        response = client.get(f'/api/logvault{query}', **headers, follow=True)
        assert response.status_code in [422, 404]
