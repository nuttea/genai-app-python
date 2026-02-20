"""Gemini-based extraction from Google Drive PDFs."""

import json

import streamlit as st
from google import genai
from google.genai import types

# Gemini structured output schema for election form data
ELECTION_DATA_SCHEMA = {
    "type": "ARRAY",
    "description": "List of election reports found in the PDF",
    "items": {
        "type": "OBJECT",
        "properties": {
            "form_info": {
                "type": "OBJECT",
                "description": "Header information",
                "properties": {
                    "form_type": {
                        "type": "STRING",
                        "enum": ["Constituency", "PartyList"],
                        "description": "Form type: Constituency or PartyList",
                    },
                    "set_number": {
                        "type": "STRING",
                        "description": "Set number (ชุดที่)",
                    },
                    "date": {"type": "STRING", "description": "Date of election"},
                    "province": {"type": "STRING", "description": "Province name"},
                    "constituency_number": {
                        "type": "STRING",
                        "description": "Constituency number",
                    },
                    "district": {"type": "STRING", "description": "District name"},
                    "sub_district": {
                        "type": "STRING",
                        "description": "Sub-district name",
                    },
                    "polling_station_number": {
                        "type": "STRING",
                        "description": "Polling station number",
                    },
                    "village_moo": {
                        "type": "STRING",
                        "description": "Village number (หมู่ที่)",
                    },
                },
                "required": [
                    "form_type",
                    "province",
                    "district",
                    "polling_station_number",
                ],
            },
            "voter_statistics": {
                "type": "OBJECT",
                "description": "Section 1: Voter statistics",
                "properties": {
                    "eligible_voters": {
                        "type": "OBJECT",
                        "description": "1.1 Total eligible voters",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                    },
                    "present_voters": {
                        "type": "OBJECT",
                        "description": "1.2 Voters who showed up",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                    },
                },
            },
            "ballot_statistics": {
                "type": "OBJECT",
                "description": "Section 2: Ballot accounting",
                "properties": {
                    "ballots_allocated": {
                        "type": "OBJECT",
                        "description": "2.1 Allocated ballots",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                    },
                    "ballots_used": {
                        "type": "OBJECT",
                        "description": "2.2 Used ballots",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                        "required": ["arabic"],
                    },
                    "good_ballots": {
                        "type": "OBJECT",
                        "description": "2.2.1 Valid ballots",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                        "required": ["arabic"],
                    },
                    "bad_ballots": {
                        "type": "OBJECT",
                        "description": "2.2.2 Invalid ballots",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                        "required": ["arabic"],
                    },
                    "no_vote_ballots": {
                        "type": "OBJECT",
                        "description": "2.2.3 No vote ballots",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                        "required": ["arabic"],
                    },
                    "ballots_remaining": {
                        "type": "OBJECT",
                        "description": "2.3 Remaining ballots",
                        "properties": {
                            "arabic": {"type": "INTEGER"},
                            "thai_text": {"type": "STRING"},
                        },
                    },
                },
            },
            "vote_results": {
                "type": "ARRAY",
                "description": "Section 3: Vote counts for all candidates/parties",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "number": {
                            "type": "INTEGER",
                            "description": "Candidate/Party number",
                        },
                        "candidate_name": {
                            "type": "STRING",
                            "description": "Candidate name (Constituency only)",
                        },
                        "party_name": {
                            "type": "STRING",
                            "description": "Party name",
                        },
                        "vote_count": {
                            "type": "OBJECT",
                            "description": "Vote count (number and Thai text)",
                            "properties": {
                                "arabic": {"type": "INTEGER"},
                                "thai_text": {"type": "STRING"},
                            },
                            "required": ["arabic"],
                        },
                    },
                    "required": ["number", "vote_count"],
                },
            },
            "total_votes_recorded": {
                "type": "OBJECT",
                "description": "Total vote count from bottom of table",
                "properties": {
                    "arabic": {"type": "INTEGER"},
                    "thai_text": {"type": "STRING"},
                },
            },
            "officials": {
                "type": "ARRAY",
                "description": "Committee members who signed the form",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING", "description": "Full name"},
                        "position": {
                            "type": "STRING",
                            "description": "Position (ประธาน, กรรมการ, etc.)",
                        },
                    },
                    "required": ["name", "position"],
                },
            },
        },
        "required": ["form_info", "vote_results"],
    },
}

