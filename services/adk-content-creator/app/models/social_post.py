"""Data models for social media posts."""

from pydantic import BaseModel, Field


class LinkedInPost(BaseModel):
    """LinkedIn post content."""

    content: str = Field(description="Post content (max 3000 chars)")
    hashtags: list[str] = Field(default=[], description="Suggested hashtags")
    image_suggestion: str = Field(
        default="", description="Suggested image or graphic"
    )


class TwitterThread(BaseModel):
    """Twitter/X thread."""

    tweets: list[str] = Field(description="Thread of tweets (max 280 chars each)")
    hashtags: list[str] = Field(default=[], description="Suggested hashtags")


class InstagramPost(BaseModel):
    """Instagram post content."""

    caption: str = Field(description="Post caption (max 2200 chars)")
    hashtags: list[str] = Field(default=[], description="Suggested hashtags")
    alt_text: str = Field(description="Alt text for image")
    image_suggestion: str = Field(description="Suggested image or design")


class SocialMediaPosts(BaseModel):
    """Collection of social media posts."""

    linkedin: LinkedInPost
    twitter: TwitterThread
    instagram: InstagramPost


class SocialMediaResponse(BaseModel):
    """Response containing social media posts."""

    social_id: str = Field(description="Unique ID")
    social_posts: SocialMediaPosts
    product_mentioned: str = Field(description="Datadog product mentioned")

