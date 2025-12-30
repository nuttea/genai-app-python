"""Data models for blog posts."""

from datetime import datetime

from pydantic import BaseModel, Field


class SEOMetadata(BaseModel):
    """SEO metadata for blog post."""

    title_tag: str = Field(description="SEO title tag (50-60 chars)")
    meta_description: str = Field(description="Meta description (150-160 chars)")
    keywords: list[str] = Field(default=[], description="Target keywords")
    canonical_url: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None


class BlogPost(BaseModel):
    """Generated blog post."""

    title: str = Field(description="Blog post title")
    subtitle: str | None = Field(default=None, description="Subtitle or tagline")
    content: str = Field(description="Blog post content (Markdown)")
    html_content: str = Field(description="Blog post content (HTML)")

    # Metadata
    author: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    word_count: int = Field(description="Word count")
    reading_time_minutes: int = Field(description="Estimated reading time")

    # SEO
    seo_metadata: SEOMetadata

    # Tags and categories
    tags: list[str] = Field(default=[], description="Blog post tags")
    category: str | None = Field(default=None, description="Primary category")

    # Source
    generated_from: str = Field(description="What this was generated from (text, video, images)")
    product_mentioned: str | None = Field(default=None, description="Datadog product mentioned")


class BlogPostResponse(BaseModel):
    """Response containing generated blog post."""

    post_id: str = Field(description="Unique post ID")
    blog_post: BlogPost
    preview_url: str = Field(description="URL to preview the post")
    download_urls: dict[str, str] = Field(description="Download URLs for markdown, html, etc.")
