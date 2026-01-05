# ✅ Dockerfile pyproject.toml Fix

**Issue**: Streamlit Dockerfile was hardcoding package versions instead of using `pyproject.toml`  
**Status**: ✅ Fixed  
**Date**: January 4, 2026

---

## 🎯 Problem

The **Streamlit Dockerfile** was hardcoding package versions, which creates maintenance issues:

```dockerfile
# ❌ BAD: Hardcoded versions (before)
RUN uv pip install --system \
    "streamlit>=1.31.1" \
    "httpx>=0.26.0" \
    "requests>=2.31.0" \
    "Pillow>=10.2.0" \
    "pandas>=2.1.4" \
    "python-dotenv>=1.0.0" \
    "ddtrace>=3.18.0"
```

**Problems**:
- ❌ Duplicates version constraints from `pyproject.toml`
- ❌ Easy to get out of sync (update one place, forget the other)
- ❌ Violates DRY (Don't Repeat Yourself) principle
- ❌ Makes dependency updates error-prone

---

## ✅ Solution

Updated to use `pyproject.toml` as the single source of truth:

```dockerfile
# ✅ GOOD: Uses pyproject.toml (after)
COPY pyproject.toml README.md ./
RUN uv pip install --system -e .
```

**Benefits**:
- ✅ Single source of truth for dependencies
- ✅ Update versions in one place (`pyproject.toml`)
- ✅ Consistent with backend Dockerfiles
- ✅ Follows best practices

---

## 📂 Files Fixed

### Streamlit Frontend Dockerfile

**File**: `frontend/streamlit/Dockerfile`

**Before** (Lines 19-34):
```dockerfile
# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
# Extract and install production dependencies from pyproject.toml
RUN uv pip install --system \
    "streamlit>=1.31.1" \
    "httpx>=0.26.0" \
    "requests>=2.31.0" \
    "Pillow>=10.2.0" \
    "pandas>=2.1.4" \
    "python-dotenv>=1.0.0" \
    "ddtrace>=3.18.0"

# Install Datadog tracer to specific directory for serverless-init
RUN pip install --target /dd_tracer/python/ ddtrace
```

**After** (Lines 19-29):
```dockerfile
# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml README.md ./

# Install dependencies using uv
# Install from pyproject.toml (uses versions defined there, not hardcoded)
RUN uv pip install --system -e .

# Install Datadog tracer to specific directory for serverless-init
RUN pip install --target /dd_tracer/python/ ddtrace
```

**Key Changes**:
1. ✅ Added `README.md` to COPY (required by pyproject.toml)
2. ✅ Changed from hardcoded packages to `-e .` (editable install)
3. ✅ Updated comment to reflect the change

---

## ✅ Backend Dockerfiles (Already Correct)

Both backend Dockerfiles were **already using** `pyproject.toml` correctly:

### FastAPI Backend - Cloud Run

**File**: `services/fastapi-backend/Dockerfile.cloudrun` (Line 33)

```dockerfile
# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml README.md ./

# Install dependencies using uv
# Extract and install production dependencies from pyproject.toml
RUN uv pip install --system -e .
```

### FastAPI Backend - Local Development

**File**: `services/fastapi-backend/Dockerfile` (Line 31)

```dockerfile
# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml README.md ./

# Install dependencies using uv
# Extract and install production dependencies from pyproject.toml
RUN uv pip install --system -e .
```

**Status**: ✅ No changes needed - already using best practices!

---

## 📋 Verification

### Check Package Versions

All package versions are now defined in `pyproject.toml`:

**Frontend** (`frontend/streamlit/pyproject.toml`):
```toml
dependencies = [
    "streamlit>=1.31.1",
    "httpx>=0.26.0",
    "requests>=2.31.0",
    "Pillow>=10.2.0",
    "pandas>=2.1.4",
    "python-dotenv>=1.0.0",
    "ddtrace>=3.18.0",
]
```

**Backend** (`services/fastapi-backend/pyproject.toml`):
```toml
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "python-multipart>=0.0.9",
    "google-cloud-aiplatform>=1.42.1",
    "google-auth>=2.27.0",
    "google-genai>=0.2.0",
    "pydantic>=2.5.3",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.26.0",
    "aiohttp>=3.9.1",
    "python-json-logger>=2.0.7",
    "structlog>=24.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "ddtrace>=4.0.0",
    "opentelemetry-api>=1.20.0",
    "slowapi>=0.1.9",
]
```

---

## 🧪 Testing

### Test the Fix

1. **Rebuild Streamlit image**:
   ```bash
   docker-compose build streamlit-frontend
   ```

2. **Verify dependencies installed**:
   ```bash
   docker run --rm genai-streamlit-frontend pip list
   ```

3. **Check versions match pyproject.toml**:
   ```bash
   # Should see versions >= those in pyproject.toml
   docker run --rm genai-streamlit-frontend pip show streamlit httpx ddtrace
   ```

4. **Start services**:
   ```bash
   docker-compose up -d
   ```

5. **Verify Streamlit works**:
   ```bash
   curl http://localhost:8501/_stcore/health
   # Should return: {"status":"ok"}
   ```

---

## 💡 Best Practices

### 1. Single Source of Truth

✅ **DO**: Define versions in `pyproject.toml`
```toml
[project]
dependencies = [
    "streamlit>=1.31.1",
    "httpx>=0.26.0",
]
```

✅ **DO**: Install from `pyproject.toml` in Dockerfile
```dockerfile
COPY pyproject.toml README.md ./
RUN uv pip install --system -e .
```

❌ **DON'T**: Duplicate versions in Dockerfile
```dockerfile
# BAD: Don't do this!
RUN uv pip install --system \
    "streamlit>=1.31.1" \
    "httpx>=0.26.0"
```

### 2. Editable Install (`-e .`)

The `-e .` flag installs the package in **editable mode**:
- ✅ Installs all dependencies from `pyproject.toml`
- ✅ Makes the package importable
- ✅ Useful for local development
- ✅ Works with `uv`, `pip`, and other tools

**Alternative**: Non-editable install
```dockerfile
# Also works (non-editable)
RUN uv pip install --system .
```

Both are fine for production Docker images. The `-e` flag is slightly more flexible for development.

### 3. Copy README.md

Many `pyproject.toml` files reference `README.md`:

```toml
[project]
readme = "README.md"
```

**Always copy it** before installing:
```dockerfile
COPY pyproject.toml README.md ./
RUN uv pip install --system -e .
```

---

## 🔄 Updating Dependencies

### Process

1. **Update version in `pyproject.toml`**:
   ```toml
   dependencies = [
       "streamlit>=1.32.0",  # Updated from 1.31.1
   ]
   ```

2. **Rebuild Docker image**:
   ```bash
   docker-compose build streamlit-frontend
   ```

3. **Test locally**:
   ```bash
   docker-compose up -d
   ```

4. **Commit and deploy**:
   ```bash
   git add frontend/streamlit/pyproject.toml
   git commit -m "chore: Update streamlit to 1.32.0"
   git push
   ```

**No Dockerfile changes needed!** 🎉

---

## 📊 Summary

| Dockerfile | Status | Uses pyproject.toml | Notes |
|------------|--------|---------------------|-------|
| `frontend/streamlit/Dockerfile` | ✅ **Fixed** | ✅ Yes (now) | Changed from hardcoded to `-e .` |
| `services/fastapi-backend/Dockerfile` | ✅ Correct | ✅ Yes | Already using best practices |
| `services/fastapi-backend/Dockerfile.cloudrun` | ✅ Correct | ✅ Yes | Already using best practices |

---

## 🎯 Key Takeaways

1. ✅ **Single source of truth**: `pyproject.toml` defines all versions
2. ✅ **No hardcoding**: Dockerfiles use `uv pip install --system -e .`
3. ✅ **Easy updates**: Change version in one place, rebuild image
4. ✅ **Consistency**: All Dockerfiles now follow the same pattern
5. ✅ **Best practices**: Follows modern Python packaging standards

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `frontend/streamlit/pyproject.toml` | Frontend dependencies |
| `services/fastapi-backend/pyproject.toml` | Backend dependencies |
| `frontend/streamlit/Dockerfile` | Frontend production image |
| `services/fastapi-backend/Dockerfile` | Backend local dev image |
| `services/fastapi-backend/Dockerfile.cloudrun` | Backend Cloud Run image |

---

## 📚 Documentation

- **PEP 621**: [Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- **uv docs**: [Installing packages](https://github.com/astral-sh/uv)
- **Python Packaging**: [pyproject.toml guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

---

**Status**: ✅ **All Dockerfiles now use pyproject.toml correctly!**

**Next Steps**:
1. Rebuild images: `docker-compose build`
2. Test locally: `docker-compose up -d`
3. Verify all services work correctly

