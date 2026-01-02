"""Authentication service with simplified IAP support."""

import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException, Request, status

logger = logging.getLogger(__name__)


class User:
    """Authenticated user information."""

    def __init__(
        self,
        email: str,
        user_id: str,
        name: Optional[str] = None,
        auth_method: str = "unknown",
    ):
        self.email = email
        self.user_id = user_id
        self.name = name or email.split("@")[0]
        self.auth_method = auth_method

    def __str__(self):
        return f"User(email={self.email}, id={self.user_id}, method={self.auth_method})"


class AuthService:
    """Service for authenticating users via IAP (simplified - no audience check)."""

    def __init__(self):
        """Initialize the authentication service."""
        logger.info("🔐 Auth Service initialized: IAP (simplified, no audience check)")

    async def decode_iap_jwt(self, jwt_token: str) -> Optional[dict]:
        """
        Decode IAP JWT token without audience verification.

        Args:
            jwt_token: JWT token from X-Serverless-Authorization or X-Goog-IAP-JWT-Assertion header

        Returns:
            dict: Decoded token claims if valid, None otherwise
        """
        try:
            # Decode JWT without verification (just parse the payload)
            import base64
            import json

            # JWT format: header.payload.signature
            parts = jwt_token.split(".")
            if len(parts) != 3:
                logger.warning(f"⚠️ Invalid JWT format (expected 3 parts, got {len(parts)})")
                return None

            # Decode payload (add padding if needed)
            payload = parts[1]
            # Add padding for base64 decoding
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding

            decoded_bytes = base64.urlsafe_b64decode(payload)
            decoded_token = json.loads(decoded_bytes)

            # Basic validation: check for required fields
            if not decoded_token.get("email") or not decoded_token.get("sub"):
                logger.warning("⚠️ IAP JWT missing required fields (email or sub)")
                return None

            logger.info(f"✅ IAP JWT decoded successfully: {decoded_token.get('email')}")
            return decoded_token

        except Exception as e:
            logger.warning(f"⚠️ IAP JWT decode failed: {e}")
            return None

    async def authenticate_user(self, request: Request) -> User:
        """
        Authenticate user from request headers.

        Tries authentication methods in order:
        1. IAP (X-Serverless-Authorization or X-Goog-IAP-JWT-Assertion header)
        2. Local development mode (if enabled)

        Args:
            request: FastAPI request object

        Returns:
            User: Authenticated user

        Raises:
            HTTPException: If authentication fails
        """
        # Try IAP authentication (Cloud Run with IAP)
        # Check both common IAP headers
        iap_jwt = request.headers.get("X-Serverless-Authorization") or request.headers.get(
            "X-Goog-IAP-JWT-Assertion"
        )
        if iap_jwt:
            logger.debug("🔍 Attempting IAP authentication (simplified - no aud check)")
            decoded = await self.decode_iap_jwt(iap_jwt)
            if decoded:
                return User(
                    email=decoded.get("email"),
                    user_id=decoded.get("sub"),
                    name=decoded.get("name"),
                    auth_method="iap",
                )

        # Local development mode (no authentication required)
        env = os.environ.get("DD_ENV", "development")
        if env in ["development", "dev"]:
            logger.warning("⚠️ Using development mode authentication (no verification)")
            return User(
                email="dev@localhost",
                user_id="dev_user",
                name="Development User",
                auth_method="development",
            )

        # Authentication failed
        logger.error("❌ Authentication failed: No IAP JWT found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide X-Serverless-Authorization or X-Goog-IAP-JWT-Assertion header.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Global auth service instance
auth_service = AuthService()


async def get_current_user(request: Request) -> User:
    """
    FastAPI dependency for getting the current authenticated user.

    Usage:
        @app.get("/protected")
        async def protected_endpoint(user: User = Depends(get_current_user)):
            return {"email": user.email}
    """
    return await auth_service.authenticate_user(request)


async def get_optional_user(request: Request) -> Optional[User]:
    """
    FastAPI dependency for getting the current user (optional).

    Returns None if not authenticated, instead of raising an exception.

    Usage:
        @app.get("/public")
        async def public_endpoint(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return {"authenticated": True, "email": user.email}
            return {"authenticated": False}
    """
    try:
        return await auth_service.authenticate_user(request)
    except HTTPException:
        return None

