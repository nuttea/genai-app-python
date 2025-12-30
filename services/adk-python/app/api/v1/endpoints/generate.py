"""
Content Generation API Endpoints

Generates blog posts, video scripts, and social media content
using Gemini's multimodal capabilities.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from ddtrace import tracer

from app.services.gemini_service import GeminiService
from app.core.file_storage import FileStorageService
from app.models.content_input import ContentGenerationRequest
from app.models.blog_post import BlogPostResponse
from app.models.video_script import VideoScriptResponse
from app.models.social_post import SocialMediaResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("/blog-post", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
@tracer.wrap(name="api.generate_blog_post", service="adk-content-creator")
async def generate_blog_post(request: ContentGenerationRequest) -> BlogPostResponse:
    """
    Generate a blog post about Datadog products/features.

    Inputs can include:
    - Text description or draft
    - Video demos (GCS URIs)
    - Screenshots/images (GCS URIs)
    - Markdown drafts

    Returns a professional, SEO-optimized blog post.
    """
    try:
        logger.info(f"Generating blog post: {request.title or 'Untitled'}")

        gemini_service = GeminiService()

        # Build generation prompt
        prompt = _build_blog_prompt(request)

        # Download media files if needed (for Gemini file API)
        media_uris = []
        if request.media_files:
            storage_service = FileStorageService()
            for gcs_uri in request.media_files:
                # For simplicity, we'll pass GCS URIs directly
                # In production, you might need to download and upload to Gemini
                media_uris.append(gcs_uri)

        # Generate content
        blog_content = await gemini_service.generate_content(
            prompt=prompt,
            media_uris=media_uris if media_uris else None,
            temperature=0.7,
            max_tokens=16384,
        )

        # Parse response (assuming markdown format)
        # Extract title, summary, tags from generated content
        title, summary, content, tags = _parse_blog_content(blog_content, request.title)

        logger.info(f"Blog post generated successfully: {len(content)} characters")

        # Generate unique post ID
        import uuid
        from datetime import datetime

        post_id = f"post_{uuid.uuid4().hex[:12]}"

        # Calculate word count and reading time
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)  # ~200 words per minute

        # Convert markdown to HTML (simple conversion)
        html_content = content.replace("\n## ", "\n<h2>").replace("</h2>", "</h2>\n")
        html_content = html_content.replace("\n# ", "\n<h1>").replace("</h1>", "</h1>\n")
        html_content = html_content.replace("\n\n", "</p>\n<p>")
        html_content = f"<div>{html_content}</div>"

        # Build SEO metadata
        from app.models.blog_post import SEOMetadata, BlogPost

        seo_metadata = SEOMetadata(
            title_tag=title[:60],
            meta_description=summary[:160] if summary else title[:160],
            keywords=tags[:5],  # Top 5 keywords
        )

        # Build blog post object
        blog_post = BlogPost(
            title=title,
            subtitle=summary if summary else None,
            content=content,
            html_content=html_content,
            word_count=word_count,
            reading_time_minutes=reading_time,
            seo_metadata=seo_metadata,
            tags=tags,
            generated_from="text" if not request.media_files else "multimodal",
            product_mentioned="Datadog",
        )

        # Build response
        return BlogPostResponse(
            post_id=post_id,
            blog_post=blog_post,
            preview_url=f"/preview/{post_id}",
            download_urls={
                "markdown": f"/download/{post_id}.md",
                "html": f"/download/{post_id}.html",
                "pdf": f"/download/{post_id}.pdf",
            },
        )

    except Exception as e:
        logger.error(f"Error generating blog post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate blog post: {str(e)}",
        )


@router.post(
    "/video-script", response_model=VideoScriptResponse, status_code=status.HTTP_201_CREATED
)
@tracer.wrap(name="api.generate_video_script", service="adk-content-creator")
async def generate_video_script(request: ContentGenerationRequest) -> VideoScriptResponse:
    """
    Generate a 60-second video script (YouTube Shorts, TikTok, Reels).

    Perfect for:
    - Product demos
    - Feature highlights
    - Quick tutorials
    - Social media content

    Returns a structured script with scenes, voiceover, and timing.
    """
    try:
        logger.info(f"Generating video script: {request.title or 'Untitled'}")

        gemini_service = GeminiService()

        # Build video script prompt
        prompt = _build_video_script_prompt(request)

        # Handle media files
        media_uris = []
        if request.media_files:
            for gcs_uri in request.media_files:
                media_uris.append(gcs_uri)

        # Generate with structured output
        script_content = await gemini_service.generate_content(
            prompt=prompt,
            media_uris=media_uris if media_uris else None,
            temperature=0.7,
            max_tokens=8192,
        )

        # Parse script
        title, description, scenes, total_duration = _parse_video_script(
            script_content, request.title
        )

        logger.info(f"Video script generated: {len(scenes)} scenes, {total_duration}s")

        return VideoScriptResponse(
            title=title,
            description=description,
            duration_seconds=total_duration,
            scenes=scenes,
            format="youtube_shorts",  # Default format
        )

    except Exception as e:
        logger.error(f"Error generating video script: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video script: {str(e)}",
        )


@router.post(
    "/social-media", response_model=SocialMediaResponse, status_code=status.HTTP_201_CREATED
)
@tracer.wrap(name="api.generate_social_media", service="adk-content-creator")
async def generate_social_media(request: ContentGenerationRequest) -> SocialMediaResponse:
    """
    Generate social media posts for multiple platforms.

    Creates optimized posts for:
    - LinkedIn (professional, detailed)
    - Twitter/X (concise, engaging)
    - Instagram (visual-focused, hashtags)

    Returns platform-specific versions of the same content.
    """
    try:
        logger.info(f"Generating social media posts: {request.title or 'Untitled'}")

        gemini_service = GeminiService()

        # Build social media prompt
        prompt = _build_social_media_prompt(request)

        # Handle media files
        media_uris = []
        if request.media_files:
            for gcs_uri in request.media_files:
                media_uris.append(gcs_uri)

        # Generate content
        social_content = await gemini_service.generate_content(
            prompt=prompt,
            media_uris=media_uris if media_uris else None,
            temperature=0.8,  # Higher for creative social content
            max_tokens=4096,
        )

        # Parse platform-specific posts
        posts = _parse_social_media_content(social_content)

        logger.info(f"Social media posts generated: {len(posts)} platforms")

        return SocialMediaResponse(
            title=request.title or "Datadog Feature",
            posts=posts,
        )

    except Exception as e:
        logger.error(f"Error generating social media posts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate social media posts: {str(e)}",
        )


def _build_blog_prompt(request: ContentGenerationRequest) -> str:
    """Build prompt for blog post generation."""
    prompt = f"""You are an expert technical writer specializing in Datadog observability products.

