# Troubleshooting: 401 Unauthorized in Jupyter Notebook Experiments

**Issue**: `Client error '401 Unauthorized'` when running experiments in Jupyter notebook  
**Component**: Jupyter Notebook, FastAPI Backend, API Authentication  
**Date**: January 4, 2026

---

## Problem Description

When running experiments in the Jupyter notebook, the task function fails with:

```
❌ Error processing บางบำหรุ1: Client error '401 Unauthorized' for url 'http://localhost:8000/api/v1/vote-extraction/extract'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401
```

---

## Root Cause

The FastAPI backend's `/api/v1/vote-extraction/extract` endpoint requires API key authentication when:
- `API_KEY` environment variable is set (non-empty), **OR**
- `API_KEY_REQUIRED=true` in environment

The notebook was not including the `X-API-Key` header in requests to the backend.

---

## Solution

### ✅ Fix 1: Update Notebook to Include API Key (APPLIED)

The notebook has been updated to automatically load and use the API key:

**File**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`

**Cell 20 (Task Function)**:

```python
import httpx
from ddtrace.llmobs.decorators import workflow

# FastAPI backend URL and API key
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")  # Load API key from environment

@workflow
def vote_extraction_task(input_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Task function that extracts vote data from election form images."""
    form_set_name = input_data.get("form_set_name")
    image_paths = input_data.get("image_paths", [])
    
    print(f"Processing: {form_set_name} ({len(image_paths)} pages)")
    
    try:
        # Read images
        files = []
        for img_path in image_paths:
            img_file = Path(img_path)
            if img_file.exists():
                files.append(("files", (img_file.name, img_file.read_bytes(), "image/jpeg")))
        
        # Prepare headers with API key (if configured)
        headers = {}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
        
        # Call extraction API
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/v1/vote-extraction/extract",
                files=files,
                headers=headers  # ✅ API key included
            )
            response.raise_for_status()
            result = response.json()
        
        # ... rest of the function
```

**Key Changes**:
1. ✅ Added `API_KEY = os.getenv("API_KEY", "")` to load from environment
2. ✅ Created `headers` dictionary with `X-API-Key` if API key is set
3. ✅ Passed `headers` parameter to `httpx.Client.post()`

---

## Configuration Options

### Option 1: Use API Key (Recommended for Production-Like Testing)

Create or update your `.env` file:

```bash
# Backend API Key
API_KEY=your-secret-key-here
API_KEY_REQUIRED=true

# Other settings...
API_BASE_URL=http://localhost:8000
```

Then **restart your Jupyter kernel** to load the new environment variables.

### Option 2: Disable API Key (Quick Local Testing)

Create or update your `.env` file:

```bash
# Disable API key requirement
API_KEY=
API_KEY_REQUIRED=false

# Other settings...
API_BASE_URL=http://localhost:8000
```

Then **restart the FastAPI backend** to apply the changes:

```bash
docker-compose restart fastapi-backend
```

---

## Backend Authentication Logic

### File: `services/fastapi-backend/app/core/security.py`

```python
async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """
    Verify API key if configured.
    
    Behavior:
    - If API_KEY_REQUIRED=false and API_KEY is empty: Allow all requests
    - If API_KEY_REQUIRED=true or API_KEY is set: Require valid API key
    """
    # If API key validation is not required and no key is configured, allow all requests
    if not settings.api_key_required and not settings.api_key:
        return "no-key-required"
    
    # If API key is configured or required, verify it
    if settings.api_key_required or settings.api_key:
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key. Include X-API-Key header in your request.",
            )
        
        if api_key != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        
        return api_key
    
    return "no-key-required"
```

**Logic Summary**:

| `API_KEY` | `API_KEY_REQUIRED` | Behavior |
|-----------|-------------------|----------|
| Empty (`""`) | `false` | ✅ No authentication required |
| Empty (`""`) | `true` | ❌ 401 error (key required but not set) |
| Set (non-empty) | `false` | ✅ Requires `X-API-Key` header |
| Set (non-empty) | `true` | ✅ Requires `X-API-Key` header |

---

## Verification Steps

### 1. Check Current Configuration

```bash
# Check .env file
cat .env | grep API_KEY

# Or check environment variables
echo "API_KEY=$API_KEY"
echo "API_KEY_REQUIRED=$API_KEY_REQUIRED"
```

### 2. Restart Services (if needed)

```bash
# If you changed .env, restart the backend
docker-compose restart fastapi-backend

# Check backend logs
docker logs genai-fastapi-backend --tail 50
```

### 3. Restart Jupyter Kernel

In Jupyter, click **Kernel** → **Restart Kernel** to reload environment variables.

### 4. Re-run Notebook Cells

```python
# Re-run Cell 1 (imports and setup)
# Re-run Cell 20 (task function)
# Re-run the experiment cells

# You should now see:
# Processing: บางบำหรุ1 (6 pages)
# ✅ Success!
```

---

## Testing API Key Manually

### Test with curl

```bash
# Without API key (should fail if API_KEY is set)
curl -X POST "http://localhost:8000/api/v1/vote-extraction/extract" \
  -F "files=@path/to/image.jpg"

# Expected: 401 Unauthorized

# With API key (should succeed)
curl -X POST "http://localhost:8000/api/v1/vote-extraction/extract" \
  -H "X-API-Key: your-secret-key-here" \
  -F "files=@path/to/image.jpg"

# Expected: 200 OK with JSON response
```

### Test in Python

```python
import httpx
import os

API_BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY", "")

headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY

with httpx.Client() as client:
    response = client.post(
        f"{API_BASE_URL}/api/v1/vote-extraction/extract",
        files=[("files", ("test.jpg", open("test.jpg", "rb"), "image/jpeg"))],
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
```

---

## Common Issues

### Issue 1: "Still getting 401 after updating notebook"

**Solution**: Restart Jupyter kernel to reload environment variables.

```
Jupyter → Kernel → Restart Kernel
```

### Issue 2: "API_KEY environment variable not found"

**Solution**: Ensure `.env` file is in the project root and load it:

```python
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

# Now API_KEY should be available
API_KEY = os.getenv("API_KEY", "")
print(f"API_KEY loaded: {'Yes' if API_KEY else 'No'}")
```

### Issue 3: "Backend still requires API key after setting API_KEY="

**Solution**: Restart the FastAPI backend:

```bash
docker-compose restart fastapi-backend
```

### Issue 4: "API key works in curl but not in notebook"

**Solution**: Check that the notebook is loading the same `.env` file:

```python
# In notebook cell
import os
from pathlib import Path

print(f"Current directory: {Path.cwd()}")
print(f"Project root: {Path.cwd().parents[0]}")
print(f"API_KEY: {os.getenv('API_KEY', '(not set)')}")
```

---

## Best Practices

### 1. **Use Environment Variables**

✅ **DO**: Store API keys in `.env` file
```bash
API_KEY=your-secret-key-here
```

❌ **DON'T**: Hardcode API keys in notebooks
```python
# BAD: Don't do this!
API_KEY = "your-secret-key-here"
```

### 2. **Document Configuration in Notebooks**

Add a markdown cell at the beginning of experiment sections:

```markdown
### ⚠️ Configuration Required

This experiment requires:
- `API_KEY` set in `.env` file
- FastAPI backend running (`docker-compose up fastapi-backend`)
- Images available in `assets/ss5-18-images/`

Run this cell to verify:
```

```python
import os
print(f"✅ API_KEY: {'Set' if os.getenv('API_KEY') else '❌ Not set'}")
print(f"✅ API_BASE_URL: {os.getenv('API_BASE_URL', 'Not set')}")
```

### 3. **Provide Clear Error Messages**

Update task functions to provide helpful error messages:

```python
try:
    response = client.post(url, files=files, headers=headers)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("❌ 401 Unauthorized: Check API_KEY in .env file")
        print("   Run: cat .env | grep API_KEY")
        print("   Then restart Jupyter kernel to reload")
    raise
```

---

## Related Resources

### Documentation
- [FastAPI Backend Security](../../services/fastapi-backend/app/core/security.py)
- [Docker Compose Configuration](../../docker-compose.yml)
- [Environment Variables Reference](../reference/environment-variables.md)

### Implementation Files
- Notebook: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
- Security: `services/fastapi-backend/app/core/security.py`
- Config: `services/fastapi-backend/app/config.py`

### Related Issues
- [ddtrace Import Errors](DDTRACE_IMPORT_ERRORS.md)
- [Dataset Object Attributes](DATASET_OBJECT_ATTRIBUTES.md)

---

## Summary

✅ **Issue**: 401 Unauthorized when calling backend from notebook

✅ **Root Cause**: Backend requires API key but notebook wasn't sending it

✅ **Solution**: Updated notebook to load `API_KEY` from environment and include `X-API-Key` header

✅ **Configuration**: Set `API_KEY` in `.env` file or disable with `API_KEY=""` and `API_KEY_REQUIRED=false`

✅ **Verification**: Restart Jupyter kernel and re-run experiment cells

---

**Status**: ✅ Fixed  
**Next Steps**: 
1. Check/update your `.env` file
2. Restart Jupyter kernel
3. Re-run Cell 20 and experiment cells


