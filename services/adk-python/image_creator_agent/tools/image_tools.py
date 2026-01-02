"""
Image generation and editing tools using Gemini 3 Pro Image.

Based on Google Cloud documentation:
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation
"""

import base64
import logging
import os
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from image_creator_agent.config import config

logger = logging.getLogger(__name__)


def generate_image(
    prompt: str,
    image_type: str = "illustration",
    aspect_ratio: str = "1:1",
    reference_image_uri: Optional[str] = None,
) -> dict[str, any]:
    """
    Generate an image from a text prompt using Gemini 3 Pro Image.

    Args:
        prompt: Text description of the image to generate
        image_type: Type of image. Options:
            - "diagram": Technical diagrams, flowcharts
            - "comic": Comic-style illustrations
            - "slide": Presentation-style visuals
            - "infographic": Data visualizations
            - "illustration": General artwork (default)
            - "photo": Photorealistic images
        aspect_ratio: Image aspect ratio. Options:
            1:1 (square), 16:9 (wide), 9:16 (tall), 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 21:9
        reference_image_uri: Optional GCS URI or local path for style reference

    Returns:
        dict with:
            - "status": "success" or "error"
            - "text_response": Text description from model
            - "image_base64": Base64-encoded image data (for frontend)
            - "mime_type": Image MIME type
            - "prompt_used": The actual prompt sent
            - "error": Error message (if status is "error")
            - "safety_blocked": True if blocked by safety filters

    Example:
        result = generate_image(
            prompt="Create a diagram showing how Datadog APM works",
            image_type="diagram",
            aspect_ratio="16:9"
        )
    """
    try:
        # Initialize client with global location for image models
        client = genai.Client(
            vertexai=True,
            project=config.project_id,
            location=config.location,  # "global"
        )

        # Build content parts
        content_parts = []

        # Add reference image if provided
        if reference_image_uri:
            if reference_image_uri.startswith("gs://"):
                # GCS URI
                mime_type = _get_mime_type(reference_image_uri)
                content_parts.append(
                    types.Part.from_uri(file_uri=reference_image_uri, mime_type=mime_type)
                )
            else:
                # Local file
                content_parts.append(_load_local_image(reference_image_uri))

        # Enhance prompt based on image type
        enhanced_prompt = _enhance_prompt(prompt, image_type)

        # Add text prompt
        content_parts.append(types.Part.from_text(text=enhanced_prompt))

        # Create content
        contents = [
            types.Content(
                role="user",
                parts=content_parts,
            ),
        ]

        # Configure generation with multimodal output
        generate_config = types.GenerateContentConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            max_output_tokens=config.max_output_tokens,
            response_modalities=config.response_modalities,  # ["TEXT", "IMAGE"]
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH", threshold=config.safety_threshold
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold=config.safety_threshold,
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold=config.safety_threshold,
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT", threshold=config.safety_threshold
                ),
            ],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=config.default_image_size,
                output_mime_type=config.output_mime_type,
            ),
        )

        logger.info(
            f"Generating {image_type} image with Gemini 3 Pro Image: {enhanced_prompt[:100]}..."
        )

        # Generate image using streaming (to collect both text and image)
        text_response = ""
        image_data = None
        image_mime_type = None
        safety_blocked = False
        finish_reason = None

        for chunk in client.models.generate_content_stream(
            model=config.model,
            contents=contents,
            config=generate_config,
        ):
            # Collect text response
            if chunk.text:
                text_response += chunk.text

            # Collect image data from inline_data
            # Based on: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation
            if hasattr(chunk, "candidates") and chunk.candidates:
                for candidate in chunk.candidates:
                    # Check finish reason for safety blocks
                    if hasattr(candidate, "finish_reason"):
                        finish_reason = str(candidate.finish_reason)
                        if "SAFETY" in finish_reason or "PROHIBITED" in finish_reason:
                            safety_blocked = True

                    # Extract image from inline_data
                    if hasattr(candidate, "content") and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, "inline_data") and part.inline_data:
                                # Image found in inline_data
                                image_data = part.inline_data.data
                                image_mime_type = part.inline_data.mime_type
                                logger.info(
                                    f"Image received: {image_mime_type}, size: {len(image_data)} bytes"
                                )

        # Check if blocked by safety filters
        if safety_blocked:
            return {
                "status": "error",
                "error": f"Content blocked by safety filters. Reason: {finish_reason}",
                "safety_blocked": True,
                "text_response": text_response,
                "prompt_used": enhanced_prompt,
            }

        # Check if image was generated
        if not image_data:
            return {
                "status": "error",
                "error": "No image was generated by the model",
                "text_response": text_response,
                "prompt_used": enhanced_prompt,
                "safety_blocked": False,
            }

        # Convert image data to base64 for frontend
        # Note: image_data from inline_data is already bytes
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode("utf-8")
        else:
            # Already string (base64)
            image_base64 = image_data

        logger.info(f"✅ Image generated successfully: {len(image_base64)} chars (base64)")

        return {
            "status": "success",
            "text_response": text_response or "Image generated successfully",
            "image_base64": image_base64,
            "mime_type": image_mime_type or config.output_mime_type,
            "prompt_used": enhanced_prompt,
            "aspect_ratio": aspect_ratio,
            "image_type": image_type,
            "safety_blocked": False,
        }

    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "safety_blocked": False,
        }


