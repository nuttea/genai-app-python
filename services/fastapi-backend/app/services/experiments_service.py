"""
Service for running LLM experiments with Datadog LLMObs.
"""

import logging
import os
from typing import Any, Callable, Dict, List, Optional

import httpx
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow

from app.models.experiments import (
    ExperimentRequest,
    ExperimentResponse,
    ExperimentSummary,
    ModelConfig,
)

logger = logging.getLogger(__name__)


def _normalize_image_path(path: str) -> str:
    """
    Normalize image path to work in both host and container environments.

    Converts absolute host paths to container paths if needed.

    Args:
        path: Original path (can be absolute host path or relative)

    Returns:
        Normalized path that works in the current environment

    Examples:
        Host: /Users/nuttee/Projects/genai-app-python/assets/...
        → Container: /app/assets/...

        Already relative: assets/ss5-18-images/file.jpg
        → Stays: assets/ss5-18-images/file.jpg (or /app/assets/... if in container)
    """
    import re

    # If path contains the project root pattern, extract assets/datasets part
    # Pattern: /path/to/genai-app-python/(assets|datasets)/...
    match = re.search(r"genai-app-python[/\\](assets|datasets)[/\\](.+)$", path)
    if match:
        # Found pattern - convert to container path
        category = match.group(1)  # 'assets' or 'datasets'
        relative_path = match.group(2)  # rest of the path
        container_path = f"/app/{category}/{relative_path}"

        # Check if container path exists (we're in container)
        if os.path.exists(container_path):
            return container_path

        # Otherwise, try original path (we're on host)
        if os.path.exists(path):
            return path

        # Last resort: try relative path from current directory
        relative = f"{category}/{relative_path}"
        if os.path.exists(relative):
            return relative

    # Not matching pattern - use as is if it exists
    if os.path.exists(path):
        return path

    # Try as relative path from /app (container)
    if path.startswith("assets/") or path.startswith("datasets/"):
        container_path = f"/app/{path}"
        if os.path.exists(container_path):
            return container_path

    # Return original path (will fail later with clear error)
    return path


