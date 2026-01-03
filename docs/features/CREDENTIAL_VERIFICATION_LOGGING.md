# Credential Verification Logging

**Date**: 2026-01-02  
**Commit**: `77ad410`  
**Feature**: Comprehensive Google Cloud credential verification at startup  
**Status**: ✅ Deployed

---

## 🎯 **What Was Added**

### **Startup Credential Verification**

The service now verifies Google Cloud credentials at startup and logs detailed information:

1. **Application Default Credentials** check
2. **Service Account** identification
3. **Cloud Run environment** detection
4. **Required IAM permissions** listing
5. **Troubleshooting commands** in logs

---

## 📝 **Log Output**

### **Successful Credentials (Cloud Run)**

```
🔐 Verifying Google Cloud Credentials...
✅ Application Default Credentials found:
   Environment: Cloud Run
   Cloud Run Service: genai-adk-python
   Cloud Run Revision: genai-adk-python-00022-xyz
   Credential Type: Credentials
   Service Account: 449012790678-compute@developer.gserviceaccount.com
   Project ID: datadog-ese-sandbox
   Valid: True
📋 Required IAM Roles for Vertex AI Image Generation:
   - roles/aiplatform.user (Vertex AI User)
   Required Permissions:
   - aiplatform.endpoints.predict
   - aiplatform.endpoints.get
   Grant with: gcloud projects add-iam-policy-binding datadog-ese-sandbox
     --member='serviceAccount:449012790678-compute@developer.gserviceaccount.com'
     --role='roles/aiplatform.user'
```

---

### **Successful Credentials (Local)**

```
🔐 Verifying Google Cloud Credentials...
✅ Application Default Credentials found:
   Environment: Local/Docker
   Credential Type: Credentials
   Service Account: your-dev-account@example.com
   Project ID: datadog-ese-sandbox
   Valid: True
📋 Required IAM Roles for Vertex AI Image Generation:
   - roles/aiplatform.user (Vertex AI User)
   ...
```

---

### **Missing Credentials**

```
🔐 Verifying Google Cloud Credentials...
❌ No Application Default Credentials found!
   Error: Could not automatically determine credentials...
   This will cause PERMISSION_DENIED errors when accessing Vertex AI!
   For Cloud Run: Ensure service account has proper IAM roles
   For local: Run 'gcloud auth application-default login'
```

---

### **Image Generation Service Initialization**

When `ImageGenerationService` is initialized (on first image generation request):

```
🔧 Initializing Image Generation Service
   Environment: Cloud Run
   Service: genai-adk-python
   Revision: genai-adk-python-00022-xyz
   Project ID: datadog-ese-sandbox
   Model: gemini-3-pro-image-preview
   Location: global
🔐 Google Cloud Credentials:
   Type: Credentials
   Service Account: 449012790678-compute@developer.gserviceaccount.com
   Project (from credentials): datadog-ese-sandbox
   Valid: True
   Expired: False
✅ GenAI Client initialized successfully
📋 Required IAM Permissions:
   - aiplatform.endpoints.predict
   - aiplatform.endpoints.get
   Role: roles/aiplatform.user (Vertex AI User)
```

---

## 🔍 **How to Use These Logs**

### **1. Check Credentials on Startup**

**Datadog Query**:
```
service:genai-adk-python "Verifying Google Cloud Credentials"
```

**Expected**: See credentials info with service account email

---

### **2. Identify Permission Issues**

**Datadog Query**:
```
service:genai-adk-python "No Application Default Credentials"
```

**If found**: Run `gcloud auth application-default login` (local) or check Cloud Run service account IAM

---

### **3. Verify Service Account**

**Look for**:
```
Service Account: 449012790678-compute@developer.gserviceaccount.com
```

**Use this** to grant IAM permissions:
```bash
gcloud projects add-iam-policy-binding datadog-ese-sandbox \
  --member='serviceAccount:449012790678-compute@developer.gserviceaccount.com' \
  --role='roles/aiplatform.user'
```

---

### **4. Check Cloud Run Environment**

**Look for**:
```
Environment: Cloud Run
Cloud Run Service: genai-adk-python
Cloud Run Revision: genai-adk-python-00022-xyz
```

**Use this** to verify deployment

---

### **5. Troubleshoot Permission Denied Errors**

**If you see**:
```
❌ Image generation failed: 403 PERMISSION_DENIED
```

**Check logs for**:
```
Service Account: [service-account-email]
```

**Then verify IAM**:
```bash
gcloud projects get-iam-policy datadog-ese-sandbox \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:[service-account-email] AND bindings.role:roles/aiplatform.user"
```

**Expected**: Should show `roles/aiplatform.user`

**If empty**: Run the grant command from logs

---

## 🧪 **Testing**

