"""Vote extraction service using Google GenAI."""

import logging
import json
import asyncio
from typing import List, Optional, Dict, Any
import os

from google import genai
from google.genai import types

from app.config import settings
from app.models.vote_extraction import ElectionFormData
from app.core.exceptions import ExtractionException, ValidationException
from app.core.constants import GEMINI_API_TIMEOUT, SCHEMA_HASH_LENGTH

# Datadog LLM Observability
try:
    from ddtrace.llmobs import LLMObs
    DDTRACE_AVAILABLE = True
except ImportError:
    DDTRACE_AVAILABLE = False
    logger.warning("ddtrace not available - LLM observability will be disabled")

logger = logging.getLogger(__name__)


# Election form schema defined as an ARRAY to handle multiple forms (Constituency + PartyList) in one response
ELECTION_DATA_SCHEMA = {
    "type": "ARRAY",
    "description": "A list of election reports found in the input images (usually one Constituency report and one PartyList report).",
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
                        "description": "Identify if this specific report is for Constituency (Candidate) or PartyList (Party only). Check the header text (e.g., 'แบบบัญชีรายชื่อ' = PartyList)."
                    },
                    "date": {"type": "STRING", "description": "Date of election"},
                    "province": {"type": "STRING", "description": "Province name"},
                    "district": {"type": "STRING", "description": "District name (Amphoe/Khet)"},
                    "sub_district": {"type": "STRING", "description": "Sub-district name (Tambon/Khwaeng)"},
                    "constituency_number": {"type": "STRING", "description": "Constituency number"},
                    "polling_station_number": {"type": "STRING", "description": "Unit number"}
                },
                "required": ["form_type", "province", "district", "polling_station_number"]
            },
            "voter_statistics": {
                "type": "OBJECT",
                "description": "Section 1: Voter statistics for this specific form.",
                "properties": {
                    "eligible_voters": {"type": "INTEGER", "description": "Item 1.1: Total eligible voters"},
                    "voters_present": {"type": "INTEGER", "description": "Item 1.2: Total voters present"}
                }
            },
            "ballot_statistics": {
                "type": "OBJECT",
                "description": "Section 2: Ballot accounting for this specific form.",
                "properties": {
                    "ballots_allocated": {"type": "INTEGER", "description": "Item 2.1: Total allocated ballots"},
                    "ballots_used": {"type": "INTEGER", "description": "Item 2.2: Total used ballots"},
                    "good_ballots": {"type": "INTEGER", "description": "Item 2.2.1: Good ballots"},
                    "bad_ballots": {"type": "INTEGER", "description": "Item 2.2.2: Bad ballots"},
                    "no_vote_ballots": {"type": "INTEGER", "description": "Item 2.2.3: No Vote ballots"},
                    "ballots_remaining": {"type": "INTEGER", "description": "Item 2.3: Remaining ballots"}
                }
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
                            "description": "Name of Candidate (for Constituency). Leave null for PartyList."
                        },
                        "party_name": {"type": "STRING"},
                        "vote_count": {"type": "INTEGER"},
                        "vote_count_text": {"type": "STRING"}
                    }
                }
            }
        },
        "required": ["form_info", "ballot_statistics", "vote_results"]
    }
}


class VoteExtractionService:
    """Service for extracting vote data from election form images."""

    def __init__(self):
        """Initialize the vote extraction service."""
        self._client: Optional[genai.Client] = None
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

    async def extract_from_images(
        self,
        image_files: List[bytes],
        image_filenames: List[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Extract vote data from multiple document pages using Gemini.

        Args:
            image_files: List of image bytes
            image_filenames: List of filenames for reference

        Returns:
            Extracted data as dictionary, or None if extraction fails
        """
        client = self._get_client()
        
        # List to hold all content parts (Text labels + Image bytes)
        content_parts = []

        # A. Process Images (Loop through files)
        for i, (image_bytes, filename) in enumerate(zip(image_files, image_filenames), 1):
            try:
                # 1. Add an Index Label BEFORE the image
                index_label = f"Page {i} (Filename: {filename})"
                content_parts.append(index_label)

                # 2. Determine MIME type from filename
                mime_type = "image/jpeg"
                if filename.lower().endswith(".png"):
                    mime_type = "image/png"
                elif filename.lower().endswith((".jpg", ".jpeg")):
                    mime_type = "image/jpeg"

                # 3. Create a Part object with the image
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
                content_parts.append(image_part)

                logger.info(f"Added page {i}: {filename} ({mime_type})")

            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
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
                "version": f"v{schema_version}-schema{schema_hash}",
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
            
            # Attach prompt metadata to the LLM span if LLMObs is enabled
            if self._llmobs_enabled and DDTRACE_AVAILABLE:
                with LLMObs.annotation_context(prompt=prompt_metadata):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=content_parts,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ELECTION_DATA_SCHEMA,
                            temperature=0.0,  # Low temperature for factual extraction
                        ),
                    )
            else:
                # Call without prompt tracking if LLMObs not available
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=content_parts,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ELECTION_DATA_SCHEMA,
                        temperature=0.0,  # Low temperature for factual extraction
                    ),
                )

            result = json.loads(response.text)
            
            # Debug log: Write full LLM response
            logger.debug(
                "LLM Response received",
                extra={
                    "response_text": response.text,
                    "response_length": len(response.text),
                    "pages_processed": len(image_files),
                }
            )
            
            logger.info(
                "Successfully extracted vote data from images",
                extra={
                    "pages_processed": len(image_files),
                    "prompt_id": prompt_metadata["id"],
                    "prompt_version": prompt_metadata["version"],
                    "result_type": type(result).__name__,
                    "result_keys": list(result.keys()) if isinstance(result, dict) else "list",
                }
            )
            return result

        except ExtractionException:
            # Re-raise extraction exceptions
            raise
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"Invalid response format from Gemini: {e}")
            raise ExtractionException(f"Invalid extraction response: {e}") from e
        except Exception as e:
            logger.critical(f"Unexpected error calling Gemini: {e}", exc_info=True)
            raise ExtractionException(f"Extraction failed: {e}") from e

    async def validate_extraction(
        self,
        data: ElectionFormData,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate extracted vote data for consistency.

        Args:
            data: Extracted election form data

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate ballot statistics if present
        if data.ballot_statistics:
            stats = data.ballot_statistics
            if all([stats.ballots_used, stats.good_ballots, stats.bad_ballots, stats.no_vote_ballots]):
                expected_total = (
                    stats.good_ballots + stats.bad_ballots + stats.no_vote_ballots
                )
                if stats.ballots_used != expected_total:
                    return False, (
                        f"Ballot mismatch: ballots_used ({stats.ballots_used}) != "
                        f"sum of good+bad+no_vote ({expected_total})"
                    )

        # Validate vote results
        if not data.vote_results:
            return False, "No vote results extracted"

        # Check that all vote counts are non-negative
        for result in data.vote_results:
            if result.vote_count < 0:
                name = result.candidate_name or result.party_name or "Unknown"
                return False, f"Negative vote count for {name}"

        return True, None


# Global service instance
vote_extraction_service = VoteExtractionService()

