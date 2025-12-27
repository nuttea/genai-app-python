"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models.vote_extraction import (
    FormInfo,
    BallotStatistics,
    VoteResult,
    ElectionFormData,
    VoteExtractionResponse,
)


class TestFormInfo:
    """Tests for FormInfo model."""

    def test_valid_form_info(self):
        """Test creating valid FormInfo."""
        form_info = FormInfo(
            date="24 May 2566",
            province="Bangkok",
            district="Bang Phlat",
            polling_station_number="25",
            form_type="Constituency",
        )
        assert form_info.province == "Bangkok"
        assert form_info.district == "Bang Phlat"
    
    def test_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            FormInfo(province="Bangkok")  # Missing district and polling_station_number
    
    def test_optional_fields(self):
        """Test that optional fields can be None."""
        form_info = FormInfo(
            district="Bang Phlat",
            polling_station_number="25",
        )
        assert form_info.date is None
        assert form_info.province is None


class TestVoteResult:
    """Tests for VoteResult model."""

    def test_constituency_vote(self):
        """Test vote result for Constituency form."""
        vote = VoteResult(
            number=1,
            candidate_name="John Doe",
            party_name="Party A",
            vote_count=100,
            vote_count_text="One hundred",
        )
        assert vote.candidate_name == "John Doe"
        assert vote.party_name == "Party A"
        assert vote.display_name == "Party A"  # Returns party_name first
    
    def test_partylist_vote(self):
        """Test vote result for PartyList form."""
        vote = VoteResult(
            number=1,
            party_name="Party B",
            vote_count=50,
        )
        assert vote.party_name == "Party B"
        assert vote.candidate_name is None
        assert vote.display_name == "Party B"
    
    def test_display_name_fallback(self):
        """Test display_name property fallback logic."""
        # Has party_name
        vote1 = VoteResult(number=1, party_name="Party A", vote_count=10)
        assert vote1.display_name == "Party A"
        
        # No party, has candidate
        vote2 = VoteResult(number=2, candidate_name="Jane Doe", vote_count=20)
        assert vote2.display_name == "Jane Doe"
        
        # Neither
        vote3 = VoteResult(number=3, vote_count=0)
        assert vote3.display_name == "N/A"


class TestElectionFormData:
    """Tests for ElectionFormData model."""

    def test_complete_data(self):
        """Test creating complete election form data."""
        data = ElectionFormData(
            form_info=FormInfo(
                district="Bang Phlat",
                polling_station_number="25",
                form_type="Constituency",
            ),
            ballot_statistics=BallotStatistics(
                ballots_used=500,
                good_ballots=480,
                bad_ballots=15,
                no_vote_ballots=5,
            ),
            vote_results=[
                VoteResult(
                    number=1,
                    candidate_name="John Doe",
                    party_name="Party A",
                    vote_count=250,
                )
            ],
        )
        assert data.form_info.district == "Bang Phlat"
        assert len(data.vote_results) == 1
    
    def test_optional_ballot_statistics(self):
        """Test that ballot_statistics is optional."""
        data = ElectionFormData(
            form_info=FormInfo(
                district="Bang Phlat",
                polling_station_number="25",
            ),
            vote_results=[],
        )
        assert data.ballot_statistics is None


class TestVoteExtractionResponse:
    """Tests for VoteExtractionResponse model."""

    def test_success_response(self):
        """Test successful extraction response."""
        response = VoteExtractionResponse(
            success=True,
            data=[
                ElectionFormData(
                    form_info=FormInfo(district="Test", polling_station_number="1"),
                    vote_results=[],
                )
            ],
            pages_processed=3,
            reports_extracted=1,
        )
        assert response.success is True
        assert len(response.data) == 1
    
    def test_failure_response(self):
        """Test failed extraction response."""
        response = VoteExtractionResponse(
            success=False,
            data=[],
            error="Extraction failed",
            pages_processed=3,
            reports_extracted=0,
        )
        assert response.success is False
        assert response.error == "Extraction failed"

