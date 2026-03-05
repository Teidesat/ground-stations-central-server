import pytest
import threading
import socket
import uvicorn

from django.conf import settings
from .fake_servers import create_fake_server


def get_free_port():

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))

    port = sock.getsockname()[1]

    sock.close()

    return port


@pytest.fixture(scope="session")
def fake_server():

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

    settings.RGS_URL = url
    settings.OGS_URL = url
    settings.FOMALHAUT_URL = url

    yield url

    server.should_exit = True

    thread.join()