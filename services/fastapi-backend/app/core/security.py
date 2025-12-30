"""Security utilities."""

import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

logger = logging.getLogger(__name__)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """
    Verify API key if configured.

    Behavior:
    - If API_KEY_REQUIRED=false and API_KEY is empty: Allow all requests
    - If API_KEY_REQUIRED=true or API_KEY is set: Require valid API key

    Args:
        api_key: API key from X-API-Key header

    Returns:
        The validated API key or "no-key-required"

    Raises:
        HTTPException: If API key is invalid or missing when required
    """
    # If API key validation is not required and no key is configured, allow all requests
    if not settings.api_key_required and not settings.api_key:
        return "no-key-required"

    # If API key is configured or required, verify it
    if settings.api_key_required or settings.api_key:
        if not api_key:
            logger.warning("Request rejected: Missing API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key. Include X-API-Key header in your request.",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        if api_key != settings.api_key:
            logger.warning(f"Request rejected: Invalid API key (prefix: {api_key[:8]}...)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        logger.debug("API key validated successfully")
        return api_key

    return "no-key-required"


async def optional_api_key(api_key: str | None = Security(api_key_header)) -> str | None:
    """
    Optional API key verification for endpoints that support both authenticated and unauthenticated access.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        The validated API key if provided and valid, None otherwise
    """
    if not api_key or not settings.api_key:
        return None

    if api_key == settings.api_key:
        return api_key

    return None
