# 🎯 Code Quality Action Plan

Prioritized action plan for improving code quality before production deployment.

## ✅ Completed (Just Now)

- [x] Fixed validation bug: `result.name` → `result.candidate_name or result.party_name`
- [x] Removed unused import: `tempfile`
- [x] Created comprehensive code quality review

## 🔴 Critical (Fix Before Production - Day 1)

### 1. Implement Vertex AI Health Checks

**Files to update:**
- `app/main.py` - `/ready` endpoint
- `app/api/v1/endpoints/health.py` - `/api/v1/ready` endpoint

**Implementation:**
```python
@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness check endpoint."""
    checks = {
        "vertex_ai": False,
        "genai_client": False,
    }

    try:
        # Test Vertex AI connection
        vertex_ai_service.initialize()
        checks["vertex_ai"] = True

        # Test GenAI client
        vote_extraction_service._get_client()
        checks["genai_client"] = True

        all_ready = all(checks.values())
        status_code = 200 if all_ready else 503

        return JSONResponse(
            content={"status": "ready" if all_ready else "not_ready", "checks": checks},
            status_code=status_code
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "not_ready", "error": str(e), "checks": checks},
            status_code=503
        )
```

**Priority**: 🔴 Critical
**Time**: 1 hour

---

### 2. Add File Size Limits

**File**: `app/api/v1/endpoints/vote_extraction.py`

**Current**: No file size validation

**Add:**
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB total

# In extract_votes function
for file in files:
    content = await file.read()

    # Check individual file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File {file.filename} exceeds 10MB limit"
        )

    total_size += len(content)

# Check total size
if total_size > MAX_TOTAL_SIZE:
    raise HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail="Total file size exceeds 50MB limit"
    )
```

**Priority**: 🔴 Critical
**Time**: 30 minutes

---

## 🟡 High Priority (Week 1)

### 3. Improve Exception Handling

**Replace broad `except Exception` with specific exceptions:**

```python
# Current pattern
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(...)

# Improved pattern
except (ValidationError, ValueError) as e:
    logger.warning(f"Validation error: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except (ConnectionError, TimeoutError) as e:
    logger.error(f"External service error: {e}")
    raise HTTPException(status_code=503, detail="Service unavailable")
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Files to update:**
- All endpoint files (5 files)
- All service files (3 files)

**Priority**: 🟡 High
**Time**: 3-4 hours

---

### 4. Add Request Timeouts

**File**: `app/services/vote_extraction_service.py`

**Add timeout to Gemini calls:**

```python
import asyncio

async def extract_from_images(...):
    try:
        # Add timeout
        response = await asyncio.wait_for(
            self._call_gemini(content_parts, config),
            timeout=120.0  # 2 minutes max
        )
    except asyncio.TimeoutError:
        logger.error("Gemini API call timed out")
        return None
```

**Priority**: 🟡 High
**Time**: 1 hour

---

### 5. Add Rate Limiting

**Install dependency:**
```bash
poetry add slowapi
```

**Implement:**
```python
# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@router.post("/extract")
@limiter.limit("10/minute")
async def extract_votes(...):
    ...
```

**Priority**: 🟡 High
**Time**: 2 hours

---

## 🟢 Medium Priority (Weeks 2-3)

### 6. Increase Test Coverage

**Target**: 80% coverage

**Tests Needed:**
- `test_api_chat.py` - Chat endpoint tests
- `test_api_generate.py` - Generation endpoint tests
- `test_services.py` - Service layer tests
- `test_config.py` - Configuration tests
- `test_security.py` - More security tests

**Priority**: 🟢 Medium
**Time**: 1-2 weeks

---

### 7. Add Logging Standards

**Create logging utility:**

```python
# app/core/logging_utils.py
def log_api_call(logger, endpoint, **kwargs):
    """Standard API call logging."""
    logger.info(
        f"API call: {endpoint}",
        extra={
            "endpoint": endpoint,
            **kwargs
        }
    )

def log_error(logger, error, context=None):
    """Standard error logging."""
    logger.error(
        f"Error: {type(error).__name__}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        },
        exc_info=True
    )
```

**Priority**: 🟢 Medium
**Time**: 2-3 hours

---

### 8. Extract Constants

**Create constants file:**

```python
# app/core/constants.py
# File upload limits
MAX_FILE_SIZE_MB = 10
MAX_TOTAL_SIZE_MB = 50
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}

# Extraction
SCHEMA_HASH_LENGTH = 8
EXTRACTION_TIMEOUT_SECONDS = 120

# Rate limits
RATE_LIMIT_PER_MINUTE = 10
RATE_LIMIT_PER_HOUR = 100
```

**Priority**: 🟢 Medium
**Time**: 1 hour

---

## ⚪ Low Priority (Month 2)

### 9. Add Caching

```python
from functools import lru_cache
from cachetools import TTLCache

# Cache expensive operations
@lru_cache(maxsize=100)
def get_schema_hash(schema: str) -> str:
    return str(hash(schema))[:8]
```

### 10. Add Circuit Breaker

```python
from pybreaker import CircuitBreaker

vertex_breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@vertex_breaker
async def call_vertex_ai(...):
    ...
```

### 11. Add Metrics

```python
from prometheus_client import Counter, Histogram

extraction_counter = Counter('vote_extractions_total', 'Total extractions')
extraction_duration = Histogram('vote_extraction_duration_seconds', 'Extraction duration')
```

## 📝 Implementation Checklist

### This Week

- [ ] Fix Vertex AI health checks (1 hour)
- [ ] Add file size limits (30 min)
- [ ] Improve exception handling (4 hours)
- [ ] Add request timeouts (1 hour)
- [ ] Add rate limiting (2 hours)
- [ ] Write 10+ unit tests (4 hours)

**Total Time**: ~13 hours

### Next Week

- [ ] Write integration tests (8 hours)
- [ ] Standardize logging (3 hours)
- [ ] Extract constants (1 hour)
- [ ] Add more security tests (2 hours)
- [ ] Document all TODOs (1 hour)

**Total Time**: ~15 hours

### Month 2

- [ ] Add caching layer
- [ ] Add circuit breakers
- [ ] Add Prometheus metrics
- [ ] Performance optimization
- [ ] Load testing

## 🎯 Success Criteria

**Code Quality Goals:**
- ✅ 0 critical bugs
- ✅ 80%+ test coverage
- ✅ 0 high-severity security issues
- ✅ All linters passing
- ✅ Type checking passing
- ✅ No TODOs in production code

**When these are met**: Ready for production! 🚀

---

**Next Action**: Implement critical fixes (estimated 2-3 hours)
