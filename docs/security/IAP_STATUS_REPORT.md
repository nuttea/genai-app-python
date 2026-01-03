# IAP Status Report for Cloud Run Services

**Investigation Date**: 2026-01-02  
**Services Checked**: 
- Frontend: https://genai-nextjs-frontend-449012790678.us-central1.run.app/
- Backend: https://genai-adk-python-cn4wkmlbva-uc.a.run.app

---

## 🔍 **Current Status: IAP NOT Enabled**

### **Evidence from Datadog**

#### **1. Service Configuration Logs**
```
🔐 Auth Service initialized: IAP=False, OAuth=False
Timestamp: 2026-01-02T16:14:39Z
Service: genai-adk-python
```

**Analysis**: 
- `IAP=False` → `IAP_AUDIENCE` environment variable is NOT set
- `OAuth=False` → `GOOGLE_CLIENT_ID` environment variable is NOT set
- Service is running in **development mode** with no authentication

#### **2. Request Headers from Traces**

Analyzed 3 recent traces for `POST /api/v1/images/generate`:

**Headers Received**:
- ✅ `user-agent`: Mozilla/5.0 (Chrome 143.0.0.0)
- ✅ `content-type`: application/json (implied)
- ❌ **No `X-Serverless-Authorization`** (IAP header)
- ❌ **No `X-Goog-IAP-JWT-Assertion`** (IAP JWT)
- ❌ **No `X-Goog-Authenticated-User-Email`** (IAP user email)
- ❌ **No `Authorization: Bearer`** (OAuth header)

**Conclusion**: No IAP headers are present in any requests.

#### **3. Authentication Flow**

Current behavior based on auth service code:

```
Request arrives → Check X-Serverless-Authorization → Not found
               → Check Authorization: Bearer → Not found
               → Check DD_ENV → "dev" ✅ 
               → Use dev@localhost (no authentication required)
```

**User Identity**:
- **Email**: `dev@localhost`
- **User ID**: `dev_user`
- **Auth Method**: `development` (fallback mode)

---

## 🌐 **Why No IAP Headers?**

### **Cloud Run Configuration**

Based on Datadog traces and previous investigations:

1. **Service is Public** (`--allow-unauthenticated`):
   - Services were explicitly set to allow unauthenticated access
   - This was done to fix CORS preflight issues
   - See previous command: `gcloud run services update ... --allow-unauthenticated`

2. **IAP Not Configured**:
   - No `IAP_AUDIENCE` environment variable set
   - No IAP resources created in GCP Console
   - Services are directly accessible without Google Sign-In

3. **Development Environment**:
   - `DD_ENV=dev` (development mode)
   - Authentication is intentionally disabled for testing
   - All users default to `dev@localhost`

---

## 🔐 **How to Enable IAP (If Needed)**

### **Step 1: Configure IAP in GCP Console**

