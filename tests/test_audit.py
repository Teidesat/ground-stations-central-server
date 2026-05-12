"""
Tests for the audit app (log management).
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone

pytestmark = pytest.mark.django_db()

@pytest.fixture(autouse=True)
def clean_logs():
    """Limpiar logs antes de cada test."""
    from apps.audit.models import LogEntry
    LogEntry.objects.all().delete()
    yield
    LogEntry.objects.all().delete()


class TestLogEntryModel:
    """Tests for LogEntry model."""

    def test_create_log_entry(self):
        from apps.audit.models import LogEntry
        
        log = LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger="test-logger",
            module="test_module",
            function="test_function",
            message="Test message"
        )
        
        assert log.pk is not None
        assert str(log).startswith('[')

    def test_log_entry_properties(self):
        from apps.audit.models import LogEntry
        
        log_info = LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger="test",
            module="test",
            function="test",
            message="Info message"
        )
        
        log_error = LogEntry.objects.create(
            timestamp=timezone.now(),
            level="ERROR",
            logger="test",
            module="test",
            function="test",
            message="Error message"
        )
        
        assert log_info.is_error is False
        assert log_error.is_error is True

    def test_log_entry_with_exception(self):
        from apps.audit.models import LogEntry
        
        log = LogEntry.objects.create(
            timestamp=timezone.now(),
            level="ERROR",
            logger="test",
            module="test",
            function="test",
            message="Error with exception",
            exception_type="ValueError",
            exception_message="Invalid value"
        )
        
        assert log.has_exception is True
        assert log.exception_type == "ValueError"


class TestLogService:
    """Tests for LogService."""

    @pytest.mark.asyncio
    async def test_create_log(self):
        from apps.audit.services import create_log
        
        log = await create_log(
            level="INFO",
            logger="test-logger",
            module="test_module",
            function="test_function",
            message="Test async message"
        )
        
        assert log is not None
        assert log.message == "Test async message"

    @pytest.mark.asyncio
    async def test_log_statistics(self):
        from apps.audit.services import LogService
        from apps.audit.models import LogEntry
        from asgiref.sync import sync_to_async
        
        # Crear logs usando sync_to_async
        @sync_to_async
        def create_test_logs():
            for i in range(10):
                LogEntry.objects.create(
                    timestamp=timezone.now(),
                    level="INFO",
                    logger="test",
                    module="test",
                    function="test",
                    message=f"Message {i}"
                )
            
            for i in range(5):
                LogEntry.objects.create(
                    timestamp=timezone.now(),
                    level="ERROR",
                    logger="test",
                    module="test",
                    function="test",
                    message=f"Error {i}"
                )
        
        await create_test_logs()
        stats = await LogService.get_statistics(hours=24)
        
        assert stats['total_count'] == 16
        assert stats['by_level']['INFO'] == 11
        assert stats['by_level']['ERROR'] == 5
        assert stats['error_rate'] > 0


class TestLogAPI:
    """Tests for Log API endpoints."""

    def test_get_logs_requires_authentication(self, client):
        response = client.get('/api/audit/')
        assert response.status_code == 401

    def test_get_logs_empty(self, api_client):
        response = api_client.get('/api/audit/')
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_logs_with_data(self, api_client):
        from apps.audit.models import LogEntry
        
        LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger="test",
            module="test",
            function="test",
            message="Test log"
        )
        
        response = api_client.get('/api/audit/')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['level'] == "INFO"

    def test_get_log_errors(self, api_client):
        from apps.audit.models import LogEntry
        
        LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger="test",
            module="test",
            function="test",
            message="Info"
        )
        LogEntry.objects.create(
            timestamp=timezone.now(),
            level="ERROR",
            logger="test",
            module="test",
            function="test",
            message="Error"
        )
        
        response = api_client.get('/api/audit/errors')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['level'] == "ERROR"

    def test_get_log_exceptions(self, api_client):
        from apps.audit.models import LogEntry
        
        LogEntry.objects.create(
            timestamp=timezone.now(),
            level="ERROR",
            logger="test",
            module="test",
            function="test",
            message="With exception",
            exception_type="ValueError"
        )
        LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger="test",
            module="test",
            function="test",
            message="Without exception"
        )
        
        response = api_client.get('/api/audit/exceptions')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_log_statistics(self, api_client):
        from apps.audit.models import LogEntry
        
        for i in range(10):
            LogEntry.objects.create(
                timestamp=timezone.now(),
                level="INFO",
                logger="test",
                module="test",
                function="test",
                message=f"Message {i}"
            )
        
        response = api_client.get('/api/audit/statistics')
        
        assert response.status_code == 200
        data = response.json()
        assert 'total_count' in data
        assert 'by_level' in data

    def test_get_log_detail(self, api_client):
        from apps.audit.models import LogEntry
        
        log = LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger="test",
            module="test",
            function="test",
            message="Test detail"
        )
        
        response = api_client.get(f'/api/audit/{log.pk}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == log.pk
        assert data['message'] == "Test detail"


    # FALLANDO
    def test_delete_all_logs(self, api_client):
        from apps.audit.models import LogEntry
        
        log = LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            logger="test",
            module="test",
            function="test",
            message="Test detail"
        )

        response = api_client.delete('/api/audit/cleanup?days=0')
        
        assert response.status_code == 200
        data = response.json()
        print(data)
        assert data['deleted'] == 1
        assert LogEntry.objects.count() == 1 # Cleaning log
