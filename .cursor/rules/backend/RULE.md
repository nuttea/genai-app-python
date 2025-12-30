# Backend Development Rules

## Scope
**Paths**: `services/fastapi-backend/**/*.py`, `services/fastapi-backend/pyproject.toml`

## FastAPI Architecture

### Project Structure
```
services/fastapi-backend/app/
├── api/v1/endpoints/     # Route handlers (thin layer)
├── core/                 # Core utilities (security, rate limiting, logging)
├── models/               # Pydantic models (request/response schemas)
├── services/             # Business logic (fat layer)
├── config.py             # Settings with Pydantic BaseSettings
└── main.py               # FastAPI app initialization
```

### Code Standards

#### Type Hints (Required)
```python
# ✅ Good
async def extract_votes(
    files: list[UploadFile],
    llm_config: Optional[LLMConfig] = None
) -> VoteExtractionResponse:
    pass

# ❌ Bad
async def extract_votes(files, llm_config=None):
    pass
```

#### Pydantic Models
```python
# ✅ Good - Use Field with validation
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    model: str = Field(default="gemini-2.5-flash", description="Model name")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=16384, gt=0, le=65536)

# ❌ Bad - No validation
class LLMConfig(BaseModel):
    model: str = "gemini-2.5-flash"
    temperature: float = 0.0
```

#### Error Handling
```python
# ✅ Good - Structured errors
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={
        "message": "Invalid file format",
        "allowed_formats": ["jpg", "jpeg", "png"],
        "received": file_extension
    }
)

# ❌ Bad - Generic errors
raise Exception("Invalid file")
```

#### Async/Await
```python
# ✅ Good - Async for I/O
async def fetch_models() -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        return response.json()

# ❌ Bad - Sync blocking call
def fetch_models() -> list[dict]:
    response = requests.get(url)
    return response.json()
```

### API Endpoint Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.rate_limiting import limiter
from app.core.security import verify_api_key
from app.models.your_model import RequestModel, ResponseModel
from app.services.your_service import your_service

router = APIRouter(prefix="/your-resource", tags=["your-resource"])

@router.post(
    "/action",
    response_model=ResponseModel,
    summary="Clear summary of what this does",
    description="Detailed description with examples"
)
@limiter.limit("10/minute")  # Rate limiting
async def action_endpoint(
    request: RequestModel,
    api_key: str = Depends(verify_api_key)  # Authentication
) -> ResponseModel:
    """
    Endpoint docstring with details.

    Args:
        request: Description of request
        api_key: API key for authentication

    Returns:
        ResponseModel: Description of response

    Raises:
        HTTPException: When validation fails
    """
    try:
        result = await your_service.process(request)
        return ResponseModel(success=True, data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### Service Layer Pattern

```python
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class YourService:
    """Service for handling business logic."""

    async def process(
        self,
        data: dict[str, Any],
        config: Optional[Config] = None
    ) -> dict[str, Any]:
        """
        Process data with optional configuration.

        Args:
            data: Input data to process
            config: Optional configuration

        Returns:
            Processed result dictionary

        Raises:
            ValueError: If data validation fails
        """
        logger.info("Processing data", extra={"data_keys": list(data.keys())})

        try:
            # Business logic here
            result = await self._do_processing(data, config)
            logger.info("Processing complete", extra={"result_size": len(result)})
            return result

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            raise ValueError(f"Failed to process: {str(e)}")
```

### Configuration Management

```python
# config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Google Cloud
    google_cloud_project: str = Field(description="GCP Project ID")
    vertex_ai_location: str = Field(default="us-central1")

    # API Configuration
    api_key_required: bool = Field(default=False)
    cors_origins: list[str] = Field(default=["*"])

    # LLM Configuration
    default_model: str = Field(default="gemini-2.5-flash")
    default_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=16384, ge=1, le=65536)

settings = Settings()
```

### Logging with Datadog

```python
import logging

logger = logging.getLogger(__name__)

# ✅ Good - Structured logging with extra fields
logger.info(
    "Processing request",
    extra={
        "user_id": user_id,
        "request_size": len(data),
        "model": llm_config.model
    }
)

# ✅ Good - Error logging with context
logger.error(
    f"Failed to process: {error}",
    extra={"error_type": type(error).__name__},
    exc_info=True
)

# ❌ Bad - Plain string logging
logger.info(f"Processing request for user {user_id}")
```

### Datadog APM Integration

```python
from ddtrace import tracer

# ✅ Good - Add custom spans
with tracer.trace("custom.operation", service="fastapi-backend") as span:
    span.set_tag("operation.type", "llm_generation")
    span.set_tag("model", model_name)
    result = await process_with_llm(data)
    span.set_metric("tokens.input", input_tokens)
    span.set_metric("tokens.output", output_tokens)
```

### Testing

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_endpoint_success():
    """Test successful endpoint response."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/resource/action",
            json={"key": "value"},
            headers={"X-API-Key": "test-key"}
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
```

## Dependencies

### Use Poetry (Not pip)
```bash
# ✅ Good
poetry add package-name
poetry add --group dev package-name

# ❌ Bad
pip install package-name
```

### Lock File
- Always commit `poetry.lock`
- Run `poetry lock --no-update` after manual `pyproject.toml` edits
- Run `poetry update` to update all dependencies

## Common Patterns

### Health Check
```python
@router.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"status": "healthy"})
```

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting
```python
from app.core.rate_limiting import limiter

@router.post("/expensive-operation")
@limiter.limit("10/minute")
@limiter.limit("100/hour")
async def expensive_operation():
    pass
```

## Don't

- ❌ Don't use `print()` - use `logger` instead
- ❌ Don't use sync I/O - use async/await
- ❌ Don't hardcode values - use settings
- ❌ Don't ignore type hints
- ❌ Don't catch generic `Exception` without re-raising
- ❌ Don't use `pip` - use `poetry`
- ❌ Don't modify `docker-compose.yml` entrypoint/command for Cloud Run
