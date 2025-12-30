"""File storage utilities for Cloud Storage."""

import logging
import os
from typing import Optional
from uuid import uuid4

from google.cloud import storage

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FileStorageService:
    """Service for handling file uploads to Cloud Storage."""

    def __init__(self):
        """Initialize storage client."""
        self.client = None
        self.bucket = None
        if settings.cloud_storage_bucket:
            try:
                self.client = storage.Client(project=settings.google_cloud_project)
                self.bucket = self.client.bucket(settings.cloud_storage_bucket)
                logger.info(f"Initialized Cloud Storage: {settings.cloud_storage_bucket}")
            except Exception as e:
                logger.warning(f"Could not initialize Cloud Storage: {e}")

    async def upload_file(
        self, file_content: bytes, filename: str, content_type: str
    ) -> Optional[str]:
        """
        Upload a file to Cloud Storage.

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type

        Returns:
            GCS URL of uploaded file, or None if upload failed
        """
        if not self.bucket:
            logger.warning("Cloud Storage not configured, saving locally")
            # Fallback to local storage
            local_path = f"uploads/{uuid4()}_{filename}"
            os.makedirs("uploads", exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(file_content)
            return local_path

        try:
            # Generate unique filename
            unique_filename = f"{uuid4()}_{filename}"
            blob = self.bucket.blob(unique_filename)

            # Upload file
            blob.upload_from_string(file_content, content_type=content_type)

            # Make public (optional, configure based on needs)
            # blob.make_public()

            gcs_url = f"gs://{settings.cloud_storage_bucket}/{unique_filename}"
            logger.info(f"Uploaded file to: {gcs_url}")
            return gcs_url

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None

    async def download_file(self, gcs_url: str) -> Optional[bytes]:
        """
        Download a file from Cloud Storage.

        Args:
            gcs_url: GCS URL (gs://bucket/path)

        Returns:
            File content as bytes, or None if download failed
        """
        if not gcs_url.startswith("gs://"):
            # Try local file
            try:
                with open(gcs_url, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read local file: {e}")
                return None

        if not self.bucket:
            logger.error("Cloud Storage not configured")
            return None

        try:
            # Parse GCS URL
            parts = gcs_url.replace("gs://", "").split("/", 1)
            if len(parts) != 2:
                logger.error(f"Invalid GCS URL: {gcs_url}")
                return None

            bucket_name, blob_name = parts
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Download file
            content = blob.download_as_bytes()
            logger.info(f"Downloaded file from: {gcs_url}")
            return content

        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None

    async def delete_file(self, gcs_url: str) -> bool:
        """
        Delete a file from Cloud Storage.

        Args:
            gcs_url: GCS URL (gs://bucket/path)

        Returns:
            True if deleted successfully, False otherwise
        """
        if not gcs_url.startswith("gs://"):
            # Try local file
            try:
                os.remove(gcs_url)
                return True
            except Exception as e:
                logger.error(f"Failed to delete local file: {e}")
                return False

        if not self.bucket:
            return False

        try:
            parts = gcs_url.replace("gs://", "").split("/", 1)
            if len(parts) != 2:
                return False

            bucket_name, blob_name = parts
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()

            logger.info(f"Deleted file: {gcs_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False


# Singleton instance
_storage_service: Optional[FileStorageService] = None


def get_storage_service() -> FileStorageService:
    """Get the global storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = FileStorageService()
    return _storage_service

