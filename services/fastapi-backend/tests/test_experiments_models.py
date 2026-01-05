"""
Unit tests for experiments models.
"""

import pytest
from pydantic import ValidationError

from app.models.experiments import (
    ExperimentRequest,
    ExperimentResponse,
    ExperimentSummary,
    ModelConfig,
)


class TestModelConfig:
    """Tests for ModelConfig model."""

    def test_valid_model_config(self):
        """Test valid model configuration."""
        config = ModelConfig(
            model="gemini-2.5-flash",
            temperature=0.0,
            name_suffix="test",
            metadata={"purpose": "test"},
        )

        assert config.model == "gemini-2.5-flash"
        assert config.temperature == 0.0
        assert config.name_suffix == "test"
        assert config.metadata == {"purpose": "test"}

    def test_model_config_without_optional_fields(self):
        """Test model config without optional fields."""
        config = ModelConfig(model="gemini-2.5-flash", temperature=0.5)

        assert config.model == "gemini-2.5-flash"
        assert config.temperature == 0.5
        assert config.name_suffix is None
        assert config.metadata == {}

    def test_temperature_validation_min(self):
        """Test temperature minimum validation."""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(model="gemini-2.5-flash", temperature=-0.1)

        assert "greater than or equal to 0" in str(exc_info.value)

    def test_temperature_validation_max(self):
        """Test temperature maximum validation."""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(model="gemini-2.5-flash", temperature=1.1)

        assert "less than or equal to 1" in str(exc_info.value)

    def test_temperature_edge_cases(self):
        """Test temperature edge cases (0.0 and 1.0)."""
        config1 = ModelConfig(model="gemini-2.5-flash", temperature=0.0)
        config2 = ModelConfig(model="gemini-2.5-flash", temperature=1.0)

        assert config1.temperature == 0.0
        assert config2.temperature == 1.0


class TestExperimentRequest:
    """Tests for ExperimentRequest model."""

    def test_valid_experiment_request(self):
        """Test valid experiment request."""
        request = ExperimentRequest(
            ml_app="vote-extractor",
            site="datadoghq.com",
            project_name="test-project",
            dataset_name="test-dataset",
            model_configs=[
                ModelConfig(model="gemini-2.5-flash", temperature=0.0),
                ModelConfig(model="gemini-2.5-flash-lite", temperature=0.1),
            ],
            sample_size=10,
            jobs=2,
        )

        assert request.ml_app == "vote-extractor"
        assert request.dataset_name == "test-dataset"
        assert len(request.model_configs) == 2
        assert request.sample_size == 10
        assert request.jobs == 2

    def test_experiment_request_with_defaults(self):
        """Test experiment request with default values."""
        request = ExperimentRequest(
            dataset_name="test-dataset",
            model_configs=[ModelConfig(model="gemini-2.5-flash", temperature=0.0)],
        )

        assert request.ml_app == "vote-extractor"
        assert request.site == "datadoghq.com"
        assert request.agentless_enabled is True
        assert request.project_name == "vote-extraction-project"
        assert request.jobs == 2
        assert request.raise_errors is True

    def test_empty_model_configs_validation(self):
        """Test validation error for empty model configs."""
        with pytest.raises(ValidationError) as exc_info:
            ExperimentRequest(dataset_name="test-dataset", model_configs=[])

        assert "at least 1 item" in str(exc_info.value).lower()

    def test_sample_size_validation(self):
        """Test sample size validation."""
        with pytest.raises(ValidationError) as exc_info:
            ExperimentRequest(
                dataset_name="test-dataset",
                model_configs=[ModelConfig(model="gemini-2.5-flash", temperature=0.0)],
                sample_size=0,
            )

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_jobs_validation(self):
        """Test jobs validation."""
        with pytest.raises(ValidationError) as exc_info:
            ExperimentRequest(
                dataset_name="test-dataset",
                model_configs=[ModelConfig(model="gemini-2.5-flash", temperature=0.0)],
                jobs=0,
            )

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_optional_api_key(self):
        """Test optional api_key field."""
        request1 = ExperimentRequest(
            dataset_name="test-dataset",
            model_configs=[ModelConfig(model="gemini-2.5-flash", temperature=0.0)],
        )

        request2 = ExperimentRequest(
            dataset_name="test-dataset",
            model_configs=[ModelConfig(model="gemini-2.5-flash", temperature=0.0)],
            api_key="test-key",
        )

        assert request1.api_key is None
        assert request2.api_key == "test-key"


