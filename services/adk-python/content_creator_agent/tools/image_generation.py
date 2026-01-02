"""
Image generation tools using Gemini 3 Pro Image model.

Supports generating diagrams, comics, slides, and key frames for blog posts and videos.
Can accept both text prompts and reference images for style/character consistency.
"""

import base64
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def generate_blog_image(
    prompt: str,
    image_type: str = "diagram",
    reference_image_uris: Optional[list[str]] = None,
    aspect_ratio: str = "16:9",
    output_filename: Optional[str] = None,
) -> dict[str, str]:
    """
    Generate an image for a blog post using Gemini 3 Pro Image model.

    Args:
        prompt: Text description of the image to generate
        image_type: Type of image to generate. Options:
            - "diagram": Technical diagrams, flowcharts, architecture diagrams
            - "comic": Comic-style illustrations for storytelling
            - "slide": Presentation-style visual with text and graphics
            - "infographic": Data visualization and infographics
            - "illustration": General illustrations and artwork
        reference_image_uris: Optional list of GCS URIs (gs://...) or local file paths
            for style reference, character consistency, or visual context
        aspect_ratio: Image aspect ratio. Options: "1:1", "16:9", "9:16", "4:3"
        output_filename: Optional filename to save the image (without extension)

    Returns:
        dict with:
            - "status": "success" or "error"
            - "image_path": Path to saved image file (if saved)
            - "image_base64": Base64-encoded image data
            - "prompt_used": The actual prompt sent to the model
            - "error": Error message (if status is "error")

    Example:
        # Generate a simple diagram
        result = generate_blog_image(
            prompt="Create a diagram showing how Datadog APM traces requests",
            image_type="diagram",
            aspect_ratio="16:9"
        )

        # Generate comic with character reference
        result = generate_blog_image(
            prompt="Comic panel: Developer debugging with Datadog dashboard",
            image_type="comic",
            reference_image_uris=["gs://my-bucket/character-style.png"],
            aspect_ratio="4:3"
        )
    """
    try:
        # Initialize Gemini client with Vertex AI (use global location for image models)
        client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location="global",  # Image generation models available in global endpoint
        )

        # Build content parts
        content_parts = []

        # Add reference images if provided
        if reference_image_uris:
            for uri in reference_image_uris:
                if uri.startswith("gs://"):
                    # GCS URI
                    mime_type = _get_mime_type(uri)
                    content_parts.append(
                        types.Part.from_uri(file_uri=uri, mime_type=mime_type)
                    )
                else:
                    # Local file path
                    content_parts.append(_load_local_image(uri))

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

        # Configure generation
        generate_config = types.GenerateContentConfig(
            temperature=1.0,  # Higher for creative images
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
                image_size="1K",  # 1024px
                output_mime_type="image/png",
            ),
        )

        # Generate image (stream for progress, but collect full response)
        logger.info(
            f"Generating {image_type} image with prompt: {enhanced_prompt[:100]}..."
        )

        response_text = ""
        image_data = None

        for chunk in client.models.generate_content_stream(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=generate_config,
        ):
            # Collect text response
            if chunk.text:
                response_text += chunk.text

            # Collect image data
            if hasattr(chunk, "candidates") and chunk.candidates:
                for candidate in chunk.candidates:
                    if hasattr(candidate, "content") and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, "inline_data") and part.inline_data:
                                image_data = part.inline_data.data

        if not image_data:
            return {
                "status": "error",
                "error": "No image was generated by the model",
                "response_text": response_text,
            }

        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # Save to file if requested
        image_path = None
        if output_filename:
            output_dir = Path("output/images")
            output_dir.mkdir(parents=True, exist_ok=True)
            image_path = output_dir / f"{output_filename}.png"

            with open(image_path, "wb") as f:
                f.write(image_data)

            logger.info(f"Image saved to: {image_path}")
            image_path = str(image_path)

        return {
            "status": "success",
            "image_path": image_path,
            "image_base64": image_base64,
            "prompt_used": enhanced_prompt,
            "response_text": response_text,
            "image_type": image_type,
            "aspect_ratio": aspect_ratio,
        }

    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }


