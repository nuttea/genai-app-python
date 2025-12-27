# Backend Tests

Test suite for the FastAPI backend.

## Structure

```
tests/
├── unit/                       Unit tests (isolated)
│   ├── test_models.py          Pydantic models
│   ├── test_security.py        Security utilities
│   └── test_services.py        Business logic (mocked)
├── integration/                Integration tests (with dependencies)
│   ├── test_api_health.py      Health endpoints
│   ├── test_api_chat.py        Chat endpoints
│   ├── test_api_generate.py    Generation endpoints
│   └── test_api_vote_extraction.py  Vote extraction
├── e2e/                        End-to-end tests (full workflow)
│   └── test_vote_extraction_workflow.py
├── fixtures/                   Test data
│   ├── sample_images/          Test images
│   └── expected_outputs/       Expected results
├── conftest.py                 Shared fixtures
└── README.md                   This file
```

## Running Tests

### All Tests

```bash
# With Poetry
poetry run pytest

# With make
make test
```

### Specific Test File

```bash
poetry run pytest app/tests/unit/test_models.py
```

### Specific Test

```bash
poetry run pytest app/tests/unit/test_models.py::TestFormInfo::test_valid_form_info
```

### With Coverage

```bash
# Generate coverage report
poetry run pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Watch Mode

```bash
# Install pytest-watch
poetry add --group dev pytest-watch

# Run in watch mode
poetry run ptw
```

## Writing Tests

### Unit Test Example

```python
def test_function():
    \"\"\"Test description.\"\"\"
    result = my_function(input)
    assert result == expected
```

### Integration Test Example

```python
def test_api_endpoint(client):
    \"\"\"Test API endpoint.\"\"\"
    response = client.post("/api/v1/endpoint", json={...})
    assert response.status_code == 200
```

### Using Fixtures

```python
@pytest.fixture
def sample_data():
    \"\"\"Provide test data.\"\"\"
    return {"key": "value"}

def test_with_fixture(sample_data):
    \"\"\"Test using fixture.\"\"\"
    assert sample_data["key"] == "value"
```

### Mocking External Services

```python
from unittest.mock import patch

@patch('app.services.vertex_ai.VertexAIService.generate_content')
def test_with_mock(mock_generate):
    \"\"\"Test with mocked service.\"\"\"
    mock_generate.return_value = {"text": "response"}
    result = call_service()
    assert result["text"] == "response"
```

## Test Coverage Goals

- **Overall**: 80%+
- **Models**: 95%+
- **Services**: 80%+
- **Endpoints**: 90%+
- **Utilities**: 85%+

## CI/CD Integration

Tests run automatically on:
- Every pull request
- Push to main
- Push to develop

See `.github/workflows/backend-ci-cd.yml`

## Best Practices

1. **Test naming**: `test_<what>_<condition>_<expected>`
2. **Docstrings**: Describe what the test does
3. **AAA pattern**: Arrange, Act, Assert
4. **One assertion per test** (when possible)
5. **Mock external services** (Vertex AI, etc.)
6. **Use fixtures** for common setup
7. **Keep tests fast** (< 1s per test)

## Debugging Tests

### Run with verbose output

```bash
poetry run pytest -v
```

### Show print statements

```bash
poetry run pytest -s
```

### Stop on first failure

```bash
poetry run pytest -x
```

### Run last failed tests

```bash
poetry run pytest --lf
```

### Debug mode

```bash
poetry run pytest --pdb
```

## TODO: Tests to Write

- [ ] test_api_chat.py - Chat completion tests
- [ ] test_api_generate.py - Text generation tests
- [ ] test_services.py - Service layer tests
- [ ] test_vote_extraction_workflow.py - E2E tests
- [ ] Add more edge cases
- [ ] Add performance tests
- [ ] Add load tests

---

**Current Coverage**: ~30%  
**Target Coverage**: 80%+  
**Priority**: High

