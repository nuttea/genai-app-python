"""Tests for configuration."""

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_settings(self):
        """Test default configuration values."""
        settings = Settings(google_cloud_project="test-project")

        assert settings.google_cloud_project == "test-project"
        assert settings.vertex_ai_location == "us-central1"
        assert settings.fastapi_env == "development"
        assert settings.log_level == "info"
        assert settings.api_key_required is False

    def test_environment_values(self):
        """Test different environment values."""
        # Test that settings can be created with valid project
        settings = Settings(google_cloud_project="test-project")
        assert settings.google_cloud_project == "test-project"

        # Test various environments
        for env in ["development", "staging", "production"]:
            s = Settings(google_cloud_project="test", fastapi_env=env)
            assert s.fastapi_env == env

    def test_cors_origins_from_string(self):
        """Test CORS origins parsing from comma-separated string."""
        settings = Settings(
            google_cloud_project="test",
            cors_origins="http://localhost:3000,http://localhost:8000,http://localhost:8501",
        )

        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) == 3
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:8501" in settings.cors_origins

    def test_cors_origins_from_list(self):
        """Test CORS origins as list."""
        origins = ["http://localhost:3000", "http://localhost:8000"]
        settings = Settings(google_cloud_project="test", cors_origins=origins)

        assert settings.cors_origins == origins

    def test_environment_detection(self):
        """Test environment detection methods."""
        # Development
        dev_settings = Settings(google_cloud_project="test", fastapi_env="development")
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False

        # Production
        prod_settings = Settings(google_cloud_project="test", fastapi_env="production")
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True

        # Staging (should not be production)
        staging_settings = Settings(google_cloud_project="test", fastapi_env="staging")
        assert staging_settings.is_development is False
        assert staging_settings.is_production is False

    def test_temperature_range_validation(self):
        """Test that temperature is within valid range."""
        settings = Settings(google_cloud_project="test", default_temperature=0.7)
        assert 0.0 <= settings.default_temperature <= 2.0

    def test_max_tokens_validation(self):
        """Test that max_tokens is positive."""
        settings = Settings(google_cloud_project="test", default_max_tokens=1024)
        assert settings.default_max_tokens > 0
