"""
Configuration for ADK Content Creator Agent
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for the content creator agent."""

    # Model configuration
    worker_model: str = "gemini-2.5-flash"
    
    # Google Cloud configuration
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "datadog-sandbox")
    vertex_ai_location: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    
    # Output configuration
    output_dir: str = "output"
    
    # Session configuration
    session_service_uri: str = os.getenv("SESSION_SERVICE_URI", "")
    
    # CORS configuration
    allowed_origins: list[str] = None
    
    # Web interface
    serve_web_interface: bool = os.getenv("SERVE_WEB_INTERFACE", "true").lower() == "true"
    
    def __post_init__(self):
        """Initialize default values."""
        if self.allowed_origins is None:
            self.allowed_origins = [
                "http://localhost:3000",
                "http://localhost:8501",
                "http://localhost:8002",
            ]


# Global config instance
config = Config()

