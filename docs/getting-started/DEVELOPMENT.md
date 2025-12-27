# Development Guide

This guide covers development practices, code organization, and contribution guidelines for the GenAI Application Platform.

## Project Philosophy

- **Modularity**: Services are independent and loosely coupled
- **Type Safety**: Use type hints and validation (Pydantic)
- **Testing**: Comprehensive test coverage for all features
- **Documentation**: Clear, up-to-date documentation
- **Code Quality**: Consistent formatting and linting

## Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- Make (optional but recommended)

### Initial Setup

```bash
# Clone and setup
git clone <repo-url>
cd genai-app-python
make dev-install

# Copy environment files
cp .env.example .env
cd services/fastapi-backend
cp .env.example .env

# Configure your GCP credentials
# Edit .env files with your settings
```

### Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Code Organization

### FastAPI Backend Structure

```
services/fastapi-backend/
├── app/
│   ├── main.py           # Application entry point
│   ├── config.py         # Configuration management
│   ├── api/              # API routes
│   │   └── v1/
│   │       ├── endpoints/  # Endpoint handlers
│   │       └── router.py   # Route aggregation
│   ├── services/         # Business logic
│   ├── models/           # Pydantic models
│   ├── core/             # Core utilities
│   └── tests/            # Test suite
```

### Adding a New Endpoint

1. **Create endpoint file** in `app/api/v1/endpoints/`:

```python
# app/api/v1/endpoints/your_endpoint.py
from fastapi import APIRouter, HTTPException
from app.models.requests import YourRequest
from app.models.responses import YourResponse

router = APIRouter(prefix="/your-endpoint", tags=["your-tag"])

@router.post("", response_model=YourResponse)
async def your_endpoint(request: YourRequest) -> YourResponse:
    """Endpoint description."""
    # Implementation
    pass
```

2. **Add models** in `app/models/`:

```python
# app/models/requests.py
class YourRequest(BaseModel):
    field: str = Field(..., description="Field description")
```

3. **Register router** in `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import your_endpoint

api_router.include_router(your_endpoint.router)
```

### Adding a New Service

1. **Create service file** in `app/services/`:

```python
# app/services/your_service.py
import logging

logger = logging.getLogger(__name__)

class YourService:
    """Service description."""
    
    def __init__(self):
        """Initialize service."""
        pass
    
    async def your_method(self) -> dict:
        """Method description."""
        # Implementation
        pass

# Global instance
your_service = YourService()
```

2. **Export service** in `app/services/__init__.py`:

```python
from app.services.your_service import YourService, your_service

__all__ = ["YourService", "your_service"]
```

## Testing

### Writing Tests

Tests are located in `app/tests/` with the following structure:

```
app/tests/
├── conftest.py           # Fixtures and configuration
├── test_api/            # API endpoint tests
│   ├── test_health.py
│   └── test_your_endpoint.py
└── test_services/       # Service tests
    └── test_your_service.py
```

### Example Test

```python
# app/tests/test_api/test_your_endpoint.py
from fastapi.testclient import TestClient

def test_your_endpoint(client: TestClient):
    """Test your endpoint."""
    response = client.post(
        "/api/v1/your-endpoint",
        json={"field": "value"}
    )
    assert response.status_code == 200
    assert response.json()["field"] == "expected"
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest app/tests/test_api/test_health.py

# Run specific test
pytest app/tests/test_api/test_health.py::test_health_check

# Run with verbose output
pytest -v

# Run with print statements
pytest -s
```

### Test Coverage

We aim for **>80% code coverage**. Check coverage:

```bash
make test-cov
open htmlcov/index.html  # View HTML report
```

## Code Quality

### Formatting with Black

```bash
# Format all code
make format

# Check formatting without changes
make format-check

# Format specific file
black app/main.py
```

Configuration in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

### Linting with Ruff

```bash
# Lint code
make lint

# Auto-fix issues
make lint-fix

# Lint specific file
ruff check app/main.py
```

### Type Checking with Mypy

