# API Key Authentication Setup

Complete guide for setting up API key authentication for the GenAI Application Platform.

## Overview

API key authentication protects your backend API from unauthorized access. This is especially important when deployed to Cloud Run with public access.

## Features

✅ **Configurable Validation** - Enable/disable API key requirement  
✅ **Secure Storage** - API keys stored in Google Secret Manager  
✅ **Automatic Integration** - Frontend automatically uses API keys  
✅ **Header-based** - Uses `X-API-Key` HTTP header  
✅ **Detailed Logging** - Track authentication attempts  

## Quick Setup

### Local Development

**Option 1: No Authentication (Default)**
```bash
# No configuration needed - API key validation is disabled by default
docker-compose up -d
```

**Option 2: With API Key**
```bash
# 1. Generate an API key
export API_KEY=$(openssl rand -hex 32)
echo "Your API Key: $API_KEY"

# 2. Add to .env file
cat >> .env <<EOF
API_KEY=${API_KEY}
API_KEY_REQUIRED=true
EOF

# 3. Update Streamlit secrets
cat > frontend/streamlit/.streamlit/secrets.toml <<EOF
API_BASE_URL = "http://fastapi-backend:8000"
API_KEY = "${API_KEY}"
EOF

# 4. Restart services
docker-compose down
docker-compose up -d
```

### Cloud Run Deployment

**Step 1: Setup API Key in Secret Manager**

```bash
# Generate and store API key
export API_KEY=$(openssl rand -hex 32)
echo "API Key: $API_KEY"

# Store in Secret Manager
cd infra/cloud-run
./setup-api-key.sh
```

**Step 2: Deploy with API Key Validation**

```bash
# Deploy backend with API key required
export API_KEY_REQUIRED=true
./deploy-backend.sh

# Deploy frontend (automatically uses API key from Secret Manager)
./deploy-frontend.sh
```

## Configuration

### Environment Variables

**Backend (FastAPI):**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | The API key value | `""` | Yes (if validation enabled) |
| `API_KEY_REQUIRED` | Enforce API key validation | `false` | No |

**Frontend (Streamlit):**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | API key to send to backend | `""` | Yes (if backend requires) |

### Behavior

**When `API_KEY_REQUIRED=false` (Default):**
- No API key validation
- All requests allowed
- Good for development/testing

**When `API_KEY_REQUIRED=true` or `API_KEY` is set:**
- API key required for all protected endpoints
- Requests without valid key get 401 Unauthorized
- Good for production

## API Key Format

API keys are 64-character hexadecimal strings:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

## Protected Endpoints

The following endpoints require API key when validation is enabled:

- `POST /api/v1/vote-extraction/extract` ✅ Protected
- `GET /api/v1/vote-extraction/health` ✅ Protected

Public endpoints (no API key needed):
- `GET /health` - Public health check
- `GET /ready` - Public readiness check
- `GET /` - Public root endpoint
- `GET /docs` - API documentation
- `GET /redoc` - API documentation

## Using API Keys

### From Streamlit Frontend

API key is automatically included when configured:

```bash
# Set in environment
export API_KEY=your-api-key

# Or in .streamlit/secrets.toml
API_KEY = "your-api-key"
```

### From curl

```bash
curl -X POST https://your-backend.run.app/api/v1/vote-extraction/extract \
  -H "X-API-Key: your-api-key-here" \
  -F "files=@page1.jpg"
```

### From Python

```python
import httpx

headers = {"X-API-Key": "your-api-key-here"}

with httpx.Client() as client:
    response = client.post(
        "https://your-backend.run.app/api/v1/vote-extraction/extract",
        headers=headers,
        files=[("files", ("page1.jpg", open("page1.jpg", "rb"), "image/jpeg"))]
    )
    result = response.json()
```

### From JavaScript

```javascript
const headers = {
  'X-API-Key': 'your-api-key-here'
};

const formData = new FormData();
formData.append('files', file);

const response = await fetch('https://your-backend.run.app/api/v1/vote-extraction/extract', {
  method: 'POST',
  headers: headers,
  body: formData
});

const result = await response.json();
```

## Error Responses

### Missing API Key

**Request:**
```bash
curl https://your-backend.run.app/api/v1/vote-extraction/extract
```

**Response:** `401 Unauthorized`
```json
{
  "detail": "Missing API key. Include X-API-Key header in your request."
}
```

### Invalid API Key

**Request:**
```bash
curl -H "X-API-Key: wrong-key" https://your-backend.run.app/api/v1/vote-extraction/extract
```

**Response:** `401 Unauthorized`
```json
{
  "detail": "Invalid API key"
}
```

## Security Best Practices

### ✅ Do's

1. **Use Secret Manager** in production
   ```bash
   ./setup-api-key.sh
   ```

2. **Generate strong keys**
   ```bash
   openssl rand -hex 32  # 64 character hex
   ```

3. **Rotate keys regularly** (every 90 days)
   ```bash
   ./setup-api-key.sh  # Updates existing secret
   ```

4. **Use different keys** for dev/staging/prod
   ```bash
   # Development
   API_KEY=dev-key-123...
   
   # Production
   API_KEY=prod-key-456...
   ```

5. **Monitor failed attempts**
   ```bash
   # Check logs for invalid API key attempts
   gcloud run services logs read genai-fastapi-backend | grep "Invalid API key"
   ```

