# ✅ Jupyter Notebook 401 Error - Quick Fix

**Issue**: `Client error '401 Unauthorized'` when running experiments  
**Status**: ✅ Fixed  
**Date**: January 4, 2026

---

## 🎯 Problem

```
❌ Error processing บางบำหรุ1: Client error '401 Unauthorized' for url 'http://localhost:8000/api/v1/vote-extraction/extract'
```

---

## ✅ Quick Fix (2 Steps)

### Step 1: Configure API Key

**Option A: Use API Key** (Recommended)

Add to your `.env` file:
```bash
API_KEY=your-secret-key-here
API_KEY_REQUIRED=true
```

**Option B: Disable API Key** (Quick Testing)

Add to your `.env` file:
```bash
API_KEY=
API_KEY_REQUIRED=false
```

Then restart the backend:
```bash
docker-compose restart fastapi-backend
```

### Step 2: Restart Jupyter Kernel

In Jupyter: **Kernel** → **Restart Kernel**

---

## ✅ What Was Fixed

The notebook now automatically loads `API_KEY` from environment and includes it in requests:

**File**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`

**Cell 20** - Updated to include API key:

```python
# Load API key from environment
API_KEY = os.getenv("API_KEY", "")

# Prepare headers with API key
headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY

# Call extraction API with authentication
with httpx.Client(timeout=300.0) as client:
    response = client.post(
        f"{API_BASE_URL}/api/v1/vote-extraction/extract",
        files=files,
        headers=headers  # ✅ API key included!
    )
```

---

## 🧪 Test the Fix

### 1. Check Your Configuration

```bash
# Check .env file
cat .env | grep API_KEY
```

### 2. Restart Services

```bash
# Restart backend (if you changed .env)
docker-compose restart fastapi-backend

# Check logs
docker logs genai-fastapi-backend --tail 20
```

### 3. Restart Jupyter + Re-run

1. **Jupyter** → **Kernel** → **Restart Kernel**
2. Re-run Cell 1 (imports)
3. Re-run Cell 20 (task function)
4. Re-run your experiment cells

**Expected Output**:
```
Processing: บางบำหรุ1 (6 pages)
✅ Success!
```

---

## 💡 Why This Happened

**Backend Authentication Logic**:

| `API_KEY` | `API_KEY_REQUIRED` | Result |
|-----------|-------------------|--------|
| Empty | `false` | ✅ No auth needed |
| Empty | `true` | ❌ 401 error |
| Set | `false` | ✅ Requires `X-API-Key` |
| Set | `true` | ✅ Requires `X-API-Key` |

**If `API_KEY` is set**, the backend requires authentication. The notebook now automatically includes the key in requests.

---

## 🔧 Files Updated

| File | Change |
|------|--------|
| `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` | ✅ Cell 19: Added API key config note<br>✅ Cell 20: Load API_KEY and add headers |
| `docs/troubleshooting/NOTEBOOK_401_API_KEY.md` | ✅ Comprehensive guide (new) |
| `docs/INDEX.md` | ✅ Added link |
| `NOTEBOOK_401_FIX.md` | ✅ Quick reference (this file) |

---

## 📚 Complete Example

### Recommended `.env` Configuration

```bash
# Project Root
GOOGLE_CLOUD_PROJECT=datadog-ese-sandbox
GCP_REGION=us-central1

# FastAPI Backend
API_BASE_URL=http://localhost:8000
API_KEY=your-secret-key-here          # ✅ Set a strong key
API_KEY_REQUIRED=true                  # ✅ Enforce authentication

# Datadog
DD_API_KEY=your-datadog-api-key
DD_APP_KEY=your-datadog-app-key
DD_SITE=datadoghq.com

# Google AI (optional, for dynamic model listing)
GEMINI_API_KEY=your-gemini-api-key
```

### Notebook Check Cell

Add this cell to verify configuration:

```python
import os

print("🔍 Configuration Check:")
print(f"  API_BASE_URL: {os.getenv('API_BASE_URL', '❌ Not set')}")
print(f"  API_KEY: {'✅ Set' if os.getenv('API_KEY') else '❌ Not set'}")
print(f"  DD_API_KEY: {'✅ Set' if os.getenv('DD_API_KEY') else '❌ Not set'}")
print(f"  DD_APP_KEY: {'✅ Set' if os.getenv('DD_APP_KEY') else '❌ Not set'}")
```

---

## 🚨 Common Issues

### "Still getting 401 after updating"

**Solution**: Restart Jupyter kernel to reload environment variables.

### "API_KEY not found in environment"

**Solution**: Check `.env` file location and reload:

```python
from dotenv import load_dotenv
from pathlib import Path

# Load from project root
project_root = Path.cwd().parents[1]  # Adjust path as needed
load_dotenv(project_root / ".env")

print(f"✅ Loaded from: {project_root / '.env'}")
print(f"   API_KEY: {'Set' if os.getenv('API_KEY') else 'Not set'}")
```

### "Backend logs show 'Missing API key'"

**Solution**: The notebook isn't including the header. Re-run Cell 20 after restarting kernel.

---

## 🔗 Related Resources

- **Detailed Guide**: [docs/troubleshooting/NOTEBOOK_401_API_KEY.md](docs/troubleshooting/NOTEBOOK_401_API_KEY.md)
- **Backend Security**: `services/fastapi-backend/app/core/security.py`
- **Docker Compose**: `docker-compose.yml`

---

## ✨ Quick Checklist

- [ ] `.env` file has `API_KEY` set (or explicitly empty)
- [ ] `.env` file has `API_KEY_REQUIRED` configured
- [ ] Backend restarted: `docker-compose restart fastapi-backend`
- [ ] Jupyter kernel restarted: **Kernel** → **Restart Kernel**
- [ ] Cell 1 (imports) re-run
- [ ] Cell 20 (task function) re-run
- [ ] Experiment cells re-run

---

**Ready!** 🚀 Your experiments should now work without 401 errors!


