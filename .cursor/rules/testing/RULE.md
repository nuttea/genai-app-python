# Testing Rules

## Scope
**Paths**: `**/tests/**/*.py`, `scripts/tests/**/*.py`

## Test Structure

### Directory Layout
```
services/fastapi-backend/
├── app/
│   └── [source code]
└── tests/
    ├── conftest.py          # Pytest fixtures
    ├── unit/
    │   ├── test_models.py
    │   └── test_services.py
    └── integration/
        └── test_api.py
```

## Pytest Standards

### Test Function Naming
```python
# ✅ Good - Descriptive names
def test_extract_votes_with_valid_images_returns_success():
    pass

def test_extract_votes_with_invalid_format_raises_error():
    pass

def test_llm_config_validates_temperature_range():
    pass

# ❌ Bad - Vague names
def test_extract():
    pass

def test_error():
    pass
```

### Test Structure (AAA Pattern)
```python
# ✅ Good - Arrange, Act, Assert
@pytest.mark.asyncio
async def test_vote_extraction_success():
    # Arrange
    files = [create_test_image()]
    llm_config = LLMConfig(model="gemini-2.5-flash", temperature=0.0)

    # Act
    result = await vote_extraction_service.extract_from_images(
        image_files=files,
        image_filenames=["test.jpg"],
        llm_config=llm_config
    )

    # Assert
    assert result is not None
    assert result["success"] is True
    assert len(result["reports"]) > 0

# ❌ Bad - Mixed concerns, unclear structure
def test_extraction():
    files = [create_test_image()]
    result = vote_extraction_service.extract(files)
    assert result
    llm_config = LLMConfig()
    assert llm_config.model == "gemini-2.5-flash"
```

### Fixtures
```python
# conftest.py

# ✅ Good - Reusable fixtures
@pytest.fixture
def test_image() -> bytes:
    """Generate test image bytes."""
    return create_test_image()

@pytest.fixture
def mock_llm_response():
    """Mock successful LLM response."""
    return {
        "reports": [{
            "province": "กรุงเทพมหานคร",
            "district": "บางกอกใหญ่",
            "vote_results": []
        }]
    }

@pytest.fixture
async def test_client():
    """FastAPI test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Usage
async def test_api_endpoint(test_client, mock_llm_response):
    response = await test_client.post("/api/v1/extract", json=data)
    assert response.status_code == 200
```

### Async Tests
```python
# ✅ Good - Use pytest-asyncio
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result is not None

# ❌ Bad - Missing asyncio marker
async def test_async_function():  # Won't run properly
    result = await async_operation()
```

### Mocking
```python
# ✅ Good - Mock external dependencies
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch('app.services.vote_extraction_service.genai.Client')
async def test_extraction_with_mock(mock_client):
    # Setup mock
    mock_client.return_value.models.generate_content = AsyncMock(
        return_value=mock_response
    )

    # Test
    result = await service.extract(files)
    assert result is not None

    # Verify mock was called
    mock_client.return_value.models.generate_content.assert_called_once()

# ❌ Bad - No mocking, calls actual API
async def test_extraction():
    result = await service.extract(files)  # Calls real Vertex AI
    assert result
```

### Parametrize Tests
```python
# ✅ Good - Test multiple cases efficiently
@pytest.mark.parametrize("temperature,expected_valid", [
    (0.0, True),
    (1.0, True),
    (2.0, True),
    (-0.1, False),  # Invalid
    (2.1, False),   # Invalid
])
def test_llm_config_temperature_validation(temperature, expected_valid):
    if expected_valid:
        config = LLMConfig(temperature=temperature)
        assert config.temperature == temperature
    else:
        with pytest.raises(ValidationError):
            LLMConfig(temperature=temperature)

# ❌ Bad - Separate test for each case
def test_temperature_0():
    config = LLMConfig(temperature=0.0)
    assert config.temperature == 0.0

def test_temperature_1():
    config = LLMConfig(temperature=1.0)
    assert config.temperature == 1.0
# ... many more
```

