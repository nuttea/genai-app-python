"""
Gemini Multimodal Service

Simplified service that uses Gemini's native multimodal capabilities
to process video, images, and audio without any preprocessing.
"""

from google import genai
from google.genai import types
from ddtrace import tracer
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from app.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interacting with Gemini's multimodal API.

    Uses Gemini 2.5 Flash's native support for:
    - Video processing (temporal understanding)
    - Image analysis
    - Audio transcription
    - Text generation

    No preprocessing required! ✨
    """

    def __init__(self):
        """Initialize Gemini client with Vertex AI."""
        self.client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.vertex_ai_location,
        )
        self.model = settings.default_llm_model
        logger.info(f"GeminiService initialized with model: {self.model}")

    @tracer.wrap(name="gemini.upload_file", service="adk-content-creator")
    async def upload_file(self, file_path: str) -> str:
        """
        Upload a file to Gemini for processing.

        Gemini handles all file types natively:
        - Videos (MP4, MOV, AVI, WebM)
        - Images (PNG, JPG, GIF, WebP)
        - Audio (MP3, WAV)

        Args:
            file_path: Local path to the file

        Returns:
            Gemini file URI for use in prompts
        """
        try:
            logger.info(f"Uploading file to Gemini: {file_path}")

            file = self.client.files.upload(path=file_path)

            logger.info(f"File uploaded successfully: {file.uri}")
            return file.uri

        except Exception as e:
            logger.error(f"Error uploading file to Gemini: {e}", exc_info=True)
            raise

    @tracer.wrap(name="gemini.analyze_video", service="adk-content-creator")
    async def analyze_video(
        self,
        video_uri: str,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
    ) -> str:
        """
        Analyze a video using Gemini's native video understanding.

        Gemini can:
        - Transcribe audio automatically
        - Understand temporal sequences
        - Identify visual elements
        - Describe actions and events

        No need for frame extraction or separate transcription!

        Args:
            video_uri: Gemini file URI from upload_file()
            prompt: Custom prompt (default: general video analysis)
            temperature: Generation temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate

        Returns:
            Analysis text from Gemini
        """
        default_prompt = """
        Analyze this video and provide:
        1. **Transcript**: Full transcription of spoken audio
        2. **Visual Summary**: Key visual elements and UI components shown
        3. **Key Features**: Main features or products demonstrated
        4. **Workflow**: Step-by-step actions shown in the video
        5. **Highlights**: Notable points or takeaways
        
        Format your response in markdown with clear sections.
        """

        analysis_prompt = prompt or default_prompt

        try:
            logger.info(f"Analyzing video with Gemini: {video_uri}")

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[analysis_prompt, video_uri],
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    response_modalities=["TEXT"],
                ),
            )

            result = response.text
            logger.info(f"Video analysis complete: {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Error analyzing video: {e}", exc_info=True)
            raise

    @tracer.wrap(name="gemini.analyze_image", service="adk-content-creator")
    async def analyze_image(
        self,
        image_uri: str,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        """
        Analyze an image using Gemini Vision.

        Gemini can:
        - Identify UI elements
        - Extract text (OCR)
        - Describe visual content
        - Understand context

        Args:
            image_uri: Gemini file URI from upload_file()
            prompt: Custom prompt (default: general image analysis)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Analysis text from Gemini
        """
        default_prompt = """
        Analyze this image and provide:
        1. **Description**: What is shown in the image
        2. **UI Elements**: Any user interface components, buttons, menus
        3. **Text Content**: Any visible text or labels
        4. **Context**: What product, feature, or concept is illustrated
        5. **Key Insights**: Important details or takeaways
        
        Format your response in markdown.
        """

        analysis_prompt = prompt or default_prompt

        try:
            logger.info(f"Analyzing image with Gemini: {image_uri}")

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[analysis_prompt, image_uri],
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    response_modalities=["TEXT"],
                ),
            )

            result = response.text
            logger.info(f"Image analysis complete: {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Error analyzing image: {e}", exc_info=True)
            raise

    @tracer.wrap(name="gemini.generate_content", service="adk-content-creator")
    async def generate_content(
        self,
        prompt: str,
        media_uris: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 16384,
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate content with Gemini.

        Can include multiple media files (videos, images) in the prompt.

        Args:
            prompt: Generation prompt
            media_uris: Optional list of Gemini file URIs to include
            temperature: Generation temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            response_schema: Optional JSON schema for structured output

        Returns:
            Generated content text
        """
        try:
            # Build contents list
            contents = [prompt]
            if media_uris:
                contents.extend(media_uris)

            logger.info(f"Generating content with {len(media_uris or [])} media files attached")

            # Build config
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_modalities=["TEXT"],
            )

            if response_schema:
                config.response_mime_type = "application/json"
                config.response_schema = response_schema

            # Generate
            response = await self.client.aio.models.generate_content(
                model=self.model, contents=contents, config=config
            )

            result = response.text
            logger.info(f"Content generation complete: {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Error generating content: {e}", exc_info=True)
            raise
