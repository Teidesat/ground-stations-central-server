from urllib import response

import pytest
from main.settings import API_TOKEN


# Historical access
def database_test(client, object, filters = None):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    
    url = f'/api/dataflow/historical/{object}'
    if filters:
        url += f'?{filters}'
    response = client.get(url, **headers, follow=True)

    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'error': 'No data available'}
    else:
        data = response.json()
        assert isinstance(data, list)
    return response.json()

# Live access
def live_test(client, object, params = None, filters = None):
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
    }
    url = f'/api/dataflow/stream/{object}'
    if filters:
        url += f'?{filters}'
    response = client.get(url, params=params, **headers, follow=True)
    print(response.status_code)
    print(response.json())
    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json() == {'error': 'No data available'}
    else:
        data = response.json()
        assert isinstance(data, list)
        return data

# Authentication TESTS

@pytest.mark.django_db
def test_historical_telemetry_data_requires_authentication(client):
    response = client.get('/api/dataflow/historical/telemetry', follow=True)
    assert response.status_code == 401

@pytest.mark.django_db
def test_live_telemetry_data_requires_authentication(client):
    response = client.get('/api/dataflow/stream/telemetry', follow=True)
    assert response.status_code == 401

@pytest.mark.django_db
def test_historical_event_data_requires_authentication(client):
    response = client.get('/api/dataflow/historical/events', follow=True)
    assert response.status_code == 401

@pytest.mark.django_db
def test_live_event_data_requires_authentication(client):
    response = client.get('/api/dataflow/stream/events', follow=True)
    assert response.status_code == 401

@pytest.mark.django_db
def test_historical_status_data_requires_authentication(client):
    response = client.get('/api/dataflow/historical/status', follow=True)
    assert response.status_code == 401

@pytest.mark.django_db
def test_live_status_data_requires_authentication(client):
    response = client.get('/api/dataflow/stream/status', follow=True)
    assert response.status_code == 401

@pytest.mark.django_db
def test_historical_command_data_requires_authentication(client):
    response = client.get('/api/dataflow/historical/commands', follow=True)
    assert response.status_code == 401


# DB TESTS

@pytest.mark.django_db
def test_historical_telemetry_data(client):
    from datetime import datetime
    from apps.core.models import TelemetryMessage
    
    TelemetryMessage.objects.create(
        message_type="TM",
        source="test",
        destination="ground_station",
        timestamp=datetime.now(),
        subsystem="power",
        module="battery",
        value=75.5,
        unit="%",
        valid=True
    )

    data = database_test(client, 'telemetry')
    if data:
        assert data[0].get('message_type') == 'TM'

@pytest.mark.django_db
def test_historical_event_data(client):
    from datetime import datetime
    from apps.core.models import EventMessage

    EventMessage.objects.create(
        message_type="EV",
        source="test",
        destination="ground_station",
        timestamp=datetime.now(),
        subsystem="communications",
        severity="CRITICAL",
        code="COMMS_FAILURE",
        description="Communication failure detected"
    )

    data = database_test(client, 'events')
    if data:
        assert data[0].get('message_type') == 'EV'

@pytest.mark.django_db
def test_historical_status_data(client):
    from datetime import datetime
    from apps.core.models import StatusMessage

    StatusMessage.objects.create(
        message_type="SM",
        source="test",
        destination="ground_station",
        timestamp=datetime.now(),
        subsystem="navigation",
        state={"mode": "safe"},
        mode="SAFE"
    )

    data = database_test(client, 'status')
    if data:
        assert data[0].get('message_type') == 'ST'

@pytest.mark.django_db
def test_historical_command_data(client):
    from datetime import datetime
    from apps.core.models import CommandMessage

    CommandMessage.objects.create(
        message_type="CM",
        source="ground_station",
        destination="test",
        timestamp=datetime.now(),
        subsystem="payload",
        parameters={"action": "activate"},
        status="PENDING",
        execution_time=datetime.now(),
        command_type="ACTIVATE_PAYLOAD"
    )

    data = database_test(client, 'commands')
    if data:
        assert data[0].get('message_type') == 'CM'

