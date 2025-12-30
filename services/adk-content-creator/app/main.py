"""Main FastAPI application for Datadog Content Creator."""

import logging
from contextlib import asynccontextmanager

from ddtrace import tracer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.endpoints import upload, generate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting {settings.service_name} v{settings.dd_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Google Cloud Project: {settings.google_cloud_project}")

    # Initialize services
    # TODO: Initialize Cloud Storage client
    # TODO: Initialize Vertex AI client

    yield

    # Cleanup
    logger.info(f"Shutting down {settings.service_name}")


# Create FastAPI application
app = FastAPI(
    title="Datadog Content Creator",
    description="ADK Agent for creating blog posts and video scripts about Datadog products",
    version=settings.dd_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
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
    }


@app.get("/health")
@tracer.wrap(service=settings.dd_service, resource="health_check")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.dd_version,
    }


@app.get("/info")
async def info():
    """Service information endpoint."""
    return {
        "service": settings.service_name,
        "version": settings.dd_version,
        "environment": settings.environment,
        "llm_model": settings.default_model,
        "capabilities": [
            "blog_post_generation",
            "video_script_generation",
            "social_media_posts",
            "video_processing",
            "image_analysis",
        ],
        "supported_inputs": [
            "text",
            "markdown",
            "video (mp4, mov, avi)",
            "images (png, jpg, jpeg)",
        ],
        "supported_outputs": [
            "blog_post (markdown, html)",
            "video_script (60s)",
            "social_media (linkedin, twitter, instagram)",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
    )
