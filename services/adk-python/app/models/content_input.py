"""
Content Generation Request Models
"""

from pydantic import BaseModel, Field


class ContentGenerationRequest(BaseModel):
    """Request for generating content (blog post, video script, social media)."""

    title: str | None = Field(None, description="Title or topic of the content")
    description: str = Field(..., description="Description or draft content")
    media_files: list[str] | None = Field(
        None,
        description="GCS URIs of uploaded media files (videos, images)",
    )
    style: str | None = Field(
        None,
        description="Writing style (professional, casual, technical, etc.)",
    )
    target_audience: str | None = Field(
        None,
        description="Target audience (e.g., DevOps engineers, developers)",
    )
    datadog_product: str | None = Field(
        None,
        description="Specific Datadog product (APM, LLM Observability, RUM, etc.)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Getting Started with Datadog LLM Observability",
                "description": "A beginner's guide to setting up LLM monitoring for AI applications",
                "style": "professional",
                "target_audience": "ML Engineers and DevOps teams",
                "datadog_product": "LLM Observability",
            },
        }
