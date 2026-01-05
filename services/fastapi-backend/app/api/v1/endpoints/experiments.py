"""
API endpoints for running LLM experiments.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.security import verify_api_key
from app.models.experiments import ExperimentRequest, ExperimentResponse
from app.services import experiments_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/run",
    response_model=ExperimentResponse,
    summary="Run model experiments",
    description="Run LLM experiments with multiple model configurations using Datadog LLMObs",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def run_experiments(
    request: ExperimentRequest,
) -> ExperimentResponse:
    """
    Run model experiments with Datadog LLMObs.

    This endpoint:
    - Initializes Datadog LLMObs
    - Pulls the specified dataset from Datadog
    - Runs experiments for each model configuration
    - Returns results with comparison URL

    **Authentication**: Requires valid API key in `X-API-Key` header.

    **Example Request**:
    ```json
    {
        "ml_app": "vote-extractor",
        "project_name": "vote-extraction-project",
        "dataset_name": "vote-extraction-bangbamru-1-10",
        "model_configs": [
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.0,
                "name_suffix": "baseline"
            },
            {
                "model": "gemini-2.5-flash-lite",
                "temperature": 0.0,
                "name_suffix": "lite"
            }
        ],
        "sample_size": 10,
        "jobs": 2,
        "raise_errors": true
    }
    ```

    **Response**: Experiment results with metrics and comparison URL.
    """
    try:
        logger.info(f"Received experiment request for {len(request.model_configs)} models")

        # Run experiments
        response = await experiments_service.run_experiments(request)

        logger.info(
            f"Experiments completed: {response.successful_experiments}/{response.total_experiments} successful"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to run experiments: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run experiments: {str(e)}",
        )


@router.post(
    "/run-async",
    summary="Run model experiments (async)",
    description="Run LLM experiments in the background and return immediately",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_api_key)],
)
async def run_experiments_async(
    request: ExperimentRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Run model experiments in the background.

    This endpoint:
    - Accepts the experiment request
    - Starts experiments in the background
    - Returns immediately with a task ID

    **Note**: Use this for long-running experiments to avoid timeouts.

    **Authentication**: Requires valid API key in `X-API-Key` header.

    **Response**: Task ID for tracking (not implemented yet).
    """
    try:
        logger.info(f"Received async experiment request for {len(request.model_configs)} models")

        # Add to background tasks
        background_tasks.add_task(experiments_service.run_experiments, request)

        return {
            "status": "accepted",
            "message": "Experiments started in background",
            "task_id": "not-implemented",  # TODO: Implement task tracking
            "note": "Results will be available in Datadog LLMObs dashboard",
        }

    except Exception as e:
        logger.error(f"Failed to start async experiments: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start async experiments: {str(e)}",
        )


@router.get(
    "/health",
    summary="Check experiments service health",
    description="Check if the experiments service is available and configured",
)
async def health_check() -> Dict[str, Any]:
    """
    Check if experiments service is healthy.

    Returns:
        Health status and configuration info
    """
    import os

    dd_api_key_set = bool(os.getenv("DD_API_KEY"))
    api_key_set = bool(os.getenv("API_KEY"))

    return {
        "status": "healthy",
        "service": "experiments",
        "datadog_configured": dd_api_key_set,
        "api_key_configured": api_key_set,
        "note": "Experiments require Datadog API key and backend API key",
    }
