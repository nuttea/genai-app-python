"""
Integration tests for experiments API endpoints.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.security import verify_api_key
from app.main import app
from app.models.experiments import (
    ExperimentResponse,
    ExperimentSummary,
)

# Test API key
TEST_API_KEY = "test-api-key-123"


# Mock security dependency
async def override_verify_api_key():
    """Mock API key verification for testing."""
    return True


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    # Override the dependency
    app.dependency_overrides[verify_api_key] = override_verify_api_key
    yield
    # Cleanup
    app.dependency_overrides.clear()


# Create test client
client = TestClient(app)


@pytest.fixture
def mock_experiment_response():
    """Mock experiment response for testing."""
    return ExperimentResponse(
        status="success",
        message="Successfully ran 2 experiments",
        total_experiments=2,
        successful_experiments=2,
        failed_experiments=0,
        experiments=[
            ExperimentSummary(
                experiment_id="exp_1",
                experiment_name="vote-extraction-lite",
                experiment_url="https://app.datadoghq.com/llm/experiments/exp_1",
                model="gemini-2.5-flash-lite",
                temperature=0.0,
                status="success",
                total_records=4,
                successful_records=4,
                failed_records=0,
                overall_accuracy=0.95,
                success_rate=1.0,
                avg_ballot_accuracy=0.98,
            ),
            ExperimentSummary(
                experiment_id="exp_2",
                experiment_name="vote-extraction-flash",
                experiment_url="https://app.datadoghq.com/llm/experiments/exp_2",
                model="gemini-2.5-flash",
                temperature=0.0,
                status="success",
                total_records=4,
                successful_records=4,
                failed_records=0,
                overall_accuracy=0.97,
                success_rate=1.0,
                avg_ballot_accuracy=0.99,
            ),
        ],
        dataset_name="vote-extraction-bangbamru-1-10",
        dataset_size=10,
        project_name="vote-extraction-project",
        comparison_url="https://app.datadoghq.com/llm/experiments?dataset=abc123&project=vote-extraction-project",
        dataset_id="abc123",
    )


class TestExperimentsHealthEndpoint:
    """Tests for /api/v1/experiments/health endpoint."""

    def test_health_check(self):
        """Test experiments health check."""
        response = client.get("/api/v1/experiments/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "experiments"
        assert "datadog_configured" in data
        assert "api_key_configured" in data

    def test_health_check_no_auth_required(self):
        """Test health check doesn't require authentication."""
        # Should work without API key
        response = client.get("/api/v1/experiments/health")
        assert response.status_code == 200


class TestExperimentsRunEndpoint:
    """Tests for /api/v1/experiments/run endpoint."""

    def test_run_experiments_without_auth(self, mock_api_key):
        """Test running experiments without authentication."""
        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
        }

        response = client.post("/api/v1/experiments/run", json=request_data)

        # Should return 401 without API key
        assert response.status_code == 401

    def test_run_experiments_with_invalid_auth(self, mock_api_key):
        """Test running experiments with invalid API key."""
        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
        }

        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": "invalid-key"},
        )

        # Should return 401 with invalid key
        assert response.status_code == 401

    @patch("app.services.experiments_service.run_experiments")
    def test_run_experiments_success(
        self, mock_run_experiments, mock_api_key, mock_experiment_response
    ):
        """Test successful experiment run."""
        # Mock the service call
        mock_run_experiments.return_value = mock_experiment_response

        request_data = {
            "dataset_name": "vote-extraction-bangbamru-1-10",
            "model_configs": [
                {"model": "gemini-2.5-flash-lite", "temperature": 0.0},
                {"model": "gemini-2.5-flash", "temperature": 0.0},
            ],
            "sample_size": 4,
            "jobs": 2,
        }

        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["total_experiments"] == 2
        assert data["successful_experiments"] == 2
        assert len(data["experiments"]) == 2
        assert data["comparison_url"] is not None

    def test_run_experiments_invalid_request(self, mock_api_key):
        """Test experiment run with invalid request."""
        # Missing required field
        request_data = {
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
        }

        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_run_experiments_empty_model_configs(self, mock_api_key):
        """Test experiment run with empty model configs."""
        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [],
        }

        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_run_experiments_invalid_temperature(self, mock_api_key):
        """Test experiment run with invalid temperature."""
        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 1.5}  # Invalid
            ],
        }

        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_run_experiments_invalid_sample_size(self, mock_api_key):
        """Test experiment run with invalid sample size."""
        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
            "sample_size": 0,  # Invalid
        }

        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    @patch("app.services.experiments_service.run_experiments")
    def test_run_experiments_service_error(self, mock_run_experiments, mock_api_key):
        """Test experiment run with service error."""
        # Mock service to raise an exception
        mock_run_experiments.side_effect = Exception("Service error")

        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
        }

        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # Should return 500 for internal error
        assert response.status_code == 500
        assert "Failed to run experiments" in response.json()["detail"]


class TestExperimentsRunAsyncEndpoint:
    """Tests for /api/v1/experiments/run-async endpoint."""

    def test_run_async_without_auth(self, mock_api_key):
        """Test running async experiments without authentication."""
        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
        }

        response = client.post("/api/v1/experiments/run-async", json=request_data)

        # Should return 401 without API key
        assert response.status_code == 401

    @patch("app.services.experiments_service.run_experiments")
    def test_run_async_success(self, mock_run_experiments, mock_api_key):
        """Test successful async experiment run."""
        # Mock the service call (will run in background)
        mock_run_experiments.return_value = AsyncMock()

        request_data = {
            "dataset_name": "vote-extraction-bangbamru-1-10",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
            "sample_size": 4,
        }

        response = client.post(
            "/api/v1/experiments/run-async",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        assert response.status_code == 202
        data = response.json()

        assert data["status"] == "accepted"
        assert "background" in data["message"].lower()
        assert data["task_id"] == "not-implemented"  # TODO: Implement task tracking

    def test_run_async_invalid_request(self, mock_api_key):
        """Test async experiment run with invalid request."""
        # Missing required field
        request_data = {
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
        }

        response = client.post(
            "/api/v1/experiments/run-async",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # Should return 422 for validation error
        assert response.status_code == 422


class TestExperimentsRequestValidation:
    """Tests for experiment request validation."""

    def test_valid_minimal_request(self, mock_api_key):
        """Test minimal valid request."""
        request_data = {
            "dataset_name": "test-dataset",
            "model_configs": [
                {"model": "gemini-2.5-flash", "temperature": 0.0}
            ],
        }

        # Should not raise validation error (will fail at service level)
        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # May return 500 if service fails, but not 422 (validation)
        assert response.status_code != 422

    def test_valid_full_request(self, mock_api_key):
        """Test full valid request with all fields."""
        request_data = {
            "ml_app": "test-app",
            "site": "datadoghq.com",
            "agentless_enabled": True,
            "project_name": "test-project",
            "dataset_name": "test-dataset",
            "dataset_version": 1,
            "model_configs": [
                {
                    "model": "gemini-2.5-flash",
                    "temperature": 0.5,
                    "name_suffix": "test",
                    "metadata": {"purpose": "test"},
                }
            ],
            "sample_size": 10,
            "jobs": 2,
            "raise_errors": True,
        }

        # Should not raise validation error
        response = client.post(
            "/api/v1/experiments/run",
            json=request_data,
            headers={"X-API-Key": TEST_API_KEY},
        )

        # May return 500 if service fails, but not 422 (validation)
        assert response.status_code != 422

