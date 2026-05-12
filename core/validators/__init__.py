"""
Common validators for data validation.
"""

import re
from pathlib import Path

def validate_image_file(filename: str) -> bool:
    """Validate image file extension."""
    valid_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    return Path(filename).suffix.lower() in valid_extensions

def validate_content_type(content_type: str) -> bool:
    """Validate MIME type."""
    valid_types = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp']
    return content_type in valid_types

def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filename."""
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)