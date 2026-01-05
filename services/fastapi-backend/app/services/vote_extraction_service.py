"""Vote extraction service using Google GenAI."""

import json
import logging
import os
from typing import Any, Optional

from app.config import settings
from app.core.exceptions import ExtractionException
from app.models.vote_extraction import ElectionFormData, LLMConfig
from google import genai
from google.genai import types

# Initialize logger first
logger = logging.getLogger(__name__)

# Datadog LLM Observability
try:
    from ddtrace.llmobs import LLMObs
    from ddtrace.llmobs.decorators import workflow

    DDTRACE_AVAILABLE = True
except ImportError:
    DDTRACE_AVAILABLE = False
    logger.warning("ddtrace not available - LLM observability will be disabled")

    # Define no-op decorators if ddtrace is not available
    def workflow(func):
        """No-op workflow decorator when ddtrace is not available."""
        return func

    def task(func):
        """No-op task decorator when ddtrace is not available."""
        return func


# Election form schema defined as an ARRAY to handle
# multiple forms (Constituency + PartyList) in one response
ELECTION_DATA_SCHEMA = {
    "type": "ARRAY",
    "description": (
        "A list of election reports found in the input images "
        "(usually one Constituency report and one PartyList report)."
    ),
    "items": {
        "type": "OBJECT",
        "properties": {
            "form_info": {
                "type": "OBJECT",
                "description": "Header information identifying the polling station and form type.",
                "properties": {
                    "form_type": {
                        "type": "STRING",
                        "enum": ["Constituency", "PartyList"],
                        "description": (
                            "Identify if this specific report is for Constituency (Candidate) "
                            "or PartyList (Party only). Check the header text "
                            "(e.g., 'แบบบัญชีรายชื่อ' = PartyList)."
                        ),
                    },
                    "date": {"type": "STRING", "description": "Date of election"},
                    "province": {"type": "STRING", "description": "Province name"},
                    "district": {"type": "STRING", "description": "District name (Amphoe/Khet)"},
                    "sub_district": {
                        "type": "STRING",
                        "description": "Sub-district name (Tambon/Khwaeng)",
                    },
                    "constituency_number": {"type": "STRING", "description": "Constituency number"},
                    "polling_station_number": {"type": "STRING", "description": "Unit number"},
                },
                "required": ["form_type", "province", "district", "polling_station_number"],
            },
            "voter_statistics": {
                "type": "OBJECT",
                "description": "Section 1: Voter statistics for this specific form.",
                "properties": {
                    "eligible_voters": {
                        "type": "INTEGER",
                        "description": "Item 1.1: Total eligible voters",
                    },
                    "voters_present": {
                        "type": "INTEGER",
                        "description": "Item 1.2: Total voters present",
                    },
                },
            },
            "ballot_statistics": {
                "type": "OBJECT",
                "description": "Section 2: Ballot accounting for this specific form.",
                "properties": {
                    "ballots_allocated": {
                        "type": "INTEGER",
                        "description": "Item 2.1: Total allocated ballots",
                    },
                    "ballots_used": {
                        "type": "INTEGER",
                        "description": "Item 2.2: Total used ballots",
                    },
                    "good_ballots": {"type": "INTEGER", "description": "Item 2.2.1: Good ballots"},
                    "bad_ballots": {"type": "INTEGER", "description": "Item 2.2.2: Bad ballots"},
                    "no_vote_ballots": {
                        "type": "INTEGER",
                        "description": "Item 2.2.3: No Vote ballots",
                    },
                    "ballots_remaining": {
                        "type": "INTEGER",
                        "description": "Item 2.3: Remaining ballots",
                    },
                },
            },
            "vote_results": {
                "type": "ARRAY",
                "description": "Section 3: Vote counts table from all pages belonging to this form type.",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "number": {"type": "INTEGER"},
                        "candidate_name": {
                            "type": "STRING",
                            "description": "Name of Candidate (for Constituency). Leave null for PartyList.",
                        },
                        "party_name": {"type": "STRING"},
                        "vote_count": {"type": "INTEGER"},
                        "vote_count_text": {"type": "STRING"},
                    },
                },
            },
        },
        "required": ["form_info", "ballot_statistics", "vote_results"],
    },
}


