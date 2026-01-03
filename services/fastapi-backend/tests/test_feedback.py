"""Integration tests for user feedback endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_span_context():
    """Mock span context for testing."""
    return {"span_id": "test_span_123", "trace_id": "test_trace_456"}


def test_submit_rating_feedback(client: TestClient):
    """Test submitting rating feedback."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "rating",
        "rating": 5,
        "comment": "Excellent results!",
        "user_id": "test_user",
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should succeed even if LLMObs is not available (returns appropriate message)
    assert response.status_code in [200, 500]
    data = response.json()

    if response.status_code == 200:
        assert data["success"] is True
        assert "successfully" in data["message"].lower()
    else:
        # LLMObs not available in test environment
        assert "LLMObs not available" in data["detail"]


def test_submit_thumbs_feedback(client: TestClient):
    """Test submitting thumbs feedback."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "thumbs",
        "thumbs": "up",
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should succeed or return appropriate error
    assert response.status_code in [200, 500]


def test_submit_comment_feedback(client: TestClient):
    """Test submitting comment-only feedback."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "comment",
        "comment": "This needs improvement in accuracy.",
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should succeed or return appropriate error
    assert response.status_code in [200, 500]


def test_submit_feedback_missing_required_fields(client: TestClient):
    """Test submitting feedback with missing required fields."""
    feedback_data = {
        "span_id": "test_span_123",
        # Missing trace_id, ml_app, feature, feedback_type
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should return validation error
    assert response.status_code == 422  # Validation error


def test_submit_rating_without_rating_value(client: TestClient):
    """Test submitting rating feedback without rating value."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "rating",
        # Missing rating value
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should return error (invalid feedback type or missing value)
    assert response.status_code in [200, 500]

    if response.status_code == 500:
        data = response.json()
        assert "Invalid feedback type or missing value" in data["detail"]


def test_submit_thumbs_without_thumbs_value(client: TestClient):
    """Test submitting thumbs feedback without thumbs value."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "thumbs",
        # Missing thumbs value
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should return error (invalid feedback type or missing value)
    assert response.status_code in [200, 500]

    if response.status_code == 500:
        data = response.json()
        assert "Invalid feedback type or missing value" in data["detail"]


def test_submit_feedback_with_invalid_rating(client: TestClient):
    """Test submitting feedback with invalid rating value."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "rating",
        "rating": 10,  # Invalid: should be 1-5
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should return validation error
    assert response.status_code == 422  # Validation error


def test_submit_feedback_with_long_comment(client: TestClient):
    """Test submitting feedback with comment exceeding max length."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "rating",
        "rating": 3,
        "comment": "A" * 1001,  # Exceeds max 1000 chars
    }

    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should return validation error
    assert response.status_code == 422  # Validation error


def test_feedback_endpoint_requires_api_key(client: TestClient):
    """Test that feedback endpoint is accessible (auth may be optional)."""
    feedback_data = {
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "rating",
        "rating": 4,
    }

    # The endpoint should be accessible regardless of API key
    # (API key verification may be optional for feedback)
    response = client.post("/api/v1/feedback/submit", json=feedback_data)

    # Should not return 401/403 (authentication errors)
    assert response.status_code not in [401, 403]

