"""
IAP Header Logger
Logs user information from IAP headers without enforcing authentication.
"""

import base64
import json
import logging
from typing import Dict, Optional

from fastapi import Request

logger = logging.getLogger(__name__)


def parse_iap_jwt(token: str) -> Optional[Dict]:
    """
    Parse IAP JWT token (base64 decode only, no verification).
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded JWT payload or None if parsing fails
    """
    try:
        # JWT format: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            return None

        # Decode the payload (base64url)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        logger.debug(f"Failed to parse IAP token: {e}")
        return None


def log_iap_headers(request: Request) -> Optional[Dict[str, str]]:
    """
    Extract and log IAP headers from request.
    
    Does NOT enforce authentication - only logs information for debugging.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with user info if IAP headers found, None otherwise
    """
    user_info = None
    
    # Check for IAP JWT assertion (primary)
    iap_jwt = request.headers.get("x-goog-iap-jwt-assertion")
    if iap_jwt:
        payload = parse_iap_jwt(iap_jwt)
        if payload:
            user_info = {
                "email": payload.get("email", "unknown@iap"),
                "user_id": payload.get("sub", "unknown_iap_user"),
                "name": payload.get("name"),
                "auth_method": "iap_jwt",
            }
            logger.info(f"🔐 IAP JWT found: user={user_info['email']}, id={user_info['user_id']}")
    
    # Check for authenticated user email header (alternative)
    if not user_info:
        user_email_header = request.headers.get("x-goog-authenticated-user-email")
        if user_email_header:
            # Format: accounts.google.com:user@example.com
            email = user_email_header.split(":")[-1] if ":" in user_email_header else user_email_header
            user_info = {
                "email": email,
                "user_id": email.split("@")[0],
                "auth_method": "iap_email_header",
            }
            logger.info(f"🔐 IAP Email Header found: user={user_info['email']}, id={user_info['user_id']}")
    
    # Check for X-Serverless-Authorization (Cloud Run IAP)
    serverless_auth = request.headers.get("x-serverless-authorization")
    if serverless_auth:
        logger.info("🔐 X-Serverless-Authorization header present")
        if not user_info:
            # Try to parse this as well
            payload = parse_iap_jwt(serverless_auth)
            if payload:
                user_info = {
                    "email": payload.get("email", "unknown@serverless"),
                    "user_id": payload.get("sub", "unknown_serverless_user"),
                    "name": payload.get("name"),
                    "auth_method": "serverless_auth",
                }
                logger.info(f"🔐 Serverless Auth parsed: user={user_info['email']}, id={user_info['user_id']}")
    
    # Log all relevant headers for debugging
    auth_headers = {}
    for header_name, header_value in request.headers.items():
        if any(keyword in header_name.lower() for keyword in ["goog", "auth", "user", "iap"]):
            # Don't log full JWT tokens (too long), just indicate presence
            if len(header_value) > 50:
                auth_headers[header_name] = f"<token:{len(header_value)}chars>"
            else:
                auth_headers[header_name] = header_value
    
    if auth_headers:
        logger.info(f"📊 Auth-related headers: {auth_headers}")
    else:
        logger.info("📊 No IAP/auth headers found in request")
    
    return user_info