def edit_image(
    edit_prompt: str,
    original_image_base64: str,
    aspect_ratio: str = "1:1",
) -> dict[str, any]:
    """
    Edit an existing image using conversational prompts (multi-turn editing).

    Gemini 3 Pro Image supports improved multi-turn editing for conversational refinement.
    Based on: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation

    Args:
        edit_prompt: Description of changes to make (e.g., "make it more colorful")
        original_image_base64: Base64-encoded original image data
        aspect_ratio: Desired aspect ratio for edited image

    Returns:
        dict with edited image data (same format as generate_image)

    Example:
        result = edit_image(
            edit_prompt="Convert this to black and white, cartoonish style",
            original_image_base64="...",
            aspect_ratio="1:1"
        )
    """
    try:
        # Initialize client
        client = genai.Client(
            vertexai=True,
            project=config.project_id,
            location=config.location,
        )

        # Decode base64 image
        try:
            image_bytes = base64.b64decode(original_image_base64)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Invalid base64 image data: {e}",
            }

        # Build content with original image + edit instructions
        content_parts = [
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=config.output_mime_type,
            ),
            types.Part.from_text(text=edit_prompt),
        ]

        contents = [
            types.Content(
                role="user",
                parts=content_parts,
            ),
        ]

        # Configure generation
        generate_config = types.GenerateContentConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            max_output_tokens=config.max_output_tokens,
            response_modalities=config.response_modalities,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH", threshold=config.safety_threshold
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold=config.safety_threshold,
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold=config.safety_threshold,
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT", threshold=config.safety_threshold
                ),
            ],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=config.default_image_size,
                output_mime_type=config.output_mime_type,
            ),
        )

        logger.info(f"Editing image with prompt: {edit_prompt}")

        # Generate edited image
        text_response = ""
        image_data = None
        image_mime_type = None

        for chunk in client.models.generate_content_stream(
            model=config.model,
            contents=contents,
            config=generate_config,
        ):
            if chunk.text:
                text_response += chunk.text

            if hasattr(chunk, "candidates") and chunk.candidates:
                for candidate in chunk.candidates:
                    if hasattr(candidate, "content") and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, "inline_data") and part.inline_data:
                                image_data = part.inline_data.data
                                image_mime_type = part.inline_data.mime_type

        if not image_data:
            return {
                "status": "error",
                "error": "No edited image was generated",
                "text_response": text_response,
            }

        # Convert to base64
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode("utf-8")
        else:
            image_base64 = image_data

        logger.info(f"✅ Image edited successfully")

        return {
            "status": "success",
            "text_response": text_response or "Image edited successfully",
            "image_base64": image_base64,
            "mime_type": image_mime_type or config.output_mime_type,
            "edit_prompt": edit_prompt,
            "aspect_ratio": aspect_ratio,
        }

    except Exception as e:
        logger.error(f"Error editing image: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }


def analyze_image(
    image_base64: str,
    analysis_prompt: str = "Describe this image in detail",
) -> dict[str, str]:
    """
    Analyze an image and provide detailed description.

    Args:
        image_base64: Base64-encoded image data
        analysis_prompt: What to analyze (default: general description)

    Returns:
        dict with analysis text

    Example:
        result = analyze_image(
            image_base64="...",
            analysis_prompt="What objects are in this image?"
        )
    """
    try:
        # Initialize client
        client = genai.Client(
            vertexai=True,
            project=config.project_id,
            location=config.location,
        )

        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Invalid base64 image data: {e}",
            }

        # Build content with image + analysis prompt
        content_parts = [
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=config.output_mime_type,
            ),
            types.Part.from_text(text=analysis_prompt),
        ]

        contents = [
            types.Content(
                role="user",
                parts=content_parts,
            ),
        ]

        # Configure for text-only response (analysis)
        generate_config = types.GenerateContentConfig(
            temperature=0.2,  # Lower for factual analysis
            top_p=0.95,
            max_output_tokens=config.max_output_tokens,
            response_modalities=["TEXT"],  # Text only for analysis
        )

        logger.info(f"Analyzing image: {analysis_prompt}")

        # Get analysis
        text_response = ""
        for chunk in client.models.generate_content_stream(
            model=config.model,
            contents=contents,
            config=generate_config,
        ):
            if chunk.text:
                text_response += chunk.text

        if not text_response:
            return {
                "status": "error",
                "error": "No analysis generated",
            }

        logger.info(f"✅ Image analyzed successfully")

        return {
            "status": "success",
            "analysis": text_response,
            "prompt": analysis_prompt,
        }

    except Exception as e:
        logger.error(f"Error analyzing image: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }


# Helper functions


def _get_mime_type(uri: str) -> str:
    """Determine MIME type from URI."""
    uri_lower = uri.lower()
    if uri_lower.endswith(".png"):
        return "image/png"
    elif uri_lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    elif uri_lower.endswith(".gif"):
        return "image/gif"
    elif uri_lower.endswith(".webp"):
        return "image/webp"
    else:
        return "image/png"  # Default


def _load_local_image(file_path: str) -> types.Part:
    """Load image from local file path."""
    with open(file_path, "rb") as f:
        image_bytes = f.read()

    mime_type = _get_mime_type(file_path)

    return types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )


def _enhance_prompt(prompt: str, image_type: str) -> str:
    """Enhance prompt based on image type for better results."""
    enhancements = {
        "diagram": "Create a clear, professional technical diagram. Use clean lines, proper spacing, and clear labels. ",
        "comic": "Create a comic-style illustration with bold outlines, dynamic composition, and expressive characters. ",
        "slide": "Create a presentation slide with a clean layout, readable text, and professional graphics. Include title and key points. ",
        "infographic": "Create an infographic with data visualizations, icons, and a clear information hierarchy. Use colors to guide attention. ",
        "illustration": "Create a high-quality illustration with good composition, lighting, and detail. ",
        "photo": "Create a photorealistic image with natural lighting, realistic textures, and accurate details. ",
    }

    enhancement = enhancements.get(image_type, "")
    return f"{enhancement}{prompt}"

