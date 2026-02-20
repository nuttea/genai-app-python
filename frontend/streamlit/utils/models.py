"""Pydantic models for Thai election form data (SS5/18) with validation."""

from typing import Optional

from pydantic import BaseModel, Field


class NumberTextPair(BaseModel):
    """Thai document number representation (both Arabic numeral and Thai text)."""

    arabic: int = Field(..., description="Arabic numeral (e.g., 120)")
    thai_text: Optional[str] = Field(None, description="Thai text (e.g., 'หนึ่งร้อยยี่สิบ')")


class FormInfo(BaseModel):
    """Header information identifying the polling station."""

    form_type: Optional[str] = Field(None, description="Constituency or PartyList")
    set_number: Optional[str] = Field(None, description="Set number (ชุดที่)")
    date: Optional[str] = Field(None, description="Date of election")
    province: Optional[str] = Field(None, description="Province name")
    constituency_number: Optional[str] = Field(None, description="Constituency number")
    district: str = Field(..., description="District name")
    sub_district: Optional[str] = Field(None, description="Sub-district name")
    polling_station_number: str = Field(..., description="Polling station number")
    village_moo: Optional[str] = Field(None, description="Village number (หมู่ที่)")


class VoterStatistics(BaseModel):
    """Voter statistics (Section 1)."""

    eligible_voters: Optional[NumberTextPair] = Field(None, description="Total eligible voters")
    present_voters: Optional[NumberTextPair] = Field(None, description="Voters who showed up")


class BallotStatistics(BaseModel):
    """Ballot accounting statistics (Section 2)."""

    ballots_allocated: Optional[NumberTextPair] = Field(None, description="Allocated ballots")
    ballots_used: Optional[NumberTextPair] = Field(None, description="Used ballots")
    good_ballots: Optional[NumberTextPair] = Field(None, description="Valid ballots")
    bad_ballots: Optional[NumberTextPair] = Field(None, description="Invalid ballots")
    no_vote_ballots: Optional[NumberTextPair] = Field(None, description="No vote ballots")
    ballots_remaining: Optional[NumberTextPair] = Field(None, description="Remaining ballots")


class VoteResult(BaseModel):
    """Individual vote result."""

    number: int = Field(..., description="Candidate/Party number")
    candidate_name: Optional[str] = Field(None, description="Candidate name")
    party_name: Optional[str] = Field(None, description="Party name")
    vote_count: NumberTextPair = Field(..., description="Vote count (number + text)")


class Official(BaseModel):
    """Committee member/official."""

    name: str = Field(..., description="Full name of official")
    position: str = Field(..., description="Position/role (e.g., ประธาน, กรรมการ)")


class ElectionFormData(BaseModel):
    """Complete election form extraction result."""

    form_info: FormInfo
    voter_statistics: Optional[VoterStatistics] = None
    ballot_statistics: Optional[BallotStatistics] = None
    vote_results: list[VoteResult] = Field(default_factory=list)
    total_votes_recorded: Optional[NumberTextPair] = Field(
        None, description="Total vote count from table footer"
    )
    officials: Optional[list[Official]] = Field(
        None, description="Committee members who signed the form"
    )


def get_number_value(num_obj) -> int:
    """Extract arabic number from NumberTextPair dict or plain int."""
    if isinstance(num_obj, dict):
        return num_obj.get("arabic", 0) or 0
    elif isinstance(num_obj, int):
        return num_obj
    return 0


def get_thai_text(num_obj) -> str:
    """Extract Thai text from NumberTextPair dict."""
    if isinstance(num_obj, dict):
        return num_obj.get("thai_text", "") or ""
    return ""


def validate_extraction(data: dict) -> tuple[bool, list[str], list[str]]:
    """
    Validate extracted election form data.

    Args:
        data: Extracted form data dict

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # 1. Ballot statistics validation
    ballot_stats = data.get("ballot_statistics")
    if ballot_stats:
        used = get_number_value(ballot_stats.get("ballots_used"))
        good = get_number_value(ballot_stats.get("good_ballots"))
        bad = get_number_value(ballot_stats.get("bad_ballots"))
        no_vote = get_number_value(ballot_stats.get("no_vote_ballots"))

        expected_total = good + bad + no_vote
        if used > 0 and expected_total > 0 and used != expected_total:
            errors.append(
                f"Ballot mismatch: ballots_used ({used:,}) != "
                f"good+bad+no_vote ({expected_total:,})"
            )

    # 2. Total votes validation
    vote_results = data.get("vote_results", [])
    total_recorded = data.get("total_votes_recorded")

    if vote_results and total_recorded:
        calculated_total = sum(get_number_value(v.get("vote_count")) for v in vote_results)
        recorded_total = get_number_value(total_recorded)

        if calculated_total != recorded_total:
            errors.append(
                f"Vote total mismatch: sum of votes ({calculated_total:,}) != "
                f"recorded total ({recorded_total:,})"
            )

    # 3. Voter statistics vs ballot statistics
    voter_stats = data.get("voter_statistics")
    if voter_stats and ballot_stats:
        present = get_number_value(voter_stats.get("present_voters"))
        used = get_number_value(ballot_stats.get("ballots_used"))

        if present > 0 and used > 0:
            discrepancy = abs(present - used)
            if discrepancy > 5:
                warnings.append(
                    f"Voter count ({present:,}) differs from "
                    f"ballots used ({used:,}) by {discrepancy}"
                )

    # 4. Vote count non-negative check
    for i, result in enumerate(vote_results, 1):
        vote_count = get_number_value(result.get("vote_count"))
        if vote_count < 0:
            name = result.get("candidate_name") or result.get("party_name") or f"Entry #{i}"
            errors.append(f"Negative vote count for {name}: {vote_count}")

    # 5. Check for empty vote results
    if not vote_results:
        errors.append("No vote results extracted")

    return len(errors) == 0, errors, warnings
