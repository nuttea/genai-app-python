"""
Upload API Response Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class FileInfo(BaseModel):
    """Information about an uploaded file."""

    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    size_bytes: int = Field(..., description="File size in bytes")
    gcs_uri: Optional[str] = Field(
        None, description="Artifact URI (artifact://<id> for ADK artifacts)"
    )
    file_type: str = Field(..., description="File type category (video, image, document)")
    extracted_text: Optional[str] = Field(
        None, description="Extracted text content (for text/markdown files)"
    )
    artifact_id: Optional[str] = Field(None, description="ADK Artifact ID for binary files")


class UploadResponse(BaseModel):
    """Response from file upload endpoints."""

    success: bool = Field(..., description="Whether upload was successful")
    message: str = Field(..., description="Success or error message")
    file: Optional[FileInfo] = Field(None, description="Single uploaded file info")
    files: Optional[List[FileInfo]] = Field(
        None, description="Multiple uploaded files info (for batch uploads)"
    )
