# 🎯 High Priority Implementation Plan

Detailed plan for implementing high-priority code quality improvements.

**Timeline**: 1 Week  
**Estimated Effort**: 13 hours  
**Priority**: High - Complete before production deployment  

## 📋 Overview

### High Priority Items

1. ✅ **File Size Limits** - DONE
2. **Improve Exception Handling** - 4 hours
3. **Add Request Timeouts** - 1 hour
4. **Add Rate Limiting** - 2 hours
5. **Write Unit Tests (50% Coverage)** - 4 hours
6. **Add Input Validation** - 2 hours

**Total**: 13 hours work

## 🔴 Item 1: Improve Exception Handling (4 hours)

### Goal
Replace broad `except Exception` with specific exception types for better error handling and debugging.

### Current State
- 15 instances of `except Exception`
- Hard to debug what went wrong
- Catches system errors unintentionally

### Implementation

#### Step 1: Create Custom Exceptions (30 min)

**File**: `app/core/exceptions.py` (NEW)

```python
"""Custom exceptions for the application."""

class GenAIException(Exception):
    """Base exception for GenAI application."""
    pass

class VertexAIException(GenAIException):
    """Exception for Vertex AI errors."""
    pass

class ExtractionException(GenAIException):
    """Exception for data extraction errors."""
    pass

class ValidationException(GenAIException):
    """Exception for validation errors."""
    pass

class ConfigurationException(GenAIException):
    """Exception for configuration errors."""
    pass
```

#### Step 2: Update Vertex AI Service (1 hour)

**File**: `app/services/vertex_ai.py`

**Replace 4 instances:**

```python
# Current
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {e}")
    raise

# New
except (ValueError, AttributeError) as e:
    logger.error(f"Configuration error: {e}")
    raise ConfigurationException(f"Vertex AI configuration error: {e}")
except ConnectionError as e:
    logger.error(f"Connection error: {e}")
    raise VertexAIException(f"Cannot connect to Vertex AI: {e}")
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise VertexAIException(f"Vertex AI error: {e}")
```

#### Step 3: Update Vote Extraction Service (1 hour)

**File**: `app/services/vote_extraction_service.py`

**Replace 3 instances:**

```python
# For file reading errors
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return None
except (IOError, OSError) as e:
    logger.error(f"File read error: {e}")
    return None

# For Gemini API errors
except (ValueError, TypeError) as e:
    logger.error(f"Invalid data format: {e}")
    return None
except ConnectionError as e:
    logger.error(f"Gemini API connection error: {e}")
    return None
except Exception as e:
    logger.critical(f"Unexpected Gemini error: {e}", exc_info=True)
    return None
```

#### Step 4: Update API Endpoints (1.5 hours)

**Files**: All endpoint files (chat, generate, vote_extraction)

**Pattern:**

```python
# Current
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail=str(e))

# New
except ValidationException as e:
    logger.warning(f"Validation error: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except VertexAIException as e:
    logger.error(f"AI service error: {e}")
    raise HTTPException(status_code=503, detail="AI service unavailable")
except ExtractionException as e:
    logger.error(f"Extraction error: {e}")
    raise HTTPException(status_code=422, detail=str(e))
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

#### Step 5: Add Tests (1 hour)

**File**: `app/tests/unit/test_exceptions.py` (NEW)

```python
"""Tests for custom exceptions."""

import pytest
from app.core.exceptions import (
    VertexAIException,
    ExtractionException,
    ValidationException,
)

def test_vertex_ai_exception():
    """Test VertexAI exception."""
    with pytest.raises(VertexAIException):
        raise VertexAIException("Test error")

def test_exception_inheritance():
    """Test exception inheritance."""
    assert issubclass(VertexAIException, GenAIException)
```

### Checklist

- [ ] Create `app/core/exceptions.py`
- [ ] Update `app/services/vertex_ai.py` (4 instances)
- [ ] Update `app/services/vote_extraction_service.py` (3 instances)
- [ ] Update `app/api/v1/endpoints/vote_extraction.py` (5 instances)
- [ ] Update `app/api/v1/endpoints/chat.py` (1 instance)
- [ ] Update `app/api/v1/endpoints/generate.py` (2 instances)
- [ ] Create `test_exceptions.py`
- [ ] Test all error paths
- [ ] Update error handling docs

**Estimated Time**: 4 hours  
**Impact**: High - Better debugging and error recovery

---

## 🔴 Item 2: Add Request Timeouts (1 hour)

### Goal
Prevent requests from hanging indefinitely when calling external services.

### Implementation

#### Step 1: Add Timeout Constants (10 min)

**File**: `app/core/constants.py` (NEW)

```python
"""Application constants."""

