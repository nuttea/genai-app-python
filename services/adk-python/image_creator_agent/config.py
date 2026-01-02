"""Configuration for Image Creator Agent."""

import os
from dataclasses import dataclass


@dataclass
class ImageCreatorConfig:
    """Configuration for the Image Creator agent."""

    # Model configuration
    model: str = "gemini-3-pro-image-preview"
    location: str = "global"  # Image models available in global endpoint
    
    # GCP Configuration
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    
    # Generation parameters
    temperature: float = 1.0  # Higher for creative image generation
    top_p: float = 0.95
    max_output_tokens: int = 32768
    
    # Response configuration
    response_modalities: list[str] = None  # Will be ["TEXT", "IMAGE"]
    
    # Image configuration defaults
    default_aspect_ratio: str = "1:1"  # 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
    default_image_size: str = "1K"  # 1024px
    output_mime_type: str = "image/png"
    
    # Safety settings (OFF for creative flexibility, adjust as needed)
    safety_threshold: str = "OFF"
    
    def __post_init__(self):
        """Initialize response modalities."""
        if self.response_modalities is None:
            self.response_modalities = ["TEXT", "IMAGE"]


# Global configuration instance
config = ImageCreatorConfig()

