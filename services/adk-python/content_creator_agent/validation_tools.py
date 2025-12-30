"""
Validation Tools for Content Creator Agent

Tools used by Loop Agents to validate generated content.
Following ADK blog-writer sample pattern.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def validate_blog_outline(outline: str) -> dict:
    """
    Validate a blog post outline.

    Used by robust_blog_planner Loop Agent to ensure outline quality.

    Args:
        outline: The blog post outline to validate (markdown format)

    Returns:
        Dictionary with validation status and feedback
    """
    try:
        # Basic validation checks
        issues = []

        # Check if outline is not empty
        if not outline or len(outline.strip()) < 50:
            issues.append("Outline is too short or empty")

        # Check for title
        if "# " not in outline and "## " not in outline:
            issues.append("Missing title or headings")

        # Check for introduction section
        if "introduction" not in outline.lower() and "intro" not in outline.lower():
            issues.append("Missing introduction section")

        # Check for main body sections
        if outline.count("##") < 2:
            issues.append("Not enough main sections (need at least 2)")

        # Check for conclusion
        if "conclusion" not in outline.lower():
            issues.append("Missing conclusion section")

        # Determine if valid
        is_valid = len(issues) == 0

        if is_valid:
            return {
                "valid": True,
                "message": "Outline is well-structured and complete",
                "feedback": "Good outline with clear sections!",
            }
        return {
            "valid": False,
            "message": "Outline needs improvements",
            "feedback": "Issues found:\n" + "\n".join(f"- {issue}" for issue in issues),
            "issues": issues,
        }

    except Exception as e:
        logger.error(f"Error validating outline: {e}")
        return {
            "valid": False,
            "message": f"Validation error: {e!s}",
        }


def validate_blog_post(blog_post: str, outline: Optional[str] = None) -> dict:
    """
    Validate a blog post for completeness and quality.

    Used by robust_blog_writer Loop Agent to ensure post quality.

    Args:
        blog_post: The blog post content to validate (markdown format)
        outline: Optional outline to check against

    Returns:
        Dictionary with validation status and feedback
    """
    try:
        issues = []

        # Check length
        if len(blog_post) < 500:
            issues.append("Blog post is too short (< 500 characters)")

        # Check for title
        if not blog_post.startswith("#"):
            issues.append("Missing title (should start with #)")

        # Check for headings
        heading_count = blog_post.count("##")
        if heading_count < 2:
            issues.append(f"Not enough sections (found {heading_count}, need at least 2)")

        # Check for code examples (important for technical content)
        has_code = "```" in blog_post or "`" in blog_post
        if not has_code:
            issues.append("No code examples or inline code found")

        # Check for Datadog references (domain-specific)
        has_datadog = "datadog" in blog_post.lower()
        if not has_datadog:
            issues.append("No mention of Datadog products/features")

        # Check if follows outline (if provided)
        if outline:
            outline_sections = [
                line.strip() for line in outline.split("\n") if line.strip().startswith("##")
            ]
            if len(outline_sections) > 0:
                # Check if post has similar structure
                post_sections = [
                    line.strip() for line in blog_post.split("\n") if line.strip().startswith("##")
                ]
                if len(post_sections) < len(outline_sections) - 1:
                    issues.append("Blog post doesn't follow outline structure")

        # Determine if valid
        is_valid = len(issues) == 0

        if is_valid:
            return {
                "valid": True,
                "message": "Blog post is complete and well-structured",
                "feedback": "Excellent blog post with good technical depth!",
                "word_count": len(blog_post.split()),
            }
        return {
            "valid": False,
            "message": "Blog post needs improvements",
            "feedback": "Issues found:\n" + "\n".join(f"- {issue}" for issue in issues),
            "issues": issues,
            "word_count": len(blog_post.split()),
        }

    except Exception as e:
        logger.error(f"Error validating blog post: {e}")
        return {
            "valid": False,
            "message": f"Validation error: {e!s}",
        }


def validate_video_script(script: str) -> dict:
    """
    Validate a video script for 60-second format.

    Args:
        script: The video script to validate

    Returns:
        Dictionary with validation status and feedback
    """
    try:
        issues = []

        # Check for timing markers
        if "[" not in script or ":" not in script:
            issues.append("Missing timing markers (e.g., [0:00-0:05])")

        # Check for visual cues
        if "[VISUAL" not in script.upper() and "[SCREEN" not in script.upper():
            issues.append("Missing visual cues ([VISUAL:] or [SCREEN:])")

        # Check for hook (first 3 seconds)
        if "hook" not in script.lower() and "[0:00" not in script:
            issues.append("Missing hook in first 3 seconds")

        # Check length (should be around 60 seconds of content)
        word_count = len(script.split())
        if word_count < 80:  # ~150 words per minute, so ~150 words for 60s
            issues.append(f"Script too short ({word_count} words, need ~100-150)")
        elif word_count > 180:
            issues.append(f"Script too long ({word_count} words, need ~100-150)")

        is_valid = len(issues) == 0

        if is_valid:
            return {
                "valid": True,
                "message": "Video script is well-structured",
                "feedback": "Great script with clear timing and visuals!",
            }
        return {
            "valid": False,
            "message": "Video script needs improvements",
            "feedback": "Issues found:\n" + "\n".join(f"- {issue}" for issue in issues),
            "issues": issues,
        }

    except Exception as e:
        logger.error(f"Error validating video script: {e}")
        return {
            "valid": False,
            "message": f"Validation error: {e!s}",
        }
