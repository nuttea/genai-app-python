"""Feedback endpoints for user feedback on LLM responses."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import feedback_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    """
    Submit user feedback for LLM-generated content.

    This endpoint accepts user feedback (ratings, thumbs, comments) and
    submits it as a custom evaluation to Datadog LLMObs, associating it
    with the specific span and trace.

    **Feedback Types:**
    - **rating**: Star rating (1-5) with optional comment
    - **thumbs**: Thumbs up/down with optional comment
    - **comment**: Text feedback only (marked as "to_be_reviewed")

    **How it works:**
    1. User provides feedback on an LLM response
    2. Feedback is validated and formatted
    3. Submitted to Datadog LLMObs as custom evaluation
    4. Comments use the "reasoning" tag (Datadog best practice)
    5. Feedback appears in Datadog traces and dashboards

    **Example Request:**
    ```json
    {
      "span_id": "abc123",
      "trace_id": "xyz789",
      "ml_app": "vote-extraction-app",
      "feature": "vote-extraction",
      "feedback_type": "rating",
      "rating": 5,
      "comment": "Excellent extraction accuracy!",
      "user_id": "user_123",
      "session_id": "rum_session_abc"
    }
    ```

    Args:
        feedback: User feedback request

    Returns:
        Feedback submission response

    Raises:
        HTTPException: If feedback submission fails
    """
    logger.info(
        f"📝 Received feedback: type={feedback.feedback_type}, "
        f"feature={feedback.feature}, ml_app={feedback.ml_app}"
    )

    result = await feedback_service.submit_feedback(feedback)

    if not result.success:
        logger.error(f"❌ Feedback submission failed: {result.message}")
        raise HTTPException(status_code=500, detail=result.message)

    logger.info(f"✅ Feedback submitted successfully")
    return result
