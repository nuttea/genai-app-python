"""Custom exceptions for the application."""


class GenAIException(Exception):
    """Base exception for GenAI application."""

    pass


class VertexAIException(GenAIException):
    """Exception for Vertex AI errors."""

    pass


class ExtractionException(GenAIException):
    """Exception for data extraction errors."""

    pass


class ValidationException(GenAIException):
    """Exception for validation errors."""

    pass


class ConfigurationException(GenAIException):
    """Exception for configuration errors."""

    pass


class TimeoutException(GenAIException):
    """Exception for timeout errors."""

    pass


class RateLimitException(GenAIException):
    """Exception for rate limit errors."""

    pass
