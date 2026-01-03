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
    from ddtrace.llmobs.decorators import task, workflow

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
        self._initialize_llmobs()

    def _initialize_llmobs(self) -> None:
        """Initialize Datadog LLM Observability if available."""
        if not DDTRACE_AVAILABLE:
            return

        # Check if required env vars are set
        ml_app = os.getenv("DD_LLMOBS_ML_APP")
        api_key = os.getenv("DD_API_KEY")
        service = os.getenv("DD_SERVICE", "vote-extraction-service")

        if ml_app and api_key:
            try:
                LLMObs.enable(
                    ml_app=ml_app,
                    api_key=api_key,
                    service=service,
                    agentless_enabled=True,
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
                "prompt_version": prompt_metadata["version"],
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
        # Set up LLM configuration (use provided config or defaults)
        if llm_config is None:
            llm_config = LLMConfig()  # Use defaults

        # For now, only Vertex AI is supported
        if llm_config.provider != "vertex_ai":
            logger.warning(f"Provider {llm_config.provider} not yet supported, using vertex_ai")
            llm_config.provider = "vertex_ai"

        logger.info(
            f"Extracting with LLM config: provider={llm_config.provider}, "
            f"model={llm_config.model}, temp={llm_config.temperature}"
        )

        client = self._get_client()

        # A. Process Images into content parts
        try:
            content_parts = self._process_images_to_content_parts(image_files, image_filenames)
        except ExtractionException:
            return None

        # B. Main Text Prompt (Placed AFTER all images)
        # Note: This is a template for prompt tracking
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
        6. Schema Version: {{schema_version}}
        """
        content_parts.append(prompt_text)

        # C. Send Request to Gemini with Prompt Tracking
        try:
            logger.info(f"Sending {len(image_files)} pages to Gemini for extraction...")

            # Schema version for tracking (increment when schema changes)
            schema_version = "1.0.0"
            schema_hash = str(hash(json.dumps(ELECTION_DATA_SCHEMA, sort_keys=True)))[:8]

            # Prompt metadata for Datadog LLMObs tracking
            prompt_metadata = {
                "id": "thai-election-form-extraction",
                # Auto Versioning, by omitting the version field
                # "version": f"v{schema_version}",
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

            # Prepare generation config
            generation_config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ELECTION_DATA_SCHEMA,
                temperature=llm_config.temperature,
                max_output_tokens=llm_config.max_tokens,
                top_p=llm_config.top_p,
                top_k=llm_config.top_k,
            )

            # Attach prompt metadata to the LLM span if LLMObs is enabled
            if self._llmobs_enabled and DDTRACE_AVAILABLE:
                with LLMObs.annotation_context(prompt=prompt_metadata):
                    response = client.models.generate_content(
                        model=llm_config.model,
                        contents=content_parts,
                        config=generation_config,
                    )
            else:
                # Call without prompt tracking if LLMObs not available
                response = client.models.generate_content(
                    model=llm_config.model,
                    contents=content_parts,
                    config=generation_config,
                )

            result = json.loads(response.text)

            # Debug log: Write full LLM response
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
                    "prompt_version": prompt_metadata["version"],
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

            return result

        except ExtractionException:
            # Annotate workflow span with error context
            if self._llmobs_enabled and DDTRACE_AVAILABLE:
                LLMObs.annotate(
                    tags={
                        "extraction_success": "false",
                        "error_type": "ExtractionException",
                    },
                )
            # Re-raise extraction exceptions
            raise
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"Invalid response format from Gemini: {e}")
            # Annotate workflow span with parse error context
            if self._llmobs_enabled and DDTRACE_AVAILABLE:
                LLMObs.annotate(
                    output_data={"error": "Invalid JSON response", "error_details": str(e)},
                    tags={
                        "extraction_success": "false",
                        "error_type": "ParseError",
                    },
                )
            raise ExtractionException(f"Invalid extraction response: {e}") from e
        except Exception as e:
            logger.critical(f"Unexpected error calling Gemini: {e}", exc_info=True)
            # Annotate workflow span with unexpected error context
            if self._llmobs_enabled and DDTRACE_AVAILABLE:
                LLMObs.annotate(
                    output_data={"error": "Unexpected error", "error_details": str(e)},
                    tags={
                        "extraction_success": "false",
                        "error_type": type(e).__name__,
                    },
                )
            raise ExtractionException(f"Extraction failed: {e}") from e

    def _annotate_validation_failure(
        self, check_type: str, error_msg: str, input_data: dict, validation_checks: list
    ) -> None:
        """Helper to annotate validation failures."""
        if not self._llmobs_enabled or not DDTRACE_AVAILABLE:
            return

        LLMObs.annotate(
            input_data=input_data,
            output_data={
                "is_valid": False,
                "error": error_msg,
                "validation_checks": validation_checks,
            },
            tags={
                "validation_result": "failed",
                "check_type": check_type,
                "feature": "vote-extraction",
            },
        )

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
            self._annotate_validation_failure(
                "ballot_statistics",
                error_msg,
                {
                    "ballots_used": stats.ballots_used,
                    "good_ballots": stats.good_ballots,
                    "bad_ballots": stats.bad_ballots,
                    "no_vote_ballots": stats.no_vote_ballots,
                },
                validation_checks,
            )
            return False, error_msg

        validation_checks.append({"check": "ballot_statistics", "passed": True})
        return True, None

    @task
    async def validate_extraction(
        self,
        data: ElectionFormData,
    ) -> tuple[bool, str | None]:
        """
        Validate extracted vote data for consistency.

        This is a task span that performs standalone data validation.

        Args:
            data: Extracted election form data

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
                return False, error_msg

        # Validate vote results
        if not data.vote_results:
            error_msg = "No vote results extracted"
            validation_checks.append({"check": "vote_results", "passed": False, "error": error_msg})
            self._annotate_validation_failure(
                "vote_results", error_msg, {"has_vote_results": False}, validation_checks
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
                self._annotate_validation_failure(
                    "vote_counts",
                    error_msg,
                    {
                        "candidate_name": result.candidate_name,
                        "party_name": result.party_name,
                        "vote_count": result.vote_count,
                    },
                    validation_checks,
                )
                return False, error_msg

        validation_checks.append({"check": "vote_counts", "passed": True})

        # All validations passed - annotate success
        if self._llmobs_enabled and DDTRACE_AVAILABLE:
            LLMObs.annotate(
                input_data={
                    "form_info": {
                        "form_type": data.form_info.form_type if data.form_info else None,
                        "province": data.form_info.province if data.form_info else None,
                    },
                    "vote_results_count": len(data.vote_results) if data.vote_results else 0,
                    "has_ballot_statistics": data.ballot_statistics is not None,
                },
                output_data={
                    "is_valid": True,
                    "validation_checks": validation_checks,
                    "checks_passed": len([c for c in validation_checks if c["passed"]]),
                    "total_checks": len(validation_checks),
                },
                metrics={
                    "vote_results_count": len(data.vote_results) if data.vote_results else 0,
                    "checks_passed": len([c for c in validation_checks if c["passed"]]),
                    "total_checks": len(validation_checks),
                },
                tags={
                    "validation_result": "passed",
                    "feature": "vote-extraction",
                    "form_type": data.form_info.form_type if data.form_info else "unknown",
                },
            )

        return True, None


# Global service instance
vote_extraction_service = VoteExtractionService()
