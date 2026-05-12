"""
Tests for the bridge app (data routing and external communication).
"""

import pytest

pytestmark = pytest.mark.django_db


class TestHistoricalDataEndpoints:
    """Tests for historical data endpoints."""

    def test_historical_telemetry_requires_auth(self, client):
        response = client.get('/api/bridge/historical/telemetry')
        assert response.status_code == 401

    def test_historical_telemetry_empty(self, api_client):
        response = api_client.get('/api/bridge/historical/telemetry')
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_historical_telemetry_with_data(self, api_client):
        from apps.control.models import TelemetryMessage
        
        TelemetryMessage.objects.create(
            subsystem="EPS",
            module="battery",
            value=28.5,
            unit="V",
            source="SATELLITE",
            destination="GROUND"
        )
        
        response = api_client.get('/api/bridge/historical/telemetry')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['subsystem'] == "EPS"

    def test_historical_events_with_data(self, api_client):
        from apps.control.models import EventMessage
        
        EventMessage.objects.create(
            subsystem="OBC",
            severity="INFO",
            code="STARTUP",
            description="System started",
            source="SATELLITE",
            destination="GROUND"
        )
        
        response = api_client.get('/api/bridge/historical/events')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['code'] == "STARTUP"

    def test_historical_status_with_data(self, api_client):
        from apps.control.models import StatusMessage
        
        StatusMessage.objects.create(
            subsystem="GENERAL",
            state={"status": "ok"},
            mode="NOMINAL",
            source="SATELLITE",
            destination="GROUND"
        )
        
        response = api_client.get('/api/bridge/historical/status')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['mode'] == "NOMINAL"

    def test_historical_commands_with_data(self, api_client):
        from apps.control.models import CommandMessage
        
        CommandMessage.objects.create(
            command_type="CHANGE_MODE",
            subsystem="ADCS",
            parameters={"mode": "nominal"},
            source="GROUND",
            destination="SATELLITE"
        )
        
        response = api_client.get('/api/bridge/historical/commands')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['command_type'] == "CHANGE_MODE"


class TestLiveDataEndpoints:
    """Tests for live data endpoints with fake server."""

    def test_live_telemetry_requires_auth(self, client):
        response = client.get('/api/bridge/stream/telemetry')
        assert response.status_code == 401

    def test_live_telemetry_with_fake_server(self, api_client, fake_server):
        response = api_client.get(
            '/api/bridge/stream/telemetry',
            {'destination': 'satellite', 'subsystem': 'EPS', 'module': 'battery'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['message']['message_type'] == 'TM'

    def test_live_events_with_fake_server(self, api_client, fake_server):
        response = api_client.get(
            '/api/bridge/stream/events',
            {'destination': 'satellite', 'subsystem': 'OBC'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['message']['message_type'] == 'EV'

    def test_live_status_with_fake_server(self, api_client, fake_server):
        response = api_client.get(
            '/api/bridge/stream/status',
            {'destination': 'satellite', 'subsystem': 'GENERAL'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['message']['message_type'] == 'SM'

    def test_send_command_with_fake_server(self, api_client, fake_server):
        from datetime import datetime
        
        command_data = {
            "message_type": "CM",
            "source": "fomalhaut",
            "destination": "satellite",
            "timestamp": datetime.now().isoformat(),
            "subsystem": "ADCS",
            "parameters": {"mode": "nominal"},
            "status": "SENT",
            "command_type": "CHANGE_MODE"
        }
        
        response = api_client.post(
            '/api/bridge/stream/commands',
            data=command_data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'

    def test_invalid_destination(self, api_client):
        response = api_client.get(
            '/api/bridge/stream/telemetry',
            {'destination': 'invalid_destination', 'subsystem': 'EPS', 'module': 'battery'}
        )
        
        assert response.status_code == 422
        error_detail = response.json()['detail']
        for error in error_detail:
            if error['loc'][-1] == 'destination':
                assert 'is invalid' in error['msg']
                break

    def test_available_destinations(self, api_client):
        response = api_client.get('/api/bridge/destinations')
        
        assert response.status_code == 200
        data = response.json()
        assert 'satellite' in data
        assert 'fomalhaut' in data