"""Image generation service using Google Gemini 3 Pro Image."""

import base64
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Image generation configuration
MODEL_NAME = "gemini-3-pro-image-preview"
UPLOADS_DIR = Path("/app/uploads")
UPLOADS_DIR.mkdir(exist_ok=True)


class ImageGenerationService:
    """Service for generating images using Gemini 3 Pro Image."""

    def __init__(self):
        """Initialize the image generation service."""
        self.client = genai.Client(
            vertexai=True,
            project=os.environ.get("GCP_PROJECT_ID", "datadog-sandbox"),
            location="global",
        )
        logger.info("✅ Image Generation Service initialized")

    async def generate_image(
        self,
        prompt: str,
        image_type: str = "illustration",
        aspect_ratio: str = "1:1",
        reference_images_base64: Optional[list[dict]] = None,
    ) -> dict:
        """
        Generate an image using Gemini 3 Pro Image.

        Args:
            prompt: Text description of the image to generate
            image_type: Type of image (comic, diagram, slide, etc.)
            aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:2)
            reference_images_base64: List of reference images with format:
                [{"data": "base64_string", "mime_type": "image/png"}, ...]

        Returns:
            dict: Response with status, image_url, and metadata
        """
        try:
            logger.info(
                f"🎨 Generating {image_type} image with aspect ratio {aspect_ratio}"
            )

            # Build content parts
            parts = []

            # Add reference images if provided
            if reference_images_base64:
                for idx, ref_img in enumerate(reference_images_base64):
                    try:
                        image_data = base64.b64decode(ref_img["data"])
                        mime_type = ref_img.get("mime_type", "image/png")
                        parts.append(
                            types.Part.from_bytes(data=image_data, mime_type=mime_type)
                        )
                        logger.info(
                            f"✅ Added reference image {idx + 1}: {mime_type}, {len(image_data)} bytes"
                        )
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Failed to process reference image {idx + 1}: {e}"
                        )

            # Build enhanced prompt based on image type
            enhanced_prompt = self._build_prompt(prompt, image_type)
            parts.append(types.Part.from_text(text=enhanced_prompt))

            # Create content
            contents = [types.Content(role="user", parts=parts)]

            # Configure generation
            generate_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                max_output_tokens=32768,
                response_modalities=["TEXT", "IMAGE"],
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT", threshold="OFF"
                    ),
                ],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size="1K",
                    output_mime_type="image/png",
                ),
            )

            # Generate image (streaming to collect both text and image)
            logger.info(f"📤 Sending request to {MODEL_NAME}...")
            text_response = ""
            image_data = None
            image_mime_type = None

            for chunk in self.client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=contents,
                config=generate_config,
            ):
                # Collect text
                if chunk.text:
                    text_response += chunk.text

                # Extract image from inline_data
                if hasattr(chunk, "candidates") and chunk.candidates:
                    for candidate in chunk.candidates:
                        if hasattr(candidate, "content") and candidate.content:
                            if hasattr(candidate.content, "parts"):
                                for part in candidate.content.parts:
                                    if hasattr(part, "inline_data") and part.inline_data:
                                        image_data = part.inline_data.data
                                        image_mime_type = part.inline_data.mime_type
                                        logger.info(
                                            f"✅ Image received: {image_mime_type}, {len(image_data)} bytes"
                                        )

            # Save image to file
            if image_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = uuid.uuid4().hex[:8]
                filename = f"{timestamp}_{unique_id}.png"
                file_path = UPLOADS_DIR / filename

                with open(file_path, "wb") as f:
                    f.write(image_data)

                image_url = f"/uploads/{filename}"
                logger.info(
                    f"✅ Image saved: {image_url} ({len(image_data)} bytes)"
                )

                return {
                    "status": "success",
                    "image_url": image_url,
                    "mime_type": image_mime_type or "image/png",
                    "text_response": text_response.strip() or "Image generated successfully",
                    "prompt": prompt,
                    "image_type": image_type,
                    "aspect_ratio": aspect_ratio,
                    "file_size_bytes": len(image_data),
                }
            else:
                logger.error("❌ No image data received from model")
                return {
                    "status": "error",
                    "error": "No image data received from model",
                    "text_response": text_response,
                }

        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }

    def _build_prompt(self, prompt: str, image_type: str) -> str:
        """Build enhanced prompt based on image type."""
        type_instructions = {
            "comic": "Create a comic-style illustration with bold outlines, dynamic composition, and expressive characters.",
            "diagram": "Create a clear, professional technical diagram with labels, arrows, and structured layout.",
            "slide": "Create a presentation slide with a clean design, clear typography, and visual hierarchy.",
            "infographic": "Create an infographic with data visualization, icons, and clear information flow.",
            "illustration": "Create a detailed illustration with artistic style and attention to visual appeal.",
            "photo": "Create a photorealistic image with natural lighting and realistic details.",
        }

        instruction = type_instructions.get(image_type, "Create an image")
        return f"{instruction}\n\n{prompt}"