Generate a professional, engaging blog post about: {request.title or "Datadog Feature"}

Topic/Description: {request.description}

Requirements:
- Professional tone, but accessible
- Include code examples where relevant
- SEO-optimized (clear headers, keywords)
- 1500-2500 words
- Markdown format
- Structure: Title, Introduction, Body (3-5 sections), Conclusion, Call-to-Action

Target Audience: DevOps engineers, SREs, developers using Datadog

Format your response as:
# [Title]

## Summary
[2-sentence summary]

## Introduction
[Engaging opening paragraph]

## [Section 1]
[Content...]

## [Section 2]
[Content...]

## Conclusion
[Summary and next steps]

---
Tags: [comma-separated tags]
"""

    if request.style:
        prompt += f"\nStyle preference: {request.style}"

    if request.target_audience:
        prompt += f"\nTarget audience: {request.target_audience}"

    return prompt


def _build_video_script_prompt(request: ContentGenerationRequest) -> str:
    """Build prompt for video script generation."""
    prompt = f"""You are a video script writer specializing in short-form technical content (YouTube Shorts, TikTok, Reels).

Create a 60-second video script about: {request.title or "Datadog Feature"}

Topic: {request.description}

Requirements:
- Exactly 60 seconds (±5 seconds)
- 5-8 scenes
- Hook in first 3 seconds
- Clear voiceover script
- Visual recommendations
- Fast-paced and engaging

Format your response as:

# Title: [Catchy title]

## Description
[One-sentence description]

## Scene 1 (0-8s) - Hook
**Visual**: [What to show]
**Voiceover**: "[Exact script]"
**Action**: [Any on-screen actions]

## Scene 2 (8-18s) - Problem
**Visual**: [What to show]
**Voiceover**: "[Exact script]"
**Action**: [Any on-screen actions]

[Continue for all scenes...]

Total Duration: 60 seconds
"""

    if request.style:
        prompt += f"\nStyle: {request.style}"

    return prompt


def _build_social_media_prompt(request: ContentGenerationRequest) -> str:
    """Build prompt for social media generation."""
    prompt = f"""You are a social media expert for tech products.

Create platform-specific posts about: {request.title or "Datadog Feature"}

Topic: {request.description}

Generate posts for:
1. LinkedIn (professional, 200-300 words, detailed)
2. Twitter/X (concise, 240 characters, engaging)
3. Instagram (visual-focused, 150 words, 10-15 hashtags)

