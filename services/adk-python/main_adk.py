"""
Main ADK FastAPI application using get_fast_api_app().

Full ADK implementation - use this instead of app/main.py for pure ADK deployment.
"""

import asyncio
import logging
import os
from pathlib import Path

from ddtrace.llmobs import LLMObs
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Datadog LLM Observability
DD_API_KEY = os.getenv("DD_API_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")
DD_ENV = os.getenv("DD_ENV", "development")
DD_SERVICE = os.getenv("DD_SERVICE", "adk-python")
DD_VERSION = os.getenv("DD_VERSION", "1.0.0")

if DD_API_KEY:
    try:
        LLMObs.enable(
            ml_app="adk-python-content-creator",
            api_key=DD_API_KEY,
            site=DD_SITE,
            agentless_enabled=True,
            env=DD_ENV,
            service=DD_SERVICE,
        )
        logger.info("Datadog LLM Observability enabled: ml_app=adk-python-content-creator")
    except Exception as e:
        logger.warning(f"Failed to enable Datadog LLM Observability: {e}")

# ADK Configuration
# Point to parent directory (this file's directory) which contains 'agents' subdirectory
BASE_DIR = Path(__file__).parent
AGENTS_DIR = str(BASE_DIR)  # Parent directory containing agents/
# For session storage, use SQLite URI format
SESSION_SERVICE_URI = os.getenv("SESSION_SERVICE_URI", f"sqlite:///{BASE_DIR}/sessions.db")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501").split(
    ",",
)
SERVE_WEB_INTERFACE = os.getenv("SERVE_WEB_INTERFACE", "true").lower() == "true"

logger.info(f"ADK Agents directory: {AGENTS_DIR}")
logger.info(f"ADK Session service URI: {SESSION_SERVICE_URI}")
logger.info(f"ADK Web interface: {SERVE_WEB_INTERFACE}")

# Create FastAPI app using ADK's get_fast_api_app
# Per https://dev.to/timtech4u/building-ai-agents-with-google-adk-fastapi-and-mcp-26h7
# and https://github.com/google/adk-python/issues/1025
# agents_dir should point to parent directory containing agent subdirectories
app: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

logger.info("ADK Python Service started with get_fast_api_app()")

# Mount static files for serving generated images
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
logger.info(f"Mounted /uploads directory at {UPLOADS_DIR}")

# Verify agent loading
try:
    from content_creator_agent.agent import root_agent

    logger.info(
        f"✅ Content Creator Agent loaded: {root_agent.name} with {len(root_agent.tools)} tools"
    )
except Exception as e:
    logger.error(f"❌ Failed to load Content Creator Agent: {e}")

try:
    from image_creator.agent import root_agent as image_creator_root_agent

    logger.info(
        f"✅ Image Creator Agent loaded: {image_creator_root_agent.name} with {len(image_creator_root_agent.tools)} tools"
    )
except Exception as e:
    logger.error(f"❌ Failed to load Image Creator Agent: {e}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Used by Cloud Run, GKE, and load balancers to verify service health.
    """
    return {
        "status": "healthy",
        "service": DD_SERVICE,
        "version": DD_VERSION,
        "adk": "enabled",
    }


# Custom non-streaming endpoint for image generation
@app.post("/api/v1/images/generate")
async def generate_image_sync(
    request: dict,
    http_request: Request,
):
    """
    Non-streaming endpoint for image generation using Google Gemini directly.
    
    Authentication:
    - IAP: X-Serverless-Authorization header (Cloud Run with IAP)
    - OAuth: Authorization: Bearer <token> (Google OAuth)
    - Dev: No auth required in development mode
    
    Request:
    {
        "prompt": "datadog and kiro bff",
        "image_type": "comic",
        "aspect_ratio": "1:1",
        "reference_images": [
            {"data": "base64_string", "mime_type": "image/png"}
        ],
        "session_id": "rum_abc123"  // From Datadog RUM
    }
    
    Response:
    {
        "status": "success",
        "image_url": "/uploads/20260102_130000_abcd1234.png",
        "mime_type": "image/png",
        "text_response": "Generated comic image...",
        "session_id": "rum_abc123",
        "user_email": "user@example.com",
        "file_size_bytes": 1234567
    }
    """
    try:
        # Authenticate user (optional - logs warning in dev mode)
        from app.services import ImageGenerationService, get_optional_user
        user = await get_optional_user(http_request)
        
        # Lazy initialization of Image Generation Service
        image_gen_service = ImageGenerationService()
        
        # Extract parameters
        prompt = request.get("prompt", "Generate an image")
        image_type = request.get("image_type", "illustration")
        aspect_ratio = request.get("aspect_ratio", "1:1")
        reference_images = request.get("reference_images", [])
        session_id = request.get("session_id", f"img_{int(__import__('time').time() * 1000)}")
        
        # Log user info
        user_info = f"user={user.email} ({user.auth_method})" if user else "anonymous"
        logger.info(
            f"🎨 Image generation request: {user_info}, type={image_type}, "
            f"ratio={aspect_ratio}, refs={len(reference_images)}, session={session_id}"
        )
        
        # Generate image using service
        result = await image_gen_service.generate_image(
            prompt=prompt,
            image_type=image_type,
            aspect_ratio=aspect_ratio,
            reference_images_base64=reference_images,
        )
        
        # Add session_id and user info to response
        result["session_id"] = session_id
        if user:
            result["user_email"] = user.email
            result["user_id"] = user.user_id
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Image generation endpoint error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "session_id": request.get("session_id", "unknown"),
        }


# Register shutdown handler for LLMObs flush
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down ADK Python Service")

    if DD_API_KEY:
        try:
            LLMObs.flush()
            logger.info("Flushed Datadog LLM Observability data")
        except Exception as e:
            logger.warning(f"Failed to flush LLM Observability data: {e}")


if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"0.0.0.0:{os.getenv('PORT', '8002')}"]
    config.worker_class = "asyncio"

    asyncio.run(serve(app, config))
