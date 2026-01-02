# Fix CORS Error: IAP Redirect Issue

## Problem

Next.js frontend encounters CORS error when accessing ADK Python backend:

```
Access to fetch at 'https://genai-adk-python-cn4wkmlbva-uc.a.run.app/...' 
from origin 'https://genai-nextjs-frontend-449012790678.us-central1.run.app' 
has been blocked by CORS policy: Response to preflight request doesn't pass 
access control check: Redirect is not allowed for a preflight request.
```

## Root Cause

**Identity-Aware Proxy (IAP)** is enabled on the Cloud Run service, which:

1. Intercepts ALL requests (including OPTIONS preflight)
2. Redirects to Google OAuth authentication
3. Returns `HTTP 302` redirect **before** CORS headers can be processed
4. Browsers reject redirects during CORS preflight

### Diagnosis Evidence

```bash
$ curl -I https://genai-adk-python-cn4wkmlbva-uc.a.run.app/health

HTTP/2 302 
x-goog-iap-generated-response: true
location: https://accounts.google.com/o/oauth2/v2/auth?...
```

**Key indicators:**
- `HTTP/2 302` - Redirect
- `x-goog-iap-generated-response: true` - IAP is intercepting
- `set-cookie: GCP_IAP_XSRF_NONCE...` - IAP CSRF token

## Solution

### Option 1: Disable IAP (Recommended for Public APIs)

Disable IAP on Cloud Run services that need to be publicly accessible:

```bash
# ADK Python Service
gcloud run services update genai-adk-python \
  --region us-central1 \
  --allow-unauthenticated

# FastAPI Backend Service
gcloud run services update genai-fastapi-backend \
  --region us-central1 \
  --allow-unauthenticated

# Next.js Frontend Service
gcloud run services update genai-nextjs-frontend \
  --region us-central1 \
  --allow-unauthenticated
```

**Verify the fix:**

```bash
curl -I https://genai-adk-python-cn4wkmlbva-uc.a.run.app/health
# Should return HTTP/2 200 (not 302)
```

### Option 2: Configure IAP Bypass for CORS (Advanced)

If you need IAP but want to allow CORS:

1. **Use API Key Authentication** instead of IAP for API endpoints
2. **Configure IAP to exclude specific paths**:
   - In GCP Console → Security → Identity-Aware Proxy
   - Add CORS paths to bypass list
3. **Use Service Account authentication** for service-to-service calls

### Option 3: Use IAP-Aware Client (Complex)

Configure Next.js frontend to:
1. Obtain IAP JWT token
2. Include `Authorization: Bearer <IAP_TOKEN>` in requests
3. Handle token refresh

**Not recommended** for simple deployments.

---

## How IAP Was Enabled

IAP can be enabled through:

1. **GCP Console**: Security → Identity-Aware Proxy → Enable
2. **gcloud CLI**: `gcloud iap web enable`
3. **Terraform/Infrastructure as Code**
4. **Organization Policy** (enforced at org/folder level)

Our GitHub Actions workflows deploy with `--allow-unauthenticated`, but IAP can be manually enabled after deployment.

---

## Updated Workflow Configuration

**Current workflow** (`.github/workflows/adk-python-prod.yml`):

```yaml
env_vars: |
  ALLOWED_ORIGINS=https://genai-nextjs-frontend-449012790678.us-central1.run.app,*
```

**Deployment includes:**
```bash
--allow-unauthenticated
```

This ensures future deployments don't have IAP issues.

---

## Verification Steps

### 1. Check IAP Status

```bash
gcloud iap web get-iam-policy \
  --resource-type=backend-services \
  --service=genai-adk-python \
  --region=us-central1
```

### 2. Test CORS Preflight

```bash
curl -X OPTIONS \
  -H "Origin: https://genai-nextjs-frontend-449012790678.us-central1.run.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -i \
  https://genai-adk-python-cn4wkmlbva-uc.a.run.app/apps/content_creator_agent/users/user_nextjs/sessions
```

**Expected (Success):**
```
HTTP/2 200
access-control-allow-origin: https://genai-nextjs-frontend-449012790678.us-central1.run.app
access-control-allow-methods: POST, OPTIONS
access-control-allow-headers: Content-Type
```

**Actual (with IAP):**
```
HTTP/2 302
x-goog-iap-generated-response: true
location: https://accounts.google.com/o/oauth2/v2/auth...
```

### 3. Test from Browser

Open DevTools Console on Next.js frontend:

```javascript
fetch('https://genai-adk-python-cn4wkmlbva-uc.a.run.app/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

**Success**: Returns `{"status": "ok"}` or similar
**Failure**: CORS error in console

---

## Prevention

### In GCP Console

1. Go to **Security → Identity-Aware Proxy**
2. Verify services are **NOT** listed under "HTTPS Resources"
3. If listed, click and select **"Disable IAP"**

### In GitHub Actions

Workflows already include `--allow-unauthenticated`:

```yaml
# .github/workflows/_reusable-cloudrun-deploy.yml
gcloud run deploy ${{ inputs.service_name }} \
  --allow-unauthenticated \
  ...
```

### Organization Policy

Check if IAP is enforced by organization policy:

```bash
gcloud resource-manager org-policies describe \
  constraints/iam.requireIap \
  --project=$GCP_PROJECT_ID
```

---

## Related Documentation

- [CORS Configuration](../reference/CORS_CONFIGURATION.md)
- [Cloud Run Authentication](../deployment/CLOUD_RUN_AUTHENTICATION.md)
- [API Security Best Practices](../reference/API_SECURITY.md)

---

## Quick Fix Checklist

- [ ] Run `gcloud run services update genai-adk-python --region us-central1 --allow-unauthenticated`
- [ ] Verify no IAP in GCP Console → Security → Identity-Aware Proxy
- [ ] Test CORS preflight (should return 200, not 302)
- [ ] Test from Next.js frontend browser console
- [ ] Monitor Datadog for successful requests

---

## Status

**Issue**: IAP enabled on Cloud Run services causing CORS redirect errors
**Fix**: Disable IAP with `--allow-unauthenticated`
**Workflow Updated**: ✅ ALLOWED_ORIGINS includes Next.js frontend URL
**Action Required**: Run gcloud commands to disable IAP on existing services

---

**Last Updated**: 2026-01-02  
**Related Issue**: CORS preflight redirect error  
**Severity**: High - Blocks frontend-backend communication

