"""
Unit tests for experiments service and evaluators.
"""

import pytest

from app.services.experiments_service import (
    avg_ballot_accuracy,
    ballot_accuracy_score,
    exact_form_match,
    has_no_errors,
    overall_accuracy,
    success_rate,
    vote_results_quality,
)


class TestExactFormMatch:
    """Tests for exact_form_match evaluator."""

    def test_exact_match(self):
        """Test exact form info match."""
        output = {"form_info": {"form_type": "Constituency", "province": "Bangkok"}}
        expected = {"form_info": {"form_type": "Constituency", "province": "Bangkok"}}

        assert exact_form_match(output, expected) is True

    def test_no_match(self):
        """Test form info mismatch."""
        output = {"form_info": {"form_type": "Constituency", "province": "Bangkok"}}
        expected = {"form_info": {"form_type": "PartyList", "province": "Bangkok"}}

        assert exact_form_match(output, expected) is False

    def test_missing_form_info(self):
        """Test missing form_info."""
        output = {}
        expected = {"form_info": {"form_type": "Constituency"}}

        assert exact_form_match(output, expected) is False

    def test_empty_form_info(self):
        """Test empty form_info."""
        output = {"form_info": {}}
        expected = {"form_info": {}}

        assert exact_form_match(output, expected) is True


class TestBallotAccuracyScore:
    """Tests for ballot_accuracy_score evaluator."""

    def test_perfect_accuracy(self):
        """Test perfect ballot accuracy."""
        output = {
            "ballot_statistics": {
                "ballots_allocated": 100,
                "ballots_used": 80,
                "good_ballots": 75,
                "bad_ballots": 2,
                "no_vote_ballots": 3,
                "ballots_remaining": 20,
            }
        }
        expected = {
            "ballot_statistics": {
                "ballots_allocated": 100,
                "ballots_used": 80,
                "good_ballots": 75,
                "bad_ballots": 2,
                "no_vote_ballots": 3,
                "ballots_remaining": 20,
            }
        }

        score = ballot_accuracy_score(output, expected)
        assert score == 1.0

    def test_partial_accuracy(self):
        """Test partial ballot accuracy."""
        output = {
            "ballot_statistics": {
                "ballots_allocated": 100,
                "ballots_used": 80,
                "good_ballots": 75,
                "bad_ballots": 2,
                "no_vote_ballots": 3,
                "ballots_remaining": 20,
            }
        }
        expected = {
            "ballot_statistics": {
                "ballots_allocated": 100,  # Match
                "ballots_used": 80,  # Match
                "good_ballots": 75,  # Match
                "bad_ballots": 3,  # Mismatch
                "no_vote_ballots": 3,  # Match
                "ballots_remaining": 19,  # Mismatch
            }
        }

        score = ballot_accuracy_score(output, expected)
        assert score == 4 / 6  # 4 matches out of 6 fields

    def test_zero_accuracy(self):
        """Test zero ballot accuracy."""
        output = {
            "ballot_statistics": {
                "ballots_allocated": 100,
                "ballots_used": 80,
                "good_ballots": 75,
                "bad_ballots": 2,
                "no_vote_ballots": 3,
                "ballots_remaining": 20,
            }
        }
        expected = {
            "ballot_statistics": {
                "ballots_allocated": 200,
                "ballots_used": 160,
                "good_ballots": 150,
                "bad_ballots": 5,
                "no_vote_ballots": 5,
                "ballots_remaining": 40,
            }
        }

        score = ballot_accuracy_score(output, expected)
        assert score == 0.0

    def test_missing_ballot_statistics(self):
        """Test missing ballot statistics."""
        output = {}
        expected = {
            "ballot_statistics": {
                "ballots_allocated": 100,
                "ballots_used": 80,
                "good_ballots": 75,
                "bad_ballots": 2,
                "no_vote_ballots": 3,
                "ballots_remaining": 20,
            }
        }

        score = ballot_accuracy_score(output, expected)
        assert score == 0.0


class TestVoteResultsQuality:
    """Tests for vote_results_quality evaluator."""

    def test_perfect_quality(self):
        """Test perfect vote results quality."""
        output = {
            "vote_results": [
                {"number": 1, "vote_count": 10},
                {"number": 2, "vote_count": 20},
                {"number": 3, "vote_count": 30},
            ]
        }
        expected = {
            "vote_results": [
                {"number": 1, "vote_count": 10},
                {"number": 2, "vote_count": 20},
                {"number": 3, "vote_count": 30},
            ]
        }

        quality = vote_results_quality(output, expected)
        assert quality == 1.0

    def test_partial_quality(self):
        """Test partial vote results quality."""
        output = {
            "vote_results": [
                {"number": 1, "vote_count": 10},
                {"number": 2, "vote_count": 25},  # Mismatch
                {"number": 3, "vote_count": 30},
            ]
        }
        expected = {
            "vote_results": [
                {"number": 1, "vote_count": 10},
                {"number": 2, "vote_count": 20},
                {"number": 3, "vote_count": 30},
            ]
        }

        quality = vote_results_quality(output, expected)
        assert quality == 2 / 3  # 2 matches out of 3

    def test_missing_candidates(self):
        """Test missing candidates in output."""
        output = {
            "vote_results": [
                {"number": 1, "vote_count": 10},
                {"number": 2, "vote_count": 20},
            ]
        }
        expected = {
            "vote_results": [
                {"number": 1, "vote_count": 10},
                {"number": 2, "vote_count": 20},
                {"number": 3, "vote_count": 30},
            ]
        }

        quality = vote_results_quality(output, expected)
        assert quality == 2 / 3  # 2 matches out of 3 expected

    def test_empty_vote_results(self):
        """Test empty vote results."""
        output = {"vote_results": []}
        expected = {
            "vote_results": [
                {"number": 1, "vote_count": 10},
                {"number": 2, "vote_count": 20},
            ]
        }

        quality = vote_results_quality(output, expected)
        assert quality == 0.0


