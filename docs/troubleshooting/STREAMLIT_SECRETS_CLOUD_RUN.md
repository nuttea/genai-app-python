# 🚨 Fix Streamlit Secrets Error on Cloud Run

## Problem

Streamlit app deployed to Cloud Run fails with:

```
streamlit.errors.StreamlitSecretNotFoundError: No secrets found.
Valid paths for a secrets.toml file or secret directories are:
/home/appuser/.streamlit/secrets.toml, /app/.streamlit/secrets.toml
```

**Error Location**: `pages/1_🗳️_Vote_Extractor.py`, line 16

**Root Cause**: The code tries to access `st.secrets.get()` which throws an exception if `secrets.toml` doesn't exist, even before it can return the default value.

## Solutions

### ✅ Solution 1: Use Try-Except (Recommended)

Gracefully handle missing `secrets.toml` file.

**Update `frontend/streamlit/pages/1_🗳️_Vote_Extractor.py`**:

```python
# Configuration - prioritize environment variable, fallback to secrets if available
def get_config(key: str, default: str = "") -> str:
    """Get configuration from environment or secrets, with fallback."""
    # First try environment variable
    env_value = os.getenv(key)
    if env_value:
        return env_value

    # Then try secrets.toml (for local development)
    try:
        return st.secrets.get(key, default)
    except Exception:
        # No secrets file (normal for Cloud Run)
        return default

API_BASE_URL = get_config("API_BASE_URL", "http://localhost:8000")
API_KEY = get_config("API_KEY", "")
```

**Benefits**:
- ✅ Works in Cloud Run (uses environment variables)
- ✅ Works locally with `secrets.toml` (development)
- ✅ Works locally without `secrets.toml` (uses defaults)
- ✅ No security issues (secrets not in repository)

---

### ✅ Solution 2: Environment Variables Only (Simplest)

Remove `st.secrets` dependency entirely.

**Update `frontend/streamlit/pages/1_🗳️_Vote_Extractor.py`**:

```python
# Configuration - use environment variables (Cloud Run best practice)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")
```

**For Local Development**, set environment variables in `docker-compose.yml`:

```yaml
streamlit-frontend:
  environment:
    - API_BASE_URL=http://fastapi-backend:8000
    - API_KEY=${API_KEY:-your-local-key}
```

Or use `.env` file (already in `.gitignore`):

```bash
# .env
API_BASE_URL=http://localhost:8000
API_KEY=your-local-api-key
```

**Benefits**:
- ✅ Simplest solution
- ✅ Consistent with Cloud Run deployment
- ✅ Works with Docker Compose
- ✅ No `secrets.toml` needed

---

### ⚠️ Solution 3: Create secrets.toml in Docker (Not Recommended)

Only use this if you absolutely need `secrets.toml` for some reason.

**Update `frontend/streamlit/Dockerfile`**:

```dockerfile
# Create empty secrets.toml
RUN mkdir -p /app/.streamlit && \
    echo "[secrets]" > /app/.streamlit/secrets.toml && \
    echo "# Secrets are loaded from environment variables" >> /app/.streamlit/secrets.toml
```

**Cons**:
- ❌ Adds unnecessary complexity
- ❌ Still need environment variables in Cloud Run
- ❌ Doesn't solve the actual problem

---

### 🔧 Solution 4: Mount Secrets as File (Advanced)

Use Cloud Run's secret mounting feature to create `secrets.toml` from Secret Manager.

**Not recommended** for this use case because:
- Environment variables are simpler
- Cloud Run already sets environment variables
- File mounting adds complexity

---

## Recommended Approach

**Use Solution 1 (Try-Except)** - Best of both worlds:
- Works in all environments
- Supports local development with `secrets.toml` (optional)
- Supports Cloud Run with environment variables
- Graceful fallback to defaults

## Implementation

1. **Update the code** (see Solution 1)
2. **Test locally**:
   ```bash
   cd frontend/streamlit
   streamlit run app.py
   ```
3. **Commit and push**:
   ```bash
   git add frontend/streamlit/pages/1_🗳️_Vote_Extractor.py
   git commit -m "fix: Handle missing secrets.toml gracefully for Cloud Run"
   git push
   ```
4. **Deploy** will happen automatically via CI/CD

## Verification

After deployment, check Cloud Run logs:
```bash
gcloud run services logs read streamlit-frontend --region=us-central1 --limit=50
```

The app should start successfully without `StreamlitSecretNotFoundError`.

## Environment Variables in Cloud Run

Cloud Run deployment already sets these (see `.github/workflows/streamlit-frontend.yml`):

```yaml
--set-env-vars API_BASE_URL=${{ steps.get-backend-url.outputs.backend_url }}
```

No additional configuration needed! ✅

---

**Created**: December 29, 2024
**Related**:
- Cloud Run deployment: `infra/cloud-run/deploy-frontend.sh`
- CI/CD workflow: `.github/workflows/streamlit-frontend.yml`
- Docker Compose: `docker-compose.yml`
