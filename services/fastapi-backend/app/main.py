"""FastAPI application entry point."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.config import settings
from app.core.logging import setup_logging
from app.core.rate_limiting import limiter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Setup logging
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Environment: {settings.fastapi_env}")
    logger.info(f"GCP Project: {settings.google_cloud_project}")
    logger.info(f"Vertex AI Location: {settings.vertex_ai_location}")

    # Log Datadog status
    dd_service = os.getenv("DD_SERVICE")
    dd_env = os.getenv("DD_ENV")
    dd_version = os.getenv("DD_VERSION")
    dd_api_key = os.getenv("DD_API_KEY")

    if dd_api_key:
        logger.info(
            f"Datadog APM enabled: service={dd_service}, env={dd_env}, version={dd_version}"
        )
    else:
        logger.info("Datadog APM not configured")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="FastAPI backend with Google Vertex AI integration",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return JSONResponse(
        content={
            "name": settings.api_title,
            "version": settings.api_version,
            "status": "running",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "datadog_apm": bool(os.getenv("DD_API_KEY")),
        }
    )


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"status": "healthy"})


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness check endpoint."""
    # TODO: Add checks for Vertex AI connection
    return JSONResponse(content={"status": "ready"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.reload and settings.is_development,
        log_level=settings.log_level.lower(),
    )
