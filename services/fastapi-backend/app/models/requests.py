"""Request models."""


from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""

    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """Chat completion request."""

    messages: list[Message] = Field(..., description="List of messages")
    model: str | None = Field(None, description="Model to use")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int | None = Field(
        None, ge=1, le=32768, description="Maximum tokens to generate"
    )
    top_p: float | None = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    top_k: int | None = Field(None, ge=1, le=100, description="Top-k sampling parameter")
    stream: bool = Field(False, description="Whether to stream the response")

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "model": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 1024,
            }
        }


class GenerateRequest(BaseModel):
    """Text generation request."""

    prompt: str = Field(..., description="Text prompt")
    model: str | None = Field(None, description="Model to use")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int | None = Field(
        None, ge=1, le=32768, description="Maximum tokens to generate"
    )
    top_p: float | None = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    top_k: int | None = Field(None, ge=1, le=100, description="Top-k sampling parameter")
    stream: bool = Field(False, description="Whether to stream the response")
    stop_sequences: list[str] | None = Field(None, description="Stop sequences")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a haiku about AI",
                "model": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 100,
            }
        }
