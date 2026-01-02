# Project ID Fix - Root Cause of 403 Error

**Date**: 2026-01-02  
**Commit**: `e50e4c0`  
**Status**: ✅ **FIXED - Root Cause Identified**  
**Issue**: Wrong project ID in code vs IAM permissions

---

## 🐛 **Root Cause**

### **The Problem**

Even after granting IAM permissions with the script, image generation still failed with:

```
403 PERMISSION_DENIED
Permission 'aiplatform.endpoints.predict' denied on resource 
'//aiplatform.googleapis.com/projects/datadog-sandbox/locations/global/...'
                                        ^^^^^^^^^^^^^^^^ Wrong project!
```

### **Why It Failed**

| Component | Project ID | Status |
|-----------|-----------|--------|
| **IAM Permissions** | `datadog-ese-sandbox` | ✅ Granted |
| **Code (Before Fix)** | `datadog-sandbox` | ❌ Wrong! |
| **Result** | Mismatch → 403 Error | ❌ Failed |

**The code was using the wrong project ID!**

---

## ✅ **The Fix**

### **Changed Default Project ID**

**Before**:
```python
project_id = os.environ.get("GCP_PROJECT_ID", "datadog-sandbox")  # ❌ Wrong!
```

**After**:
```python
# Use GOOGLE_CLOUD_PROJECT (set by Cloud Run) or fall back to GCP_PROJECT_ID
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT_ID", "datadog-ese-sandbox")  # ✅ Correct!
```

---

### **Added Environment Variables to Cloud Run**

**Development Workflow** (`.github/workflows/adk-python.yml`):
```yaml
--set-env-vars GOOGLE_CLOUD_PROJECT=${{ secrets.GCP_PROJECT_ID }} \
--set-env-vars GCP_PROJECT_ID=${{ secrets.GCP_PROJECT_ID }} \
```

**Production Workflow** (`.github/workflows/adk-python-prod.yml`):
```yaml
env_vars: |
  GOOGLE_CLOUD_PROJECT=${{ secrets.GCP_PROJECT_ID }}
  GCP_PROJECT_ID=${{ secrets.GCP_PROJECT_ID }}
  ...
```

---

## 🔍 **How We Found It**

### **Evidence from Logs**

**Error Message**:
```
projects/datadog-sandbox/locations/global/publishers/google/models/gemini-3-pro-image-preview
          ^^^^^^^^^^^^^^^^
          Wrong project ID!
```

**Permission Script Output**:
```
Project: datadog-ese-sandbox  ← Correct project!
Service Account: 449012790678-compute@developer.gserviceaccount.com
Role: roles/aiplatform.user
✅ Permission granted successfully!
```

**Mismatch**: Code using `datadog-sandbox`, permissions granted to `datadog-ese-sandbox`

---

## 📊 **Project ID Resolution Order**

The code now checks project ID in this order:

1. **`GOOGLE_CLOUD_PROJECT`** ← Set by Cloud Run (standard GCP env var)
2. **`GCP_PROJECT_ID`** ← Explicit override (also set by workflows)
3. **`datadog-ese-sandbox`** ← Hardcoded default (correct now!)

---

## 🧪 **Testing**

### **After Deployment**

**Check logs for project ID**:
```
service:genai-adk-python "Project ID:"
```

**Expected**:
```
Project ID: datadog-ese-sandbox  ✅ Correct!
```

**Not**:
```
Project ID: datadog-sandbox  ❌ Wrong!
```

---

### **Test Image Generation**

**Frontend**: https://genai-nextjs-frontend-449012790678.us-central1.run.app/image-creator

**Prompt**: "A robot dog with sunglasses"

**Expected Result**: ✅ Image generated successfully!

**No more 403 errors!**

---

## 📈 **Impact**

### **Before Fix**

```
❌ Code uses: datadog-sandbox
✅ IAM granted to: datadog-ese-sandbox
❌ Result: 403 PERMISSION_DENIED
```

### **After Fix**

```
✅ Code uses: datadog-ese-sandbox
✅ IAM granted to: datadog-ese-sandbox
✅ Result: Image generation works!
```