def generate_video_keyframes(
    script: str,
    num_keyframes: int = 4,
    reference_style_uri: Optional[str] = None,
    aspect_ratio: str = "16:9",
) -> dict[str, any]:
    """
    Generate key frames for a video based on a script.

    Args:
        script: Video script with scene descriptions
        num_keyframes: Number of key frames to generate (default: 4)
        reference_style_uri: Optional GCS URI or local path for visual style reference
        aspect_ratio: Aspect ratio for frames. Options: "16:9", "9:16", "1:1"

    Returns:
        dict with:
            - "status": "success" or "error"
            - "keyframes": List of dicts, each with:
                - "frame_number": Frame index (1-based)
                - "scene_description": Text description of the scene
                - "image_path": Path to saved frame
                - "image_base64": Base64-encoded frame data
            - "error": Error message (if status is "error")

    Example:
        result = generate_video_keyframes(
            script="Scene 1: Developer opens Datadog dashboard...",
            num_keyframes=4,
            aspect_ratio="16:9"
        )
    """
    try:
        # Split script into scenes
        scenes = _extract_scenes_from_script(script, num_keyframes)

        keyframes = []
        for i, scene_desc in enumerate(scenes, start=1):
            logger.info(f"Generating keyframe {i}/{num_keyframes}...")

            # Generate image for this scene
            reference_uris = [reference_style_uri] if reference_style_uri else None

            result = generate_blog_image(
                prompt=f"Video keyframe: {scene_desc}",
                image_type="illustration",
                reference_image_uris=reference_uris,
                aspect_ratio=aspect_ratio,
                output_filename=f"keyframe_{i}",
            )

            if result["status"] == "success":
                keyframes.append(
                    {
                        "frame_number": i,
                        "scene_description": scene_desc,
                        "image_path": result.get("image_path"),
                        "image_base64": result.get("image_base64"),
                    }
                )
            else:
                logger.warning(f"Failed to generate keyframe {i}: {result.get('error')}")

        return {
            "status": "success",
            "keyframes": keyframes,
            "total_frames": len(keyframes),
        }

    except Exception as e:
        logger.error(f"Error generating video keyframes: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }


def create_character_reference(
    description: str,
    style: str = "professional",
    output_filename: str = "character_ref",
) -> dict[str, str]:
    """
    Create a character reference image for consistent visual style.

    Args:
        description: Description of the character (appearance, clothing, style)
        style: Visual style. Options:
            - "professional": Business/professional style
            - "comic": Comic book style
            - "cartoon": Cartoon/animated style
            - "realistic": Photorealistic style
        output_filename: Filename for the reference image

    Returns:
        dict with character reference details and image data

    Example:
        result = create_character_reference(
            description="Friendly developer wearing Datadog t-shirt, casual style",
            style="comic",
            output_filename="datadog_developer"
        )
    """
    prompt = f"""Create a character reference sheet for: {description}

Style: {style}

Include:
- Front view
- Side view (profile)
- Expression variations (neutral, happy, focused)
- Color palette reference
- Key distinctive features

This will be used for consistent character appearance across multiple images."""

    return generate_blog_image(
        prompt=prompt,
        image_type="illustration",
        aspect_ratio="16:9",
        output_filename=output_filename,
    )


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
    """Enhance prompt based on image type."""
    enhancements = {
        "diagram": "Create a clear, professional technical diagram. Use clean lines, proper spacing, and clear labels. ",
        "comic": "Create a comic-style illustration with bold outlines, dynamic composition, and expressive characters. ",
        "slide": "Create a presentation slide with a clean layout, readable text, and professional graphics. Include title and key points. ",
        "infographic": "Create an infographic with data visualizations, icons, and a clear information hierarchy. Use colors to guide attention. ",
        "illustration": "Create a high-quality illustration with good composition, lighting, and detail. ",
    }

    enhancement = enhancements.get(image_type, "")
    return f"{enhancement}{prompt}"


def _extract_scenes_from_script(script: str, num_scenes: int) -> list[str]:
    """Extract scene descriptions from script for keyframe generation."""
    # Simple extraction: split by common scene markers
    lines = script.split("\n")

    scenes = []
    current_scene = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Scene markers
        if any(
            marker in line.lower()
            for marker in ["scene", "[", "visual:", "shot:", "frame:"]
        ):
            if current_scene:
                scenes.append(" ".join(current_scene))
                current_scene = []
            current_scene.append(line)
        else:
            current_scene.append(line)

    # Add last scene
    if current_scene:
        scenes.append(" ".join(current_scene))

    # If we have more scenes than needed, sample evenly
    if len(scenes) > num_scenes:
        step = len(scenes) / num_scenes
        scenes = [scenes[int(i * step)] for i in range(num_scenes)]

    # If we have fewer scenes, duplicate evenly
    while len(scenes) < num_scenes:
        scenes.append(scenes[-1] if scenes else "Generic scene")

    return scenes[:num_scenes]

