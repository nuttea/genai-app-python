"""Vote extraction endpoints."""

import json
import logging
import re
import time
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.constants import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    MAX_FILENAME_LENGTH,
    MAX_TOTAL_SIZE_BYTES,
    MAX_TOTAL_SIZE_MB,
    RATE_LIMIT_VOTE_EXTRACTION,
    RATE_LIMIT_VOTE_EXTRACTION_HOURLY,
)
from app.core.rate_limiting import limiter
from app.core.security import verify_api_key
from app.models.vote_extraction import ElectionFormData, LLMConfig, VoteExtractionResponse
from app.services.vote_extraction_service import vote_extraction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vote-extraction", tags=["vote-extraction"])

# Cache for dynamically fetched models
_models_cache: Optional[list[dict]] = None
_cache_timestamp: Optional[float] = None
CACHE_TTL = 3600  # 1 hour cache


async def _validate_and_read_files(
    files: list[UploadFile],
) -> tuple[list[bytes], list[str]]:
    """
    Validate and read uploaded files.
    
    Returns:
        Tuple of (image_files, image_filenames)
        
    Raises:
        HTTPException for validation errors
    """
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
        if re.search(r'[/\\:*?"<>|]', file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid filename: {file.filename}. Filename cannot contain: / \\ : * ? " < > |',
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

            # Check total size
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
            raise
        except Exception as e:
            logger.error(f"Error reading file {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading file: {file.filename}",
            )

    return image_files, image_filenames


async def _parse_llm_config(llm_config_json: str | None) -> LLMConfig | None:
    """Parse LLM configuration from JSON string."""
    if not llm_config_json:
        return None

    try:
        llm_config_dict = json.loads(llm_config_json)
        llm_config = LLMConfig(**llm_config_dict)
        logger.info(
            f"Using custom LLM config: provider={llm_config.provider}, model={llm_config.model}"
        )
        return llm_config
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Invalid LLM config JSON, using defaults: {e}")
        return None


async def _parse_extraction_results(
    result: dict | list,
    image_files_count: int,
) -> tuple[list[ElectionFormData], list[str]]:
    """
    Parse and validate extraction results.
    
    Returns:
        Tuple of (extracted_reports, validation_warnings)
        
    Raises:
        HTTPException if no valid reports could be extracted
    """
    extracted_reports = []
    validation_warnings = []

    # Handle both single dict and list of dicts
    if isinstance(result, dict):
        results_to_process = [result]
    elif isinstance(result, list):
        results_to_process = result
    else:
        logger.error(f"Unexpected result type: {type(result)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unexpected result type: {type(result).__name__}",
        )

    # Process each report
    for idx, report_data in enumerate(results_to_process):
        if not isinstance(report_data, dict):
            logger.warning(f"Skipping non-dict element at index {idx}: {type(report_data)}")
            continue

        try:
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

    # Check if any reports were successfully extracted
    if not extracted_reports:
        error_detail = "No valid reports could be extracted from the data"
        if validation_warnings:
            error_detail += ":\n" + "\n".join(validation_warnings)

        logger.error(
            "All reports failed to parse",
            extra={
                "pages_processed": image_files_count,
                "errors": validation_warnings,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": error_detail,
                "pages_processed": image_files_count,
                "errors": validation_warnings,
            },
        )

    return extracted_reports, validation_warnings


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
    files: list[UploadFile] = File(
        ..., description="Election form images (multiple pages supported)"
    ),
    llm_config_json: str = Form(None, description="Optional LLM configuration as JSON"),
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

    # Validate and read files
    image_files, image_filenames = await _validate_and_read_files(files)

    # Parse LLM configuration
    llm_config = await _parse_llm_config(llm_config_json)

    # Extract vote data
    try:
        result = await vote_extraction_service.extract_from_images(
            image_files=image_files,
            image_filenames=image_filenames,
            llm_config=llm_config,
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
            extracted_reports, validation_warnings = await _parse_extraction_results(
                result, len(image_files)
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
            # Re-raise HTTP exceptions (already handled)
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


async def fetch_models_from_api() -> list[dict]:
    """
    Fetch models dynamically from Google AI API REST endpoint.

    Returns:
        List of model dictionaries, or empty list if fetch fails
    """
    global _models_cache, _cache_timestamp

    # Check cache first
    if _models_cache and _cache_timestamp:
        if time.time() - _cache_timestamp < CACHE_TTL:
            logger.info("Returning models from cache")
            return _models_cache

    # Check if API key is configured
    api_key = settings.gemini_api_key
    if not api_key:
        logger.info("GEMINI_API_KEY not configured, using static fallback")
        return []

    try:
        logger.info("Fetching models from Google AI API")
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            response = await client.get(url)
            response.raise_for_status()

            models_data = response.json()

            # Transform to our format - filter for Gemini models only
            transformed = []
            for model in models_data.get("models", []):
                model_name = model.get("name", "").replace("models/", "")

                # Only include Gemini models (not embeddings or Gemma)
                if not model_name.startswith("gemini-"):
                    continue

                # Only include models that support generateContent
                supported_actions = model.get("supportedGenerationMethods", [])
                if "generateContent" not in supported_actions:
                    continue

                transformed.append(
                    {
                        "name": model_name,
                        "display_name": model.get("displayName", model_name),
                        "description": model.get("description", "")[:200],
                        "context_window": model.get("inputTokenLimit", 0),
                        "max_output_tokens": model.get("outputTokenLimit", 0),
                        "version": model_name.split("-")[1] if "-" in model_name else "unknown",
                        "temperature": 0.0,
                        "max_temperature": model.get("temperature", 2.0),
                        "top_p": model.get("topP", 0.95),
                        "top_k": model.get("topK", 40),
                    }
                )

            # Update cache
            _models_cache = transformed
            _cache_timestamp = time.time()

            logger.info(f"Successfully fetched {len(transformed)} models from API")
            return transformed

    except httpx.TimeoutException:
        logger.warning("Timeout fetching models from API, using fallback")
        return []
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching models from API: {e.response.status_code}")
        return []
    except Exception as e:
        logger.error(f"Error fetching models from API: {e}", exc_info=True)
        return []


def get_static_gemini_models() -> list[dict]:
    """
    Get curated static list of Gemini models as fallback.

    Returns:
        List of model dictionaries
    """
    return [
        {
            "name": "gemini-2.5-flash",
            "display_name": "Gemini 2.5 Flash",
            "description": "Fast and efficient model for most tasks",
            "context_window": 1048576,
            "max_output_tokens": 8192,
            "version": "2.5",
            "temperature": 0.0,
            "max_temperature": 2.0,
            "top_p": 0.95,
            "top_k": 40,
        },
        {
            "name": "gemini-2.0-flash-exp",
            "display_name": "Gemini 2.0 Flash (Experimental)",
            "description": "Experimental features and improvements",
            "context_window": 1048576,
            "max_output_tokens": 8192,
            "version": "2.0",
            "temperature": 0.0,
            "max_temperature": 2.0,
            "top_p": 0.95,
            "top_k": 40,
        },
        {
            "name": "gemini-1.5-flash-002",
            "display_name": "Gemini 1.5 Flash",
            "description": "Stable and reliable model",
            "context_window": 1048576,
            "max_output_tokens": 8192,
            "version": "1.5",
            "temperature": 0.0,
            "max_temperature": 2.0,
            "top_p": 0.95,
            "top_k": 40,
        },
        {
            "name": "gemini-1.5-pro-002",
            "display_name": "Gemini 1.5 Pro",
            "description": "Most capable model for complex tasks",
            "context_window": 2097152,
            "max_output_tokens": 8192,
            "version": "1.5",
            "temperature": 0.0,
            "max_temperature": 2.0,
            "top_p": 0.95,
            "top_k": 40,
        },
    ]


@router.get("/models", summary="List available LLM models")
async def list_models() -> JSONResponse:
    """
    List available LLM providers and their models.

    Dynamically fetches models from Google AI API if GEMINI_API_KEY is configured,
    otherwise falls back to curated static list.

    Benefits of dynamic fetching:
    - Always up-to-date with latest models
    - Auto-discovers new models

    Cache: Models are cached for 1 hour to reduce API calls
    Fallback: If API fetch fails, uses static list automatically

    Reference: https://ai.google.dev/api/models
    """
    # Try dynamic fetch first
    gemini_models = await fetch_models_from_api()

    # Fallback to static list if dynamic fetch returns empty
    if not gemini_models:
        logger.info("Using static fallback models list")
        gemini_models = get_static_gemini_models()

    models_config = {
        "providers": [
            {
                "name": "vertex_ai",
                "display_name": "Google Vertex AI / Gemini API",
                "models": gemini_models,
                "default_model": "gemini-2.5-flash",
                "supported": True,
                "dynamic_listing": bool(settings.gemini_api_key),
            },
            {
                "name": "openai",
                "display_name": "OpenAI",
                "models": [
                    {
                        "name": "gpt-4o",
                        "display_name": "GPT-4o",
                        "context_window": 128000,
                        "max_output_tokens": 16384,
                    },
                    {
                        "name": "gpt-4o-mini",
                        "display_name": "GPT-4o Mini",
                        "context_window": 128000,
                        "max_output_tokens": 16384,
                    },
                ],
                "default_model": "gpt-4o-mini",
                "supported": False,
                "note": "Coming soon",
            },
            {
                "name": "anthropic",
                "display_name": "Anthropic",
                "models": [
                    {
                        "name": "claude-3-5-sonnet-20241022",
                        "display_name": "Claude 3.5 Sonnet",
                        "context_window": 200000,
                        "max_output_tokens": 8192,
                    },
                    {
                        "name": "claude-3-5-haiku-20241022",
                        "display_name": "Claude 3.5 Haiku",
                        "context_window": 200000,
                        "max_output_tokens": 8192,
                    },
                ],
                "default_model": "claude-3-5-sonnet-20241022",
                "supported": False,
                "note": "Coming soon",
            },
        ],
        "default_config": {
            "provider": "vertex_ai",
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "max_tokens": 16384,
            "top_p": 0.95,
            "top_k": 40,
        },
    }

    return JSONResponse(content=models_config)


@router.get(
    "/health",
    summary="Health check for vote extraction service",
)
async def vote_extraction_health() -> JSONResponse:
    """Check if vote extraction service is available."""
    try:
        # Try to get the client to verify Google GenAI is accessible
        _ = vote_extraction_service._get_client()  # noqa: F841
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
