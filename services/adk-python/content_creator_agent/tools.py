"""
Tools for Content Creator Agent

Functions that agents can use to perform actions.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def save_content_to_file(content: str, filename: str, output_dir: str = "output") -> dict:
    """
    Save generated content to a markdown file.

    Args:
        content: The content to save (markdown format)
        filename: Filename without extension (e.g., "my-blog-post")
        output_dir: Output directory (default: "output")

    Returns:
        Dictionary with status and file path
    """
    try:
        # Ensure filename has .md extension
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Full file path
        file_path = output_path / filename

        # Write content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Content saved to: {file_path}")

        return {
            "status": "success",
            "message": f"Content saved successfully",
            "file_path": str(file_path.absolute()),
            "size_bytes": len(content.encode("utf-8")),
        }

    except Exception as e:
        logger.error(f"Error saving content: {e}")
        return {
            "status": "error",
            "message": f"Failed to save content: {str(e)}",
        }


def analyze_media_file(file_path: str) -> dict:
    """
    Analyze a media file (video, image, document) to extract insights.

    This is a placeholder that would integrate with:
    - Gemini multimodal for video/image analysis
    - Text extraction for documents
    - ADK Artifacts for file management

    Args:
        file_path: Path to the media file

    Returns:
        Dictionary with analysis results
    """
    try:
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return {
                "status": "error",
                "message": f"File not found: {file_path}",
            }

        # Get file info
        file_ext = file_path_obj.suffix.lower()
        file_size = file_path_obj.stat().st_size

        # Determine file type
        if file_ext in [".mp4", ".mov", ".avi", ".webm"]:
            file_type = "video"
            analysis = "Video file detected. In production, this would use Gemini's native video processing to extract key frames, identify UI elements, and generate descriptions."

        elif file_ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            file_type = "image"
            analysis = "Image file detected. In production, this would use Gemini's image analysis to identify Datadog UI components, charts, and visual elements."

        elif file_ext in [".txt", ".md", ".pdf"]:
            file_type = "document"
            # For text files, we can actually read them
            if file_ext in [".txt", ".md"]:
                with open(file_path_obj, "r", encoding="utf-8") as f:
                    content = f.read()
                    analysis = f"Document contains {len(content)} characters. Preview: {content[:500]}..."
            else:
                analysis = "PDF file detected. In production, this would extract text content."

        else:
            file_type = "unknown"
            analysis = f"Unknown file type: {file_ext}"

        logger.info(f"Analyzed file: {file_path} ({file_type})")

        return {
            "status": "success",
            "file_type": file_type,
            "file_name": file_path_obj.name,
            "file_size_bytes": file_size,
            "analysis": analysis,
            "suggestions": [
                "Use visual elements to support key points",
                "Reference specific UI components shown",
                "Include step-by-step instructions if applicable",
            ],
        }

    except Exception as e:
        logger.error(f"Error analyzing file: {e}")
        return {
            "status": "error",
            "message": f"Failed to analyze file: {str(e)}",
        }

