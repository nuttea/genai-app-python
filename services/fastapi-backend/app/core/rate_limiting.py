"""Rate limiting utilities."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def get_api_key_or_ip(request: Request) -> str:
    """
    Get rate limit key based on API key or IP address.
    
    This allows different rate limits for authenticated vs anonymous users.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rate limit key (either "apikey:..." or "ip:...")
    """
    # Try to get API key from header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        # Use first 16 chars of API key as identifier
        return f"apikey:{api_key[:16]}"
    
    # Fall back to IP address
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


# Create limiter with custom key function
limiter = Limiter(
    key_func=get_api_key_or_ip,
    default_limits=["1000/hour"],  # Global default
    storage_uri="memory://",  # In-memory storage (use Redis for production)
)


# Alternative: Simple IP-based limiter
ip_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"],
    storage_uri="memory://",
)

