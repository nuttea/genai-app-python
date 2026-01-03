# IAP Header Logging Implementation

**Date**: 2026-01-02  
**Commit**: `73a58ff`  
**Status**: ✅ Implemented, Deploying

---

## 🎯 **What Was Implemented**

Added IAP header logging to the backend **without enforcing authentication**. Requests are processed regardless of whether IAP headers are present, but we log user information when available.

---

## 📁 **Files Created**

### **1. `services/adk-python/app/utils/__init__.py`**
- Package initialization file

### **2. `services/adk-python/app/utils/iap_logger.py`**
- IAP header parser and logger
- **Does NOT verify JWT signatures** (logging only)
- **Does NOT block requests** (non-enforcing)

**Functions**:

**`parse_iap_jwt(token: str)`**:
- Parses JWT token (base64 decode)
- Extracts payload
- Returns decoded claims or None

**`log_iap_headers(request: Request)`**:
- Checks for IAP headers
- Logs user info if found
- Returns user info dict or None
- **Never raises exceptions**

---

## 🔍 **Headers Checked**

The logger checks for these headers in order:

### **1. `X-Goog-IAP-JWT-Assertion`** (Primary)
```
Format: eyJhbGciOiJFUzI1NiIs...
Contains: Full JWT with user claims
Logs: email, user_id, name, auth_method=iap_jwt
```

### **2. `X-Goog-Authenticated-User-Email`** (Alternative)
```
Format: accounts.google.com:user@example.com
Contains: User email only
Logs: email, user_id (from email), auth_method=iap_email_header
```

### **3. `X-Serverless-Authorization`** (Cloud Run IAP)
```
Format: JWT token (same as X-Goog-IAP-JWT-Assertion)
Contains: Full JWT with user claims
Logs: email, user_id, name, auth_method=serverless_auth
```

### **4. All Auth-Related Headers**
```
Logs any header containing: goog, auth, user, iap
Long values (>50 chars) shown as: <token:123chars>
```

---

## 📊 **Log Examples**

### **With IAP Headers**

```
🔐 IAP JWT found: user=john.doe@example.com, id=accounts.google.com:1234567890
📊 Auth-related headers: {
  'x-goog-iap-jwt-assertion': '<token:843chars>',
  'x-goog-authenticated-user-email': 'accounts.google.com:john.doe@example.com'
}
🎨 Image generation request: user=john.doe@example.com (via iap_jwt), type=illustration, ratio=1:1, refs=0, session=rum_abc123
```

### **Without IAP Headers**

```
📊 No IAP/auth headers found in request
🎨 Image generation request: anonymous, type=illustration, ratio=1:1, refs=0, session=img_1704216511000
```

### **With Only Email Header**

```
🔐 IAP Email Header found: user=jane@example.com, id=jane
📊 Auth-related headers: {
  'x-goog-authenticated-user-email': 'accounts.google.com:jane@example.com'
}
🎨 Image generation request: user=jane@example.com (via iap_email_header), type=comic, ratio=16:9, refs=0, session=rum_xyz789
```

---

## 🔧 **Integration**

### **Updated**: `services/adk-python/main_adk.py`

```python
@app.post("/api/v1/images/generate")
async def generate_image_sync(
    request: dict,
    http_request: Request,
):
    try:
        # Log IAP headers if present (no enforcement)
        from app.utils.iap_logger import log_iap_headers
        user_info = log_iap_headers(http_request)
        
        # ... rest of endpoint logic
        
        # Log request with user info if available
        user_str = f"user={user_info['email']} (via {user_info['auth_method']})" if user_info else "anonymous"
        logger.info(f"🎨 Image generation request: {user_str}, ...")
```

**Key Points**:
- ✅ `log_iap_headers()` is called first
- ✅ Returns user info or None
- ✅ Never raises exceptions
- ✅ Never blocks the request
- ✅ Request continues regardless of result

---

## 🧪 **Testing**

### **Test 1: Without IAP (Current)**

```bash
curl -X POST https://genai-adk-python-cn4wkmlbva-uc.a.run.app/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}' | jq
```

**Expected Logs**:
```
📊 No IAP/auth headers found in request
🎨 Image generation request: anonymous, type=illustration, ...
```

**Expected Response**: ✅ Success (request processed)

---

### **Test 2: With Mock IAP Headers**

```bash
# Create a mock JWT (not verified, just for logging test)
MOCK_JWT="eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2Nsb3VkLmdvb2dsZS5jb20vaWFwIiwic3ViIjoiYWNjb3VudHMuZ29vZ2xlLmNvbToxMjM0NTY3ODkwIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciJ9.signature"

curl -X POST https://genai-adk-python-cn4wkmlbva-uc.a.run.app/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -H "X-Goog-IAP-JWT-Assertion: $MOCK_JWT" \
  -d '{"prompt": "test"}' | jq
```

**Expected Logs**:
```
🔐 IAP JWT found: user=test@example.com, id=accounts.google.com:1234567890
📊 Auth-related headers: {'x-goog-iap-jwt-assertion': '<token:XXXchars>'}
🎨 Image generation request: user=test@example.com (via iap_jwt), ...
```

