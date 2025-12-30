"""Vertex AI service integration."""

import logging
import uuid
from collections.abc import AsyncGenerator

import vertexai
from app.config import settings
from app.core.exceptions import ConfigurationException, VertexAIException
from vertexai.generative_models import ChatSession, GenerativeModel

logger = logging.getLogger(__name__)


class VertexAIService:
    """Service for interacting with Google Vertex AI."""

    def __init__(self) -> None:
        """Initialize Vertex AI service."""
        self._initialized = False
        self._model: GenerativeModel | None = None
        self._chat: ChatSession | None = None

    def initialize(self) -> None:
        """Initialize Vertex AI connection."""
        if self._initialized:
            return

        try:
            # Initialize Vertex AI
            vertexai.init(
                project=settings.google_cloud_project,
                location=settings.vertex_ai_location,
            )

            logger.info(
                f"Initialized Vertex AI: project={settings.google_cloud_project}, "
                f"location={settings.vertex_ai_location}"
            )
            self._initialized = True
        except (ValueError, AttributeError, TypeError) as e:
            logger.error(f"Configuration error initializing Vertex AI: {e}")
            raise ConfigurationException(f"Vertex AI configuration error: {e}") from e
        except ConnectionError as e:
            logger.error(f"Connection error initializing Vertex AI: {e}")
            raise VertexAIException(f"Cannot connect to Vertex AI: {e}") from e
        except Exception as e:
            logger.critical(f"Unexpected error initializing Vertex AI: {e}", exc_info=True)
            raise VertexAIException(f"Vertex AI initialization failed: {e}") from e

    def get_model(self, model_name: str | None = None) -> GenerativeModel:
        """Get a generative model instance."""
        if not self._initialized:
            self.initialize()

        model_name = model_name or settings.default_model
        return GenerativeModel(model_name)

    async def generate_content(
        self,
        prompt: str,
        model_name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        stop_sequences: list[str] | None = None,
    ) -> dict:
        """Generate content from a prompt.

        Args:
            prompt: Text prompt
            model_name: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: Stop sequences

        Returns:
            Dictionary with generated content and metadata
        """
        model = self.get_model(model_name)

        # Build generation config
        generation_config = {
            "temperature": temperature or settings.default_temperature,
            "max_output_tokens": max_tokens or settings.default_max_tokens,
            "top_p": top_p or settings.default_top_p,
            "top_k": top_k or settings.default_top_k,
        }

        if stop_sequences:
            generation_config["stop_sequences"] = stop_sequences

        try:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
            )

            return {
                "id": str(uuid.uuid4()),
                "model": model_name or settings.default_model,
                "text": response.text,
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": 0,  # Vertex AI doesn't provide this
                    "completion_tokens": 0,  # Vertex AI doesn't provide this
                    "total_tokens": 0,
                },
            }
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    async def generate_content_stream(
        self,
        prompt: str,
        model_name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream generated content from a prompt."""
        model = self.get_model(model_name)

        generation_config = {
            "temperature": temperature or settings.default_temperature,
            "max_output_tokens": max_tokens or settings.default_max_tokens,
            "top_p": top_p or settings.default_top_p,
            "top_k": top_k or settings.default_top_k,
        }

        try:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid parameters for streaming: {e}")
            raise VertexAIException(f"Invalid streaming parameters: {e}") from e
        except Exception as e:
            logger.critical(f"Unexpected error streaming content: {e}", exc_info=True)
            raise VertexAIException(f"Content streaming failed: {e}") from e

    async def chat_completion(
        self,
        messages: list[dict],
        model_name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
    ) -> dict:
        """Generate a chat completion."""
        model = self.get_model(model_name)

        generation_config = {
            "temperature": temperature or settings.default_temperature,
            "max_output_tokens": max_tokens or settings.default_max_tokens,
            "top_p": top_p or settings.default_top_p,
            "top_k": top_k or settings.default_top_k,
        }

        try:
            # Start a chat session
            chat = model.start_chat()

            # Send messages (skip system messages, handle user/assistant messages)
            for message in messages[:-1]:  # All but last message
                if message["role"] == "user":
                    chat.send_message(message["content"])

            # Send the last message and get response
            last_message = messages[-1]
            if last_message["role"] == "user":
                response = chat.send_message(
                    last_message["content"],
                    generation_config=generation_config,
                )

                return {
                    "id": str(uuid.uuid4()),
                    "model": model_name or settings.default_model,
                    "content": response.text,
                    "role": "assistant",
                    "finish_reason": "stop",
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                }
            else:
                raise ValueError("Last message must be from user")
        except ValueError as e:
            logger.warning(f"Chat validation error: {e}")
            raise VertexAIException(f"Invalid chat messages: {e}") from e
        except (TypeError, AttributeError) as e:
            logger.error(f"Invalid chat parameters: {e}")
            raise VertexAIException(f"Chat completion error: {e}") from e
        except Exception as e:
            logger.critical(f"Unexpected error in chat completion: {e}", exc_info=True)
            raise VertexAIException(f"Chat completion failed: {e}") from e


# Global service instance
vertex_ai_service = VertexAIService()