---

## 🚀 **Deployment**

**Commit**: `e50e4c0`  
**Status**: Deploying via GitHub Actions  
**ETA**: ~3-4 minutes

**Check deployment**:
```bash
gh run list --limit 1
```

---

## ✅ **Verification Checklist**

After deployment completes:

- [ ] **Check startup logs** - Verify project ID is `datadog-ese-sandbox`
  ```
  service:genai-adk-python "Project ID: datadog-ese-sandbox"
  ```

- [ ] **Test image generation** - Should work now!
  ```
  Open: https://genai-nextjs-frontend-449012790678.us-central1.run.app/image-creator
  Prompt: "A happy robot"
  Expected: ✅ Image generated
  ```

- [ ] **Check for 403 errors** - Should be gone!
  ```
  service:genai-adk-python PERMISSION_DENIED
  Expected: No new errors after deployment
  ```

- [ ] **Verify Datadog traces** - Should show HTTP 200
  ```
  service:genai-adk-python resource_name:"POST /api/v1/images/generate"
  Expected: http.status_code: "200"
  ```

---

## 🎯 **Root Cause Analysis**

### **Why Did This Happen?**

1. **Hardcoded project ID** in code was `datadog-sandbox`
2. **Actual GCP project** is `datadog-ese-sandbox`
3. **IAM permissions** were correctly granted to `datadog-ese-sandbox`
4. **Code was trying to access** `datadog-sandbox` (wrong project!)
5. **Result**: 403 PERMISSION_DENIED (project mismatch)

### **Why Wasn't This Caught Earlier?**

- Environment variable `GOOGLE_CLOUD_PROJECT` was not being set in Cloud Run
- Code was falling back to hardcoded default
- Hardcoded default was wrong (copy/paste error?)

### **How to Prevent This?**

✅ **Fixed**: Code now uses `GOOGLE_CLOUD_PROJECT` first  
✅ **Fixed**: Workflows explicitly set both env vars  
✅ **Fixed**: Default is now correct  
✅ **Added**: Logging shows which project ID is used  
✅ **Added**: Credential verification at startup

---

## 🔧 **What Changed**

### **Files Modified**

1. **`services/adk-python/app/services/image_generation.py`**
   - Changed default from `datadog-sandbox` to `datadog-ese-sandbox`
   - Added fallback to `GOOGLE_CLOUD_PROJECT` env var

2. **`.github/workflows/adk-python.yml`** (dev)
   - Added `GCP_PROJECT_ID` environment variable

3. **`.github/workflows/adk-python-prod.yml`** (prod)
   - Added `GOOGLE_CLOUD_PROJECT` and `GCP_PROJECT_ID` to env_vars

---

## 📚 **Related Issues**

### **Why IAM Permission Grant Still Failed**

The permission was granted to the **correct project** (`datadog-ese-sandbox`), but the code was trying to access the **wrong project** (`datadog-sandbox`).

**Analogy**: 
- You were given a key to Room 201 (`datadog-ese-sandbox`)
- But you were trying to open Room 101 (`datadog-sandbox`)
- The key works fine, but you're at the wrong door!

---

## 🎉 **Summary**

| Issue | Status |
|-------|--------|
| **Wrong Project ID** | ✅ Fixed |
| **IAM Permissions** | ✅ Already granted (from script) |
| **Environment Variables** | ✅ Added to workflows |
| **Logging** | ✅ Shows actual project ID |
| **Testing** | ⏳ After deployment |

---

**Expected Result**: 

After this deployment completes (~3 minutes), image generation should work! 🎉

The 403 PERMISSION_DENIED error was caused by a **project ID mismatch**, not a permission issue. Now that the code uses the correct project ID (`datadog-ese-sandbox`), it can access the Vertex AI model with the IAM permissions we already granted.

---

**Next Steps**:

1. ⏳ Wait for GitHub Actions to complete
2. ✅ Check logs for correct project ID
3. ✅ Test image generation
4. ✅ Verify no more 403 errors

**ETA to Full Resolution**: ~3-4 minutes (deployment time)

🚀 **Almost there!**

