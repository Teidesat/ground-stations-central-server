# core/schemas/schemas.py
"""Core Pydantic/Ninja schemas for common data structures."""

from ninja import Schema


class UserSchema(Schema):
    """User information response schema."""

    username: str
    email: str = ''
    first_name: str = ''
    last_name: str = ''


class UserError(Schema):
    """User error response schema."""

    message: str


class MsgSchema(Schema):
    """Generic message response schema."""

    content: str