# Timeouts (seconds)
GEMINI_API_TIMEOUT = 120  # 2 minutes for Gemini calls
VERTEX_AI_TIMEOUT = 60    # 1 minute for other Vertex AI calls
DEFAULT_API_TIMEOUT = 30  # 30 seconds default

# File limits
MAX_FILE_SIZE_MB = 10
MAX_TOTAL_SIZE_MB = 30

# Rate limits
RATE_LIMIT_PER_MINUTE = 10
RATE_LIMIT_PER_HOUR = 100
```

#### Step 2: Add Timeout Wrapper (20 min)

**File**: `app/core/utils.py` (NEW)

```python
"""Utility functions."""

import asyncio
from typing import TypeVar, Callable, Awaitable
from functools import wraps

T = TypeVar('T')

def with_timeout(seconds: float):
    """Decorator to add timeout to async functions."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"{func.__name__} timed out after {seconds}s")
        return wrapper
    return decorator
```

#### Step 3: Apply Timeouts to Services (30 min)

**File**: `app/services/vote_extraction_service.py`

```python
from app.core.utils import with_timeout
from app.core.constants import GEMINI_API_TIMEOUT

@with_timeout(GEMINI_API_TIMEOUT)
async def _call_gemini(self, content_parts, config):
    """Call Gemini API with timeout."""
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content_parts,
        config=config,
    )

async def extract_from_images(...):
    try:
        response = await self._call_gemini(content_parts, config)
    except TimeoutError as e:
        logger.error(f"Gemini API timeout: {e}")
        return None
```

### Checklist

- [ ] Create `app/core/constants.py`
- [ ] Create `app/core/utils.py` with timeout decorator
- [ ] Apply timeout to `vote_extraction_service.py`
- [ ] Apply timeout to `vertex_ai.py`
- [ ] Add timeout tests
- [ ] Document timeout behavior

**Estimated Time**: 1 hour  
**Impact**: High - Prevents hanging requests

---

## 🔴 Item 3: Add Rate Limiting (2 hours)

### Goal
Prevent abuse and control costs by limiting request rates.

### Implementation

#### Step 1: Install Dependencies (5 min)

```bash
cd services/fastapi-backend
poetry add slowapi
```

#### Step 2: Configure Rate Limiter (30 min)

**File**: `app/main.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter
limiter = Limiter(key_func=get_remote_address)

# Add to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

#### Step 3: Apply Rate Limits (45 min)

**File**: `app/api/v1/endpoints/vote_extraction.py`

```python
from slowapi import Limiter
from app.main import limiter

@router.post("/extract")
@limiter.limit("10/minute")  # 10 requests per minute
@limiter.limit("100/hour")   # 100 requests per hour
async def extract_votes(...):
    ...
```

**Apply to all endpoints:**

| Endpoint | Rate Limit | Reasoning |
|----------|------------|-----------|
| `/vote-extraction/extract` | 10/min, 100/hour | Expensive (AI calls) |
| `/chat/completions` | 30/min, 500/hour | Moderate cost |
| `/generate` | 30/min, 500/hour | Moderate cost |
| `/health`, `/ready` | 100/min | Cheap, monitoring |

#### Step 4: Custom Rate Limit by API Key (40 min)

**File**: `app/core/rate_limiting.py` (NEW)

```python
"""Rate limiting utilities."""

from slowapi import Limiter
from fastapi import Request

def get_api_key_or_ip(request: Request) -> str:
    """Get rate limit key (API key or IP)."""
    # Try to get API key from header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key}"
    
    # Fall back to IP address
    return f"ip:{request.client.host}"

# Create limiter with custom key function
limiter = Limiter(key_func=get_api_key_or_ip)
```

**Benefits:**
- ✅ Rate limit by API key (authenticated users)
- ✅ Rate limit by IP (anonymous users)
- ✅ Different limits per user type

### Checklist

- [ ] Install slowapi
- [ ] Add limiter to `app/main.py`
- [ ] Apply limits to vote extraction (10/min)
- [ ] Apply limits to chat (30/min)
- [ ] Apply limits to generate (30/min)
- [ ] Create `app/core/rate_limiting.py`
- [ ] Add rate limit tests
- [ ] Document rate limits in API docs
- [ ] Add to .env.example

**Estimated Time**: 2 hours  
**Impact**: High - Prevents abuse, controls costs

---

## 🔴 Item 4: Write Unit Tests - 50% Coverage (4 hours)

### Goal
Increase test coverage from 30% to 50% minimum.

### Current Coverage
- Models: ~60%
- Services: ~10%
- Endpoints: ~30%
- Utils: 0%

### Tests to Write

#### Priority 1: Service Layer Tests (2 hours)

**File**: `app/tests/unit/test_services.py` (NEW)

```python
"""Unit tests for service layer."""

import pytest
from unittest.mock import patch, MagicMock

from app.services.genai_service import GenAIService
from app.services.vertex_ai import VertexAIService

class TestGenAIService:
    """Tests for GenAI service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GenAIService()
    
    @patch('app.services.vertex_ai.VertexAIService.generate_content')
    async def test_generate_text(self, mock_generate, service):
        """Test text generation."""
        mock_generate.return_value = {
            "id": "test-123",
            "text": "Generated text",
            "model": "gemini-pro"
        }
        
        result = await service.generate_text(prompt="Test prompt")
        
        assert result["text"] == "Generated text"
        mock_generate.assert_called_once()
    
    @patch('app.services.vertex_ai.VertexAIService.chat_completion')
    async def test_chat_completion(self, mock_chat, service):
        """Test chat completion."""
        mock_chat.return_value = {
            "id": "test-123",
            "content": "Response",
            "role": "assistant"
        }
        
        from app.models.requests import Message
        messages = [Message(role="user", content="Hello")]
        
        result = await service.chat_completion(messages=messages)
        
        assert result["content"] == "Response"
        mock_chat.assert_called_once()