### ❌ Don'ts

1. **Never commit API keys** to version control
2. **Don't use simple keys** like "test123" or "password"
3. **Don't share keys** across different environments
4. **Don't log full API keys** (only prefixes)
5. **Don't use API keys in URLs** (use headers only)

## Secret Manager Setup

### Create API Key Secret

**Automatic (Recommended):**
```bash
cd infra/cloud-run
export API_KEY=$(openssl rand -hex 32)  # Or use your own key
./setup-api-key.sh
```

**Manual:**
```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create api-key \
    --data-file=- \
    --replication-policy="automatic" \
    --project=YOUR_PROJECT_ID

# Grant access to Cloud Run
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding api-key \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=YOUR_PROJECT_ID
```

### Update API Key

```bash
# Generate new key
export API_KEY=$(openssl rand -hex 32)

# Update secret
echo -n "${API_KEY}" | gcloud secrets versions add api-key \
    --data-file=- \
    --project=YOUR_PROJECT_ID

# Redeploy services (they'll automatically pick up the new version)
cd infra/cloud-run
./deploy-backend.sh
./deploy-frontend.sh
```

### View API Key (Emergency Only)

```bash
# View current API key
gcloud secrets versions access latest --secret=api-key --project=YOUR_PROJECT_ID
```

⚠️ **Warning**: Only view API keys when absolutely necessary!

## Deployment Scenarios

### Scenario 1: Open Access (No API Key)

**Use Case**: Development, internal tools, MVP testing

```bash
# Deploy without API key
export API_KEY_REQUIRED=false
./deploy-backend.sh
./deploy-frontend.sh
```

### Scenario 2: API Key Protected

**Use Case**: Production, public deployment, cost control

```bash
# Setup API key
./setup-api-key.sh

# Deploy with API key required
export API_KEY_REQUIRED=true
./deploy-backend.sh
./deploy-frontend.sh
```

### Scenario 3: Mixed (Some endpoints protected)

**Use Case**: Public docs, protected operations

Currently all `/api/v1/*` endpoints are protected when API key is required.
Health checks (`/health`, `/ready`) and documentation (`/docs`) remain public.

## Troubleshooting

### Frontend can't connect to backend

**Symptom:** 401 Unauthorized errors

**Check:**
1. ✅ Backend has API key configured
2. ✅ Frontend has same API key
3. ✅ API key is stored in Secret Manager
4. ✅ Both services have access to the secret

**Fix:**
```bash
# Verify secrets exist
gcloud secrets list --project=YOUR_PROJECT_ID

# Check backend env vars
gcloud run services describe genai-fastapi-backend \
    --region us-central1 \
    --format="value(spec.template.spec.containers[0].env)"

# Check frontend env vars
gcloud run services describe genai-streamlit-frontend \
    --region us-central1 \
    --format="value(spec.template.spec.containers[0].env)"

# Redeploy if needed
cd infra/cloud-run
./deploy-all.sh
```

### API key not working

**Check the key is correct:**
```bash
# Get the key from Secret Manager
STORED_KEY=$(gcloud secrets versions access latest --secret=api-key)

# Test with curl
curl -H "X-API-Key: ${STORED_KEY}" https://your-backend.run.app/api/v1/vote-extraction/health
```

### Can't access Secret Manager

**Check permissions:**
```bash
# List IAM policy
gcloud secrets get-iam-policy api-key --project=YOUR_PROJECT_ID

# Add missing permission
gcloud secrets add-iam-policy-binding api-key \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --project=YOUR_PROJECT_ID
```

## Monitoring

### Track Authentication Events

**In Datadog (if configured):**
- Failed auth attempts: Filter logs by "Invalid API key"
- Success rate: Track 401 vs 200 responses
- API usage by key: Custom spans with key prefix

**In Cloud Logging:**
```bash
# View failed authentication attempts
gcloud logging read "jsonPayload.message=~\"Invalid API key\"" \
    --project=YOUR_PROJECT_ID \
    --limit=50
```

### Create Alert for Failed Auth

```bash
# In Cloud Monitoring, create alert:
# Condition: Count of 401 responses > 10 in 5 minutes
# Notification: Email or Slack
```

## Advanced: Multiple API Keys

To support multiple API keys (different clients):

**Option 1: Modify security.py**

```python
# app/core/security.py
VALID_API_KEYS = [
    settings.api_key,
    os.getenv("API_KEY_PARTNER_1"),
    os.getenv("API_KEY_PARTNER_2"),
]

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(status_code=401, detail="Invalid API key")
```

**Option 2: Use Database** (future enhancement)

Store API keys in Firestore/Cloud SQL with metadata:
- Client name
- Usage limits
- Expiration date
- Permissions

## Rate Limiting (Future Enhancement)

Combine API keys with rate limiting:

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.post("/extract", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def extract_votes(...):
    # Limited to 10 requests per minute per API key
    pass
```

## Resources

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Google Secret Manager](https://cloud.google.com/secret-manager/docs)
- [API Key Best Practices](https://cloud.google.com/endpoints/docs/openapi/when-why-api-key)

---

**Quick Start**: Run `./setup-api-key.sh` to generate and store a secure API key! 🔐