1. Go to [GCP Console > Security > Identity-Aware Proxy](https://console.cloud.google.com/security/iap?project=datadog-ese-sandbox)

2. Enable IAP API:
   ```bash
   gcloud services enable iap.googleapis.com --project=datadog-ese-sandbox
   ```

3. Create OAuth consent screen and credentials

4. Enable IAP for Cloud Run services:
   - Select `genai-adk-python`
   - Toggle "IAP" to ON
   - Add authorized users/groups

### **Step 2: Update Cloud Run Deployment**

```bash
# Remove --allow-unauthenticated flag
gcloud run services update genai-adk-python \
  --region us-central1 \
  --project datadog-ese-sandbox \
  --no-allow-unauthenticated

gcloud run services update genai-nextjs-frontend \
  --region us-central1 \
  --project datadog-ese-sandbox \
  --no-allow-unauthenticated
```

### **Step 3: Set IAP Environment Variables**

Update `.github/workflows/adk-python.yml`:

```yaml
env_vars: |
  DD_ENV=dev
  IAP_AUDIENCE=YOUR_IAP_CLIENT_ID.apps.googleusercontent.com
```

**Find IAP_AUDIENCE**:
```bash
gcloud iap oauth-brands list --project=datadog-ese-sandbox
gcloud iap oauth-clients list --brand=YOUR_BRAND \
  --project=datadog-ese-sandbox
```

### **Step 4: Verify IAP Headers**

After enabling IAP, requests will include:
- `X-Goog-IAP-JWT-Assertion`: JWT token with user info
- `X-Goog-Authenticated-User-Email`: User's email (format: `accounts.google.com:user@example.com`)
- `X-Serverless-Authorization`: Cloud Run IAP header

---

## 🧪 **Testing IAP**

### **Without IAP (Current)**

```bash
# Direct access works
curl https://genai-adk-python-cn4wkmlbva-uc.a.run.app/health
# ✅ Returns 200 OK
```

### **With IAP Enabled**

```bash
# Direct access will redirect to Google Sign-In
curl https://genai-adk-python-cn4wkmlbva-uc.a.run.app/health
# 🔐 Returns 302 Redirect to accounts.google.com

# Access with valid IAP token
curl https://genai-adk-python-cn4wkmlbva-uc.a.run.app/health \
  -H "X-Goog-IAP-JWT-Assertion: $IAP_TOKEN"
# ✅ Returns 200 OK (if token is valid)
```

### **Check Logs for IAP Headers**

After enabling IAP, you'll see in Datadog:

```
🔐 Auth Service initialized: IAP=True, OAuth=False
🔍 Attempting IAP authentication
✅ IAP authentication successful: user@example.com
```

---

## 📊 **Current vs. IAP-Enabled**

| Aspect | Current (No IAP) | With IAP Enabled |
|--------|-----------------|------------------|
| **Public Access** | ✅ Yes | ❌ No (requires Google Sign-In) |
| **Authentication** | Development mode | Real Google accounts |
| **User Identity** | `dev@localhost` | Actual email addresses |
| **CORS Preflight** | ✅ Works | ⚠️ May require special handling |
| **Security** | ⚠️ Low (dev only) | ✅ High (production ready) |
| **Headers Sent** | None | IAP JWT, user email |

---

## ⚠️ **Important Notes**

### **Why IAP Was Previously Disabled**

From previous investigation (see `GEMINI_IMAGE_PERMISSION_FIX.md`):

```
Access to fetch at 'https://genai-adk-python-cn4wkmlbva-uc.a.run.app/...'
has been blocked by CORS policy: Response to preflight request doesn't 
pass access control check: Redirect is not allowed for a preflight request.
```

**Problem**: IAP redirects to Google Sign-In BEFORE CORS headers can be applied, breaking CORS preflight requests.

**Solution Used**: Disabled IAP with `--allow-unauthenticated`

### **Production Recommendations**

For production deployment:

1. **Enable IAP** for security
2. **Configure CORS** properly:
   - Add frontend domain to `ALLOWED_ORIGINS`
   - Ensure backend sends CORS headers even for 401/302 responses
3. **Use Service-to-Service Auth** for backend-to-backend calls
4. **Set `DD_ENV=production`** to disable development fallback

---

## 🔗 **Monitoring IAP in Datadog**

### **Queries to Use**

**Check IAP Status**:
```
service:genai-adk-python "Auth Service initialized"
```

**Track Authentication Methods**:
```
service:genai-adk-python 
("IAP authentication successful" OR "OAuth authentication successful" OR "development mode authentication")
```

**Monitor IAP Failures**:
```
service:genai-adk-python status:error "IAP"
```

### **Expected Metrics After IAP**

- User emails visible in logs
- `auth_method:iap` tags in traces
- Real user IDs instead of `dev_user`

---

## ✅ **Summary**

### **Current State** (as of 2026-01-02 16:14:39 UTC)

| Item | Status |
|------|--------|
| **IAP Enabled** | ❌ No |
| **IAP Headers Present** | ❌ No |
| **User Authentication** | Development mode (`dev@localhost`) |
| **Environment** | `DD_ENV=dev` |
| **Public Access** | ✅ Yes (`--allow-unauthenticated`) |
| **Security Level** | ⚠️ Development only |

### **To See IAP Headers**

1. Enable IAP in GCP Console
2. Remove `--allow-unauthenticated` from Cloud Run
3. Set `IAP_AUDIENCE` environment variable
4. Redeploy services
5. Access services through browser (will require Google Sign-In)
6. Check Datadog logs for IAP authentication messages

---

**Status**: IAP is NOT currently enabled. Services are running in development mode with no authentication.

**Recommendation**: Keep IAP disabled for `dev` environment, enable for `prod` environment with proper CORS configuration.

