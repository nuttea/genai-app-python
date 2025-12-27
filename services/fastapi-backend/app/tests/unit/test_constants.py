"""Tests for application constants."""

from app.core.constants import (
    GEMINI_API_TIMEOUT,
    MAX_FILE_SIZE_MB,
    MAX_TOTAL_SIZE_MB,
    MAX_PROMPT_LENGTH,
    SCHEMA_HASH_LENGTH,
)


class TestConstants:
    """Tests for application constants."""

    def test_timeouts_are_positive(self):
        """Test that timeout values are positive."""
        assert GEMINI_API_TIMEOUT > 0
        assert GEMINI_API_TIMEOUT <= 300  # Reasonable max (5 min)
    
    def test_file_size_limits(self):
        """Test file size limits are reasonable."""
        assert MAX_FILE_SIZE_MB > 0
        assert MAX_FILE_SIZE_MB <= 10  # Per file limit
        assert MAX_TOTAL_SIZE_MB > MAX_FILE_SIZE_MB  # Total should be larger
        assert MAX_TOTAL_SIZE_MB <= 32  # Cloud Run limit
    
    def test_prompt_length_limit(self):
        """Test prompt length limit is reasonable."""
        assert MAX_PROMPT_LENGTH > 0
        assert MAX_PROMPT_LENGTH >= 1000  # At least 1K
        assert MAX_PROMPT_LENGTH <= 100000  # Not too large
    
    def test_schema_hash_length(self):
        """Test schema hash length."""
        assert SCHEMA_HASH_LENGTH == 8
        assert isinstance(SCHEMA_HASH_LENGTH, int)