class TestExperimentSummary:
    """Tests for ExperimentSummary model."""

    def test_valid_experiment_summary(self):
        """Test valid experiment summary."""
        summary = ExperimentSummary(
            experiment_id="exp_123",
            experiment_name="test-experiment",
            experiment_url="https://app.datadoghq.com/experiments/exp_123",
            model="gemini-2.5-flash",
            temperature=0.0,
            status="success",
            total_records=10,
            successful_records=9,
            failed_records=1,
            overall_accuracy=0.95,
            success_rate=0.90,
            avg_ballot_accuracy=0.98,
        )

        assert summary.experiment_id == "exp_123"
        assert summary.model == "gemini-2.5-flash"
        assert summary.status == "success"
        assert summary.total_records == 10
        assert summary.overall_accuracy == 0.95

    def test_experiment_summary_without_optional_metrics(self):
        """Test experiment summary without optional metrics."""
        summary = ExperimentSummary(
            experiment_id="exp_123",
            experiment_name="test-experiment",
            experiment_url="https://app.datadoghq.com/experiments/exp_123",
            model="gemini-2.5-flash",
            temperature=0.0,
            status="failed",
            total_records=0,
            successful_records=0,
            failed_records=0,
        )

        assert summary.overall_accuracy is None
        assert summary.success_rate is None
        assert summary.avg_ballot_accuracy is None


class TestExperimentResponse:
    """Tests for ExperimentResponse model."""

    def test_valid_experiment_response(self):
        """Test valid experiment response."""
        response = ExperimentResponse(
            status="success",
            message="Successfully ran 2 experiments",
            total_experiments=2,
            successful_experiments=2,
            failed_experiments=0,
            experiments=[
                ExperimentSummary(
                    experiment_id="exp_1",
                    experiment_name="exp-1",
                    experiment_url="https://...",
                    model="gemini-2.5-flash",
                    temperature=0.0,
                    status="success",
                    total_records=10,
                    successful_records=10,
                    failed_records=0,
                )
            ],
            dataset_name="test-dataset",
            dataset_size=10,
            project_name="test-project",
        )

        assert response.status == "success"
        assert response.total_experiments == 2
        assert response.successful_experiments == 2
        assert len(response.experiments) == 1

    def test_experiment_response_with_comparison_url(self):
        """Test experiment response with comparison URL."""
        response = ExperimentResponse(
            status="success",
            message="Success",
            total_experiments=1,
            successful_experiments=1,
            failed_experiments=0,
            experiments=[],
            dataset_name="test-dataset",
            dataset_size=10,
            project_name="test-project",
            comparison_url="https://app.datadoghq.com/llm/experiments?dataset=123",
            dataset_id="123",
        )

        assert response.comparison_url is not None
        assert "dataset=123" in response.comparison_url
        assert response.dataset_id == "123"

    def test_experiment_response_partial_failure(self):
        """Test experiment response with partial failures."""
        response = ExperimentResponse(
            status="partial",
            message="Ran 2/3 experiments",
            total_experiments=3,
            successful_experiments=2,
            failed_experiments=1,
            experiments=[],
            dataset_name="test-dataset",
            dataset_size=10,
            project_name="test-project",
        )

        assert response.status == "partial"
        assert response.successful_experiments == 2
        assert response.failed_experiments == 1

