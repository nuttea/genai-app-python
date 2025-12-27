"""Unit tests for security utilities."""

import pytest
from fastapi import HTTPException

from app.core.security import verify_api_key
from app.config import settings


class TestAPIKeyValidation:
    """Tests for API key validation."""

    @pytest.mark.asyncio
    async def test_no_key_required(self, monkeypatch):
        """Test when API key is not required."""
        monkeypatch.setattr(settings, "api_key", "")
        monkeypatch.setattr(settings, "api_key_required", False)
        
        # Should allow requests without API key
        result = await verify_api_key(None)
        assert result == "no-key-required"
    
    @pytest.mark.asyncio
    async def test_valid_api_key(self, monkeypatch):
        """Test with valid API key."""
        monkeypatch.setattr(settings, "api_key", "test-key-123")
        monkeypatch.setattr(settings, "api_key_required", True)
        
        # Valid key should pass
        result = await verify_api_key("test-key-123")
        assert result == "test-key-123"
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self, monkeypatch):
        """Test with missing API key when required."""
        monkeypatch.setattr(settings, "api_key", "test-key-123")
        monkeypatch.setattr(settings, "api_key_required", True)
        
        # Missing key should raise 401
        with pytest.raises(HTTPException) as exc:
            await verify_api_key(None)
        assert exc.value.status_code == 401
        assert "Missing API key" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self, monkeypatch):
        """Test with invalid API key."""
        monkeypatch.setattr(settings, "api_key", "correct-key")
        monkeypatch.setattr(settings, "api_key_required", True)
        
        # Invalid key should raise 401
        with pytest.raises(HTTPException) as exc:
            await verify_api_key("wrong-key")
        assert exc.value.status_code == 401
        assert "Invalid API key" in exc.value.detail

