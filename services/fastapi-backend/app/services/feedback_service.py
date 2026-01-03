"""Service for submitting user feedback to Datadog LLM Observability."""

import logging
from typing import Any, Dict

from app.models.feedback import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for submitting user feedback as evaluations to Datadog LLMObs."""

    def __init__(self):
        """Initialize the feedback service."""
        self._llmobs_enabled = self._check_llmobs()

    def _check_llmobs(self) -> bool:
        """Check if LLMObs is available and enabled."""
        try:
            from ddtrace.llmobs import LLMObs  # noqa: F401

            return True
        except ImportError:
            logger.warning("ddtrace.llmobs not available - feedback will not be submitted")
            return False

    async def submit_feedback(self, feedback: FeedbackRequest) -> FeedbackResponse:
        """
        Submit user feedback as a custom evaluation to Datadog LLMObs.

        Args:
            feedback: User feedback request

        Returns:
            Feedback submission response
        """
        if not self._llmobs_enabled:
            return FeedbackResponse(
                success=False,
                message="LLMObs not available - cannot submit feedback",
            )

        try:
            from ddtrace.llmobs import LLMObs

            # Prepare span context (IDs are in hexadecimal format from backend)
            # Convert hex strings to integers for Datadog API
            span_context = {
                "span_id": int(feedback.span_id, 16),
                "trace_id": int(feedback.trace_id, 16),
            }

            # Determine metric type, value, and label based on feedback type
            metric_type, value, label = self._determine_evaluation_params(feedback)

            if not metric_type:
                return FeedbackResponse(
                    success=False,
                    message="Invalid feedback type or missing value",
                )

            # Prepare tags with context
            tags = self._prepare_tags(feedback)

            # Submit evaluation to Datadog LLMObs
            # Note: User comments are submitted using the "reasoning" tag, which is
            # the Datadog-recommended field for providing explanations/justifications
            # for evaluation scores. This keeps comments structured and queryable.
            LLMObs.submit_evaluation(
                span=span_context,  # Pass span context dict with span_id and trace_id
                ml_app=feedback.ml_app,
                label=label,
                metric_type=metric_type,
                value=value,
                tags=tags,
            )

            logger.info(
                f"✅ Submitted feedback: {feedback.feedback_type} for "
                f"span {feedback.span_id} in {feedback.ml_app}"
            )

            return FeedbackResponse(success=True, message="Feedback submitted successfully")

        except Exception as e:
            logger.error(f"❌ Failed to submit feedback: {e}", exc_info=True)
            return FeedbackResponse(success=False, message=f"Failed to submit feedback: {str(e)}")

    def _determine_evaluation_params(self, feedback: FeedbackRequest) -> tuple[str, Any, str]:
        """
        Determine metric type, value, and label from feedback.

        Returns:
            Tuple of (metric_type, value, label)
        """
        if feedback.feedback_type == "rating" and feedback.rating is not None:
            # Score type for star ratings (1-5)
            return ("score", feedback.rating, "user_rating")

        elif feedback.feedback_type == "thumbs" and feedback.thumbs:
            # Categorical type for thumbs up/down
            return ("categorical", feedback.thumbs, "user_thumbs")

        elif feedback.feedback_type == "comment" and feedback.comment:
            # Categorical type with "to_be_reviewed" value
            # The actual comment goes in the reasoning tag
            return ("categorical", "to_be_reviewed", "user_comment")

        # Invalid or incomplete feedback
        return (None, None, None)

    def _prepare_tags(self, feedback: FeedbackRequest) -> Dict[str, str]:
        """
        Prepare tags for the evaluation.

        Args:
            feedback: User feedback request

        Returns:
            Dictionary of tags
        """
        tags = {
            "feature": feedback.feature,
            "feedback_type": feedback.feedback_type,
        }

        # Add comment as reasoning field (Datadog best practice)
        # The reasoning field is the recommended tag for providing explanations
        if feedback.comment:
            tags["reasoning"] = feedback.comment

        # Add user context if available
        if feedback.user_id:
            tags["user_id"] = feedback.user_id

        if feedback.session_id:
            tags["session_id"] = feedback.session_id

        return tags


# Global service instance
feedback_service = FeedbackService()