class VoteExtractionService:
    """Service for extracting vote data from election form images."""

    def __init__(self):
        """Initialize the vote extraction service."""
        self._client: genai.Client | None = None
        self._llmobs_enabled = False
        self._last_workflow_span_context: dict[str, str] | None = (
            None  # Store span context from workflow
        )
        self._initialize_llmobs()

    def get_workflow_span_context(self) -> dict[str, str] | None:
        """
        Get the most recent workflow span context.

        This returns the span context captured from the last workflow execution.
        Used to associate user feedback with the correct LLMObs workflow span.

        Returns:
            Dictionary with 'span_id' and 'trace_id' as strings, or None if not available
        """
        return self._last_workflow_span_context

    def _initialize_llmobs(self) -> None:
        """Initialize Datadog LLMObs if available."""
        if not DDTRACE_AVAILABLE:
            return

        # Check if required env vars are set
        ml_app = os.getenv("DD_LLMOBS_ML_APP")
        api_key = os.getenv("DD_API_KEY")
        service = os.getenv("DD_SERVICE", "vote-extraction-service")
        project_name = os.getenv("DD_PROJECT_NAME", "vote-extraction-project")

        if ml_app and api_key:
            try:
                LLMObs.enable(
                    ml_app=ml_app,
                    api_key=api_key,
                    service=service,
                    agentless_enabled=True,
                    project_name=project_name,
                )
                self._llmobs_enabled = True
                logger.info(f"Datadog LLMObs enabled for service: {service}")
            except Exception as e:
                logger.warning(f"Failed to enable Datadog LLMObs: {e}")
        else:
            logger.info("Datadog LLMObs not configured (missing DD_LLMOBS_ML_APP or DD_API_KEY)")

    def _get_client(self) -> genai.Client:
        """Get or create the GenAI client."""
        if self._client is None:
            # Initialize with Vertex AI credentials
            self._client = genai.Client(
                vertexai=True,
                project=settings.google_cloud_project,
                location=settings.vertex_ai_location,
            )
            logger.info(
                f"Initialized Google GenAI client for vote extraction "
                f"(project={settings.google_cloud_project}, location={settings.vertex_ai_location})"
            )
        return self._client

    def _process_images_to_content_parts(
        self, image_files: list[bytes], image_filenames: list[str]
    ) -> list:
        """Process image files into content parts for Gemini."""
        content_parts = []
        for i, (image_bytes, filename) in enumerate(
            zip(image_files, image_filenames, strict=False), 1
        ):
            try:
                # Add an Index Label BEFORE the image
                index_label = f"Page {i} (Filename: {filename})"
                content_parts.append(index_label)

                # Determine MIME type from filename
                mime_type = "image/jpeg"
                if filename.lower().endswith(".png"):
                    mime_type = "image/png"
                elif filename.lower().endswith((".jpg", ".jpeg")):
                    mime_type = "image/jpeg"

                # Create a Part object with the image
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
                content_parts.append(image_part)

                logger.info(f"Added page {i}: {filename} ({mime_type})")

            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                raise ExtractionException(f"Failed to process image {filename}: {e}") from e

        return content_parts

    async def _validate_within_workflow(self, result: dict | list) -> None:
        """
        Validate extracted data within the workflow span context.

        This method is called BEFORE the workflow returns, ensuring that
        LLMObs.export_span() can find the active workflow context for
        submitting custom evaluations.

        Args:
            result: Raw extraction result (dict or list of dicts)
        """
        # Import here to avoid circular dependency
        from app.models.vote_extraction import ElectionFormData

        # Normalize result to list
        results_to_validate = [result] if isinstance(result, dict) else result

        # Validate each form
        for idx, report_data in enumerate(results_to_validate):
            if not isinstance(report_data, dict):
                logger.warning(f"Skipping non-dict element at index {idx} during validation")
                continue

            try:
                # Parse into Pydantic model
                extracted_data = ElectionFormData(**report_data)

                # Validate and submit custom evaluation
                # Pass form_index to make evaluation labels unique per form
                is_valid, error_msg = await self.validate_extraction(
                    data=extracted_data, form_index=idx
                )

                if is_valid:
                    logger.info(f"✅ Form {idx + 1}/{len(results_to_validate)} passed validation")
                else:
                    logger.warning(
                        f"⚠️ Form {idx + 1}/{len(results_to_validate)} validation warning: {error_msg}"
                    )

            except Exception as e:
                logger.error(
                    f"❌ Failed to validate form {idx + 1}/{len(results_to_validate)}: {e}",
                    exc_info=True,
                )
                # Continue with other forms even if one fails
                continue

    def _annotate_extraction_success(
        self,
        result: dict,
        response_text: str,
        image_files: list,
        image_filenames: list,
        llm_config: LLMConfig,
        prompt_text: str,
        schema_version: str,
        schema_hash: str,
        prompt_metadata: dict,
    ) -> None:
        """Annotate workflow span with successful extraction context."""
        if not self._llmobs_enabled or not DDTRACE_AVAILABLE:
            return

        # Calculate token counts (approximate for multimodal)
        approx_input_tokens = len(image_files) * 258 + 100
        approx_output_tokens = len(response_text) // 4

        # Count extracted forms
        num_forms = len(result) if isinstance(result, list) else 1

        LLMObs.annotate(
            input_data={
                "images_count": len(image_files),
                "filenames": image_filenames,
                "prompt_template": prompt_text.strip()[:200] + "...",
                "schema_version": schema_version,
                "schema_hash": schema_hash,
            },
            output_data={
                "forms_extracted": num_forms,
                "result_type": type(result).__name__,
                "result_keys": (
                    list(result[0].keys()) if isinstance(result, list) and result else []
                ),
            },
            metadata={
                "model": llm_config.model,
                "provider": llm_config.provider,
                "temperature": llm_config.temperature,
                "max_tokens": llm_config.max_tokens,
                "top_p": llm_config.top_p,
                "top_k": llm_config.top_k,
                "response_mime_type": "application/json",
                "prompt_id": prompt_metadata["id"],
                "prompt_version": prompt_metadata.get(
                    "version", "auto"
                ),  # Auto-versioned by Datadog
                "schema_version": schema_version,
            },
            metrics={
                "input_tokens": approx_input_tokens,
                "output_tokens": approx_output_tokens,
                "total_tokens": approx_input_tokens + approx_output_tokens,
                "pages_processed": len(image_files),
                "forms_extracted": num_forms,
                "response_length": len(response_text),
            },
            tags={
                "feature": "vote-extraction",
                "document_type": "thai-election-form",
                "form_standard": "Form S.S. 5/18",
                "language": "thai",
                "model": llm_config.model,
                "provider": llm_config.provider,
                "schema_version": schema_version,
                "multimodal": "true",
                "extraction_success": "true",
            },
        )

    def _build_prompt_and_metadata(self) -> tuple[str, str, str, dict]:
        """
        Build extraction prompt and metadata for LLMObs tracking.

        Returns:
            Tuple of (prompt_text, schema_version, schema_hash, prompt_metadata)
        """
        prompt_text = """
        You are an expert data entry assistant for Thai Election documents (Form S.S. 5/18).

        Instructions:
        1. Analyze the sequence of images labeled Page 1, Page 2, etc. provided above. These pages belong to the SAME single report.
        2. Extract information strictly according to the JSON schema provided.
        3. Consolidate data from all pages.
           - The header information (District, Date) is usually on Page 1.
           - The 'Vote Results' table often spans across multiple pages. Merge them into a single list.
        4. Validation: Ensure the 'total ballots used' matches the sum of 'good', 'bad', and 'no vote' ballots.
        5. Form Type: Detect if this is a 'Constituency' form (candidates with names) or 'PartyList' form (party names only).
        """

        # Schema version for tracking
        schema_version = "1.0.0"
        schema_hash = str(hash(json.dumps(ELECTION_DATA_SCHEMA, sort_keys=True)))[:8]

        # Prompt metadata for Datadog LLMObs tracking
        prompt_metadata = {
            "id": "thai-election-form-extraction",
            "template": prompt_text.strip(),
            "variables": {
                "model": "gemini-2.5-flash",
                "schema_version": schema_version,
                "schema_hash": schema_hash,
                "form_type": "Form S.S. 5/18",
                "temperature": 0.0,
                "response_format": "application/json",
            },
            "tags": {
                "feature": "vote-extraction",
                "document_type": "thai-election-form",
                "schema_version": schema_version,
                "model": "gemini-2.5-flash",
                "language": "thai",
            },
        }

        return prompt_text, schema_version, schema_hash, prompt_metadata

    def _call_gemini_api(
        self,
        client: Any,
        content_parts: list,
        llm_config: "LLMConfig",
        prompt_metadata: dict,
    ) -> Any:
        """
        Call Gemini API with prompt tracking.

        Args:
            client: Gemini client
            content_parts: Content parts (images + prompt)
            llm_config: LLM configuration
            prompt_metadata: Prompt metadata for tracking

        Returns:
            Gemini API response
        """
        generation_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ELECTION_DATA_SCHEMA,
            temperature=llm_config.temperature,
            max_output_tokens=llm_config.max_tokens,
            top_p=llm_config.top_p,
            top_k=llm_config.top_k,
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,
            ),
        )

        # Attach prompt metadata to the LLM span if LLMObs is enabled
        if self._llmobs_enabled and DDTRACE_AVAILABLE:
            with LLMObs.annotation_context(prompt=prompt_metadata):
                return client.models.generate_content(
                    model=llm_config.model,
                    contents=content_parts,
                    config=generation_config,
                )
        else:
            # Call without prompt tracking if LLMObs not available
            return client.models.generate_content(
                model=llm_config.model,
                contents=content_parts,
                config=generation_config,
            )

    def _capture_workflow_span_context(self) -> None:
        """Capture workflow span context for user feedback submission."""
        if self._llmobs_enabled and DDTRACE_AVAILABLE:
            try:
                self._last_workflow_span_context = LLMObs.export_span(span=None)
                if self._last_workflow_span_context:
                    logger.debug(
                        f"📊 Captured workflow span context: "
                        f"span_id={self._last_workflow_span_context.get('span_id')}, "
                        f"trace_id={self._last_workflow_span_context.get('trace_id')}"
                    )
            except Exception as e:
                logger.warning(f"Failed to capture workflow span context: {e}")
                self._last_workflow_span_context = None

    def _handle_extraction_error(self, error: Exception, error_type: str) -> None:
        """
        Handle extraction errors with LLMObs annotation.

        Args:
            error: The exception that occurred
            error_type: Type of error for classification
        """
        if self._llmobs_enabled and DDTRACE_AVAILABLE:
            LLMObs.annotate(
                output_data={"error": error_type, "error_details": str(error)},
                tags={
                    "extraction_success": "false",
                    "error_type": error_type,
                },
            )

    @workflow
    async def extract_from_images(
        self,
        image_files: list[bytes],
        image_filenames: list[str],
        llm_config: Optional["LLMConfig"] = None,
    ) -> dict[str, Any] | None:
        """
        Extract vote data from multiple document pages using Gemini.

        This is a workflow span that orchestrates the complete vote extraction process.

        Args:
            image_files: List of image bytes
            image_filenames: List of filenames for reference
            llm_config: Optional LLM configuration (provider, model, parameters)

        Returns:
            Extracted data as dictionary, or None if extraction fails
        """
        # Set up LLM configuration
        if llm_config is None:
            llm_config = LLMConfig()

        if llm_config.provider != "vertex_ai":
            logger.warning(f"Provider {llm_config.provider} not yet supported, using vertex_ai")
            llm_config.provider = "vertex_ai"

        logger.info(
            f"Extracting with LLM config: provider={llm_config.provider}, "
            f"model={llm_config.model}, temp={llm_config.temperature}"
        )

        client = self._get_client()

        # Process images into content parts
        try:
            content_parts = self._process_images_to_content_parts(image_files, image_filenames)
        except ExtractionException:
            return None

        # Build prompt and metadata
        prompt_text, schema_version, schema_hash, prompt_metadata = (
            self._build_prompt_and_metadata()
        )
        content_parts.append(prompt_text)

        # Send request to Gemini
        try:
            logger.info(f"Sending {len(image_files)} pages to Gemini for extraction...")

            response = self._call_gemini_api(client, content_parts, llm_config, prompt_metadata)
            result = json.loads(response.text)

            logger.debug(
                "LLM Response received",
                extra={
                    "response_text": response.text,
                    "response_length": len(response.text),
                    "pages_processed": len(image_files),
                },
            )

            logger.info(
                "Successfully extracted vote data from images",
                extra={
                    "pages_processed": len(image_files),
                    "prompt_id": prompt_metadata["id"],
                    "prompt_version": prompt_metadata.get("version", "auto"),
                    "result_type": type(result).__name__,
                    "result_keys": list(result.keys()) if isinstance(result, dict) else "list",
                },
            )

            # Annotate workflow span with comprehensive context
            self._annotate_extraction_success(
                result,
                response.text,
                image_files,
                image_filenames,
                llm_config,
                prompt_text,
                schema_version,
                schema_hash,
                prompt_metadata,
            )

            # Validate extracted data within workflow span
            await self._validate_within_workflow(result)

            # Capture workflow span context for user feedback
            self._capture_workflow_span_context()

            return result

        except ExtractionException:
            self._handle_extraction_error(ExtractionException(), "ExtractionException")
            raise
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"Invalid response format from Gemini: {e}")
            self._handle_extraction_error(e, "ParseError")
            raise ExtractionException(f"Invalid extraction response: {e}") from e
        except Exception as e:
            logger.critical(f"Unexpected error calling Gemini: {e}", exc_info=True)
            self._handle_extraction_error(e, type(e).__name__)
            raise ExtractionException(f"Extraction failed: {e}") from e

    def _submit_validation_evaluation(
        self,
        is_valid: bool,
        check_type: str,
        error_msg: str | None,
        validation_checks: list,
        data: ElectionFormData,
        form_index: int = 0,
    ) -> None:
        """
        Submit validation result as a Datadog LLMObs Custom Evaluation.

        Uses LLMObs.export_span() to get the current span context and attach
        the evaluation to it, following Datadog's official SDK pattern.

        Args:
            is_valid: Whether validation passed
            check_type: Type of validation check (ballot_statistics, vote_counts, etc.)
            error_msg: Error message if validation failed
            validation_checks: List of all validation checks performed
            data: Extracted election form data
            form_index: Index of the form being validated (for unique labels)
        """
        if not self._llmobs_enabled or not DDTRACE_AVAILABLE:
            return

        try:
            # Export current span context using official SDK method
            # https://docs.datadoghq.com/llm_observability/evaluations/external_evaluations#submitting-external-evaluations-with-the-sdk
            span_context = LLMObs.export_span(span=None)

            if not span_context:
                logger.warning("Cannot submit validation evaluation: no active span context")
                return

            # Debug: Log the span context to verify it's correct
            logger.debug(
                f"📊 Span context for evaluation: span_id={span_context.get('span_id')}, "
                f"trace_id={span_context.get('trace_id')}, type={type(span_context)}"
            )

            # Prepare tags with context (include form_index for traceability)
            tags = {
                "feature": "vote-extraction",
                "validation_check": check_type,
                "form_type": data.form_info.form_type if data.form_info else "unknown",
                "form_index": str(form_index),
                "vote_results_count": str(len(data.vote_results) if data.vote_results else 0),
                "has_ballot_statistics": str(data.ballot_statistics is not None),
            }

            # Make labels unique per form to avoid duplicates when multiple forms are extracted
            label_suffix = f"_form_{form_index}"

            # Submit overall validation result as categorical (pass/fail)
            # Note: SDK only supports "score" and "categorical" metric types
            # https://docs.datadoghq.com/llm_observability/evaluations/external_evaluations#submitting-external-evaluations-with-the-sdk
            LLMObs.submit_evaluation(
                span=span_context,
                ml_app="vote-extractor",
                label=f"validation_passed{label_suffix}",
                metric_type="categorical",
                value="pass" if is_valid else "fail",
                tags=tags,
                assessment="pass" if is_valid else "fail",
                reasoning=error_msg if error_msg else "All validation checks passed",
            )

            # Submit validation check type as categorical
            LLMObs.submit_evaluation(
                span=span_context,
                ml_app="vote-extractor",
                label=f"validation_check_type{label_suffix}",
                metric_type="categorical",
                value=check_type,
                tags=tags,
                assessment="pass" if is_valid else "fail",
                reasoning=error_msg if error_msg else f"Validated {check_type} successfully",
            )

            # Submit validation score (checks passed / total checks)
            checks_passed = len([c for c in validation_checks if c.get("passed", False)])
            total_checks = len(validation_checks)
            validation_score = checks_passed / total_checks if total_checks > 0 else 1.0

            LLMObs.submit_evaluation(
                span=span_context,
                ml_app="vote-extractor",
                label=f"validation_score{label_suffix}",
                metric_type="score",
                value=validation_score,
                tags=tags,
                assessment="pass" if is_valid else "fail",
                reasoning=f"Passed {checks_passed}/{total_checks} validation checks",
            )

            logger.info(
                f"✅ Submitted validation evaluation: {check_type} for form {form_index} "
                f"(passed={is_valid}, score={validation_score:.2f})"
            )

        except Exception as e:
            logger.error(f"❌ Failed to submit validation evaluation: {e}", exc_info=True)

    def _validate_ballot_statistics(
        self, stats, validation_checks: list
    ) -> tuple[bool, str | None]:
        """Validate ballot statistics consistency."""
        if not all(
            [stats.ballots_used, stats.good_ballots, stats.bad_ballots, stats.no_vote_ballots]
        ):
            validation_checks.append(
                {"check": "ballot_statistics", "passed": True, "note": "Incomplete data"}
            )
            return True, None

        expected_total = stats.good_ballots + stats.bad_ballots + stats.no_vote_ballots
        if stats.ballots_used != expected_total:
            error_msg = (
                f"Ballot mismatch: ballots_used ({stats.ballots_used}) != "
                f"sum of good+bad+no_vote ({expected_total})"
            )
            validation_checks.append(
                {"check": "ballot_statistics", "passed": False, "error": error_msg}
            )
            return False, error_msg

        validation_checks.append({"check": "ballot_statistics", "passed": True})
        return True, None

    async def validate_extraction(
        self,
        data: ElectionFormData,
        form_index: int = 0,
    ) -> tuple[bool, str | None]:
        """
        Validate extracted vote data for consistency and submit as Custom Evaluation.

        This validation is called after the extraction workflow completes,
        and submits validation results as Datadog LLMObs Custom Evaluations.

        Uses LLMObs.export_span() to automatically get the current span context
        and attach evaluations to it, following Datadog's official SDK pattern.

        Args:
            data: Extracted election form data
            form_index: Index of the form being validated (for unique evaluation labels)

        Returns:
            Tuple of (is_valid, error_message)
        """
        validation_checks = []

        # Validate ballot statistics if present
        if data.ballot_statistics:
            is_valid, error_msg = self._validate_ballot_statistics(
                data.ballot_statistics, validation_checks
            )
            if not is_valid:
                self._submit_validation_evaluation(
                    is_valid=False,
                    check_type="ballot_statistics",
                    error_msg=error_msg,
                    validation_checks=validation_checks,
                    data=data,
                    form_index=form_index,
                )
                return False, error_msg

        # Validate vote results
        if not data.vote_results:
            error_msg = "No vote results extracted"
            validation_checks.append({"check": "vote_results", "passed": False, "error": error_msg})
            self._submit_validation_evaluation(
                is_valid=False,
                check_type="vote_results",
                error_msg=error_msg,
                validation_checks=validation_checks,
                data=data,
                form_index=form_index,
            )
            return False, error_msg

        # Check that all vote counts are non-negative
        for result in data.vote_results:
            if result.vote_count < 0:
                name = result.candidate_name or result.party_name or "Unknown"
                error_msg = f"Negative vote count for {name}"
                validation_checks.append(
                    {"check": "vote_counts", "passed": False, "error": error_msg, "candidate": name}
                )
                self._submit_validation_evaluation(
                    is_valid=False,
                    check_type="vote_counts",
                    error_msg=error_msg,
                    validation_checks=validation_checks,
                    data=data,
                    form_index=form_index,
                )
                return False, error_msg

        validation_checks.append({"check": "vote_counts", "passed": True})

        # All validations passed - submit success evaluation
        self._submit_validation_evaluation(
            is_valid=True,
            check_type="all_checks",
            error_msg=None,
            validation_checks=validation_checks,
            data=data,
            form_index=form_index,
        )

        return True, None


# Global service instance
vote_extraction_service = VoteExtractionService()
