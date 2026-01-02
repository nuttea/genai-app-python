"""Authentication service with IAP and Google OAuth support."""

import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)

# Environment configuration
IAP_AUDIENCE = os.environ.get("IAP_AUDIENCE")  # For IAP JWT verification
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")  # For Google OAuth


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
    """Service for authenticating users via IAP or Google OAuth."""

    def __init__(self):
        """Initialize the authentication service."""
        self.iap_enabled = bool(IAP_AUDIENCE)
        self.google_oauth_enabled = bool(GOOGLE_CLIENT_ID)
        logger.info(
            f"🔐 Auth Service initialized: IAP={self.iap_enabled}, OAuth={self.google_oauth_enabled}"
        )

    async def verify_iap_jwt(self, jwt_token: str) -> Optional[dict]:
        """
        Verify IAP JWT token.

        Args:
            jwt_token: JWT token from X-Serverless-Authorization header

        Returns:
            dict: Decoded token claims if valid, None otherwise
        """
        if not self.iap_enabled:
            return None

        try:
            # Verify the token
            decoded_token = id_token.verify_oauth2_token(
                jwt_token,
                google_requests.Request(),
                audience=IAP_AUDIENCE,
            )

            # Validate issuer
            if decoded_token.get("iss") not in [
                "https://cloud.google.com/iap",
                "https://accounts.google.com",
            ]:
                logger.warning(f"⚠️ Invalid IAP token issuer: {decoded_token.get('iss')}")
                return None

            logger.info(f"✅ IAP authentication successful: {decoded_token.get('email')}")
            return decoded_token

        except Exception as e:
            logger.warning(f"⚠️ IAP JWT verification failed: {e}")
            return None

    async def verify_google_oauth(self, id_token_str: str) -> Optional[dict]:
        """
        Verify Google OAuth ID token.

        Args:
            id_token_str: Google OAuth ID token from Authorization header

        Returns:
            dict: Decoded token claims if valid, None otherwise
        """
        if not self.google_oauth_enabled:
            return None

        try:
            # Verify the token
            decoded_token = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=GOOGLE_CLIENT_ID,
            )

            # Validate issuer
            if decoded_token.get("iss") not in [
                "https://accounts.google.com",
                "accounts.google.com",
            ]:
                logger.warning(
                    f"⚠️ Invalid Google OAuth issuer: {decoded_token.get('iss')}"
                )
                return None

            logger.info(
                f"✅ Google OAuth authentication successful: {decoded_token.get('email')}"
            )
            return decoded_token

        except Exception as e:
            logger.warning(f"⚠️ Google OAuth verification failed: {e}")
            return None

    async def authenticate_user(self, request: Request) -> User:
        """
        Authenticate user from request headers.

        Tries authentication methods in order:
        1. IAP (X-Serverless-Authorization header)
        2. Google OAuth (Authorization: Bearer header)
        3. Local development mode (if enabled)

        Args:
            request: FastAPI request object

        Returns:
            User: Authenticated user

        Raises:
            HTTPException: If authentication fails
        """
        # Try IAP authentication first (Cloud Run with IAP)
        iap_jwt = request.headers.get("X-Serverless-Authorization")
        if iap_jwt:
            logger.debug("🔍 Attempting IAP authentication")
            decoded = await self.verify_iap_jwt(iap_jwt)
            if decoded:
                return User(
                    email=decoded.get("email"),
                    user_id=decoded.get("sub"),
                    name=decoded.get("name"),
                    auth_method="iap",
                )

        # Try Google OAuth (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            logger.debug("🔍 Attempting Google OAuth authentication")
            token = auth_header.replace("Bearer ", "")
            decoded = await self.verify_google_oauth(token)
            if decoded:
                return User(
                    email=decoded.get("email"),
                    user_id=decoded.get("sub"),
                    name=decoded.get("name"),
                    auth_method="google_oauth",
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
        logger.error("❌ Authentication failed: No valid credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide X-Serverless-Authorization (IAP) or Authorization: Bearer (Google OAuth) header.",
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

