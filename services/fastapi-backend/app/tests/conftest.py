"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_vertex_ai(monkeypatch):
    """Mock Vertex AI service for testing."""
    # TODO: Implement mock for Vertex AI
    pass

