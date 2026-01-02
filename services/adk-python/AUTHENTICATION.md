# Authentication for Image Generation Service

## Overview

The image generation service supports multiple authentication methods:

1. **IAP (Identity-Aware Proxy)** - For Cloud Run deployments with IAP enabled
2. **Google OAuth** - For applications using Google Sign-In
3. **Development Mode** - No authentication required (local testing)

## Authentication Methods

### 1. IAP Authentication (Recommended for Production)

**When to use**: Cloud Run deployments with Identity-Aware Proxy enabled.

**How it works**:
- Cloud Run's IAP adds `X-Serverless-Authorization` header with JWT token
- Backend verifies the JWT token using Google's verification library
- User email and ID extracted from verified token

**Setup**:
```bash
# Set IAP audience (OAuth 2.0 Client ID from IAP)
export IAP_AUDIENCE="your-iap-client-id.apps.googleusercontent.com"
```

**Request Example**:
```bash
curl -X POST https://your-service.run.app/api/v1/images/generate \
  -H "X-Serverless-Authorization: <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "datadog mascot", "image_type": "comic"}'
```

**IAP automatically adds this header** - no manual intervention needed.

### 2. Google OAuth Authentication

**When to use**: Frontend applications using Google Sign-In.

**How it works**:
- Frontend obtains Google OAuth ID token via `gapi.auth2` or similar
- Frontend sends token in `Authorization: Bearer` header
- Backend verifies token using Google's verification library

**Setup**:
```bash
# Set Google OAuth Client ID (from Google Cloud Console)
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
```

**Request Example**:
```bash
curl -X POST http://localhost:8002/api/v1/images/generate \
  -H "Authorization: Bearer <GOOGLE_ID_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "datadog mascot", "image_type": "comic"}'
```

**Frontend Integration** (Next.js example):
```typescript
// After Google Sign-In
const user = gapi.auth2.getAuthInstance().currentUser.get();
const idToken = user.getAuthResponse().id_token;

// Include in API requests
const response = await fetch('/api/v1/images/generate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${idToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'datadog mascot',
    image_type: 'comic',
  }),
});
```

### 3. Development Mode (Local Testing)

**When to use**: Local development and testing.

**How it works**:
- If `DD_ENV=development` and no valid auth headers
- Service accepts requests with mock user (`dev@localhost`)
- **⚠️ WARNING**: Not secure, only for local testing

**Setup**:
```bash
# Automatically enabled when DD_ENV=development
export DD_ENV=development
```

**Request Example**:
```bash
# No authentication headers needed
curl -X POST http://localhost:8002/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "datadog mascot", "image_type": "comic"}'
```

## Authentication Flow

```
┌─────────────────────┐
│   Client Request    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Check X-Serverless-Authorization?   │
│         (IAP Header)                  │
└──────────┬───────────────────────────┘
           │ Yes
           ▼
    ┌──────────────┐
    │ Verify IAP   │──► Success ──► Proceed
    │ JWT Token    │
    └──────────────┘
           │ No/Invalid
           ▼
┌──────────────────────────────────────┐
│  Check Authorization: Bearer?         │
│      (Google OAuth)                   │
└──────────┬───────────────────────────┘
           │ Yes
           ▼
    ┌──────────────┐
    │ Verify OAuth │──► Success ──► Proceed
    │  ID Token    │
    └──────────────┘
           │ No/Invalid
           ▼
┌──────────────────────────────────────┐
│  DD_ENV == development?               │
└──────────┬───────────────────────────┘
           │ Yes
           ▼
    ┌──────────────┐
    │ Allow Dev    │──► Proceed
    │   Access     │
    └──────────────┘
           │ No
           ▼
    ┌──────────────┐
    │ Return 401   │
    │ Unauthorized │
    └──────────────┘
```

## Response Format

Successful authentication adds user information to response:

```json
{
  "status": "success",
  "image_url": "/uploads/20260102_130000_abc.png",
  "mime_type": "image/png",
  "session_id": "rum_abc123",
  "user_email": "user@example.com",
  "user_id": "1234567890",
  "text_response": "Image generated successfully",
  "file_size_bytes": 1234567
}
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `IAP_AUDIENCE` | For IAP | OAuth 2.0 Client ID from IAP settings | `123456.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_ID` | For OAuth | OAuth Client ID from Google Cloud Console | `your-app.apps.googleusercontent.com` |
| `DD_ENV` | No | Environment name (enables dev mode if `development`) | `production` |

## Cloud Run Deployment

### With IAP Enabled

```bash
# Deploy with IAP audience
gcloud run deploy genai-adk-python \
  --image gcr.io/your-project/genai-adk-python \
  --set-env-vars="IAP_AUDIENCE=your-iap-client-id.apps.googleusercontent.com"

