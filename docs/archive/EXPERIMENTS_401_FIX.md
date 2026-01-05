# ✅ Fixed: Experiments 401 Unauthorized Error

**Issue**: Streamlit experiments page returned `401 Unauthorized` when trying to run experiments  
**Root Cause**: Missing `DD_APP_KEY` environment variable in FastAPI backend  
**Solution**: Added `DD_APP_KEY` to docker-compose.yml  
**Status**: ✅ Fixed  
**Date**: January 4, 2026

---

## 🐛 Problem

When trying to run experiments from the Streamlit UI, users encountered:

```
❌ Error 500: {"detail":"Failed to run experiments: Failed to create project vote-extraction-project: 401 {'errors': ['Unauthorized']}"}
```

---

## 🔍 Root Cause

The FastAPI backend was missing the `DD_APP_KEY` environment variable, which is required for Datadog LLMObs API operations like:
- Creating projects
- Creating/pulling datasets
- Running experiments

The backend had `DD_API_KEY` but not `DD_APP_KEY`.

---

## ✅ Solution

### 1. Updated docker-compose.yml

Added `DD_APP_KEY` to the fastapi-backend service:

```yaml
# docker-compose.yml
services:
  fastapi-backend:
    environment:
      # Datadog APM and LLM Observability (optional)
      - DD_API_KEY=${DD_API_KEY:-}
      - DD_APP_KEY=${DD_APP_KEY:-}  # ✅ Added this line
      - DD_SITE=${DD_SITE:-datadoghq.com}
```

### 2. Verified .env File

Ensured `.env` file contains both keys:

```bash
DD_API_KEY="your-datadog-api-key"
DD_APP_KEY="your-datadog-app-key"
```

### 3. Restarted Backend

```bash
docker compose down fastapi-backend
docker compose up -d fastapi-backend
```

---

## 🧪 Verification

### 1. Check Environment Variables

```bash
docker exec genai-fastapi-backend printenv | grep DD_APP_KEY
# Should output: DD_APP_KEY=your-key
```

### 2. Check Experiments Health

```bash
curl http://localhost:8000/api/v1/experiments/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "experiments",
  "datadog_configured": true,
  "api_key_configured": true
}
```

### 3. Test in Streamlit

1. Open http://localhost:8501
2. Navigate to "🧪 Run Experiments"
3. Configure and run an experiment
4. Should now work without 401 errors!

---

## 📝 Required Environment Variables

For experiments to work, the following environment variables must be set:

### In `.env` file:

```bash
# Datadog Configuration
DD_API_KEY="your-datadog-api-key"      # Required for APM
DD_APP_KEY="your-datadog-app-key"      # Required for LLMObs API
DD_SITE="datadoghq.com"                # Your Datadog site

# Backend API
API_KEY="your-backend-api-key"         # Required for Streamlit → Backend auth

# GCP Configuration
GOOGLE_CLOUD_PROJECT="your-gcp-project"
```

### How to Get Datadog Keys:

1. **DD_API_KEY**:
   - Go to Datadog → Organization Settings → API Keys
   - Create or copy an existing API key

2. **DD_APP_KEY**:
   - Go to Datadog → Organization Settings → Application Keys
   - Create or copy an existing application key

---

## 🔧 Troubleshooting

### Issue: Still getting 401 after restart

**Solution**: Make sure to recreate the container, not just restart:

```bash
docker compose down fastapi-backend
docker compose up -d fastapi-backend
```

### Issue: DD_APP_KEY not showing in environment

**Check 1**: Verify `.env` file has no typos:
```bash
grep DD_APP_KEY .env
```

**Check 2**: Verify docker-compose.yml has the line:
```bash
grep "DD_APP_KEY" docker-compose.yml
```

**Check 3**: Recreate containers:
```bash
docker compose down
docker compose up -d
```

### Issue: 403 Forbidden instead of 401

**Solution**: Your API key is valid but doesn't have the required permissions. Make sure the Datadog App Key has:
- `llm_obs_read` permission
- `llm_obs_write` permission

---

## 🎯 Summary

| Aspect | Before | After |
|--------|--------|-------|
| **DD_APP_KEY in backend** | ❌ Missing | ✅ Present |
| **Experiments API** | ❌ 401 Error | ✅ Working |
| **Streamlit UI** | ❌ Failed | ✅ Working |
| **Project Creation** | ❌ Unauthorized | ✅ Authorized |

---

## 📖 Related Files

- `docker-compose.yml` - Updated to pass DD_APP_KEY
- `.env` - Contains both DD_API_KEY and DD_APP_KEY
- `frontend/streamlit/pages/3_🧪_Run_Experiments.py` - Experiments UI
- `services/fastapi-backend/app/api/v1/endpoints/experiments.py` - Backend API

---

## ✅ Fixed!

The experiments feature now works correctly with proper Datadog authentication. You can run experiments from:
1. **Streamlit UI**: http://localhost:8501 → "🧪 Run Experiments"
2. **API**: `POST http://localhost:8000/api/v1/experiments/run`
3. **GitHub Actions**: `.github/workflows/run-experiments.yml`

**All three interfaces now work with proper Datadog authentication!** 🎉

