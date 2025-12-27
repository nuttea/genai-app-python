"""Health check endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "fastapi-backend",
        }
    )


@router.get("/ready")
async def readiness_check() -> JSONResponse:
    """Readiness check endpoint."""
    # TODO: Add checks for Vertex AI connectivity
    return JSONResponse(
        content={
            "status": "ready",
            "service": "fastapi-backend",
        }
    )
