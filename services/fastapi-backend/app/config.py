"""Configuration management using Pydantic Settings."""

from typing import Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Google Cloud Configuration
    google_cloud_project: str = Field(default="test-project", description="GCP Project ID")
    google_application_credentials: str = Field(
        default="",
        description="Optional: Path to service account key. If not set, uses gcloud application-default credentials",
    )
    vertex_ai_location: str = Field(default="us-central1", description="GCP region")

    # FastAPI Configuration
    fastapi_env: str = Field(default="development", description="Environment")
    fastapi_host: str = Field(default="0.0.0.0", description="Host to bind to")
    fastapi_port: int = Field(default=8000, description="Port to bind to")
    log_level: str = Field(default="info", description="Logging level")

    # CORS Configuration
    cors_origins: Union[list[str], str] = Field(
        default="http://localhost:3000,http://localhost:8000,http://localhost:8501",
        description="Allowed CORS origins (comma-separated or list)",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    api_title: str = Field(default="GenAI FastAPI Backend", description="API title")
    api_version: str = Field(default="0.1.0", description="API version")
    api_key: str = Field(default="", description="API key for authentication (required if set)")
    api_key_required: bool = Field(
        default=False, description="Whether API key validation is enforced"
    )

    # Vertex AI Model Configuration
    default_model: str = Field(default="gemini-2.5-flash", description="Default model")
    default_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=16384, ge=1, le=65536)
    default_top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    default_top_k: int = Field(default=40, ge=1, le=100)
    
    # Google AI API Configuration (for dynamic model listing)
    gemini_api_key: str = Field(
        default="", 
        description="Google AI API key for dynamic model listing (optional)"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60)

    # Monitoring
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=False)

    # Development
    debug: bool = Field(default=False)
    reload: bool = Field(default=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.fastapi_env.lower() in ("development", "dev", "local")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.fastapi_env.lower() in ("production", "prod")


# Global settings instance
settings = Settings()
