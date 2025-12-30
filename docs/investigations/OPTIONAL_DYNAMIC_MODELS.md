# Optional: Dynamic Model Listing with Google AI API

## Overview

You have `GEMINI_API_KEY` in Secret Manager. Here's how you **could** use it for dynamic model listing, but **we recommend the static list approach** for production.

## Option 1: Static List (Current - Recommended) ✅

**Pros:**
- ✅ No external API dependency
- ✅ Fast response (no network calls)
- ✅ Reliable (no timeout risk)
- ✅ Simple (one auth mechanism)
- ✅ No rate limits to worry about

**Cons:**
- Requires manual updates (but Gemini models are stable)

## Option 2: Dynamic Listing with REST API

### Configuration

**1. Update Cloud Run workflow to include GEMINI_API_KEY:**

```yaml
# .github/workflows/fastapi-backend.yml
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy ${{ env.SERVICE_NAME }} \
      # ... existing config ...
      --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

**2. Add environment variable to docker-compose for local dev:**

```yaml
# docker-compose.yml
fastapi-backend:
  environment:
    - GEMINI_API_KEY=${GEMINI_API_KEY}
```

**3. Update settings to include API key:**

```python
# services/fastapi-backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    gemini_api_key: Optional[str] = None  # For dynamic model listing
```

**4. Implement dynamic model listing:**

```python
# services/fastapi-backend/app/api/v1/endpoints/vote_extraction.py

import httpx
from typing import Optional

# Cache for models (refresh every hour)
_models_cache: Optional[dict] = None
_cache_timestamp: Optional[float] = None
CACHE_TTL = 3600  # 1 hour

async def fetch_models_from_api() -> list[dict]:
    """Fetch models dynamically from Google AI API."""
    global _models_cache, _cache_timestamp

    # Check cache
    if _models_cache and _cache_timestamp:
        if time.time() - _cache_timestamp < CACHE_TTL:
            return _models_cache

    # Fetch from API
    api_key = settings.gemini_api_key
    if not api_key:
        return []  # Fallback to static list

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            response = await client.get(url)
            response.raise_for_status()

            models_data = response.json()

            # Transform to our format
            transformed = []
            for model in models_data.get("models", []):
                if "gemini" in model["name"].lower():
                    transformed.append({
                        "name": model["name"].replace("models/", ""),
                        "display_name": model.get("displayName", ""),
                        "description": model.get("description", "")[:200],
                        "context_window": model.get("inputTokenLimit", 0),
                        "output_tokens": model.get("outputTokenLimit", 0),
                        "supported": True,
                    })

            # Update cache
            _models_cache = transformed
            _cache_timestamp = time.time()

            return transformed

    except Exception as e:
        logger.error(f"Failed to fetch models from API: {e}")
        return []  # Fallback to static list

@router.get("/models", summary="List available LLM models")
async def list_models() -> JSONResponse:
    """List available LLM models with dynamic fetching."""

    # Try dynamic fetch first
    dynamic_models = await fetch_models_from_api()

    # Fallback to static list if dynamic fails
    if not dynamic_models:
        dynamic_models = gemini_models  # Our curated static list

    models_config = {
        "providers": [
            {
                "name": "vertex_ai",
                "display_name": "Google Vertex AI / Gemini API",
                "models": dynamic_models,
                "default_model": "gemini-2.5-flash",
                "supported": True,
            }
        ],
        "default_config": {
            "provider": "vertex_ai",
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "max_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40,
        },
    }

    return JSONResponse(content=models_config)
```

### Pros of Dynamic Listing
- ✅ Always up-to-date with latest models
- ✅ Auto-discovers new Gemini models

### Cons of Dynamic Listing
- ❌ External API dependency (timeout risk)
- ❌ Requires managing API key separately from Vertex AI auth
- ❌ Potential rate limits
- ❌ Added complexity (two auth mechanisms)
- ❌ Slower response (network call)
- ❌ Python SDK doesn't support it (must use REST API)

## Recommendation

### For Production: Use Static List ✅

**Why?**
1. **Gemini models are stable** - New models released infrequently
2. **Reliability > Freshness** - Better UX with instant, reliable response
3. **Simpler Architecture** - One auth mechanism (GCP Workload Identity)
4. **Security** - Fewer credentials to manage
5. **Performance** - No network latency

### When to Consider Dynamic Listing

Only if:
- Models change frequently (they don't)
- You need to support many model families (we only use Gemini)
- You're building a model marketplace/explorer app

## Current Status

✅ **We already have the optimal solution!**

Your `GEMINI_API_KEY` in Secret Manager is available if needed, but our static list approach is:
- Faster
- More reliable
- Simpler to maintain
- Better for production

No changes recommended! 🎉
