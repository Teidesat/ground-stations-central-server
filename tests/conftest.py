"""
Pytest configuration and fixtures for the satellite ground station tests.
"""

import pytest
import threading
import socket
import uvicorn
from typing import Generator
from django.conf import settings
from .fake_servers import create_fake_server


def get_free_port() -> int:
    """Get a free port for the fake server."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture(scope="session")
def fake_server() -> Generator[str, None, None]:
    """
    Fixture that starts a fake server for external service simulation.
    
    Yields:
        URL of the fake server
    """
    port = get_free_port()
    app = create_fake_server()

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="error"
    )

    server = uvicorn.Server(config)

    thread = threading.Thread(
        target=server.run,
        daemon=True
    )
    thread.start()

    url = f"http://127.0.0.1:{port}"

    # Configure settings to use fake server
    settings.RGS_URL = url
    settings.OGS_URL = url
    settings.FOMALHAUT_URL = url

    yield url

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def auth_headers() -> dict:
    """Fixture providing authentication headers."""
    from django.conf import settings
    return {
        'HTTP_AUTHORIZATION': f'Bearer {settings.API_TOKEN}'
    }


@pytest.fixture
def api_client(client, auth_headers):
    """Fixture providing an authenticated client."""
    client.defaults.update(auth_headers)
    return client