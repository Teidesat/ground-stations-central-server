# apps/bridge/clients.py
"""HTTP clients for external service communication."""

import logging
from typing import Dict, Any, Optional

import httpx

from .config import ServiceEndpoint
from .exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class ExternalServiceClient:
    """Async HTTP client for communicating with external services."""

    def __init__(self, service: ServiceEndpoint):
        """Initialize the client with a service endpoint.

        Args:
            service: ServiceEndpoint configuration containing base URL and timeout.
        """
        self.service = service
        self.timeout = httpx.Timeout(service.timeout)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Return an existing HTTP client or create a new one.

        Returns:
            Configured httpx.AsyncClient instance.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
        return self._client

    async def close(self):
        """Close the HTTP client and release resources."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a POST request to the external service.

        Args:
            path: API path to append to the base URL (e.g., 'commands').
            data: JSON-serializable data to send in the request body.

        Returns:
            Response JSON as a dictionary.

        Raises:
            ExternalServiceError: If the request fails due to timeout,
                HTTP error, or other communication issues.
        """
        url = self.service.get_url(path)
        client = await self._get_client()

        try:
            logger.debug(f"POST {url} - Sending data: {data}")
            response = await client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            logger.info(f"POST {url} - Success (status={response.status_code})")
            return result

        except httpx.TimeoutException as e:
            error_msg = f"Timeout connecting to {self.service.name} at {url}"
            logger.error(error_msg)
            raise ExternalServiceError(error_msg) from e

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} from {self.service.name}: {e.response.text}"
            logger.error(error_msg)
            raise ExternalServiceError(error_msg) from e

        except Exception as e:
            error_msg = f"Failed to communicate with {self.service.name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ExternalServiceError(error_msg) from e

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a GET request to the external service.

        Args:
            path: API path to append to the base URL.
            params: Optional query parameters to include in the request.

        Returns:
            Response JSON as a dictionary.

        Raises:
            ExternalServiceError: If the request fails due to timeout,
                HTTP error, or other communication issues.
        """
        url = self.service.get_url(path)
        client = await self._get_client()

        try:
            logger.debug(f"GET {url} - Params: {params}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            logger.info(f"GET {url} - Success (status={response.status_code})")
            return result

        except httpx.TimeoutException as e:
            error_msg = f"Timeout connecting to {self.service.name} at {url}"
            logger.error(error_msg)
            raise ExternalServiceError(error_msg) from e

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} from {self.service.name}: {e.response.text}"
            logger.error(error_msg)
            raise ExternalServiceError(error_msg) from e

        except Exception as e:
            error_msg = f"Failed to communicate with {self.service.name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ExternalServiceError(error_msg) from e


class ServiceClientPool:
    """Pool of HTTP clients for managing connections to multiple services."""

    _clients: Dict[str, ExternalServiceClient] = {}

    @classmethod
    def get_client(cls, destination: str, service_endpoint) -> ExternalServiceClient:
        """Return an existing client for the destination or create a new one.

        Args:
            destination: The destination service identifier.
            service_endpoint: ServiceEndpoint configuration for the destination.

        Returns:
            ExternalServiceClient instance for the destination.
        """
        if destination not in cls._clients:
            cls._clients[destination] = ExternalServiceClient(service_endpoint)
        return cls._clients[destination]

    @classmethod
    async def close_all(cls):
        """Close all client connections and clear the pool."""
        for client in cls._clients.values():
            await client.close()
        cls._clients.clear()