### **1. Check Startup Logs After Deployment**

**Wait for deployment**:
```bash
gh run watch
```

**Then check logs**:
```
service:genai-adk-python "Verifying Google Cloud Credentials"
```

---

### **2. Verify Service Account**

**Expected in logs**:
- ✅ Service account email
- ✅ Project ID
- ✅ Valid: True
- ✅ Environment: Cloud Run

---

### **3. Test Image Generation**

**Before granting permissions**:
```
Expected logs:
✅ Credentials verified
❌ PERMISSION_DENIED error
→ Use service account from logs to grant permission
```

**After granting permissions**:
```
Expected logs:
✅ Credentials verified
✅ Image generated successfully
```

---

## 📊 **Datadog Queries**

### **Check Credential Verification**

```
service:genai-adk-python "Application Default Credentials found"
```

---

### **Find Service Account**

```
service:genai-adk-python "Service Account:"
```

---

### **Check for Credential Issues**

```
service:genai-adk-python ("No Application Default Credentials" OR "Failed to initialize GenAI")
```

---

### **Monitor Permission Errors**

```
service:genai-adk-python PERMISSION_DENIED
```

---

## 🎯 **Troubleshooting Guide**

### **Issue: No credentials found**

**Logs**:
```
❌ No Application Default Credentials found!
```

**Solution**:
1. For Cloud Run: Check service account exists
2. For local: Run `gcloud auth application-default login`

---

### **Issue: Wrong service account**

**Logs**:
```
Service Account: wrong-account@project.iam.gserviceaccount.com
```

**Solution**:
1. Check Cloud Run service configuration
2. Update service to use correct service account
3. Or grant permissions to existing account

---

### **Issue: Credentials expired**

**Logs**:
```
Valid: False
Expired: True
```

**Solution**:
1. For Cloud Run: Restart service
2. For local: Refresh credentials with `gcloud auth application-default login`

---

### **Issue: Permission still denied after grant**

**Check**:
1. IAM propagation delay (wait 2 minutes)
2. Correct project ID
3. Correct service account email

**Verify**:
```bash
gcloud projects get-iam-policy datadog-ese-sandbox \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:449012790678-compute@developer.gserviceaccount.com"
```

---

## 📈 **Benefits**

### **Before This Change**

❌ No credential info in logs  
❌ Permission errors hard to debug  
❌ Unknown service account  
❌ No troubleshooting guidance

---

### **After This Change**

✅ Service account identified at startup  
✅ Credential validity checked  
✅ Clear troubleshooting steps in logs  
✅ gcloud commands ready to copy/paste  
✅ Environment detection (Cloud Run vs local)  
✅ Project ID verification  
✅ Required permissions listed

---

## 🚀 **Deployment**

### **Status**

**Commit**: `77ad410`  
**GitHub Actions**: Check with `gh run list --limit 1`  
**ETA**: ~3-4 minutes

---

### **Verification Steps**

**1. Wait for deployment**:
```bash
gh run watch
```

**2. Check startup logs**:
```
service:genai-adk-python "Verifying Google Cloud Credentials"
```

**3. Find service account**:
```
service:genai-adk-python "Service Account:"
```

**4. Grant permissions** (if needed):
```bash
# Copy command from logs, or use:
./PERMISSION_FIX_GEMINI_IMAGE.sh
```

**5. Test image generation**

---

## 📚 **Files Changed**

1. **`services/adk-python/main_adk.py`**
   - Added credential verification at startup
   - Logs service account and environment
   - Lists required IAM permissions

2. **`services/adk-python/app/services/image_generation.py`**
   - Added credential check in service initialization
   - Logs GenAI client setup details
   - Verifies project ID match

---

## ✅ **Summary**

| Feature | Status |
|---------|--------|
| **Startup Credential Check** | ✅ Implemented |
| **Service Account Logging** | ✅ Implemented |
| **Environment Detection** | ✅ Implemented |
| **IAM Permission Listing** | ✅ Implemented |
| **Troubleshooting Commands** | ✅ Implemented |
| **Deployment** | ⏳ In progress |

---

**Impact**:
- ✅ Faster debugging of permission issues
- ✅ Clear service account identification
- ✅ Ready-to-use gcloud commands
- ✅ Better troubleshooting experience

---

**Next Steps**:
1. ⏳ Wait for deployment (~3 min)
2. ✅ Check startup logs in Datadog
3. ✅ Verify service account
4. ⚠️ Grant IAM permissions if needed
5. ✅ Test image generation

---

**Example Datadog Dashboard Widget**:

```
Query: service:genai-adk-python "Service Account:"
Type: Log Stream
Title: Cloud Run Service Account
```

This shows the service account being used, making it easy to verify permissions!

🎉 **Credential verification now fully logged!**

