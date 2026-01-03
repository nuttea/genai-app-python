"""Feedback models for user feedback on LLM responses."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """User feedback submission request."""

    span_id: str = Field(..., description="Span ID from LLMObs trace")
    trace_id: str = Field(..., description="Trace ID from LLMObs trace")
    ml_app: str = Field(..., description="ML application name")
    feature: str = Field(
        ...,
        description="Feature name (vote-extraction, content-creator, image-creator, etc.)",
    )

    # Feedback content
    feedback_type: Literal["rating", "thumbs", "comment"] = Field(
        ..., description="Type of feedback"
    )
    rating: Optional[int] = Field(None, ge=1, le=5, description="Star rating (1-5)")
    thumbs: Optional[Literal["up", "down"]] = Field(None, description="Thumbs up/down")
    comment: Optional[str] = Field(None, max_length=1000, description="User comment or reasoning")

    # User context
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "span_id": "abc123",
                "trace_id": "xyz789",
                "ml_app": "vote-extraction-app",
                "feature": "vote-extraction",
                "feedback_type": "rating",
                "rating": 5,
                "comment": "Excellent extraction accuracy!",
                "user_id": "user_123",
                "session_id": "rum_session_abc",
            }
        }


class FeedbackResponse(BaseModel):
    """Feedback submission response."""

    success: bool = Field(..., description="Whether feedback was submitted successfully")
    evaluation_id: Optional[str] = Field(
        None, description="Evaluation ID from Datadog (if available)"
    )
    message: str = Field(..., description="Response message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "success": True,
                "evaluation_id": "eval_123",
                "message": "Feedback submitted successfully",
            }
        }
