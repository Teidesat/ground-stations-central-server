import pytest
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from apps.analyze_image.models import Imagen
from apps.dataflow.models import SatelliteData
from apps.logvault.models import LogEntry


@pytest.mark.django_db
def test_required_apps_are_installed():
    PROPER_APPS = ('apps.analyze_image', 'apps.dataflow', 'apps.logvault')

    custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django')]
    for app in PROPER_APPS:
        app_config = f"{app}.apps.{app.replace('apps.','').title()}Config"
        assert (
            app_config in custom_apps
        ), f'La aplicación <{app}> no está "creada/instalada" en el proyecto.'
    assert len(custom_apps) >= len(
        PROPER_APPS
    ), 'El número de aplicaciones propias definidas en el proyecto no es correcto.'

@pytest.mark.django_db
def test_image_model_has_proper_fields():
    PROPER_FIELDS = ('format', 'header', 'exif', 'fecha', 'created_at', 'raw_data', 'content')
    for field in PROPER_FIELDS:
        assert (
            getattr(Imagen, field) is not None
        ), f'El campo <{field}> no está en el modelo Subject.'

@pytest.mark.django_db
def test_satellite_data_model_has_proper_fields():
    PROPER_FIELDS = ('category', 'content', 'timestamp', 'raw_data')
    for field in PROPER_FIELDS:
        assert (
            getattr(SatelliteData, field) is not None
        ), f'El campo <{field}> no está en el modelo Subject.'

@pytest.mark.django_db
def test_logentry_model_has_proper_fields():
    PROPER_FIELDS = ('timestamp', 'level', 'logger', 'module', 'function', 'message', 'request_method', 'request_path', 'request_status_code', 'request_client_ip', 'request_user', 'exception_type', 'exception_message', 'exception_stack_trace', 'extra_data')
    for field in PROPER_FIELDS:
        assert (
            getattr(LogEntry, field) is not None
        ), f'El campo <{field}> no está en el modelo Subject.'

@pytest.mark.django_db
def test_models_are_available_on_admin(admin_client):
    MODELS = ('analyze_image.imagen', 'dataflow.satellitedata', 'logvault.logentry')

    for model in MODELS:
        url_model_path = model.replace('.', '/').lower()
        url = f'/admin/{url_model_path}/'
        response = admin_client.get(url)
        assert response.status_code == 200, f'El modelo <{model}> no está habilitado en el admin.'


AUTH_URLS_GET = [
    '/api/analyze-image',
    '/api/dataflow/satellite-data',
    '/api/logvault',
]

AUTH_URLS_POST = [
    '/api',
    '/api/RGS',
]


@pytest.mark.parametrize('auth_url', AUTH_URLS_GET)
@pytest.mark.django_db
def test_protected_routes_require_token_for_get(client, auth_url):
    response = client.get(auth_url, follow=True)
    assert response.status_code == 401


@pytest.mark.parametrize('auth_url', AUTH_URLS_POST)
@pytest.mark.django_db
def test_protected_routes_require_token_for_post(client, auth_url):
    response = client.post(auth_url)
    if isinstance(response, HttpResponsePermanentRedirect):
        assert response.status_code == 301
    else:
        assert response.status_code == 401