Format:

## LinkedIn
[Professional post with context and details]

## Twitter/X
[Concise, punchy tweet]

## Instagram
[Engaging caption]

#hashtag1 #hashtag2 #hashtag3 [...]
"""

    return prompt


def _parse_blog_content(content: str, requested_title: Optional[str]) -> tuple:
    """Parse generated blog content into structured components."""
    lines = content.split("\n")

    title = requested_title or "Untitled Blog Post"
    summary = ""
    tags = ["datadog", "observability", "monitoring"]
    main_content = content

    # Extract title (first H1)
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Extract summary (usually after ## Summary)
    summary_start = False
    for i, line in enumerate(lines):
        if "## Summary" in line or "## Introduction" in line:
            summary_start = True
            continue
        if summary_start and line.strip() and not line.startswith("#"):
            summary = line.strip()
            break

    # Extract tags (usually at the end)
    for line in lines:
        if line.startswith("Tags:") or line.startswith("tags:"):
            tags_str = line.split(":", 1)[1].strip()
            tags = [tag.strip() for tag in tags_str.split(",")]
            break

    if not summary:
        summary = f"Learn about {title} and how it can improve your Datadog observability."

    return title, summary, main_content, tags


def _parse_video_script(content: str, requested_title: Optional[str]) -> tuple:
    """Parse video script into scenes."""
    from app.models.video_script import SceneDescription

    lines = content.split("\n")

    title = requested_title or "Datadog Feature Demo"
    description = ""
    scenes = []
    current_scene = None
    total_duration = 60

    # Simple parsing (in production, use more robust parsing or JSON schema)
    for line in lines:
        if line.startswith("# Title:"):
            title = line.split(":", 1)[1].strip()
        elif line.startswith("## Description"):
            description_idx = lines.index(line) + 1
            if description_idx < len(lines):
                description = lines[description_idx].strip()
        elif line.startswith("## Scene"):
            # Parse scene number and timing
            if current_scene:
                scenes.append(current_scene)

            # Extract timing from format: "## Scene 1 (0-8s)"
            import re

            match = re.search(r"Scene (\d+) \((\d+)-(\d+)s\)", line)
            if match:
                scene_num = int(match.group(1))
                start_time = int(match.group(2))
                end_time = int(match.group(3))
                duration = end_time - start_time

                current_scene = {
                    "scene_number": scene_num,
                    "start_time": start_time,
                    "duration": duration,
                    "visual_description": "",
                    "voiceover": "",
                    "on_screen_text": "",
                }
        elif current_scene:
            if "**Visual**:" in line:
                current_scene["visual_description"] = line.split(":", 1)[1].strip()
            elif "**Voiceover**:" in line:
                current_scene["voiceover"] = line.split(":", 1)[1].strip().strip('"')
            elif "**Action**:" in line or "**On-screen**:" in line:
                current_scene["on_screen_text"] = line.split(":", 1)[1].strip()

    if current_scene:
        scenes.append(current_scene)

    # Convert to SceneDescription objects
    scene_objects = [
        SceneDescription(
            scene_number=s["scene_number"],
            timing=f"{int(s['start_time'])}:{int(s['start_time'] + s['duration'])}",
            start_seconds=s["start_time"],
            end_seconds=s["start_time"] + s["duration"],
            voiceover=s["voiceover"],
            visual=s["visual_description"],
            text_overlay=s.get("on_screen_text"),
        )
        for s in scenes
    ]

    return title, description, scene_objects, total_duration


def _parse_social_media_content(content: str) -> List[dict]:
    """Parse social media posts for different platforms."""
    posts = []

    lines = content.split("\n")
    current_platform = None
    current_content = []

    for line in lines:
        if "## LinkedIn" in line:
            if current_platform and current_content:
                posts.append(
                    {"platform": current_platform, "content": "\n".join(current_content).strip()}
                )
            current_platform = "linkedin"
            current_content = []
        elif "## Twitter" in line or "## X" in line:
            if current_platform and current_content:
                posts.append(
                    {"platform": current_platform, "content": "\n".join(current_content).strip()}
                )
            current_platform = "twitter"
            current_content = []
        elif "## Instagram" in line:
            if current_platform and current_content:
                posts.append(
                    {"platform": current_platform, "content": "\n".join(current_content).strip()}
                )
            current_platform = "instagram"
            current_content = []
        elif current_platform and line.strip() and not line.startswith("#"):
            current_content.append(line)

    # Add last platform
    if current_platform and current_content:
        posts.append({"platform": current_platform, "content": "\n".join(current_content).strip()})

    return posts
