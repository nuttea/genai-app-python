"""
Main FastAPI application for Datadog Content Creator.

Hybrid approach: Custom FastAPI with ADK-compatible structure for future migration.
"""

import logging
from contextlib import asynccontextmanager

from ddtrace import tracer
from ddtrace.llmobs import LLMObs
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.endpoints import upload, generate
from app.core.artifact_service import InMemoryArtifactService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize Datadog LLM Observability with auto-instrumentation
# All LLM integrations (google_adk, google_genai, vertexai, etc.) are enabled by default
if settings.dd_llmobs_enabled and settings.dd_api_key:
    try:
        LLMObs.enable(
            ml_app=settings.dd_llmobs_ml_app,
            api_key=settings.dd_api_key,
            site=settings.dd_site,
            agentless_enabled=settings.dd_llmobs_agentless,
            env=settings.dd_env,
            service=settings.dd_service,
            # integrations_enabled=True by default (auto-instrumentation)
        )
        logger.info(
            f"Datadog LLM Observability enabled with auto-instrumentation: "
            f"ml_app={settings.dd_llmobs_ml_app}, site={settings.dd_site}, "
            f"agentless={settings.dd_llmobs_agentless}"
        )
    except Exception as e:
        logger.warning(f"Failed to enable Datadog LLM Observability: {e}")
else:
    logger.info(
        f"Datadog LLM Observability disabled: enabled={settings.dd_llmobs_enabled}, "
        f"api_key_present={bool(settings.dd_api_key)}"
    )

# Initialize ADK Artifact Service (InMemory for development)
artifact_service = InMemoryArtifactService()
logger.info("Initialized InMemoryArtifactService for ADK Artifacts")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting {settings.service_name} v{settings.dd_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Google Cloud Project: {settings.google_cloud_project}")
    logger.info(f"Artifact Service: {type(artifact_service).__name__}")
    logger.info("Note: ADK agents available in /agents directory for future `adk run`/`adk web` usage")

    yield

    # Cleanup
    logger.info(f"Shutting down {settings.service_name}")
    
    # Flush LLMObs data before shutdown (important for serverless)
    if settings.dd_llmobs_enabled and settings.dd_api_key:
        try:
            LLMObs.flush()
            logger.info("Flushed Datadog LLM Observability data")
        except Exception as e:
            logger.warning(f"Failed to flush LLM Observability data: {e}")


# Create FastAPI application
# Note: ADK agents are defined in /agents directory and can be run with:
#   - adk run agents/content_creator.py (CLI)
#   - adk web --port 8000 (Web UI)
# This FastAPI app provides custom endpoints for specialized functionality
app = FastAPI(
    title="Datadog Content Creator",
    description="ADK-compatible service for creating blog posts and video scripts about Datadog products. "
                "Custom REST API with ADK agent support.",
    version=settings.dd_version,
    lifespan=lifespan,
)

# Store artifact service in app state for access in endpoints
app.state.artifact_service = artifact_service

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include custom API routers
app.include_router(upload.router, prefix="/api/v1")
app.include_router(generate.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.service_name,
        "version": settings.dd_version,
        "status": "running",
        "environment": settings.environment,
        "adk_compatible": True,
        "docs": "/docs",
        "info": "/info",
    }


@app.get("/info")
@tracer.wrap(service=settings.dd_service, resource="info")
async def info():
    """
    Service information endpoint.
    
    Shows capabilities and how to use ADK agents.
    """
    return {
        "service": settings.service_name,
        "version": settings.dd_version,
        "environment": settings.environment,
        "llm_model": settings.default_model,
        "adk_support": {
            "agents_directory": "/agents",
            "available_agents": ["content_creator (root_agent)"],
            "cli_usage": "adk run agents/content_creator.py",
            "web_ui_usage": "adk web --port 8000 (from project root)",
            "note": "ADK provides /run, /run_sse, /list-apps endpoints when using adk web/run",
        },
        "custom_api_endpoints": {
            "upload_single": "POST /api/v1/upload/single - Upload file with smart handling",
            "upload_batch": "POST /api/v1/upload/batch - Upload multiple files",
            "generate_blog": "POST /api/v1/generate/blog-post - Generate blog post",
            "generate_video": "POST /api/v1/generate/video-script - Generate video script",
            "generate_social": "POST /api/v1/generate/social-media - Generate social media posts",
        },
        "capabilities": [
            "blog_post_generation",
            "video_script_generation",
            "social_media_posts",
            "video_processing (native Gemini multimodal)",
            "image_analysis (native Gemini multimodal)",
            "file_upload_with_artifacts",
            "smart_file_handling (text extraction + artifact storage)",
        ],
        "supported_inputs": [
            "text",
            "markdown",
            "video (mp4, mov, avi, webm)",
            "images (png, jpg, jpeg, gif, webp)",
            "documents (txt, md, pdf)",
        ],
        "supported_outputs": [
            "blog_post (markdown, html)",
            "video_script (60s shorts)",
            "social_media (linkedin, twitter, instagram)",
        ],
        "artifact_storage": "InMemoryArtifactService (development)",
        "deployment": {
            "current": "Custom FastAPI with Hypercorn (HTTP/2 h2c)",
            "future": "Can use `adk deploy` for Cloud Run/GKE deployment",
        },
    }


@app.get("/health")
@tracer.wrap(service=settings.dd_service, resource="health_check")
async def health_check():
    """
    Health check endpoint.
    
    Used by Cloud Run, GKE, and load balancers to verify service health.
    """
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.dd_version,
        "adk": "enabled",
    }


# Note: ADK's get_fast_api_app() already provides a root "/" endpoint
# that lists available agents. Our custom /info endpoint provides more details.

if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"0.0.0.0:{settings.port}"]
    config.worker_class = "asyncio"

    if settings.debug:
        config.use_reloader = True

    logger.info(f"Starting Hypercorn with asyncio worker on port {settings.port}")
    asyncio.run(serve(app, config))