class TestHasNoErrors:
    """Tests for has_no_errors evaluator."""

    def test_no_errors(self):
        """Test output without errors."""
        output = {"form_info": {}, "ballot_statistics": {}}
        expected = {}

        assert has_no_errors(output, expected) is True

    def test_with_errors(self):
        """Test output with errors."""
        output = {"error": "Failed to extract"}
        expected = {}

        assert has_no_errors(output, expected) is False

    def test_empty_output(self):
        """Test empty output."""
        output = {}
        expected = {}

        assert has_no_errors(output, expected) is True


class TestOverallAccuracy:
    """Tests for overall_accuracy summary evaluator."""

    def test_perfect_accuracy(self):
        """Test perfect overall accuracy."""
        results = [
            {
                "metrics": {
                    "exact_form_match": 1,
                    "ballot_accuracy_score": 1.0,
                    "vote_results_quality": 1.0,
                }
            },
            {
                "metrics": {
                    "exact_form_match": 1,
                    "ballot_accuracy_score": 1.0,
                    "vote_results_quality": 1.0,
                }
            },
        ]

        accuracy = overall_accuracy(results)
        assert accuracy == 1.0

    def test_partial_accuracy(self):
        """Test partial overall accuracy."""
        results = [
            {
                "metrics": {
                    "exact_form_match": 1,
                    "ballot_accuracy_score": 0.8,
                    "vote_results_quality": 0.9,
                }
            },
            {
                "metrics": {
                    "exact_form_match": 0,
                    "ballot_accuracy_score": 0.6,
                    "vote_results_quality": 0.7,
                }
            },
        ]

        # First result: 1*0.2 + 0.8*0.4 + 0.9*0.4 = 0.2 + 0.32 + 0.36 = 0.88
        # Second result: 0*0.2 + 0.6*0.4 + 0.7*0.4 = 0 + 0.24 + 0.28 = 0.52
        # Average: (0.88 + 0.52) / 2 = 0.70
        accuracy = overall_accuracy(results)
        assert abs(accuracy - 0.70) < 0.01

    def test_empty_results(self):
        """Test empty results."""
        results = []
        accuracy = overall_accuracy(results)
        assert accuracy == 0.0


class TestSuccessRate:
    """Tests for success_rate summary evaluator."""

    def test_perfect_success_rate(self):
        """Test perfect success rate."""
        results = [
            {"metrics": {"has_no_errors": True}},
            {"metrics": {"has_no_errors": True}},
            {"metrics": {"has_no_errors": True}},
        ]

        rate = success_rate(results)
        assert rate == 1.0

    def test_partial_success_rate(self):
        """Test partial success rate."""
        results = [
            {"metrics": {"has_no_errors": True}},
            {"metrics": {"has_no_errors": False}},
            {"metrics": {"has_no_errors": True}},
            {"metrics": {"has_no_errors": False}},
        ]

        rate = success_rate(results)
        assert rate == 0.5

    def test_zero_success_rate(self):
        """Test zero success rate."""
        results = [
            {"metrics": {"has_no_errors": False}},
            {"metrics": {"has_no_errors": False}},
        ]

        rate = success_rate(results)
        assert rate == 0.0

    def test_empty_results(self):
        """Test empty results."""
        results = []
        rate = success_rate(results)
        assert rate == 0.0


class TestAvgBallotAccuracy:
    """Tests for avg_ballot_accuracy summary evaluator."""

    def test_perfect_ballot_accuracy(self):
        """Test perfect average ballot accuracy."""
        results = [
            {"metrics": {"ballot_accuracy_score": 1.0}},
            {"metrics": {"ballot_accuracy_score": 1.0}},
        ]

        avg = avg_ballot_accuracy(results)
        assert avg == 1.0

    def test_partial_ballot_accuracy(self):
        """Test partial average ballot accuracy."""
        results = [
            {"metrics": {"ballot_accuracy_score": 1.0}},
            {"metrics": {"ballot_accuracy_score": 0.8}},
            {"metrics": {"ballot_accuracy_score": 0.6}},
        ]

        avg = avg_ballot_accuracy(results)
        assert abs(avg - 0.8) < 0.01  # (1.0 + 0.8 + 0.6) / 3 = 0.8

    def test_zero_ballot_accuracy(self):
        """Test zero average ballot accuracy."""
        results = [
            {"metrics": {"ballot_accuracy_score": 0.0}},
            {"metrics": {"ballot_accuracy_score": 0.0}},
        ]

        avg = avg_ballot_accuracy(results)
        assert avg == 0.0

    def test_empty_results(self):
        """Test empty results."""
        results = []
        avg = avg_ballot_accuracy(results)
        assert avg == 0.0

