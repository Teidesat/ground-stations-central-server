# config/auth.py
"""Authentication configuration for the Ninja API."""

from django.conf import settings
from ninja.security import HttpBearer


class SimpleTokenAuth(HttpBearer):
    """Simple token-based authentication using Bearer tokens.

    Expects 'Authorization: Bearer <token>' header in requests.
    """

    def authenticate(self, request, token: str):
        """Validate the provided Bearer token.

        Args:
            request: The HTTP request object.
            token: The Bearer token string from the Authorization header.

        Returns:
            String "authenticated" if token is valid, None otherwise.
        """
        if token == settings.API_TOKEN:
            return "authenticated"
        return None