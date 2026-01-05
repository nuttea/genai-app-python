"""API v1 router."""

from app.api.v1.endpoints import (
    chat,
    experiments,
    feedback,
    generate,
    health,
    vote_extraction,
)
from fastapi import APIRouter

# Create API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(generate.router)
api_router.include_router(vote_extraction.router)
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
