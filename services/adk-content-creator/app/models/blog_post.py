"""Data models for blog posts."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SEOMetadata(BaseModel):
    """SEO metadata for blog post."""

    title_tag: str = Field(description="SEO title tag (50-60 chars)")
    meta_description: str = Field(
        description="Meta description (150-160 chars)"
    )
    keywords: list[str] = Field(default=[], description="Target keywords")
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None


class BlogPost(BaseModel):
    """Generated blog post."""

    title: str = Field(description="Blog post title")
    subtitle: Optional[str] = Field(default=None, description="Subtitle or tagline")
    content: str = Field(description="Blog post content (Markdown)")
    html_content: str = Field(description="Blog post content (HTML)")

    # Metadata
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    word_count: int = Field(description="Word count")
    reading_time_minutes: int = Field(description="Estimated reading time")

    # SEO
    seo_metadata: SEOMetadata

    # Tags and categories
    tags: list[str] = Field(default=[], description="Blog post tags")
    category: Optional[str] = Field(default=None, description="Primary category")

    # Source
    generated_from: str = Field(
        description="What this was generated from (text, video, images)"
    )
    product_mentioned: Optional[str] = Field(
        default=None, description="Datadog product mentioned"
    )


class BlogPostResponse(BaseModel):
    """Response containing generated blog post."""

    post_id: str = Field(description="Unique post ID")
    blog_post: BlogPost
    preview_url: str = Field(description="URL to preview the post")
    download_urls: dict[str, str] = Field(
        description="Download URLs for markdown, html, etc."
    )

