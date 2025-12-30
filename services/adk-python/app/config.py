"""Configuration settings for the Content Creator service."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Configuration
    service_name: str = Field(
        default="adk-content-creator",
        description="Service name for logging and monitoring",
    )
    port: int = Field(default=8002, description="Port to run the service on")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="development", description="Environment (dev/prod)")

    # Google Cloud Configuration
    google_cloud_project: str = Field(..., description="Google Cloud project ID (REQUIRED)")
    vertex_ai_location: str = Field(default="us-central1", description="Vertex AI region")

    # Cloud Storage Configuration
    cloud_storage_bucket: Optional[str] = Field(
        default=None, description="GCS bucket for file uploads"
    )
    gcs_bucket_name: Optional[str] = Field(
        default=None, description="GCS bucket name (alias for cloud_storage_bucket)"
    )
    upload_max_size_mb: int = Field(default=500, description="Max upload size in MB")

    # LLM Configuration
    default_model: str = Field(
        default="gemini-2.5-flash",
        description="Default LLM model for content generation",
    )
    default_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature (0.7 for creative)"
    )
    default_max_tokens: int = Field(
        default=8192, ge=1, le=65536, description="Max tokens to generate"
    )

    # Video Processing Configuration
    video_frame_interval: int = Field(default=2, description="Extract 1 frame every N seconds")
    max_video_duration: int = Field(
        default=600, description="Max video duration in seconds (10 min)"
    )

    # Content Generation Configuration
    default_blog_length: str = Field(
        default="medium", description="Default blog length (short/medium/long)"
    )
    default_tone: str = Field(
        default="professional", description="Default tone (casual/professional/technical)"
    )
    default_audience: str = Field(default="developers", description="Default target audience")

    # API Configuration
    api_key: Optional[SecretStr] = Field(
        default=None, description="API key for authentication (optional)"
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:8501", "http://localhost:3000"],
        description="CORS allowed origins",
    )

    # Datadog Configuration
    dd_service: str = Field(default="adk-content-creator", description="Datadog service name")
    dd_env: str = Field(default="development", description="Datadog environment")
    dd_version: str = Field(default="0.1.0", description="Datadog version")
    dd_trace_enabled: bool = Field(default=True, description="Enable Datadog APM tracing")
    dd_api_key: Optional[str] = Field(default=None, description="Datadog API key")
    dd_site: str = Field(default="datadoghq.com", description="Datadog site")
    
    # Datadog LLM Observability
    dd_llmobs_enabled: bool = Field(
        default=True, description="Enable Datadog LLM Observability"
    )
    dd_llmobs_ml_app: str = Field(
        default="datadog-content-creator", description="LLM Observability ML app name"
    )
    dd_llmobs_agentless: bool = Field(
        default=True, description="Enable agentless mode for LLMObs"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
