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

    def test_historical_software_updates_with_data(self, api_client):
        """Test retrieving historical software updates."""
        from apps.control.models import SoftwareUpdateMessage
        import hashlib
        
        test_data = b"test_firmware_data_1"
        checksum1 = hashlib.sha256(test_data).hexdigest()
        
        test_data2 = b"test_firmware_data_2"
        checksum2 = hashlib.sha256(test_data2).hexdigest()
        
        SoftwareUpdateMessage.objects.create(
            version="1.0.0",
            checksum=checksum1,
            size_bytes=len(test_data),
            verified=True,
            data=test_data,
            source="GROUND",
            destination="SATELLITE"
        )
        
        SoftwareUpdateMessage.objects.create(
            version="2.0.0",
            checksum=checksum2,
            size_bytes=len(test_data2),
            verified=False,
            data=test_data2,
            source="GROUND",
            destination="SATELLITE"
        )
        
        response = api_client.get('/api/bridge/historical/software_updates')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]['message_type'] == "UP"
        assert 'verified' in data[0]
        assert data[0]['verified'] is not False

    def test_historical_software_updates_with_filters(self, api_client):
        """Test filtering software updates."""
        from apps.control.models import SoftwareUpdateMessage
        import hashlib
        
        test_data = b"test_firmware_data_1"
        checksum1 = hashlib.sha256(test_data).hexdigest()
        
        test_data2 = b"test_firmware_data_2"
        checksum2 = hashlib.sha256(test_data2).hexdigest()
        
        SoftwareUpdateMessage.objects.create(
            version="1.0.0",
            checksum=checksum1,
            size_bytes=len(test_data),
            verified=True,
            data=test_data,
            source="GROUND",
            destination="SATELLITE"
        )
        
        SoftwareUpdateMessage.objects.create(
            version="2.0.0",
            checksum=checksum2,
            size_bytes=len(test_data2),
            verified=False,
            data=test_data2,
            source="GROUND",
            destination="SATELLITE"
        )
        
        response = api_client.get(
            '/api/bridge/historical/software_updates',
            {'verified': True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['version'] == "1.0.0"
        assert data[0]['verified'] is True
        assert data[0]['message_type'] == "UP"

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

    def test_live_software_update_with_fake_server(self, api_client):
        """Test getting live software update from fake server."""
        from apps.control.models import SoftwareUpdateMessage
        
        response = api_client.get(
            '/api/bridge/stream/software_update',
            {'destination': 'satellite'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['stored'] is True
        assert data['data']['version'] == "3.0.0"
        assert data['data']['verified'] is True
        assert data['data']['size_bytes'] == 3145728
        
        assert SoftwareUpdateMessage.objects.filter(version="3.0.0").exists()

    def test_live_software_update_without_version(self, api_client, fake_server):
        """Test getting latest live software update without specifying version."""
        
        response = api_client.get(
            '/api/bridge/stream/software_update',
            {'destination': 'satellite'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['stored'] is True

    def test_live_software_update_invalid_destination(self, api_client):
        """Test live software update with invalid destination."""
        response = api_client.get(
            '/api/bridge/stream/software_update',
            {'destination': 'invalid'}
        )
        
        assert response.status_code == 422
        error_msg = response.json()["detail"][0]["msg"]

        assert "Destination 'invalid' is invalid" in error_msg

    def test_live_verify_update_with_fake_server(self, api_client):
        """Test verifying a software update."""
        import base64
        import hashlib
        from apps.control.models import SoftwareUpdateMessage
        
        firmware_data = b"test_firmware_data_for_version_1_5_0"
        encoded_data = base64.b64encode(firmware_data).decode()
        valid_checksum = hashlib.sha256(firmware_data).hexdigest()
        
        response = api_client.post(
            '/api/bridge/stream/software_update',
            {
                'destination': 'satellite',
                'version': '1.5.0',
                'checksum': valid_checksum,
                'data': encoded_data,
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['message']['verified'] is True
        
        assert SoftwareUpdateMessage.objects.filter(version="1.5.0", verified=True).exists()

    def test_live_verify_update_wrong_checksum(self, api_client):
        """Test verifying with wrong checksum."""
        import base64
        import hashlib
        from apps.control.models import SoftwareUpdateMessage
        
        firmware_data = b"test_firmware_data_for_version_1_5_0"
        firmware_invalid = b"test_firmware_data_for_invalid_checksum"
        encoded_data = base64.b64encode(firmware_data).decode()
        invalid_checksum = hashlib.sha256(firmware_invalid).hexdigest()
        
        response = api_client.post(
            '/api/bridge/stream/software_update',
            {
                'destination': 'satellite',
                'version': '1.5.0',
                'checksum': invalid_checksum,
                'data': encoded_data,
            },
            content_type='application/json'
        )
        
        assert response.status_code == 502
        assert response.json()['error'] == 'Failed to send software update'

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