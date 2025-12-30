"""Tests for custom exceptions."""

import pytest
from app.core.exceptions import (
    ConfigurationException,
    ExtractionException,
    GenAIException,
    RateLimitException,
    TimeoutException,
    ValidationException,
    VertexAIException,
)


class TestCustomExceptions:
    """Tests for custom exception classes."""

    def test_genai_exception(self):
        """Test base GenAI exception."""
        with pytest.raises(GenAIException):
            raise GenAIException("Test error")

    def test_vertex_ai_exception(self):
        """Test VertexAI exception."""
        with pytest.raises(VertexAIException):
            raise VertexAIException("Vertex AI error")

    def test_extraction_exception(self):
        """Test Extraction exception."""
        with pytest.raises(ExtractionException):
            raise ExtractionException("Extraction failed")

    def test_validation_exception(self):
        """Test Validation exception."""
        with pytest.raises(ValidationException):
            raise ValidationException("Validation failed")

    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from GenAIException."""
        assert issubclass(VertexAIException, GenAIException)
        assert issubclass(ExtractionException, GenAIException)
        assert issubclass(ValidationException, GenAIException)
        assert issubclass(ConfigurationException, GenAIException)
        assert issubclass(TimeoutException, GenAIException)
        assert issubclass(RateLimitException, GenAIException)

    def test_exception_with_message(self):
        """Test exception with custom message."""
        msg = "Custom error message"
        exc = VertexAIException(msg)
        assert str(exc) == msg

    def test_exception_chain(self):
        """Test exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise VertexAIException("Wrapped error") from e
        except VertexAIException as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