### Exception Testing
```python
# ✅ Good - Test specific exceptions
import pytest
from fastapi import HTTPException

def test_invalid_file_format_raises_http_exception():
    with pytest.raises(HTTPException) as exc_info:
        validate_file("file.txt")

    assert exc_info.value.status_code == 400
    assert "Invalid format" in exc_info.value.detail

# ❌ Bad - Generic exception catch
def test_invalid_file():
    try:
        validate_file("file.txt")
        assert False, "Should have raised"
    except Exception:
        pass  # Too generic
```

## Integration Tests

### API Endpoint Tests
```python
# ✅ Good - Test full request/response cycle
@pytest.mark.asyncio
async def test_extract_votes_endpoint_success(test_client):
    # Prepare test data
    files = [("files", ("test.jpg", test_image, "image/jpeg"))]

    # Call endpoint
    response = await test_client.post(
        "/api/v1/vote-extraction/extract",
        files=files,
        headers={"X-API-Key": "test-key"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert len(data["data"]) > 0

# ❌ Bad - Only tests happy path, no error cases
async def test_endpoint(test_client):
    response = await test_client.post("/api/v1/extract", files=files)
    assert response.status_code == 200
```

### Database/External Service Tests
```python
# ✅ Good - Use test database or mocks
@pytest.fixture
def test_db():
    """Create test database."""
    db = create_test_database()
    yield db
    db.cleanup()

@pytest.mark.integration
async def test_with_database(test_db):
    result = await operation_with_db(test_db)
    assert result is not None

# ❌ Bad - Uses production database
async def test_with_database():
    result = await operation_with_db(production_db)
```

## Coverage

### Target Coverage
- **Minimum**: 80% code coverage
- **Goal**: 90%+ for critical paths
- **Focus**: Business logic, API endpoints, data validation

### Running Coverage
```bash
# ✅ Run tests with coverage
poetry run pytest tests/ --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Coverage Configuration
```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = """
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
"""
```

## Test Scripts (scripts/tests/)

### Script Structure
```python
#!/usr/bin/env python3
"""
Test script description.

Tests: What this tests
Requirements: What's needed
Usage: python scripts/tests/test_script.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
print(f"✅ Loaded environment from: {env_path}\n")

# Run tests
def test_feature():
    """Test specific feature."""
    try:
        result = perform_test()
        print("✅ Test passed")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_feature()
    exit(0 if success else 1)
```

## Best Practices

### Test Independence
```python
# ✅ Good - Each test is independent
def test_feature_a():
    setup_data_for_a()
    result = test_a()
    cleanup_data_for_a()
    assert result

def test_feature_b():
    setup_data_for_b()
    result = test_b()
    cleanup_data_for_b()
    assert result

# ❌ Bad - Tests depend on order
def test_step_1():
    global data
    data = setup()

def test_step_2():
    result = process(data)  # Depends on test_step_1
```

### Test Data
```python
# ✅ Good - Use factories or builders
def create_test_image(format="jpeg", size=(100, 100)):
    """Create test image with specified parameters."""
    return generate_image(format, size)

def create_test_config(**overrides):
    """Create test LLM config with overrides."""
    defaults = {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "max_tokens": 16384
    }
    return LLMConfig(**{**defaults, **overrides})

# ❌ Bad - Hardcoded test data everywhere
def test_a():
    config = LLMConfig(model="gemini-2.5-flash", temperature=0.0, max_tokens=16384)

def test_b():
    config = LLMConfig(model="gemini-2.5-flash", temperature=0.0, max_tokens=16384)
```

### Assertions
```python
# ✅ Good - Specific assertions with messages
assert result is not None, "Result should not be None"
assert result["success"] is True, f"Expected success, got {result}"
assert len(result["data"]) > 0, "Data should not be empty"

# ❌ Bad - Generic assertions
assert result
assert result["success"]
assert result["data"]
```

## Don't

- ❌ Don't skip tests when refactoring
- ❌ Don't test implementation details (test behavior)
- ❌ Don't use sleep() for async (use proper async patterns)
- ❌ Don't commit commented-out tests
- ❌ Don't write tests that depend on external services without mocks
- ❌ Don't ignore test failures
- ❌ Don't write tests without assertions
- ❌ Don't test private methods directly (test through public API)