EXTRACTION_PROMPT = """
You are an expert data entry assistant for Thai Election documents (Form S.S. 5/18).

CRITICAL INSTRUCTIONS:

1. **Analyze all pages** of this PDF document carefully.

2. **Extract BOTH number formats** for all numerical values:
   - Arabic numerals (e.g., 120)
   - Thai text (e.g., "หนึ่งร้อยยี่สิบ")
   This applies to: voter statistics, ballot statistics, vote counts, and total votes.

3. **Header Information** (usually on first page):
   - Form type: "Constituency" (แบบแบ่งเขต) or "PartyList" (บัญชีรายชื่อ)
   - Set number (ชุดที่) if present
   - Date, Province, District, Sub-district
   - Polling station number (หน่วยเลือกตั้งที่)
   - Village number (หมู่ที่) if present

4. **Section 1 - Voter Statistics:**
   - 1.1 Eligible voters (ผู้มีสิทธิเลือกตั้งตามบัญชี)
   - 1.2 Present voters (ผู้มาแสดงตน)
   Extract both arabic and thai_text for each.

5. **Section 2 - Ballot Statistics:**
   - 2.1 Allocated ballots (บัตรที่ได้รับจัดสรร)
   - 2.2 Used ballots (บัตรที่ใช้)
   - 2.2.1 Valid ballots (บัตรดี)
   - 2.2.2 Invalid ballots (บัตรเสีย)
   - 2.2.3 No vote ballots (ไม่เลือก)
   - 2.3 Remaining ballots (บัตรเหลือ)
   Extract both arabic and thai_text for each.

6. **Section 3 - Vote Results Table:**
   - Consolidate all pages (table often spans multiple pages)
   - For each entry: number, candidate name (if Constituency), party name, vote count
   - Extract vote_count as {arabic: int, thai_text: str}

7. **Total Votes Recorded:**
   - Look for "รวม" (total) at the bottom of the vote results table
   - Extract both arabic and thai_text

8. **Officials (Committee Members):**
   - Extract names and positions from signature section
   - Common positions: ประธาน (Chair), กรรมการ (Member), เลขานุการ (Secretary)

9. **Validation:**
   - ballots_used.arabic = good_ballots.arabic + bad_ballots.arabic + no_vote_ballots.arabic
   - total_votes_recorded.arabic = sum of all vote_count.arabic
"""

# Available model options
MODEL_OPTIONS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite-preview-06-17",
    "gemini-3-flash-preview",
    "gemini-2.5-pro-preview-06-05",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


@st.cache_resource
def get_gemini_client(api_key: str) -> genai.Client:
    """Get cached Gemini client instance."""
    return genai.Client(api_key=api_key, vertexai=False)


def build_drive_uri(file_id: str) -> str:
    """Construct Google Drive download URI from file ID."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def build_drive_preview_url(file_id: str) -> str:
    """Construct Google Drive preview URL for iframe embedding."""
    return f"https://drive.google.com/file/d/{file_id}/preview"


def extract_from_drive(
    api_key: str,
    file_id: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
) -> tuple[list[dict], dict]:
    """
    Extract vote data from a Google Drive PDF using Gemini.

    Args:
        api_key: Gemini API key
        file_id: Google Drive file ID
        model: Gemini model name
        temperature: Sampling temperature
        max_tokens: Maximum output tokens

    Returns:
        Tuple of (extracted_data_list, usage_metadata_dict)

    Raises:
        ValueError: If API key is missing
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    client = get_gemini_client(api_key)
    drive_uri = build_drive_uri(file_id)

    file_part = types.Part.from_uri(file_uri=drive_uri, mime_type="application/pdf")

    generation_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ELECTION_DATA_SCHEMA,
        temperature=temperature,
        max_output_tokens=max_tokens,
        top_p=0.95,
        top_k=40,
    )

    response = client.models.generate_content(
        model=model,
        contents=[file_part, EXTRACTION_PROMPT],
        config=generation_config,
    )

    result = json.loads(response.text)

    # Build usage metadata dict
    usage_metadata = {"model": model}
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        um = response.usage_metadata
        usage_metadata.update(
            {
                "prompt_token_count": getattr(um, "prompt_token_count", 0) or 0,
                "candidates_token_count": getattr(um, "candidates_token_count", 0) or 0,
                "cached_content_token_count": getattr(um, "cached_content_token_count", 0) or 0,
                "thoughts_token_count": getattr(um, "thoughts_token_count", 0) or 0,
                "total_token_count": getattr(um, "total_token_count", 0) or 0,
            }
        )
    usage_metadata["generation_config"] = {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
        "top_p": 0.95,
        "top_k": 40,
    }

    return result, usage_metadata
