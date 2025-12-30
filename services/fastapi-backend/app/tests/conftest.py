"""Test configuration and fixtures."""

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_vertex_ai(monkeypatch):
    """Mock Vertex AI service for testing."""
    # TODO: Implement mock for Vertex AI
    pass
