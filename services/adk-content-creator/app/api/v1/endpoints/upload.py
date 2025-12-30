"""
File Upload API Endpoints

Handles uploading of various media files (video, images, documents)
to Google Cloud Storage for processing by Gemini.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from pathlib import Path
import uuid
from datetime import datetime

from app.core.file_storage import FileStorageService
from app.core.media_utils import MediaValidator
from app.models.upload_response import UploadResponse, FileInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


# File size limits (in bytes)
MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024  # 2GB (Gemini supports up to 2GB)
MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB

# Supported file types
SUPPORTED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/jpg"}
SUPPORTED_DOCUMENT_TYPES = {
    "text/plain",
    "text/markdown",
    "text/x-markdown",
    "application/pdf",
    "application/octet-stream",  # Fallback for unknown types
}


@router.post("/single", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_single_file(
    file: UploadFile = File(..., description="File to upload (video, image, or document)")
) -> UploadResponse:
    """
    Upload a single file for content creation.

    Supported formats:
    - Video: MP4, MOV, AVI, WebM (max 2GB)
    - Images: PNG, JPG, GIF, WebP (max 20MB)
    - Documents: TXT, MD, PDF (max 50MB)

    Smart handling:
    - Text/Markdown files: Content extracted and returned as text
    - Images/Videos: Stored as ADK Artifacts for Gemini multimodal processing

    Returns:
    - File info with content or artifact reference
    """
    try:
        # Validate file type (with fallback detection from filename)
        content_type = file.content_type or ""
        filename = file.filename or ""
        
        # Try to determine type from content_type first, then from filename extension
        file_type = _determine_file_type(content_type, filename)

        if not file_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {content_type} ({filename}). "
                f"Supported: video (MP4, MOV, AVI, WebM), "
                f"images (PNG, JPG, GIF, WebP), "
                f"documents (TXT, MD, PDF)",
            )

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Validate file size
        _validate_file_size(file_size, file_type)

        # Generate unique filename
        file_extension = Path(file.filename or "file").suffix
        unique_filename = (
            f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
        )

        # Smart handling based on file type
        gcs_uri = None
        extracted_text = None
        local_path = None

        # Determine if we should extract text or store as artifact
        ext = Path(filename).suffix.lower()
        should_extract_text = ext in {".txt", ".md", ".markdown"} or content_type in {
            "text/plain",
            "text/markdown",
            "text/x-markdown",
        }

        if should_extract_text:
            # For text/markdown files, extract content directly (no GCS needed)
            try:
                extracted_text = content.decode("utf-8")
                logger.info(
                    f"Extracted text from {file.filename}: {len(extracted_text)} characters"
                )
            except UnicodeDecodeError:
                logger.warning(
                    f"Failed to decode {file.filename} as UTF-8, will store as artifact"
                )
                should_extract_text = False

        if not should_extract_text:
            # For images, videos, PDFs: Store locally for ADK Artifacts
            # (Gemini will process these as multimodal inputs)
            local_dir = Path("/app/uploads")
            local_dir.mkdir(parents=True, exist_ok=True)
            local_path = str(local_dir / unique_filename)

            # Write to local file
            with open(local_path, "wb") as f:
                f.write(content)

            # For artifact reference, use local path
            gcs_uri = f"file://{local_path}"
            logger.info(
                f"File stored locally for artifact processing: {file.filename} -> {local_path}"
            )

        # Build response
        file_info = FileInfo(
            filename=file.filename or unique_filename,
            content_type=content_type,
            size_bytes=file_size,
            gcs_uri=gcs_uri,
            file_type=file_type,
            extracted_text=extracted_text,  # Will be None for non-text files
        )

        logger.info(
            f"File processed successfully: {file.filename} "
            f"({'text extracted' if extracted_text else 'stored as artifact'}, {file_size} bytes)"
        )

        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            file=file_info,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )
    finally:
        await file.close()


@router.post("/batch", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_batch(
    files: List[UploadFile] = File(..., description="Multiple files to upload (max 10 files)")
) -> UploadResponse:
    """
    Upload multiple files at once.

    Useful for:
    - Multiple screenshots from a demo
    - Video + supporting images
    - Multiple markdown drafts

    Max 10 files per request.
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per batch upload",
        )

    uploaded_files = []
    errors = []

    for file in files:
        try:
            # Upload each file
            result = await upload_single_file(file)
            uploaded_files.append(result.file)
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            errors.append(f"{file.filename}: {str(e)}")

    if not uploaded_files and errors:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"All uploads failed: {', '.join(errors)}",
        )

    message = f"Uploaded {len(uploaded_files)} file(s) successfully"
    if errors:
        message += f" ({len(errors)} failed: {', '.join(errors)})"

    return UploadResponse(
        success=True,
        message=message,
        file=uploaded_files[0] if len(uploaded_files) == 1 else None,
        files=uploaded_files if len(uploaded_files) > 1 else None,
    )


def _determine_file_type(content_type: str, filename: str = "") -> Optional[str]:
    """Determine file type category from content type or filename extension."""
    # Try content type first
    if content_type in SUPPORTED_VIDEO_TYPES:
        return "video"
    elif content_type in SUPPORTED_IMAGE_TYPES:
        return "image"
    elif content_type in SUPPORTED_DOCUMENT_TYPES:
        # For octet-stream, try to determine from filename
        if content_type == "application/octet-stream" and filename:
            ext = Path(filename).suffix.lower()
            if ext in {".txt", ".md", ".markdown"}:
                return "document"
            elif ext in {".pdf"}:
                return "document"
            elif ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                return "image"
            elif ext in {".mp4", ".mov", ".avi", ".webm"}:
                return "video"
        else:
            return "document"
    
    # Fallback: try filename extension
    if filename:
        ext = Path(filename).suffix.lower()
        if ext in {".txt", ".md", ".markdown", ".pdf"}:
            return "document"
        elif ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            return "image"
        elif ext in {".mp4", ".mov", ".avi", ".webm"}:
            return "video"
    
    return None


def _validate_file_size(file_size: int, file_type: str) -> None:
    """Validate file size based on type."""
    if file_type == "video" and file_size > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Video file too large. Max size: {MAX_VIDEO_SIZE / (1024**3):.1f}GB",
        )
    elif file_type == "image" and file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image file too large. Max size: {MAX_IMAGE_SIZE / (1024**2):.1f}MB",
        )
    elif file_type == "document" and file_size > MAX_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document file too large. Max size: {MAX_DOCUMENT_SIZE / (1024**2):.1f}MB",
        )
