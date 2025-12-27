"""Tests for health endpoints."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check(client: TestClient):
    """Test readiness check endpoint."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
