"""Pydantic models for vote extraction."""

from typing import Optional

from pydantic import BaseModel, Field


class FormInfo(BaseModel):
    """Header information identifying the polling station."""

    date: Optional[str] = Field(None, description="Date of election (e.g., 14 May 2566)")
    province: Optional[str] = Field(None, description="Province name")
    district: str = Field(..., description="District name (Amphoe/Khet)")
    sub_district: Optional[str] = Field(None, description="Sub-district name (Tambon/Khwaeng)")
    constituency_number: Optional[str] = Field(None, description="Constituency number")
    polling_station_number: str = Field(..., description="Unit/Polling Station number")
    form_type: Optional[str] = Field(
        None,
        description="Type of form: Constituency (Candidates) or PartyList (Parties)",
    )


class BallotStatistics(BaseModel):
    """Section 2: Ballot accounting statistics."""

    ballots_allocated: Optional[int] = Field(None, description="Total ballots allocated to station")
    ballots_used: Optional[int] = Field(None, description="Item 2.2: Total used ballots")
    ballots_remaining: Optional[int] = Field(None, description="Ballots remaining/unused")
    good_ballots: Optional[int] = Field(None, description="Item 2.2.1: Valid ballots")
    bad_ballots: Optional[int] = Field(None, description="Item 2.2.2: Void/Spoiled ballots")
    no_vote_ballots: Optional[int] = Field(None, description="Item 2.2.3: No Vote ballots")


class VoteResult(BaseModel):
    """Individual vote result for a candidate or party."""

    number: int = Field(..., description="Candidate/Party Number")
    candidate_name: Optional[str] = Field(
        None, description="Candidate Name (for Constituency forms)"
    )
    party_name: Optional[str] = Field(
        None, description="Party Name (for both Constituency and PartyList)"
    )
    vote_count: int = Field(..., description="Vote count (numeric)")
    vote_count_text: Optional[str] = Field(None, description="Vote count (Thai written text)")

    class Config:
        # Removed alias - keep both fields separate
        populate_by_name = True

    @property
    def display_name(self) -> str:
        """Get the appropriate name to display (party or candidate)."""
        if self.party_name and self.party_name != "null":
            return self.party_name
        if self.candidate_name and self.candidate_name != "null":
            return self.candidate_name
        return "N/A"


class ElectionFormData(BaseModel):
    """Complete election form extraction result."""

    form_info: FormInfo
    ballot_statistics: Optional[BallotStatistics] = None
    vote_results: list[VoteResult] = Field(
        default_factory=list, description="Vote counts for all candidates/parties"
    )


class VoteExtractionResponse(BaseModel):
    """Response for vote extraction request."""

    success: bool = Field(..., description="Whether extraction was successful")
    data: list[ElectionFormData] = Field(
        default_factory=list, description="List of extracted data (one per report)"
    )
    error: Optional[str] = Field(None, description="Error message if extraction failed")
    pages_processed: int = Field(..., description="Number of pages processed")
    reports_extracted: int = Field(
        default=0, description="Number of reports successfully extracted"
    )
