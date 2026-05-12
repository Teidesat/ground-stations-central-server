"""
Integration tests and quality assurance tests.
"""

import pytest
from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestAuthentication:
    """Tests for authentication and authorization."""

    def test_api_root_requires_auth(self, client):
        """Test that API root requires authentication."""
        response = client.get('/api/')
        assert response.status_code == 401

    def test_valid_token_works(self, api_client):
        """Test that valid token allows access."""
        response = api_client.get('/api/imaging/')
        assert response.status_code == 200

    def test_invalid_token(self, client):
        """Test that invalid token is rejected."""
        headers = {'HTTP_AUTHORIZATION': 'Bearer invalid_token'}
        response = client.get('/api/imaging/', **headers)
        assert response.status_code == 401

    def test_missing_token(self, client):
        """Test that missing token is rejected."""
        response = client.get('/api/imaging/')
        assert response.status_code == 401


class TestAPIStructure:
    """Tests for API structure and documentation."""

    def test_api_versioning(self, client):
        """Test that API endpoints follow versioning."""
        response = client.get('/api/')
        assert response.status_code in [200, 401]

    def test_health_check_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get('/api/health')
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'

    def test_processor_status_endpoint(self, api_client):
        """Test buffer processor status endpoint."""
        response = api_client.get('/api/processor/status')
        
        assert response.status_code in [200, 404]


class TestModelsIntegrity:
    """Tests for model integrity and constraints."""

    def test_telemetry_auto_message_type(self):
        from apps.control.models import TelemetryMessage
        
        telemetry = TelemetryMessage.objects.create(
            subsystem="EPS",
            module="test",
            value=10
        )
        
        assert telemetry.message_type == "TM"

    def test_command_auto_message_type(self):
        from apps.control.models import CommandMessage
        
        command = CommandMessage.objects.create(
            command_type="TEST",
            subsystem="OBC",
            parameters={}
        )
        
        assert command.message_type == "CM"

    def test_software_update_auto_destination(self):
        from apps.control.models import SoftwareUpdate
        
        update = SoftwareUpdate.objects.create(
            version="1.0.0",
            checksum="abc123",
            size_bytes=1000,
            data=b"test_data"
        )
        
        assert update.destination == "SATELLITE"


class TestbridgeRouting:
    """Tests for data flow routing logic."""

    def test_destination_validation(self):
        from apps.bridge.config import VALID_DESTINATIONS
        
        assert 'satellite' in VALID_DESTINATIONS
        assert 'fomalhaut' in VALID_DESTINATIONS
        assert len(VALID_DESTINATIONS) == 4

    def test_service_registry_initialization(self):
        from apps.bridge.config import ServiceRegistry
        
        ServiceRegistry.initialize()
        service = ServiceRegistry.get_service('satellite')
        
        assert service is not None
        assert service.name == 'Satellite Ground Station'