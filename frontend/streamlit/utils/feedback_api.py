"""API client for submitting user feedback to Datadog LLMObs."""

import logging
from typing import Any, Dict, Literal, Optional

import httpx
import streamlit as st

logger = logging.getLogger(__name__)


class FeedbackAPIClient:
    """Client for submitting user feedback to the backend API."""

    def __init__(self, api_base_url: str):
        """
        Initialize the feedback API client.

        Args:
            api_base_url: Base URL of the FastAPI backend
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.feedback_endpoint = f"{self.api_base_url}/api/v1/feedback/submit"

    async def submit_feedback(
        self,
        span_id: str,
        trace_id: str,
        ml_app: str,
        feature: str,
        feedback_type: Literal["rating", "thumbs", "comment"],
        rating: Optional[int] = None,
        thumbs: Optional[Literal["up", "down"]] = None,
        comment: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit user feedback for an LLM response.

        Args:
            span_id: Span ID from Datadog trace
            trace_id: Trace ID from Datadog trace
            ml_app: ML application name (e.g., "vote-extraction-app")
            feature: Feature name (e.g., "vote-extraction")
            feedback_type: Type of feedback: "rating", "thumbs", or "comment"
            rating: Star rating (1-5) for rating feedback
            thumbs: "up" or "down" for thumbs feedback
            comment: User comment or reasoning
            user_id: User identifier (optional)
            session_id: Session identifier (optional)

        Returns:
            Response from the API

        Raises:
            Exception: If API request fails
        """
        payload = {
            "span_id": span_id,
            "trace_id": trace_id,
            "ml_app": ml_app,
            "feature": feature,
            "feedback_type": feedback_type,
        }

        # Add optional fields
        if rating is not None:
            payload["rating"] = rating
        if thumbs:
            payload["thumbs"] = thumbs
        if comment:
            payload["comment"] = comment
        if user_id:
            payload["user_id"] = user_id
        if session_id:
            payload["session_id"] = session_id

        try:
            # Get API key from secrets
            api_key = st.secrets.get("api", {}).get("key")
            if not api_key:
                raise ValueError("API key not found in secrets")

            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.feedback_endpoint, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error submitting feedback: {e.response.status_code}")
            raise Exception(
                f"Failed to submit feedback: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            raise


def get_feedback_client() -> FeedbackAPIClient:
    """
    Get a feedback API client instance.

    Returns:
        FeedbackAPIClient instance
    """
    api_base_url = st.secrets.get("api", {}).get("url", "http://localhost:8000")
    return FeedbackAPIClient(api_base_url)
