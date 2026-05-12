# apps/imaging/services.py
"""Business logic services for image processing and validation."""

import io
import logging
from typing import Optional, Dict, Any, Tuple

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)


class ImageProcessingService:
    """Service class for image processing operations."""

    @staticmethod
    def extract_metadata(image_file) -> Dict[str, Any]:
        """Extract metadata from an uploaded image.

        Args:
            image_file: Uploaded file object (PIL-compatible).

        Returns:
            Dictionary containing format, mode, size, width, and height.
        """
        try:
            img = Image.open(image_file)
            metadata = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.size[0],
                'height': img.size[1],
            }
            return metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            return {}

    @staticmethod
    def convert_to_jpeg(image_file, quality: int = 85) -> InMemoryUploadedFile:
        """Convert an image to JPEG format.

        Args:
            image_file: Original image file object.
            quality: JPEG compression quality (1-100, default: 85).

        Returns:
            InMemoryUploadedFile containing JPEG data.
        """
        img = Image.open(image_file)

        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality)
        output.seek(0)

        return InMemoryUploadedFile(
            output,
            field_name='content',
            name='image.jpg',
            content_type='image/jpeg',
            size=len(output.getvalue()),
            charset=None
        )

    @staticmethod
    def validate_image(image_file) -> Tuple[bool, Optional[str]]:
        """Validate that the file is a proper image.

        Args:
            image_file: The file to validate.

        Returns:
            Tuple of (is_valid, error_message). error_message is None if valid.
        """
        try:
            img = Image.open(image_file)
            img.verify()
            return True, None
        except Exception as e:
            return False, str(e)