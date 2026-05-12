"""
Custom exceptions for bridge module.
"""

class BridgeException(Exception):
    """Base exception for bridge module."""
    pass

class ExternalServiceError(BridgeException):
    """Raised when external service request fails."""
    pass

class InvalidDestinationError(BridgeException):
    """Raised when destination is invalid."""
    pass

class DataValidationError(BridgeException):
    """Raised when data validation fails."""
    pass