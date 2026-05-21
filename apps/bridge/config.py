# apps/bridge/config.py
"""Configuration for bridge module including service URLs and constants."""

from dataclasses import dataclass
from typing import Dict, Optional

from django.conf import settings


@dataclass(frozen=True)
class ServiceEndpoint:
    """Configuration for a single service endpoint.

    Attributes:
        name: Human-readable service name.
        base_url: Base URL of the service API.
        timeout: Request timeout in seconds (default: 30).
    """

    name: str
    base_url: str
    timeout: int = 30

    def get_url(self, path: str) -> str:
        """Construct the full URL by joining base URL with the given path.

        Args:
            path: API path to append.

        Returns:
            Full URL string.
        """
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"


class ServiceRegistry:
    """Registry of all external services available for routing."""

    SERVICES: Dict[str, ServiceEndpoint] = {}

    @classmethod
    def initialize(cls):
        """Initialize the service registry from Django settings.

        Reads URLs from settings variables:
            - RGS_URL: Radio/Satellite ground station URL
            - OGS_URL: Optical ground station URL
            - FOMALHAUT_URL: Fomalhaut central panel URL
        """
        cls.SERVICES = {
            'satellite': ServiceEndpoint(
                name='Satellite Ground Station',
                base_url=getattr(settings, 'RGS_URL', 'http://localhost:20002'),
                timeout=30
            ),
            'radio_station': ServiceEndpoint(
                name='Radio Station',
                base_url=getattr(settings, 'RGS_URL', 'http://localhost:20002'),
                timeout=30
            ),
            'optical_station': ServiceEndpoint(
                name='Optical Ground Station',
                base_url=getattr(settings, 'OGS_URL', 'http://localhost:20003'),
                timeout=30
            ),
            'fomalhaut': ServiceEndpoint(
                name='Fomalhaut Central Panel',
                base_url=getattr(settings, 'FOMALHAUT_URL', 'http://localhost:20004'),
                timeout=30
            ),
        }

    @classmethod
    def get_service(cls, destination: str) -> Optional[ServiceEndpoint]:
        """Return the service endpoint for a given destination.

        Args:
            destination: Destination identifier (case-insensitive).

        Returns:
            ServiceEndpoint if found, None otherwise.
        """
        if not cls.SERVICES:
            cls.initialize()
        return cls.SERVICES.get(destination.lower())

    @classmethod
    def get_all_destinations(cls) -> list:
        """Return a list of all available destination names."""
        return list(cls.SERVICES.keys())


# Valid destination identifiers for API validation
VALID_DESTINATIONS = ['satellite', 'radio_station', 'optical_station', 'fomalhaut']


class APIPaths:
    """API path constants for external service endpoints."""

    COMMANDS = 'commands'
    TELEMETRY = 'telemetry'
    EVENTS = 'events'
    STATUS = 'status'
    SOFTWARE_UPDATE = 'software_update'