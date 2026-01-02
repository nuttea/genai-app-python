"""
Main ADK FastAPI application using get_fast_api_app().

Full ADK implementation - use this instead of app/main.py for pure ADK deployment.
"""

import asyncio
import logging
import os
from pathlib import Path

from ddtrace.llmobs import LLMObs
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Datadog LLM Observability and Source Code Integration
DD_API_KEY = os.getenv("DD_API_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")
DD_ENV = os.getenv("DD_ENV", "development")
DD_SERVICE = os.getenv("DD_SERVICE", "adk-python")
DD_VERSION = os.getenv("DD_VERSION", "1.0.0")
DD_GIT_REPOSITORY_URL = os.getenv("DD_GIT_REPOSITORY_URL")
DD_GIT_COMMIT_SHA = os.getenv("DD_GIT_COMMIT_SHA")

# Log Datadog Source Code Integration status
if DD_GIT_REPOSITORY_URL and DD_GIT_COMMIT_SHA:
    logger.info(f"📝 Datadog Source Code Integration enabled:")
    logger.info(f"   Repository: {DD_GIT_REPOSITORY_URL}")
    logger.info(f"   Commit: {DD_GIT_COMMIT_SHA[:8]}")
else:
    logger.warning("⚠️  Datadog Source Code Integration not configured (missing git metadata)")

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

# Verify Google Cloud Credentials for Vertex AI
logger.info("🔐 Verifying Google Cloud Credentials...")
try:
    credentials, project_id = default()
    
    # Get service account email if available
    service_account_email = "unknown"
    if hasattr(credentials, "service_account_email"):
        service_account_email = credentials.service_account_email
    elif hasattr(credentials, "_service_account_email"):
        service_account_email = credentials._service_account_email
    
    # Check Cloud Run environment
    is_cloud_run = os.getenv("K_SERVICE") is not None
    k_service = os.getenv("K_SERVICE", "N/A")
    k_revision = os.getenv("K_REVISION", "N/A")
    
    logger.info(f"✅ Application Default Credentials found:")
    logger.info(f"   Environment: {'Cloud Run' if is_cloud_run else 'Local/Docker'}")
    if is_cloud_run:
        logger.info(f"   Cloud Run Service: {k_service}")
        logger.info(f"   Cloud Run Revision: {k_revision}")
    logger.info(f"   Credential Type: {type(credentials).__name__}")
    logger.info(f"   Service Account: {service_account_email}")
    logger.info(f"   Project ID: {project_id or 'N/A'}")
    logger.info(f"   Valid: {credentials.valid if hasattr(credentials, 'valid') else 'N/A'}")
    
    # Log required permissions for Vertex AI
    logger.info(f"📋 Required IAM Roles for Vertex AI Image Generation:")
    logger.info(f"   - roles/aiplatform.user (Vertex AI User)")
    logger.info(f"   Required Permissions:")
    logger.info(f"   - aiplatform.endpoints.predict")
    logger.info(f"   - aiplatform.endpoints.get")
    logger.info(f"   Grant with: gcloud projects add-iam-policy-binding {project_id or 'PROJECT_ID'}")
    logger.info(f"     --member='serviceAccount:{service_account_email}'")
    logger.info(f"     --role='roles/aiplatform.user'")
    
except DefaultCredentialsError as e:
    logger.error(f"❌ No Application Default Credentials found!")
    logger.error(f"   Error: {e}")
    logger.error(f"   This will cause PERMISSION_DENIED errors when accessing Vertex AI!")
    logger.error(f"   For Cloud Run: Ensure service account has proper IAM roles")
    logger.error(f"   For local: Run 'gcloud auth application-default login'")
except Exception as e:
    logger.warning(f"⚠️  Could not verify credentials: {e}")

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
    
    Authentication: None required (open access)
    IAP Headers: Logged if present, but not enforced
    
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
        "session_id": "rum_abc123"
    }
    """
    try:
        # Log IAP headers if present (no enforcement)
        from app.utils.iap_logger import log_iap_headers
        user_info = log_iap_headers(http_request)
        
        # No authentication required - open access
        from app.services import ImageGenerationService
        
        # Lazy initialization of Image Generation Service
        image_gen_service = ImageGenerationService()
        
        # Extract parameters
        prompt = request.get("prompt", "Generate an image")
        image_type = request.get("image_type", "illustration")
        aspect_ratio = request.get("aspect_ratio", "1:1")
        reference_images = request.get("reference_images", [])
        session_id = request.get("session_id", f"img_{int(__import__('time').time() * 1000)}")
        
        # Log request with user info if available
        user_str = f"user={user_info['email']} (via {user_info['auth_method']})" if user_info else "anonymous"
        logger.info(
            f"🎨 Image generation request: {user_str}, type={image_type}, "
            f"ratio={aspect_ratio}, refs={len(reference_images)}, session={session_id}"
        )
        
        # Generate image using service
        result = await image_gen_service.generate_image(
            prompt=prompt,
            image_type=image_type,
            aspect_ratio=aspect_ratio,
            reference_images_base64=reference_images,
        )
        
        # Check if result has error status
        if result.get("status") == "error":
            error_msg = result.get("error", "Unknown error")
            logger.error(f"❌ Image generation failed: {error_msg}")
            
            # Determine HTTP status code based on error
            if "PERMISSION_DENIED" in error_msg or "403" in error_msg:
                status_code = 503  # Service Unavailable (backend permission issue)
            elif "INVALID_ARGUMENT" in error_msg or "400" in error_msg:
                status_code = 400  # Bad Request
            elif "NOT_FOUND" in error_msg or "404" in error_msg:
                status_code = 404  # Not Found
            else:
                status_code = 500  # Internal Server Error
            
            raise HTTPException(
                status_code=status_code,
                detail={
                    "error": error_msg,
                    "session_id": session_id,
                    "status": "error"
                }
            )
        
        # Add session_id to response
        result["session_id"] = session_id
        
        return result
        
    except HTTPException:
        # Re-raise HTTPException (already handled above)
        raise
    except Exception as e:
        logger.error(f"❌ Image generation endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "session_id": request.get("session_id", "unknown"),
                "status": "error"
            }
        )


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