# Enable IAP (via Console or gcloud)
# IAP automatically adds X-Serverless-Authorization header
```

### With Google OAuth (No IAP)

```bash
# Deploy with Google OAuth Client ID
gcloud run deploy genai-adk-python \
  --image gcr.io/your-project/genai-adk-python \
  --set-env-vars="GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com" \
  --allow-unauthenticated  # Frontend handles auth
```

## Security Best Practices

### Production

✅ **DO**:
- Enable IAP for Cloud Run services
- Use HTTPS/TLS for all communications
- Set `DD_ENV=production` (disables dev mode)
- Rotate OAuth credentials regularly
- Monitor authentication failures

❌ **DON'T**:
- Use development mode in production
- Expose IAP audience or OAuth credentials
- Allow unauthenticated access to production
- Skip token verification

### Development

✅ **DO**:
- Use `DD_ENV=development` for local testing
- Test with real OAuth tokens when possible
- Document authentication requirements

❌ **DON'T**:
- Commit OAuth credentials to git
- Use production credentials in development
- Expose development endpoints publicly

## Troubleshooting

### 401 Unauthorized

**Symptoms**: `{"detail": "Authentication required. Provide X-Serverless-Authorization (IAP) or Authorization: Bearer (Google OAuth) header."}`

**Solutions**:
1. **IAP**: Ensure IAP is enabled and `IAP_AUDIENCE` is set correctly
2. **OAuth**: Verify `GOOGLE_CLIENT_ID` matches your OAuth app
3. **Dev Mode**: Set `DD_ENV=development` for local testing

### Invalid Token

**Symptoms**: `⚠️ IAP JWT verification failed` or `⚠️ Google OAuth verification failed` in logs

**Solutions**:
1. **Expired Token**: Tokens expire (typically 1 hour) - refresh and retry
2. **Wrong Audience**: Verify `IAP_AUDIENCE` or `GOOGLE_CLIENT_ID`
3. **Invalid Issuer**: Token must be from Google (`accounts.google.com` or `cloud.google.com/iap`)

### Development Mode Not Working

**Symptoms**: Still getting 401 even with `DD_ENV=development`

**Solutions**:
1. Verify environment variable: `echo $DD_ENV`
2. Restart service after setting environment variable
3. Check logs for "Using development mode authentication"

## Testing

### Test IAP Authentication

```python
import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Get IAP token (Cloud Shell or authenticated environment)
request = google_requests.Request()
token = id_token.fetch_id_token(request, "your-iap-audience")

# Make authenticated request
response = requests.post(
    "https://your-service.run.app/api/v1/images/generate",
    headers={"X-Serverless-Authorization": token},
    json={"prompt": "test", "image_type": "diagram"},
)
print(response.json())
```

### Test Google OAuth

```python
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Get OAuth token (after user signs in via frontend)
# This example assumes you already have the token
oauth_token = "your-google-oauth-id-token"

# Make authenticated request
response = requests.post(
    "http://localhost:8002/api/v1/images/generate",
    headers={"Authorization": f"Bearer {oauth_token}"},
    json={"prompt": "test", "image_type": "diagram"},
)
print(response.json())
```

### Test Development Mode

```bash
# Set development environment
export DD_ENV=development

# Start service
python main_adk.py

# Make unauthenticated request (will succeed in dev mode)
curl -X POST http://localhost:8002/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "image_type": "diagram"}'
```

## Implementation Details

### Code Structure

```
app/services/
├── auth.py                 # Authentication service
│   ├── AuthService         # Main auth service class
│   ├── User                # User data model
│   ├── get_current_user    # FastAPI dependency (required)
│   └── get_optional_user   # FastAPI dependency (optional)
└── __init__.py             # Exports
```

### FastAPI Dependency Injection

```python
from fastapi import Depends
from app.services import User, get_current_user, get_optional_user

# Required authentication
@app.post("/protected")
async def protected_endpoint(user: User = Depends(get_current_user)):
    return {"user": user.email}

# Optional authentication
@app.post("/public")
async def public_endpoint(user: User = Depends(get_optional_user)):
    if user:
        return {"authenticated": True, "user": user.email}
    return {"authenticated": False}
```

## References

- [Google Cloud IAP Documentation](https://cloud.google.com/iap/docs)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Verifying Google ID Tokens](https://cloud.google.com/docs/authentication/token-types#id)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

