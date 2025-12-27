"""Integration tests for vote extraction API."""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_image_file():
    """Create mock image file."""
    # Create a simple 1x1 pixel JPEG
    image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    return ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")


class TestVoteExtractionEndpoint:
    """Tests for vote extraction endpoint."""

    def test_health_check(self, client):
        """Test vote extraction health check."""
        response = client.get("/api/v1/vote-extraction/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "vote-extraction"

    @patch("app.services.vote_extraction_service.vote_extraction_service.extract_from_images")
    def test_extract_success(self, mock_extract, client, mock_image_file):
        """Test successful vote extraction."""
        # Mock the extraction service
        mock_extract.return_value = {
            "form_info": {
                "province": "Bangkok",
                "district": "Bang Phlat",
                "polling_station_number": "25",
                "form_type": "Constituency",
            },
            "ballot_statistics": {
                "ballots_used": 500,
                "good_ballots": 480,
                "bad_ballots": 15,
                "no_vote_ballots": 5,
            },
            "vote_results": [
                {
                    "number": 1,
                    "candidate_name": "John Doe",
                    "party_name": "Party A",
                    "vote_count": 250,
                    "vote_count_text": "Two hundred fifty",
                }
            ],
        }

        # Make request
        response = client.post(
            "/api/v1/vote-extraction/extract",
            files=[("files", mock_image_file)],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["pages_processed"] == 1
        assert data["reports_extracted"] == 1
        assert len(data["data"]) == 1

    def test_extract_no_files(self, client):
        """Test extraction with no files."""
        response = client.post("/api/v1/vote-extraction/extract")
        assert response.status_code == 422  # Validation error

    def test_extract_invalid_file_type(self, client):
        """Test extraction with invalid file type."""
        pdf_file = ("test.pdf", io.BytesIO(b"PDF content"), "application/pdf")

        response = client.post(
            "/api/v1/vote-extraction/extract",
            files=[("files", pdf_file)],
        )

        assert response.status_code == 400
        detail = response.json()["detail"]
        # Updated error message mentions "extension"
        assert "Invalid file extension" in detail or "Invalid file type" in detail

    @patch("app.services.vote_extraction_service.vote_extraction_service.extract_from_images")
    def test_extract_with_api_key(self, mock_extract, client, mock_image_file, monkeypatch):
        """Test extraction with API key authentication."""
        # Import settings to modify
        from app.config import settings

        # Set API key requirement
        monkeypatch.setattr(settings, "api_key", "test-api-key")
        monkeypatch.setattr(settings, "api_key_required", True)

        # Mock extraction to return list format
        mock_extract.return_value = [
            {
                "form_info": {
                    "province": "Bangkok",
                    "district": "Test",
                    "polling_station_number": "1",
                },
                "vote_results": [],
            }
        ]

        # Request without API key should fail
        response = client.post(
            "/api/v1/vote-extraction/extract",
            files=[("files", mock_image_file)],
        )
        assert response.status_code == 401

        # Request with valid API key should succeed
        response = client.post(
            "/api/v1/vote-extraction/extract",
            files=[("files", mock_image_file)],
            headers={"X-API-Key": "test-api-key"},
        )
        assert response.status_code == 200

    @patch("app.services.vote_extraction_service.vote_extraction_service.extract_from_images")
    def test_extract_multiple_reports(self, mock_extract, client, mock_image_file):
        """Test extraction returning multiple reports."""
        # Mock returning list of 2 reports
        mock_extract.return_value = [
            {
                "form_info": {
                    "province": "Bangkok",
                    "district": "Bang Phlat",
                    "polling_station_number": "25",
                },
                "vote_results": [],
            },
            {
                "form_info": {
                    "province": "Bangkok",
                    "district": "Bang Phlat",
                    "polling_station_number": "26",
                },
                "vote_results": [],
            },
        ]

        response = client.post(
            "/api/v1/vote-extraction/extract",
            files=[
                ("files", mock_image_file),
                ("files", mock_image_file),
            ],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["reports_extracted"] == 2
        assert len(data["data"]) == 2