```

**Tests to add:**
- `test_generate_text` - Text generation
- `test_generate_text_stream` - Streaming
- `test_chat_completion` - Chat
- `test_error_handling` - Error cases
- `test_parameter_validation` - Parameter handling

#### Priority 2: Configuration Tests (1 hour)

**File**: `app/tests/unit/test_config.py` (NEW)

```python
"""Tests for configuration."""

import pytest
from app.config import Settings

def test_default_config():
    """Test default configuration values."""
    settings = Settings(google_cloud_project="test-project")
    assert settings.vertex_ai_location == "us-central1"
    assert settings.default_model == "gemini-pro"
    assert settings.api_key_required is False

def test_cors_origins_parsing():
    """Test CORS origins parsing from string."""
    settings = Settings(
        google_cloud_project="test",
        cors_origins="http://localhost:3000,http://localhost:8000"
    )
    assert len(settings.cors_origins) == 2
    assert "http://localhost:3000" in settings.cors_origins

def test_environment_detection():
    """Test environment detection methods."""
    dev_settings = Settings(
        google_cloud_project="test",
        fastapi_env="development"
    )
    assert dev_settings.is_development is True
    assert dev_settings.is_production is False
    
    prod_settings = Settings(
        google_cloud_project="test",
        fastapi_env="production"
    )
    assert prod_settings.is_development is False
    assert prod_settings.is_production is True
