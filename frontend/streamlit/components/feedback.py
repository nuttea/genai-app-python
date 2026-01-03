"""Feedback UI components for collecting user feedback."""

import asyncio
import logging
from typing import Optional

import streamlit as st

from utils.feedback_api import get_feedback_client

logger = logging.getLogger(__name__)


def render_star_rating(
    span_id: str,
    trace_id: str,
    ml_app: str,
    feature: str,
    key_suffix: str = "",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """
    Render a star rating feedback component.

    Args:
        span_id: Span ID from Datadog trace
        trace_id: Trace ID from Datadog trace
        ml_app: ML application name
        feature: Feature name
        key_suffix: Suffix for Streamlit component keys (for uniqueness)
        user_id: User identifier (optional)
        session_id: Session identifier (optional)
    """
    st.subheader("📊 Rate this result")

    col1, col2 = st.columns([3, 1])

    with col1:
        rating = st.slider(
            "How accurate was this result?",
            min_value=1,
            max_value=5,
            value=3,
            key=f"rating_{key_suffix}",
            help="1 = Very Poor, 5 = Excellent",
        )

    with col2:
        if st.button("Submit Rating", key=f"submit_rating_{key_suffix}"):
            # Submit feedback
            try:
                feedback_client = get_feedback_client()

                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    feedback_client.submit_feedback(
                        span_id=span_id,
                        trace_id=trace_id,
                        ml_app=ml_app,
                        feature=feature,
                        feedback_type="rating",
                        rating=rating,
                        user_id=user_id,
                        session_id=session_id,
                    )
                )
                loop.close()

                if result.get("success"):
                    st.success("✅ Thank you for your feedback!")
                else:
                    st.error(f"❌ Failed to submit feedback: {result.get('message')}")

            except Exception as e:
                logger.error(f"Error submitting feedback: {e}")
                st.error("❌ Failed to submit feedback. Please try again.")


def render_thumbs_feedback(
    span_id: str,
    trace_id: str,
    ml_app: str,
    feature: str,
    key_suffix: str = "",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """
    Render a thumbs up/down feedback component.

    Args:
        span_id: Span ID from Datadog trace
        trace_id: Trace ID from Datadog trace
        ml_app: ML application name
        feature: Feature name
        key_suffix: Suffix for Streamlit component keys
        user_id: User identifier (optional)
        session_id: Session identifier (optional)
    """
    st.subheader("👍 Was this helpful?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Yes", key=f"thumbs_up_{key_suffix}"):
            _submit_thumbs(
                span_id,
                trace_id,
                ml_app,
                feature,
                "up",
                user_id,
                session_id,
            )

    with col2:
        if st.button("👎 No", key=f"thumbs_down_{key_suffix}"):
            _submit_thumbs(
                span_id,
                trace_id,
                ml_app,
                feature,
                "down",
                user_id,
                session_id,
            )


def render_feedback_with_comment(
    span_id: str,
    trace_id: str,
    ml_app: str,
    feature: str,
    key_suffix: str = "",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """
    Render a combined rating + comment feedback component.

    Args:
        span_id: Span ID from Datadog trace
        trace_id: Trace ID from Datadog trace
        ml_app: ML application name
        feature: Feature name
        key_suffix: Suffix for Streamlit component keys
        user_id: User identifier (optional)
        session_id: Session identifier (optional)
    """
    st.subheader("📝 Provide Feedback")

    rating = st.slider(
        "Rate this result",
        min_value=1,
        max_value=5,
        value=3,
        key=f"rating_with_comment_{key_suffix}",
        help="1 = Very Poor, 5 = Excellent",
    )

    comment = st.text_area(
        "Additional comments (optional)",
        placeholder="Tell us what you think...",
        max_chars=1000,
        key=f"comment_{key_suffix}",
    )

    if st.button("Submit Feedback", key=f"submit_feedback_{key_suffix}"):
        try:
            feedback_client = get_feedback_client()

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                feedback_client.submit_feedback(
                    span_id=span_id,
                    trace_id=trace_id,
                    ml_app=ml_app,
                    feature=feature,
                    feedback_type="rating",
                    rating=rating,
                    comment=comment if comment else None,
                    user_id=user_id,
                    session_id=session_id,
                )
            )
            loop.close()

            if result.get("success"):
                st.success("✅ Thank you for your feedback!")
            else:
                st.error(f"❌ Failed to submit feedback: {result.get('message')}")

        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            st.error("❌ Failed to submit feedback. Please try again.")


def _submit_thumbs(
    span_id: str,
    trace_id: str,
    ml_app: str,
    feature: str,
    thumbs: str,
    user_id: Optional[str],
    session_id: Optional[str],
) -> None:
    """
    Internal helper to submit thumbs feedback.

    Args:
        span_id: Span ID
        trace_id: Trace ID
        ml_app: ML app name
        feature: Feature name
        thumbs: "up" or "down"
        user_id: User ID
        session_id: Session ID
    """
    try:
        feedback_client = get_feedback_client()

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            feedback_client.submit_feedback(
                span_id=span_id,
                trace_id=trace_id,
                ml_app=ml_app,
                feature=feature,
                feedback_type="thumbs",
                thumbs=thumbs,
                user_id=user_id,
                session_id=session_id,
            )
        )
        loop.close()

        if result.get("success"):
            st.success("✅ Thank you for your feedback!")
        else:
            st.error(f"❌ Failed to submit feedback: {result.get('message')}")

    except Exception as e:
        logger.error(f"Error submitting thumbs feedback: {e}")
        st.error("❌ Failed to submit feedback. Please try again.")