```bash
# Type check
make typecheck

# Type check specific file
mypy app/main.py
```

### Run All Checks

```bash
make check-all
```

## Docker Development

### Building Images

```bash
# Build all services
make docker-build

# Build specific service
make docker-build-fastapi
```

### Running Services

```bash
# Start all services
make docker-up

# Start in foreground (see logs)
docker-compose up

# Start specific service
docker-compose up fastapi-backend
```

### Debugging in Docker

```bash
# View logs
make docker-logs
make docker-logs-fastapi

# Access container shell
make docker-shell-fastapi

# Execute command in container
docker-compose exec fastapi-backend python -c "import app; print(app.__version__)"
```

### Hot Reload in Docker

The `docker-compose.yml` mounts code as volumes for hot reload:

```yaml
volumes:
  - ./services/fastapi-backend/app:/app/app:ro
```

Changes to code will trigger automatic reload.

## Environment Management

### Environment Variables

Environment variables are managed in `.env` files:

- **Root `.env`**: Global settings
- **Service `.env`**: Service-specific settings

Load order:
1. System environment variables
2. Service `.env` file
3. Root `.env` file
4. Default values in code

### Configuration

Configuration is managed using Pydantic Settings:

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_cloud_project: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Logging

### Structured Logging

All logs are JSON-formatted for easy parsing:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Processing request", extra={
    "user_id": user_id,
    "request_id": request_id,
})
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical issues requiring immediate attention

### Viewing Logs

```bash
# Local development
# Logs appear in console with JSON formatting

# Docker
make docker-logs
make docker-logs-fastapi

# Filter logs by level
docker-compose logs fastapi-backend | grep '"level":"ERROR"'
```

## API Documentation

### OpenAPI/Swagger

FastAPI automatically generates OpenAPI documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Documenting Endpoints

```python
@router.post(
    "/endpoint",
    response_model=YourResponse,
    summary="Short summary",
    description="Detailed description",
    responses={
        200: {"description": "Success"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def your_endpoint(
    request: YourRequest = Body(..., example={
        "field": "example value"
    })
) -> YourResponse:
    """
    Detailed docstring for the endpoint.
    
    Args:
        request: Request object with field descriptions
        
    Returns:
        Response object with results
        
    Raises:
        HTTPException: When something goes wrong
    """
    pass
```

## Git Workflow

### Branch Naming

- `main` - Production-ready code
- `develop` - Development branch
- `feature/your-feature` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation updates

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

Examples:
```
feat(api): add streaming support for text generation
fix(vertex): handle connection timeout errors
docs(readme): update installation instructions
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Performance Optimization

### Async Best Practices

- Use `async/await` for I/O operations
- Don't block the event loop
- Use connection pooling

```python
# Good
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Bad - blocks event loop
def fetch_data_sync():
    response = requests.get(url)
    return response.json()
```

### Caching

Consider caching for expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_computation(param: str) -> str:
    # Cached result
    pass
```

## Debugging

### Local Debugging

Add breakpoints with `breakpoint()` or use an IDE debugger.

### Remote Debugging

For Docker containers, use `debugpy`:

```python
# In your code
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

Then connect with VS Code or PyCharm.

## Common Issues

### Issue: Import errors

**Solution**: Ensure you're in the correct directory and virtual environment is activated.

### Issue: Tests failing

**Solution**: Check test dependencies are installed, database/mocks are set up correctly.

### Issue: Docker build slow

**Solution**: Use Docker layer caching, `.dockerignore`, and multi-stage builds.

## Best Practices

1. **Type Hints**: Always use type hints
2. **Validation**: Use Pydantic for data validation
3. **Error Handling**: Use proper exception handling
4. **Logging**: Log important events and errors
5. **Testing**: Write tests for new features
6. **Documentation**: Document complex logic
7. **Security**: Never commit secrets
8. **Performance**: Profile before optimizing

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Python Best Practices](https://docs.python-guide.org/)

---

Happy coding! 🚀