@pytest.mark.django_db
def test_wrong_historical_data(client):
    response = client.get('/api/dataflow/historical/unknown', follow=True)
    assert response.status_code == 404


# Live TESTS
def test_live_telemetry_data(client):
    from apps.dataflow.schemas import TelemetryRequestSchema
    requestSchema = TelemetryRequestSchema(
        destination="satellite",
        subsystem="power",
        module="battery"
    )

    data = live_test(client, 'telemetry', params=requestSchema)
    if data:
        assert data.get('status') == 'success'
        assert data.get('message').get('message_type') == 'TM'

# def test_live_event_data(client):
#     data = live_test(client, 'events')
#     if data:
#         assert data.get('status') == 'success'
#         assert data.get('message').get('message_type') == 'EVENT'

# def test_live_status_data(client):
#     data = live_test(client, 'status')
#     if data:
#         assert data.get('status') == 'success'
#         assert data.get('message').get('message_type') == 'STATUS'

# def test_live_command_data(client):
#     data = live_test(client, 'commands')
#     if data:
#         assert data.get('status') == 'success'
#         assert data.get('message').get('message_type') == 'COMMAND'
    


# Filters TESTS

# @pytest.mark.django_db
# def test_historical_telemetry_data_with_filters(client):
#     filters = 'format=json&created_at=2023-05-10'
#     database_test(client, 'telemetry', filters)

# @pytest.mark.django_db
# def test_historical_event_data_with_filters(client):
#     filters = 'header=communication&created_at=2024-01-01'
#     database_test(client, 'events', filters)

# @pytest.mark.django_db
# def test_historical_status_data_with_filters(client):
#     filters = 'format=xml&header=satellite'
#     database_test(client, 'status', filters)

# @pytest.mark.django_db
# def test_historical_command_data_with_filters(client):
#     filters = 'created_at=2022-01-01'
#     database_test(client, 'commands', filters) 


# 





# @pytest.mark.django_db
# def test_satellite_data_returns_empty(client):
#     headers = {
#         "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
#     }
#     response = client.get('/api/dataflow/satellite-data', **headers, follow=True)

#     assert response.status_code in [200, 404]
#     if response.status_code == 404:
#         assert response.json() == {'error': 'No data available'}
#     else:
#         data = response.json()
#         assert isinstance(data, list)


# @pytest.mark.django_db
# def test_satellite_data_with_filter_format(client):
#     queries = ['format=bin', 'format=json', 'format=xml']
#     for query in queries:
#         basic_satellite_test(client, query)


# @pytest.mark.django_db
# def test_satellite_data_with_filter_header(client):
#     queries = ['header=telemetry', 'header=communication', 'header=satellite']
#     for query in queries:
#         basic_satellite_test(client, query)


# @pytest.mark.django_db
# def test_satellite_data_with_filter_created_at(client):
#     queries = [
#         'created_at=2022-01-01',
#         'created_at=2023-05-15',
#         'created_at=2024-12-01',
#         'created_at=2025-04-11',
#     ]
#     for query in queries:
#         basic_satellite_test(client, query)


# @pytest.mark.django_db
# def test_satellite_data_with_combined_filters(client):
#     queries = [
#         'format=json&header=satellite',
#         'format=xml&created_at=2023-05-10',
#         'format=bin&header=telemetry&created_at=2024-01-01',
#     ]
#     for query in queries:
#         basic_satellite_test(client, query)


# @pytest.mark.django_db
# def test_satellite_data_filter_case_insensitive(client):
#     queries = [
#         'format=JSON',
#         'format=Json',
#         'header=Satellite',
#         'header=SATELLITE',
#     ]
#     for query in queries:
#         basic_satellite_test(client, query)


# @pytest.mark.django_db
# def test_satellite_data_with_invalid_filters(client):
#     queries = [
#         'created_at=invalid-date',
#         'format=<>',
#         'header=',
#         'created_at=2025-13-01' 
#     ]
#     for query in queries:
#         headers = {
#             "HTTP_AUTHORIZATION": f"Bearer {API_TOKEN}"
#         }
#         response = client.get(f'/api/dataflow/satellite-data?{query}', **headers, follow=True)
#         assert response.status_code in [422, 404]
