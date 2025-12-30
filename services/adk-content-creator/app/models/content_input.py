"""Data models for content input."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Type of content to create."""

    PRODUCT_ANNOUNCEMENT = "product_announcement"
    FEATURE_TUTORIAL = "feature_tutorial"
    RELEASE_NOTES = "release_notes"
    BEST_PRACTICES = "best_practices"
    CASE_STUDY = "case_study"
    VIDEO_DEMO = "video_demo"
    CUSTOM = "custom"


class InputMethod(str, Enum):
    """Method of providing content input."""

    TEXT = "text"
    MARKDOWN = "markdown"
    VIDEO = "video"
    IMAGES = "images"
    DRAFT = "draft"


class ToneStyle(str, Enum):
    """Tone of the generated content."""

    CASUAL = "casual"
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"


class BlogLength(str, Enum):
    """Length of blog post."""

    SHORT = "short"  # ~500 words
    MEDIUM = "medium"  # ~1000 words
    LONG = "long"  # ~2000+ words


class TargetAudience(str, Enum):
    """Target audience for content."""

    DEVELOPERS = "developers"
    DEVOPS = "devops"
    SRES = "sres"
    BUSINESS_USERS = "business"
    GENERAL = "general"


class OutputFormat(BaseModel):
    """Requested output formats."""

    blog: bool = Field(default=True, description="Generate blog post")
    video_script: bool = Field(default=False, description="Generate video script")
    social_media: bool = Field(default=False, description="Generate social media posts")


class ContentStyleOptions(BaseModel):
    """Style options for content generation."""

    tone: ToneStyle = Field(default=ToneStyle.PROFESSIONAL)
    blog_length: BlogLength = Field(default=BlogLength.MEDIUM)
    audience: TargetAudience = Field(default=TargetAudience.DEVELOPERS)
    seo_optimize: bool = Field(default=True, description="Optimize for SEO")
    include_code_examples: bool = Field(
        default=False, description="Include code examples"
    )


class VideoScriptOptions(BaseModel):
    """Options for video script generation."""

    duration: int = Field(default=60, ge=15, le=60, description="Duration in seconds")
    platforms: list[str] = Field(
        default=["YouTube Shorts"],
        description="Target platforms (YouTube Shorts, TikTok, Instagram Reels)",
    )
    include_b_roll: bool = Field(default=True, description="Include B-roll suggestions")


class ContentGenerationRequest(BaseModel):
    """Request to generate content."""

    content_type: ContentType
    input_method: InputMethod
    input_text: Optional[str] = Field(default=None, description="Text or markdown input")
    video_url: Optional[str] = Field(default=None, description="GCS URL of uploaded video")
    image_urls: list[str] = Field(default=[], description="GCS URLs of uploaded images")

    output_formats: OutputFormat = Field(default_factory=OutputFormat)
    style_options: ContentStyleOptions = Field(default_factory=ContentStyleOptions)
    video_options: Optional[VideoScriptOptions] = None

    # Additional context
    product_name: Optional[str] = Field(
        default=None, description="Datadog product/feature name"
    )
    additional_notes: Optional[str] = Field(
        default=None, description="Additional context or requirements"
    )


class VideoAnalysis(BaseModel):
    """Analysis results from video processing."""

    transcript: str = Field(description="Video transcript")
    key_frames: list[str] = Field(
        default=[], description="URLs of extracted key frames"
    )
    duration: float = Field(description="Video duration in seconds")
    visual_description: str = Field(description="Description of visual elements")
    key_points: list[str] = Field(default=[], description="Key points from the video")


class ImageAnalysis(BaseModel):
    """Analysis results from image processing."""

    description: str = Field(description="Description of the image")
    text_extracted: Optional[str] = Field(
        default=None, description="Text extracted via OCR"
    )
    ui_elements: list[str] = Field(
        default=[], description="Identified UI elements (for screenshots)"
    )
    key_features: list[str] = Field(
        default=[], description="Key features visible in image"
    )