@workflow
def vote_extraction_task(input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task function for vote extraction experiments.

    Required signature for Datadog LLMObs experiments.

    Args:
        input_data: Input data containing form_set_name, image_paths, num_pages
        config: Configuration containing model, temperature, api_key, backend_url

    Returns:
        Extracted data dictionary
    """
    # Extract parameters from input_data
    form_set_name = input_data.get("form_set_name")
    image_paths = input_data.get("image_paths", [])
    num_pages = input_data.get("num_pages", len(image_paths))

    # Extract parameters from config
    model = config.get("model")
    temperature = config.get("temperature", 0.0)
    api_key = config.get("api_key", "")
    backend_url = config.get("backend_url", "http://localhost:8000")

    # Call the FastAPI backend extraction endpoint
    with httpx.Client(timeout=120.0) as client:
        # Read images from paths (normalize for container/host compatibility)
        files = []
        for path in image_paths:
            # Normalize path to work in both container and host
            normalized_path = _normalize_image_path(path)

            if os.path.exists(normalized_path):
                with open(normalized_path, "rb") as f:
                    files.append(("images", (os.path.basename(path), f.read(), "image/jpeg")))
            else:
                logger.warning(f"Image not found: {path} (normalized: {normalized_path})")

        if not files:
            raise FileNotFoundError(
                f"No images found for form {form_set_name}. Paths: {image_paths}"
            )

        # Prepare headers
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        # Make request
        response = client.post(
            f"{backend_url}/api/v1/vote-extraction/extract",
            files=files,
            data={
                "model": model,
                "temperature": temperature,
            },
            headers=headers,
        )
        response.raise_for_status()

        return response.json()


def exact_form_match(input_data: Dict, output_data: Dict, expected_output: Dict) -> bool:
    """Evaluator: Check if form_info matches exactly."""
    output_form = output_data.get("form_info", {})
    expected_form = expected_output.get("form_info", {})
    return output_form == expected_form


def ballot_accuracy_score(input_data: Dict, output_data: Dict, expected_output: Dict) -> float:
    """Evaluator: Calculate ballot statistics accuracy."""
    output_ballot = output_data.get("ballot_statistics", {})
    expected_ballot = expected_output.get("ballot_statistics", {})

    if not output_ballot or not expected_ballot:
        return 0.0

    fields = [
        "ballots_allocated",
        "ballots_used",
        "good_ballots",
        "bad_ballots",
        "no_vote_ballots",
        "ballots_remaining",
    ]

    matches = sum(1 for field in fields if output_ballot.get(field) == expected_ballot.get(field))
    return matches / len(fields)


def vote_results_quality(input_data: Dict, output_data: Dict, expected_output: Dict) -> float:
    """Evaluator: Calculate vote results accuracy."""
    output_votes = output_data.get("vote_results", [])
    expected_votes = expected_output.get("vote_results", [])

    if not output_votes or not expected_votes:
        return 0.0

    # Match by candidate number
    output_map = {v.get("number"): v for v in output_votes}
    expected_map = {v.get("number"): v for v in expected_votes}

    total = len(expected_map)
    if total == 0:
        return 0.0

    matches = sum(
        1
        for num, exp_vote in expected_map.items()
        if output_map.get(num, {}).get("vote_count") == exp_vote.get("vote_count")
    )

    return matches / total


def has_no_errors(input_data: Dict, output_data: Dict, expected_output: Dict) -> bool:
    """Evaluator: Check if extraction had no errors."""
    return "error" not in output_data


def llm_judge_evaluator(input_data: Dict, output_data: Dict, expected_output: Dict) -> float:
    """
    LLM-as-Judge evaluator using gemini-3-pro-preview via Vertex AI.

    Uses a more powerful LLM to evaluate the quality of extraction outputs
    by comparing them with ground truth. Provides detailed reasoning in logs.

    Uses Google GenAI SDK with Vertex AI (same as main extraction service).
    Includes retry logic with exponential backoff for empty responses.

    Args:
        input_data: Original input (form_set_name, image_paths)
        output_data: Model extraction output
        expected_output: Ground truth data

    Returns:
        float: Quality score between 0.0 and 1.0
    """
    import json
    import time
    from google import genai
    from google.genai import types
    from ddtrace import tracer

    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0  # seconds

    # Define response schema for structured output
    EVALUATION_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "score": {
                "type": "NUMBER",
                "description": "Quality score between 0.0 (worst) and 1.0 (perfect)",
            },
            "reasoning": {"type": "STRING", "description": "Brief explanation of the score"},
            "errors": {
                "type": "ARRAY",
                "description": "List of specific errors found",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "field": {"type": "STRING", "description": "Field path with error"},
                        "expected": {"type": "STRING", "description": "Expected value"},
                        "actual": {"type": "STRING", "description": "Actual value"},
                        "severity": {"type": "STRING", "enum": ["minor", "major", "critical"]},
                    },
                },
            },
        },
        "required": ["score", "reasoning", "errors"],
    }

    # Create main evaluation span
    form_set_name = input_data.get("form_set_name", "Unknown")

    with tracer.trace(
        "llm_judge.evaluate", service="vote-extractor", resource=f"evaluate_{form_set_name}"
    ) as eval_span:
        eval_span.set_tag("form_set_name", form_set_name)
        eval_span.set_tag("evaluator", "llm_judge")
        eval_span.set_tag("model", "gemini-3-pro-preview")

        try:
            # Get GCP configuration
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("VERTEX_AI_LOCATION", "global")

            if not project_id:
                logger.warning("LLM Judge: GOOGLE_CLOUD_PROJECT not set, skipping evaluation")
                eval_span.set_tag("error.skip", "missing_gcp_project")
                return 0.0  # Cannot evaluate without project

            # Initialize Google GenAI client with Vertex AI
            # Uses Application Default Credentials (same as main extraction)
            with tracer.trace("llm_judge.initialize_client", service="vote-extractor") as init_span:
                init_span.set_tag("project_id", project_id)
                init_span.set_tag("location", location)

                client = genai.Client(
                    vertexai=True,
                    project=project_id,
                    location=location,
                )

            # Build evaluation prompt with tracing
            with tracer.trace("llm_judge.build_prompt", service="vote-extractor") as prompt_span:
                prompt_span.set_tag("form_set_name", form_set_name)
                prompt_span.set_metric("output_data_size", len(json.dumps(output_data)))
                prompt_span.set_metric("expected_output_size", len(json.dumps(expected_output)))

                prompt = f"""You are an expert election data quality evaluator. Your task is to assess the quality and accuracy of extracted election vote data.

**Context:**
- Form Set: {form_set_name}
- Task: Extraction of Thai election vote data from scanned images

**Model Output (Extracted Data):**
```json
{json.dumps(output_data, indent=2, ensure_ascii=False)}
```

**Ground Truth (Expected Output):**
```json
{json.dumps(expected_output, indent=2, ensure_ascii=False)}
```

**Your Task:**
1. Compare the model output with the ground truth
2. Evaluate accuracy across these dimensions:
   - **Form Information** (date, location, polling station): How accurate?
   - **Voter Statistics** (eligible voters, voters present): Are numbers correct?
   - **Ballot Statistics** (allocated, used, good, bad, no-vote): Do they match?
   - **Vote Results** (candidate numbers, names, vote counts): How many are correct?

3. Identify specific errors:
   - Which fields are wrong?
   - What are the incorrect values vs correct values?
   - Are there any missing or extra data?

4. Provide an overall quality score from 0.0 to 1.0:
   - 1.0 = Perfect match, all data correct
   - 0.8-0.9 = Very good, minor errors
   - 0.6-0.7 = Good, some errors
   - 0.4-0.5 = Fair, many errors
   - 0.0-0.3 = Poor, mostly incorrect
```

Provide your evaluation in JSON format only."""
                prompt_span.set_metric("prompt_length", len(prompt))

            # Call Gemini 3 Pro Preview as judge via Vertex AI with structured schema
            # Retry logic for empty responses
            logger.info(
                f"LLM Judge: Evaluating form {form_set_name} with gemini-3-pro-preview (Vertex AI)"
            )

            response = None
            retry_delay = INITIAL_RETRY_DELAY

            for attempt in range(1, MAX_RETRIES + 1):
                with tracer.trace("llm_judge.api_call", service="vote-extractor") as api_span:
                    api_span.set_tag("model", "gemini-3-pro-preview")
                    api_span.set_tag("provider", "google")
                    api_span.set_tag("temperature", "0.0")
                    api_span.set_metric("max_output_tokens", 4096)
                    api_span.set_metric("attempt", attempt)
                    api_span.set_metric("max_retries", MAX_RETRIES)

                    try:
                        response = client.models.generate_content(
                            model="gemini-3-pro-preview",
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=EVALUATION_SCHEMA,  # Enforce structured output
                                temperature=0.0,  # Deterministic evaluation
                                max_output_tokens=4096,
                            ),
                        )

                        api_span.set_tag("response_received", response is not None)

                        # Debug: Inspect response structure
                        if response:
                            # Log finish reason and other metadata
                            finish_reason = getattr(response, "finish_reason", "N/A")
                            api_span.set_tag("finish_reason", str(finish_reason))

                            # Check for candidates (Gemini response structure)
                            candidates = getattr(response, "candidates", [])
                            api_span.set_metric(
                                "candidates_count", len(candidates) if candidates else 0
                            )

                            # Check safety ratings
                            if hasattr(response, "prompt_feedback"):
                                prompt_feedback = response.prompt_feedback
                                api_span.set_tag("prompt_feedback", str(prompt_feedback))

                            # Log detailed response for debugging
                            logger.info(
                                f"LLM Judge Response Debug - {form_set_name} (attempt {attempt})",
                                extra={
                                    "response_debug": {
                                        "has_text": (
                                            bool(response.text)
                                            if hasattr(response, "text")
                                            else False
                                        ),
                                        "text_length": (
                                            len(response.text)
                                            if hasattr(response, "text") and response.text
                                            else 0
                                        ),
                                        "finish_reason": str(finish_reason),
                                        "candidates_count": len(candidates) if candidates else 0,
                                        "has_prompt_feedback": hasattr(response, "prompt_feedback"),
                                        "response_type": type(response).__name__,
                                    }
                                },
                            )

                        # Check if response has content
                        if response and response.text:
                            api_span.set_tag("response_valid", True)
                            logger.info(
                                f"LLM Judge: Received valid response for {form_set_name} (attempt {attempt})"
                            )
                            break  # Success! Exit retry loop
                        else:
                            api_span.set_tag("response_valid", False)
                            api_span.set_tag("retry_reason", "empty_response")

                            # Detailed error logging for empty responses
                            error_details = {
                                "form_set_name": form_set_name,
                                "attempt": attempt,
                                "max_retries": MAX_RETRIES,
                                "response_exists": response is not None,
                            }

                            if response:
                                error_details.update(
                                    {
                                        "finish_reason": str(
                                            getattr(response, "finish_reason", "N/A")
                                        ),
                                        "candidates": len(getattr(response, "candidates", [])),
                                        "has_text": hasattr(response, "text"),
                                        "text_value": (
                                            str(response.text)
                                            if hasattr(response, "text")
                                            else "N/A"
                                        ),
                                    }
                                )

                                # Check for safety/blocking issues
                                if hasattr(response, "prompt_feedback"):
                                    error_details["prompt_feedback"] = str(response.prompt_feedback)

                            if attempt < MAX_RETRIES:
                                logger.warning(
                                    f"LLM Judge: Empty response for {form_set_name} (attempt {attempt}/{MAX_RETRIES}), "
                                    f"retrying in {retry_delay:.1f}s...",
                                    extra={"empty_response_debug": error_details},
                                )
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                            else:
                                logger.error(
                                    f"LLM Judge: Empty response for {form_set_name} after {MAX_RETRIES} attempts",
                                    extra={"empty_response_final": error_details},
                                )

                    except Exception as api_error:
                        api_span.set_tag("api_error", str(api_error))

                        if attempt < MAX_RETRIES:
                            logger.warning(
                                f"LLM Judge: API error for {form_set_name} (attempt {attempt}/{MAX_RETRIES}): {api_error}, "
                                f"retrying in {retry_delay:.1f}s..."
                            )
                            time.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            logger.error(
                                f"LLM Judge: API error for {form_set_name} after {MAX_RETRIES} attempts: {api_error}"
                            )
                            raise

            # Parse and validate response
            with tracer.trace("llm_judge.parse_response", service="vote-extractor") as parse_span:
                if not response or not response.text:
                    logger.warning(f"LLM Judge: Empty or None response for {form_set_name}")
                    parse_span.set_tag("error", "empty_response")
                    eval_span.set_tag("result", "failed")
                    eval_span.set_metric("score", 0.0)
                    return 0.0

                parse_span.set_metric("response_length", len(response.text))

                evaluation = json.loads(response.text)

                score = float(evaluation.get("score", 0.0))
                reasoning = evaluation.get("reasoning", "No reasoning provided")
                errors = evaluation.get("errors", [])
                summary = evaluation.get("summary", "No summary provided")

                parse_span.set_metric("score", score)
                parse_span.set_metric("error_count", len(errors))
                parse_span.set_tag("has_reasoning", bool(reasoning))

            # Log detailed evaluation with tracing
            with tracer.trace("llm_judge.log_results", service="vote-extractor") as log_span:
                log_span.set_metric("score", score)
                log_span.set_metric("error_count", len(errors))
                log_span.set_tag("summary", summary[:100] if summary else "")  # Truncate for tag

                logger.info(
                    f"LLM Judge Evaluation - {form_set_name}",
                    extra={
                        "llm_judge": {
                            "form_set_name": form_set_name,
                            "score": score,
                            "summary": summary,
                            "reasoning": reasoning,
                            "error_count": len(errors),
                            "errors": errors,
                            "judge_model": "gemini-3-pro-preview",
                        }
                    },
                )

                # Log errors individually for better searchability
                if errors:
                    for error in errors:
                        logger.warning(
                            f"LLM Judge Error - {form_set_name}: {error.get('field', 'unknown')}",
                            extra={
                                "llm_judge_error": {
                                    "form_set_name": form_set_name,
                                    "field": error.get("field", "unknown"),
                                    "expected": error.get("expected", "N/A"),
                                    "actual": error.get("actual", "N/A"),
                                    "severity": error.get("severity", "unknown"),
                                }
                            },
                        )

            # Log summary at appropriate level
            if score >= 0.8:
                logger.info(
                    f"LLM Judge: {form_set_name} - Excellent quality (score={score:.2f}): {summary}"
                )
                eval_span.set_tag("quality_level", "excellent")
            elif score >= 0.6:
                logger.info(
                    f"LLM Judge: {form_set_name} - Good quality (score={score:.2f}): {summary}"
                )
                eval_span.set_tag("quality_level", "good")
            elif score >= 0.4:
                logger.warning(
                    f"LLM Judge: {form_set_name} - Fair quality (score={score:.2f}): {summary}"
                )
                eval_span.set_tag("quality_level", "fair")
            else:
                logger.error(
                    f"LLM Judge: {form_set_name} - Poor quality (score={score:.2f}): {summary}"
                )
                eval_span.set_tag("quality_level", "poor")

            # Set final metrics on eval span
            eval_span.set_metric("final_score", score)
            eval_span.set_metric("total_errors", len(errors))
            eval_span.set_tag("result", "success")

            return score

        except json.JSONDecodeError as e:
            logger.error(
                f"LLM Judge: Failed to parse JSON response for {form_set_name}: {e}",
                extra={
                    "error_type": "JSONDecodeError",
                    "form_set_name": form_set_name,
                    "raw_response": response.text if "response" in locals() else None,
                },
            )
            eval_span.set_tag("error", "json_decode_error")
            eval_span.set_tag("error.message", str(e))
            eval_span.set_metric("final_score", 0.0)
            return 0.0  # Score 0 on parse error

        except Exception as e:
            logger.error(
                f"LLM Judge: Error evaluating {form_set_name}: {e}",
                extra={
                    "error_type": type(e).__name__,
                    "form_set_name": form_set_name,
                    "error_message": str(e),
                },
                exc_info=True,
            )
            eval_span.set_tag("error", type(e).__name__)
            eval_span.set_tag("error.message", str(e))
            eval_span.set_metric("final_score", 0.0)
            return 0.0  # Score 0 on error


def overall_accuracy(
    inputs: List[Dict],
    outputs: List[Dict],
    expected_outputs: List[Dict],
    evaluators_results: List[Dict],
) -> float:
    """Summary evaluator: Overall accuracy across all metrics."""
    if not evaluators_results:
        return 0.0

    total_score = 0.0
    for result in evaluators_results:
        # Weighted average of all evaluators
        # LLM judge gets 30% weight as it provides holistic assessment
        score = (
            result.get("exact_form_match", 0) * 0.15
            + result.get("ballot_accuracy_score", 0) * 0.25
            + result.get("vote_results_quality", 0) * 0.30
            + result.get("llm_judge_evaluator", 0.0) * 0.30  # LLM judge (default 0.5 if missing)
        )
        total_score += score

    return total_score / len(evaluators_results)


def success_rate(
    inputs: List[Dict],
    outputs: List[Dict],
    expected_outputs: List[Dict],
    evaluators_results: List[Dict],
) -> float:
    """Summary evaluator: Success rate (no errors)."""
    if not evaluators_results:
        return 0.0
    successful = sum(1 for r in evaluators_results if r.get("has_no_errors", False))
    return successful / len(evaluators_results)


def avg_ballot_accuracy(
    inputs: List[Dict],
    outputs: List[Dict],
    expected_outputs: List[Dict],
    evaluators_results: List[Dict],
) -> float:
    """Summary evaluator: Average ballot accuracy."""
    if not evaluators_results:
        return 0.0
    total = sum(r.get("ballot_accuracy_score", 0) for r in evaluators_results)
    return total / len(evaluators_results)


def avg_llm_judge_score(
    inputs: List[Dict],
    outputs: List[Dict],
    expected_outputs: List[Dict],
    evaluators_results: List[Dict],
) -> float:
    """Summary evaluator: Average LLM judge quality score."""
    if not evaluators_results:
        return 0.0
    total = sum(r.get("llm_judge_evaluator", 0.0) for r in evaluators_results)
    return total / len(evaluators_results)


async def run_experiments(request: ExperimentRequest) -> ExperimentResponse:
    """
    Run model experiments with Datadog LLMObs.

    Args:
        request: Experiment request configuration

    Returns:
        Experiment response with results

    Raises:
        Exception: If experiments fail and raise_errors is True
    """
    logger.info(f"Starting experiments for project: {request.project_name}")
    logger.info(f"Dataset: {request.dataset_name}, Models: {len(request.model_configs)}")

    # Initialize LLMObs
    llmobs_config = {
        "ml_app": request.ml_app,
        "site": request.site,
        "agentless_enabled": request.agentless_enabled,
    }

    if request.api_key:
        llmobs_config["api_key"] = request.api_key

    LLMObs.enable(**llmobs_config)
    logger.info(f"LLMObs enabled: {request.ml_app} @ {request.site}")

    try:
        # Pull dataset from Datadog
        logger.info(f"Pulling dataset: {request.dataset_name}")
        dataset = LLMObs.pull_dataset(
            dataset_name=request.dataset_name,
            project_name=request.project_name,
            version=request.dataset_version,
        )
        logger.info(f"Dataset loaded: {len(dataset)} records")

        # Extract dataset ID from URL
        dataset_id = None
        try:
            if hasattr(dataset, "url") and dataset.url:
                dataset_id = dataset.url.split("/datasets/")[-1]
                logger.info(f"Dataset ID: {dataset_id}")
        except Exception as e:
            logger.warning(f"Could not extract dataset ID: {e}")

        # Define evaluators
        evaluators = [
            exact_form_match,
            ballot_accuracy_score,
            vote_results_quality,
            has_no_errors,
            llm_judge_evaluator,  # LLM-as-Judge using gemini-3-pro-preview
        ]

        summary_evaluators = [
            overall_accuracy,
            success_rate,
            avg_ballot_accuracy,
            avg_llm_judge_score,  # Average LLM judge quality assessment
        ]

        # Get backend URL and API key
        backend_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        api_key = os.getenv("API_KEY", "")

        # Run experiments for each model config
        all_results = []
        for config in request.model_configs:
            logger.info(f"Running experiment: {config.model} (T={config.temperature})")

            try:
                # Generate experiment name
                name_suffix = config.name_suffix or f"{config.model}-t{config.temperature}"
                experiment_name = f"vote-extraction-{name_suffix}"

                # Prepare tags
                tags = {
                    "model": config.model,
                    "temperature": str(config.temperature),
                    **{k: str(v) for k, v in config.metadata.items()},
                }

                # Prepare config for the task (bind parameters for this model)
                bound_config = {
                    "model": config.model,
                    "temperature": config.temperature,
                    "api_key": api_key,
                    "backend_url": backend_url,
                }

                # Create task function with correct signature for Datadog
                def task_fn(input_data: Dict, config: Dict) -> Dict:
                    # Merge bound config with any config passed by experiment runner
                    final_config = {**bound_config, **config}
                    return vote_extraction_task(input_data, final_config)

                # Create experiment
                experiment = LLMObs.experiment(
                    name=experiment_name,
                    task=task_fn,
                    dataset=dataset,
                    evaluators=evaluators,
                    summary_evaluators=summary_evaluators,
                    tags=tags,
                )

                logger.info(f"Created experiment: {experiment.name}")
                logger.info(f"Experiment URL: {experiment.url}")

                # Run experiment
                experiment.run(
                    sample_size=request.sample_size,
                    jobs=request.jobs,
                    raise_errors=request.raise_errors,
                )

                # Get summary metrics
                summary = experiment.summary()
                logger.info(f"Experiment completed: {summary}")

                # Create experiment summary
                exp_summary = ExperimentSummary(
                    experiment_id=getattr(experiment, "id", "unknown"),
                    experiment_name=experiment.name,
                    experiment_url=experiment.url,
                    model=config.model,
                    temperature=config.temperature,
                    status="success",
                    total_records=len(experiment.results),
                    successful_records=sum(
                        1
                        for r in experiment.results
                        if r.get("metrics", {}).get("has_no_errors", False)
                    ),
                    failed_records=sum(
                        1
                        for r in experiment.results
                        if not r.get("metrics", {}).get("has_no_errors", False)
                    ),
                    overall_accuracy=summary.get("overall_accuracy"),
                    success_rate=summary.get("success_rate"),
                    avg_ballot_accuracy=summary.get("avg_ballot_accuracy"),
                )

                all_results.append(exp_summary)

            except Exception as e:
                logger.error(f"Experiment failed for {config.model}: {e}")

                exp_summary = ExperimentSummary(
                    experiment_id="unknown",
                    experiment_name=f"vote-extraction-{config.name_suffix or config.model}",
                    experiment_url="",
                    model=config.model,
                    temperature=config.temperature,
                    status="failed",
                    total_records=0,
                    successful_records=0,
                    failed_records=0,
                )

                all_results.append(exp_summary)

                if request.raise_errors:
                    raise

        # Generate comparison URL
        comparison_url = None
        if dataset_id:
            comparison_url = f"https://app.{request.site}/llm/experiments?dataset={dataset_id}&project={request.project_name}"

        # Create response
        successful = sum(1 for r in all_results if r.status == "success")
        failed = len(all_results) - successful

        response = ExperimentResponse(
            status="success" if failed == 0 else "partial" if successful > 0 else "failed",
            message=f"Successfully ran {successful}/{len(all_results)} experiments",
            total_experiments=len(all_results),
            successful_experiments=successful,
            failed_experiments=failed,
            experiments=all_results,
            dataset_name=request.dataset_name,
            dataset_size=len(dataset),
            project_name=request.project_name,
            comparison_url=comparison_url,
            dataset_id=dataset_id,
        )

        logger.info(f"Experiments completed: {successful} success, {failed} failed")

        return response

    finally:
        # Cleanup (optional - LLMObs will flush on exit)
        pass
