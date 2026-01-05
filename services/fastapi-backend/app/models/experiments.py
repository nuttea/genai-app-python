"""
Pydantic models for LLM experiments.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for a single model experiment."""

    model: str = Field(..., description="Model name (e.g., 'gemini-2.5-flash')")
    temperature: float = Field(
        ..., ge=0.0, le=1.0, description="Temperature for generation (0.0-1.0)"
    )
    name_suffix: Optional[str] = Field(None, description="Custom experiment name suffix")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional tags/metadata"
    )


class ExperimentRequest(BaseModel):
    """Request to run model experiments."""

    # LLMObs configuration
    ml_app: str = Field(default="vote-extractor", description="ML app name")
    api_key: Optional[str] = Field(None, description="Datadog API key (optional)")
    site: str = Field(default="datadoghq.com", description="Datadog site")
    agentless_enabled: bool = Field(default=True, description="Enable agentless mode")
    project_name: str = Field(default="vote-extraction-project", description="Project name")

    # Dataset configuration
    dataset_name: str = Field(
        ..., description="Dataset name (e.g., 'vote-extraction-bangbamru-1-10')"
    )
    dataset_version: Optional[int] = Field(None, description="Dataset version (None = latest)")

    # Model configurations
    model_configs: List[ModelConfig] = Field(
        ..., min_length=1, description="List of model configurations to test"
    )

    # Experiment configuration
    sample_size: Optional[int] = Field(
        None, ge=1, description="Number of samples to test (None = all)"
    )
    jobs: int = Field(default=2, ge=1, description="Number of parallel jobs")
    raise_errors: bool = Field(default=True, description="Raise errors on experiment failure")

    class Config:
        json_schema_extra = {
            "example": {
                "ml_app": "vote-extractor",
                "site": "datadoghq.com",
                "agentless_enabled": True,
                "project_name": "vote-extraction-project",
                "dataset_name": "vote-extraction-bangbamru-1-10",
                "dataset_version": None,
                "model_configs": [
                    {
                        "model": "gemini-2.5-flash",
                        "temperature": 0.0,
                        "name_suffix": "baseline",
                        "metadata": {"purpose": "baseline test"},
                    },
                    {
                        "model": "gemini-2.5-flash-lite",
                        "temperature": 0.0,
                        "name_suffix": "lite",
                        "metadata": {"purpose": "cost optimization"},
                    },
                ],
                "sample_size": 10,
                "jobs": 2,
                "raise_errors": True,
            }
        }


class ExperimentSummary(BaseModel):
    """Summary of a single experiment run."""

    experiment_id: str
    experiment_name: str
    experiment_url: str
    model: str
    temperature: float
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    overall_accuracy: Optional[float] = None
    success_rate: Optional[float] = None
    avg_ballot_accuracy: Optional[float] = None


class ExperimentResponse(BaseModel):
    """Response from running experiments."""

    status: str = Field(..., description="Overall status: 'success' or 'failed'")
    message: str = Field(..., description="Status message")
    total_experiments: int
    successful_experiments: int
    failed_experiments: int
    experiments: List[ExperimentSummary]
    dataset_name: str
    dataset_size: int
    project_name: str
    comparison_url: Optional[str] = Field(
        None, description="Direct URL to compare experiments in Datadog"
    )
    dataset_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Successfully ran 2 experiments",
                "total_experiments": 2,
                "successful_experiments": 2,
                "failed_experiments": 0,
                "experiments": [
                    {
                        "experiment_id": "exp_123",
                        "experiment_name": "vote-extraction-baseline",
                        "experiment_url": "https://app.datadoghq.com/llm/experiments/exp_123",
                        "model": "gemini-2.5-flash",
                        "temperature": 0.0,
                        "status": "success",
                        "total_records": 10,
                        "successful_records": 10,
                        "failed_records": 0,
                        "overall_accuracy": 0.95,
                        "success_rate": 1.0,
                        "avg_ballot_accuracy": 0.98,
                    }
                ],
                "dataset_name": "vote-extraction-bangbamru-1-10",
                "dataset_size": 10,
                "project_name": "vote-extraction-project",
                "comparison_url": "https://app.datadoghq.com/llm/experiments?dataset=abc123&project=vote-extraction-project",
                "dataset_id": "abc123",
            }
        }
