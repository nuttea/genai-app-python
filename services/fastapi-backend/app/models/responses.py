"""Response models."""

from typing import Any

from pydantic import BaseModel, Field


class Usage(BaseModel):
    """Token usage information."""

    prompt_tokens: int = Field(..., description="Number of tokens in prompt")
    completion_tokens: int = Field(..., description="Number of tokens in completion")
    total_tokens: int = Field(..., description="Total number of tokens")


class ChatCompletionResponse(BaseModel):
    """Chat completion response."""

    id: str = Field(..., description="Unique response ID")
    model: str = Field(..., description="Model used")
    content: str = Field(..., description="Generated content")
    role: str = Field(default="assistant", description="Response role")
    finish_reason: str | None = Field(None, description="Reason for finishing")
    usage: Usage | None = Field(None, description="Token usage")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class GenerateResponse(BaseModel):
    """Text generation response."""

    id: str = Field(..., description="Unique response ID")
    model: str = Field(..., description="Model used")
    text: str = Field(..., description="Generated text")
    finish_reason: str | None = Field(None, description="Reason for finishing")
    usage: Usage | None = Field(None, description="Token usage")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
    code: str | None = Field(None, description="Error code")
