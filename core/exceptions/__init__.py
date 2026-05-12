"""
Custom exceptions for the core module.
"""

class CoreException(Exception):
    """Base exception for core module."""
    pass

class BufferFullException(CoreException):
    """Raised when attempting to add to a full buffer."""
    pass

class BufferEmptyException(CoreException):
    """Raised when attempting to get from an empty buffer."""
    pass

class ClassificationError(CoreException):
    """Raised when image classification fails."""
    pass