"""GenAI service layer combining Vertex AI functionality."""

import logging
from typing import List, Optional, AsyncGenerator

from app.services.vertex_ai import vertex_ai_service
from app.models.requests import Message

logger = logging.getLogger(__name__)


class GenAIService:
    """High-level GenAI service."""

    def __init__(self) -> None:
        """Initialize GenAI service."""
        self.vertex_service = vertex_ai_service
        self.vertex_service.initialize()

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> dict:
        """Generate text from a prompt."""
        return await self.vertex_service.generate_content(
            prompt=prompt,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            stop_sequences=stop_sequences,
        )

    async def generate_text_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream generated text from a prompt."""
        async for chunk in self.vertex_service.generate_content_stream(
            prompt=prompt,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
        ):
            yield chunk

    async def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> dict:
        """Generate a chat completion."""
        # Convert Pydantic models to dicts
        messages_dict = [msg.model_dump() for msg in messages]

        return await self.vertex_service.chat_completion(
            messages=messages_dict,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
        )


# Global service instance
genai_service = GenAIService()
