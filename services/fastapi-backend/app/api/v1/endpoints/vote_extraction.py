"""Vote extraction endpoints."""

import logging
import re
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse

from app.models.vote_extraction import VoteExtractionResponse, ElectionFormData
from app.services.vote_extraction_service import vote_extraction_service
from app.core.security import verify_api_key
from app.core.rate_limiting import limiter
from app.core.constants import (
    MAX_FILE_SIZE_MB,
    MAX_TOTAL_SIZE_MB,
    MAX_FILE_SIZE_BYTES,
    MAX_TOTAL_SIZE_BYTES,
    RATE_LIMIT_VOTE_EXTRACTION,
    RATE_LIMIT_VOTE_EXTRACTION_HOURLY,
    MAX_FILENAME_LENGTH,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vote-extraction", tags=["vote-extraction"])


@router.post(
    "/extract",
    response_model=VoteExtractionResponse,
    summary="Extract vote data from election form images",
    description="Upload multiple images of Thai election forms (Form S.S. 5/18) to extract structured vote data. Rate limit: 10/minute.",
)
@limiter.limit(RATE_LIMIT_VOTE_EXTRACTION)
@limiter.limit(RATE_LIMIT_VOTE_EXTRACTION_HOURLY)
async def extract_votes(
    request: Request,
    files: List[UploadFile] = File(
        ..., description="Election form images (multiple pages supported)"
    ),
    api_key: str = Depends(verify_api_key),
) -> VoteExtractionResponse:
    """
    Extract vote data from uploaded election form images.

    Args:
        files: List of image files (JPG, JPEG, PNG) representing pages of the election form.
               Maximum 10MB per file, 30MB total.

    Returns:
        Extracted vote data including form info, ballot statistics, and vote results

    Raises:
        HTTPException:
            - 400: No files provided, invalid file types, or empty files
            - 413: File size exceeds limits
            - 422: Validation errors in extracted data
            - 500: Server errors during extraction
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided. Please upload at least one image.",
        )

    # Validate file types and sizes
    allowed_types = {"image/jpeg", "image/jpg", "image/png"}
    image_files = []
    image_filenames = []
    total_size = 0

    for file in files:
        # Validate filename
        if not file.filename or len(file.filename) > MAX_FILENAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filename length. Maximum {MAX_FILENAME_LENGTH} characters.",
            )

        # Validate filename characters (prevent path traversal)
        if not re.match(r"^[\w\-. ]+$", file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filename: {file.filename}. Only alphanumeric, dash, dot, underscore and space allowed.",
            )

        # Validate file extension
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension for {file.filename}. Only JPG and PNG are supported.",
            )

        # Check content type
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.filename}. Only JPG and PNG images are supported.",
            )

        # Read file content
        try:
            content = await file.read()

            # Check if file is empty
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Empty file: {file.filename}",
                )

            # Check individual file size
            file_size_mb = len(content) / (1024 * 1024)
            if len(content) > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=(
                        f"File {file.filename} is too large ({file_size_mb:.1f}MB). "
                        f"Maximum file size is {MAX_FILE_SIZE_MB}MB."
                    ),
                )

            # Track total size
            total_size += len(content)

            # Check total size (Cloud Run limit is 32MB)
            if total_size > MAX_TOTAL_SIZE_BYTES:
                total_size_mb = total_size / (1024 * 1024)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=(
                        f"Total upload size ({total_size_mb:.1f}MB) exceeds limit ({MAX_TOTAL_SIZE_MB}MB). "
                        f"Please reduce the number of files or image quality."
                    ),
                )

            image_files.append(content)
            image_filenames.append(file.filename)
            logger.info(
                f"Received file: {file.filename}",
                extra={
                    "file_size_bytes": len(content),
                    "file_size_mb": f"{file_size_mb:.2f}",
                },
            )

        except HTTPException:
            # Re-raise HTTP exceptions (validation errors)
            raise
        except Exception as e:
            logger.error(f"Error reading file {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading file: {file.filename}",
            )

    # Extract vote data
    try:
        result = await vote_extraction_service.extract_from_images(
            image_files=image_files,
            image_filenames=image_filenames,
        )

        if not result:
            return VoteExtractionResponse(
                success=False,
                data=[],
                error="Failed to extract vote data. The images may not contain valid election forms.",
                pages_processed=len(image_files),
                reports_extracted=0,
            )

        # Parse and validate extracted data
        try:
            extracted_reports = []
            validation_warnings = []

            # Handle both single dict and list of dicts
            if isinstance(result, dict):
                # Single report - wrap in list
                results_to_process = [result]
            elif isinstance(result, list):
                # Multiple reports or list response
                results_to_process = result
            else:
                logger.error(f"Unexpected result type: {type(result)}")
                return VoteExtractionResponse(
                    success=False,
                    data=[],
                    error=f"Unexpected result type: {type(result).__name__}",
                    pages_processed=len(image_files),
                    reports_extracted=0,
                )

            # Process each report
            for idx, report_data in enumerate(results_to_process):
                if not isinstance(report_data, dict):
                    logger.warning(f"Skipping non-dict element at index {idx}: {type(report_data)}")
                    continue

                try:
                    # Log raw report data for debugging
                    logger.debug(
                        f"Parsing report {idx + 1}",
                        extra={
                            "report_index": idx + 1,
                            "report_data_keys": (
                                list(report_data.keys())
                                if isinstance(report_data, dict)
                                else "not_dict"
                            ),
                            "vote_results_count": (
                                len(report_data.get("vote_results", []))
                                if isinstance(report_data, dict)
                                else 0
                            ),
                        },
                    )

                    extracted_data = ElectionFormData(**report_data)

                    # Validate consistency
                    is_valid, error_msg = await vote_extraction_service.validate_extraction(
                        extracted_data
                    )
                    if not is_valid:
                        logger.warning(f"Validation warning for report {idx + 1}: {error_msg}")
                        validation_warnings.append(f"Report {idx + 1}: {error_msg}")

                    extracted_reports.append(extracted_data)
                    logger.info(f"Successfully parsed report {idx + 1}/{len(results_to_process)}")

                except Exception as e:
                    # Log at ERROR level for parsing failures with full details
                    logger.error(
                        f"Error parsing report {idx + 1}: {e}",
                        extra={
                            "report_index": idx + 1,
                            "error_type": type(e).__name__,
                            "report_data_sample": str(report_data)[:500] if report_data else "None",
                        },
                        exc_info=True,
                    )
                    validation_warnings.append(f"Report {idx + 1}: Failed to parse - {str(e)}")

            # Return results
            if not extracted_reports:
                error_detail = "No valid reports could be extracted from the data"
                if validation_warnings:
                    error_detail += ":\n" + "\n".join(validation_warnings)

                logger.error(
                    "All reports failed to parse",
                    extra={
                        "pages_processed": len(image_files),
                        "errors": validation_warnings,
                    },
                )

                # Return 422 Unprocessable Entity for validation errors
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "message": error_detail,
                        "pages_processed": len(image_files),
                        "errors": validation_warnings,
                    },
                )

            # Build response with warnings if any
            error_msg = None
            if validation_warnings:
                error_msg = "Data extracted with warnings:\n" + "\n".join(validation_warnings)

            return VoteExtractionResponse(
                success=True,
                data=extracted_reports,
                error=error_msg,
                pages_processed=len(image_files),
                reports_extracted=len(extracted_reports),
            )

        except HTTPException:
            # Re-raise HTTP exceptions (already handled above)
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error parsing extracted data: {e}",
                extra={
                    "error_type": type(e).__name__,
                    "pages_processed": len(image_files),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error parsing extracted data: {str(e)}",
            )

    except Exception as e:
        logger.error(f"Error during vote extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during extraction: {str(e)}",
        )


@router.get(
    "/health",
    summary="Health check for vote extraction service",
)
async def vote_extraction_health() -> JSONResponse:
    """Check if vote extraction service is available."""
    try:
        # Try to get the client to verify Google GenAI is accessible
        client = vote_extraction_service._get_client()
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "vote-extraction",
                "genai_client": "connected",
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "vote-extraction",
                "error": str(e),
            },
        )