```

#### Priority 3: More Endpoint Tests (1 hour)

**File**: `app/tests/integration/test_api_generate.py` (NEW)

```python
"""Integration tests for generation endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

@patch('app.services.genai_service.genai_service.generate_text')
def test_generate_text_success(mock_generate, client):
    """Test successful text generation."""
    mock_generate.return_value = {
        "id": "test-123",
        "text": "Generated response",
        "model": "gemini-pro"
    }
    
    response = client.post(
        "/api/v1/generate",
        json={
            "prompt": "Test prompt",
            "model": "gemini-pro",
            "temperature": 0.7
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Generated response"

def test_generate_empty_prompt(client):
    """Test with empty prompt."""
    response = client.post(
        "/api/v1/generate",
        json={"prompt": ""}
    )
    
    # Should validate and reject
    assert response.status_code in [400, 422]
```

### Checklist

- [ ] Create `app/core/exceptions.py` with custom exceptions
- [ ] Update `app/services/vertex_ai.py` (4 handlers)
- [ ] Update `app/services/vote_extraction_service.py` (3 handlers)
- [ ] Update `app/services/genai_service.py` (if needed)
- [ ] Update `app/api/v1/endpoints/vote_extraction.py` (5 handlers)
- [ ] Update `app/api/v1/endpoints/chat.py` (1 handler)
- [ ] Update `app/api/v1/endpoints/generate.py` (2 handlers)
- [ ] Create `app/tests/unit/test_services.py`
- [ ] Create `app/tests/unit/test_config.py`
- [ ] Create `app/tests/integration/test_api_generate.py`
- [ ] Create `app/tests/integration/test_api_chat.py`
- [ ] Run tests: `poetry run pytest --cov=app`
- [ ] Verify 50%+ coverage

**Estimated Time**: 4 hours  
**Impact**: High - Better error handling, testable code

---

## 🔴 Item 5: Add Input Validation (2 hours)

### Goal
Validate all inputs beyond Pydantic defaults.

### Implementation

#### Step 1: Validate Prompts (30 min)

**File**: `app/api/v1/endpoints/generate.py`

```python
# Add validation
if not request.prompt or not request.prompt.strip():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Prompt cannot be empty"
    )

if len(request.prompt) > 10000:  # 10K characters max
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Prompt too long (max 10,000 characters)"
    )
```

#### Step 2: Validate Chat Messages (30 min)

**File**: `app/api/v1/endpoints/chat.py`

```python
if not request.messages:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Messages cannot be empty"
    )

if len(request.messages) > 100:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Too many messages (max 100)"
    )

# Validate last message is from user
if request.messages[-1].role != "user":
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Last message must be from user"
    )
```

#### Step 3: Validate File Names (30 min)

**File**: `app/api/v1/endpoints/vote_extraction.py`

```python
import re

# Validate filenames
for file in files:
    # Check filename is safe
    if not re.match(r'^[\w\-. ]+$', file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filename: {file.filename}"
        )
    
    # Check file extension
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension: {file.filename}"
        )
```

#### Step 4: Add Validation Tests (30 min)

**File**: `app/tests/integration/test_input_validation.py` (NEW)

```python
"""Tests for input validation."""

def test_empty_prompt(client):
    """Test empty prompt is rejected."""
    response = client.post("/api/v1/generate", json={"prompt": ""})
    assert response.status_code == 400

def test_prompt_too_long(client):
    """Test overly long prompt is rejected."""
    response = client.post(
        "/api/v1/generate",
        json={"prompt": "a" * 10001}  # Over 10K limit
    )
    assert response.status_code == 400

def test_invalid_filename(client):
    """Test invalid filename is rejected."""
    response = client.post(
        "/api/v1/vote-extraction/extract",
        files=[("files", ("../../../etc/passwd", b"content", "image/jpeg"))]
    )
    assert response.status_code == 400
```

### Checklist

- [ ] Add prompt length validation
- [ ] Add message count validation
- [ ] Add filename validation
- [ ] Add parameter range validation
- [ ] Create validation utility functions
- [ ] Add validation tests
- [ ] Document validation rules

**Estimated Time**: 2 hours  
**Impact**: High - Security and data quality

---

## 📅 Weekly Schedule

### Monday (3 hours)
- Morning: Create custom exceptions (30 min)
- Morning: Update Vertex AI service (1 hour)
- Afternoon: Update Vote Extraction service (1 hour)
- Afternoon: Start endpoint updates (30 min)

### Tuesday (3 hours)
- Morning: Finish endpoint updates (1 hour)
- Morning: Add timeout wrapper (1 hour)
- Afternoon: Apply timeouts to services (1 hour)

### Wednesday (3 hours)
- Morning: Install and configure rate limiting (1 hour)
- Afternoon: Apply rate limits to endpoints (1 hour)
- Afternoon: Test rate limiting (1 hour)

### Thursday (2 hours)
- Morning: Add input validation (1.5 hours)
- Afternoon: Create validation tests (30 min)

### Friday (2 hours)
- Morning: Write service tests (1 hour)
- Afternoon: Write config tests (30 min)
- Afternoon: Write endpoint tests (30 min)

**Total**: 13 hours over 5 days

## 🎯 Success Criteria

### Code Quality
- [x] 0 critical bugs
- [ ] 0 high-priority issues
- [ ] 50%+ test coverage
- [ ] All linters passing
- [ ] All tests passing

### Functionality
- [ ] Exception handling improved
- [ ] Timeouts implemented
- [ ] Rate limiting working
- [ ] Input validation complete

### Testing
- [ ] Custom exceptions tested
- [ ] Timeout behavior tested
- [ ] Rate limits tested
- [ ] Validation rules tested

## 🚀 After Completion

**You'll have:**
- ✅ Robust error handling
- ✅ Protected against hanging requests
- ✅ Rate limiting to prevent abuse
- ✅ Strong input validation
- ✅ 50%+ test coverage
- ✅ Production-ready codebase

**Next steps:**
1. Deploy to staging
2. Run load tests
3. Monitor for 1 week
4. Deploy to production

---

**Start Date**: Monday  
**End Date**: Friday  
**Total Effort**: 13 hours  
**Outcome**: Production-ready code quality 🎉

