"""
Google Cloud Storage utility for file uploads.

Handles uploading user files to GCS for later processing by Gemini.
"""

from google.cloud import storage
from typing import Dict, Optional
import logging
from pathlib import Path
import os

from app.config import settings

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for managing file uploads to Google Cloud Storage."""

    def __init__(self):
        self.client = storage.Client(project=settings.google_cloud_project)
        self.bucket_name = settings.gcs_bucket_name
        logger.info(f"FileStorageService initialized with bucket: {self.bucket_name}")

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Upload a file to Google Cloud Storage.

        Args:
            file_content: File content as bytes
            filename: Destination filename
            content_type: MIME type
            metadata: Optional metadata dict

        Returns:
            GCS URI (gs://bucket/path)
        """
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(filename)

            # Set content type
            blob.content_type = content_type

            # Set metadata
            if metadata:
                blob.metadata = metadata

            # Upload
            blob.upload_from_string(file_content, content_type=content_type)

            gcs_uri = f"gs://{self.bucket_name}/{filename}"
            logger.info(f"File uploaded to GCS: {gcs_uri}")
            return gcs_uri

        except Exception as e:
            logger.error(f"Error uploading to GCS: {e}", exc_info=True)
            raise

    async def download_to_local(self, gcs_uri: str, local_path: str) -> str:
        """
        Download a file from GCS to local filesystem.

        Used for passing files to Gemini's file API.

        Args:
            gcs_uri: GCS URI (gs://bucket/path)
            local_path: Local destination path

        Returns:
            Local file path
        """
        try:
            # Parse GCS URI
            if not gcs_uri.startswith("gs://"):
                raise ValueError(f"Invalid GCS URI: {gcs_uri}")

            parts = gcs_uri[5:].split("/", 1)
            bucket_name = parts[0]
            blob_name = parts[1] if len(parts) > 1 else ""

            # Download
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Create parent directories
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            blob.download_to_filename(local_path)

            logger.info(f"Downloaded {gcs_uri} to {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"Error downloading from GCS: {e}", exc_info=True)
            raise

    async def delete_file(self, gcs_uri: str) -> bool:
        """
        Delete a file from Cloud Storage.

        Args:
            gcs_uri: GCS URL (gs://bucket/path)

        Returns:
            True if deleted successfully, False otherwise
        """
        if not gcs_uri.startswith("gs://"):
            logger.error(f"Invalid GCS URI: {gcs_uri}")
            return False

        try:
            parts = gcs_uri[5:].split("/", 1)
            bucket_name = parts[0]
            blob_name = parts[1] if len(parts) > 1 else ""

            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()

            logger.info(f"Deleted file: {gcs_uri}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file: {e}", exc_info=True)
            return False