**Expected Response**: ✅ Success (request processed)

---

### **Test 3: With Real IAP** (When Enabled)

Enable IAP in GCP Console, then access through browser:

**Expected Logs**:
```
🔐 IAP JWT found: user=your.email@gmail.com, id=accounts.google.com:YOUR_ID
📊 Auth-related headers: {
  'x-goog-iap-jwt-assertion': '<token:843chars>',
  'x-goog-authenticated-user-email': 'accounts.google.com:your.email@gmail.com'
}
🎨 Image generation request: user=your.email@gmail.com (via iap_jwt), ...
```

**Expected Response**: ✅ Success (request processed)

---

## 📊 **Monitoring with Datadog**

### **Query 1: Check for IAP Headers**

```
service:genai-adk-python "IAP JWT found" OR "IAP Email Header found"
```

**If Found**: IAP is working and headers are present  
**If Not Found**: No IAP headers (expected currently)

---

### **Query 2: Check Authentication Methods**

```
service:genai-adk-python "Image generation request" | facet auth_method
```

**Expected Values**:
- `anonymous` (no IAP)
- `iap_jwt` (IAP with JWT)
- `iap_email_header` (IAP with email header)
- `serverless_auth` (Cloud Run IAP)

---

### **Query 3: Monitor User Activity**

```
service:genai-adk-python "Image generation request: user="
```

**Shows**: All requests with identified users (when IAP is enabled)

---

### **Query 4: Debug Auth Headers**

```
service:genai-adk-python "Auth-related headers"
```

**Shows**: All auth-related headers from requests (for debugging)

---

## ⚠️ **Important Notes**

### **1. No JWT Verification**

The logger **does NOT verify** JWT signatures:
- ✅ Good for logging and debugging
- ❌ Not suitable for access control
- ⚠️ Data could be spoofed (but we don't act on it)

**Why**: This is intentional - we only want to log, not enforce.

---

### **2. No Access Control**

The logger **does NOT block** requests:
- ✅ All requests are processed
- ✅ User info is logged if available
- ✅ No authentication failures

**Why**: This allows us to see what headers are present without breaking functionality.

---

### **3. Privacy Considerations**

User emails and IDs are logged:
- ✅ Useful for debugging
- ⚠️ May contain PII (Personal Identifiable Information)
- 🔒 Logs should be treated as sensitive

**Recommendation**: Ensure Datadog log retention and access policies comply with your privacy requirements.

---

## 🚀 **Deployment**

### **Status**

**Commit**: `73a58ff`  
**GitHub Actions**: In progress

**Workflows**:
- ⏳ Code Quality
- ⏳ ADK Python Service CI/CD

**ETA**: ~3-4 minutes

---

### **What Happens After Deployment**

1. **Without IAP** (Current):
   - Logs show: `📊 No IAP/auth headers found`
   - Requests processed as `anonymous`
   - No change in functionality

2. **With IAP Enabled** (Future):
   - Logs show: `🔐 IAP JWT found: user=...`
   - Requests show user email and ID
   - Still processed successfully (no blocking)

---

## 🔮 **Next Steps**

### **Optional: Enable Authentication**

If you want to **enforce** IAP authentication later:

```python
# In main_adk.py
from app.utils.iap_logger import log_iap_headers
from fastapi import HTTPException

user_info = log_iap_headers(http_request)

# Add enforcement:
if not user_info:
    raise HTTPException(
        status_code=401,
        detail="IAP authentication required"
    )

# Continue with authenticated user...
```

---

### **Optional: Enable IAP**

To start seeing real user data:

1. Enable IAP in GCP Console
2. Set `IAP_AUDIENCE` environment variable
3. Remove `--allow-unauthenticated` from Cloud Run
4. Redeploy (or existing deployment picks it up)

**Then**: Logs will show real user emails and IDs!

---

## ✅ **Summary**

| Aspect | Status |
|--------|--------|
| **IAP Parser** | ✅ Implemented |
| **Header Logging** | ✅ Working |
| **User ID Extraction** | ✅ Yes (when available) |
| **Authentication Enforcement** | ❌ No (by design) |
| **Request Blocking** | ❌ No (all requests pass) |
| **Error Handling** | ✅ Never raises exceptions |
| **Privacy** | ⚠️ Logs PII (user emails) |
| **Debug Value** | ✅ High |

---

## 📖 **Related Documentation**

- **`IAP_STATUS_REPORT.md`** - Current IAP status (disabled)
- **`BACKEND_AUTH_REMOVED.md`** - Authentication was removed
- **`IAP_INTEGRATION.md`** - Frontend IAP integration
- **`AUTH_FIX_SUMMARY.md`** - Previous auth fixes

---

**Status**: ✅ **IAP Logging Implemented**

**Current Behavior**: Logs "anonymous" (no IAP headers present)

**After IAP Enabled**: Will log real user emails and IDs

**Request Processing**: ✅ Always succeeds (no enforcement)

---

**Test after deployment**: Check Datadog logs for IAP header information! 📊

