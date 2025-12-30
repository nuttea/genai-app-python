"""Media processing utilities."""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class MediaValidator:
    """Validator for media files."""

    def validate_file(
        self, file_path: str, content_type: str, file_size: int
    ) -> Tuple[bool, str]:
        """
        Validate a media file.

        Args:
            file_path: Path to the media file
            content_type: MIME type of the file
            file_size: File size in bytes

        Returns:
            Tuple of (is_valid, message)
        """
        # Basic validation - file size already checked by upload endpoint
        # This is just for additional checks

        # Check if content type is reasonable
        if not content_type:
            return False, "Missing content type"

        logger.info(
            f"Media file validated: {file_path} ({content_type}, {file_size / (1024**2):.1f}MB)"
        )
        return True, "Valid"


def validate_file_size(file_size: int, max_size_mb: int = 500) -> bool:
    """
    Validate file size.

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        True if valid, False otherwise
    """
    max_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_bytes


def validate_file_type(filename: str, allowed_types: list[str]) -> bool:
    """
    Validate file type by extension.

    Args:
        filename: Original filename
        allowed_types: List of allowed extensions (e.g., ['.mp4', '.mov'])

    Returns:
        True if valid, False otherwise
    """
    ext = Path(filename).suffix.lower()
    return ext in allowed_types


def get_temp_file_path(suffix: str = "") -> str:
    """
    Get a temporary file path.

    Args:
        suffix: File suffix/extension

    Returns:
        Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.close()
    return temp_file.name


def estimate_reading_time(word_count: int, words_per_minute: int = 200) -> int:
    """
    Estimate reading time for content.

    Args:
        word_count: Number of words
        words_per_minute: Average reading speed

    Returns:
        Estimated reading time in minutes
    """
    return max(1, round(word_count / words_per_minute))


def extract_hashtags(text: str, max_count: int = 10) -> list[str]:
    """
    Extract hashtags from text.

    Args:
        text: Text to search
        max_count: Maximum number of hashtags

    Returns:
        List of hashtags (without # symbol)
    """
    words = text.split()
    hashtags = [word[1:] for word in words if word.startswith("#")]
    return hashtags[:max_count]


# File type constants
VIDEO_TYPES = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
IMAGE_TYPES = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
DOCUMENT_TYPES = [".md", ".txt", ".pdf"]

# MIME type mapping
MIME_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
}


def get_mime_type(filename: str) -> Optional[str]:
    """Get MIME type for a filename."""
    ext = Path(filename).suffix.lower()
    return MIME_TYPES.get(ext)
