"""Data models for video scripts."""

from typing import Optional

from pydantic import BaseModel, Field


class SceneDescription(BaseModel):
    """Description of a single scene in the video."""

    scene_number: int = Field(description="Scene number (1-based)")
    timing: str = Field(description="Timing (e.g., '0:00-0:05')")
    start_seconds: float = Field(description="Start time in seconds")
    end_seconds: float = Field(description="End time in seconds")

    voiceover: str = Field(description="Voiceover script for this scene")
    visual: str = Field(description="What to show visually")
    text_overlay: Optional[str] = Field(default=None, description="Text to overlay on screen")
    b_roll: Optional[str] = Field(default=None, description="B-roll suggestions")
    transition: str = Field(default="fade", description="Transition to next scene")


class VideoMetadata(BaseModel):
    """Metadata for video script."""

    platform: str = Field(description="Target platform")
    orientation: str = Field(default="vertical_9_16", description="Video orientation")
    music_suggestion: Optional[str] = Field(default=None, description="Suggested background music")
    hashtags: list[str] = Field(default=[], description="Suggested hashtags")
    thumbnail_idea: Optional[str] = Field(default=None, description="Thumbnail suggestion")
    caption: Optional[str] = Field(default=None, description="Video caption")


class VideoScript(BaseModel):
    """Generated video script."""

    title: str = Field(description="Video title")
    duration: int = Field(description="Total duration in seconds")
    scenes: list[SceneDescription] = Field(description="Scene breakdown")
    metadata: VideoMetadata

    # Hook (0-5s)
    hook_summary: str = Field(description="Summary of the hook")

    # Additional info
    product_featured: Optional[str] = Field(default=None, description="Datadog product featured")
    call_to_action: str = Field(description="Call to action message")


class VideoScriptResponse(BaseModel):
    """Response containing generated video script."""

    script_id: str = Field(description="Unique script ID")
    video_script: VideoScript
    download_url: str = Field(description="URL to download script as JSON")
