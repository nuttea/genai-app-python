# Datadog Source Code Integration - Implementation Summary

**Date**: 2026-01-02  
**Commit**: `15de6e9`  
**Service**: `genai-adk-python`  
**Status**: ✅ Implemented, Deploying

---

## 🎯 **What Was Added**

Configured Datadog Source Code Integration to link APM traces, logs, and errors directly to source code in GitHub.

---

## 🔧 **Changes Made**

### **1. Dockerfile.cloudrun** (Updated)

**Added Build Arguments**:
```dockerfile
# Build arguments for Datadog Source Code Integration
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
```

**Set as Environment Variables**:
```dockerfile
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL} \
    DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}
```

**Result**: Git metadata is available at runtime for Datadog APM

---

### **2. main_adk.py** (Updated)

**Added Git Metadata Logging**:
```python
DD_GIT_REPOSITORY_URL = os.getenv("DD_GIT_REPOSITORY_URL")
DD_GIT_COMMIT_SHA = os.getenv("DD_GIT_COMMIT_SHA")

if DD_GIT_REPOSITORY_URL and DD_GIT_COMMIT_SHA:
    logger.info(f"📝 Datadog Source Code Integration enabled:")
    logger.info(f"   Repository: {DD_GIT_REPOSITORY_URL}")
    logger.info(f"   Commit: {DD_GIT_COMMIT_SHA[:8]}")
else:
    logger.warning("⚠️  Datadog Source Code Integration not configured")
```

**Result**: Easy verification that Source Code Integration is working

---

### **3. GitHub Actions** (Already Configured)

`.github/workflows/adk-python.yml` already passes git metadata:
```yaml
build-args: |
  DD_GIT_REPOSITORY_URL=${{ github.repositoryUrl }}
  DD_GIT_COMMIT_SHA=${{ github.sha }}
```

**No changes needed** - was already set up! ✅

---

## 📊 **What This Enables**

### **1. APM Trace Links**

```
APM Trace → Span → Stack Trace → Click "View Code"
→ Opens GitHub at exact file and line
```

**Example**:
```
Error in /app/main_adk.py:150
→ https://github.com/nuttea/genai-app-python/blob/15de6e9/services/adk-python/main_adk.py#L150
```

---

### **2. Error Tracking Links**

```
Error Tracking → Stack Trace → Click file name
→ Opens GitHub at the error location
```

**Example**:
```
File "/app/app/services/image_generation.py", line 119
→ https://github.com/nuttea/genai-app-python/blob/15de6e9/services/adk-python/app/services/image_generation.py#L119
```

---

### **3. Commit Tracking**

```
APM → Filter by git.commit.sha
→ See all traces from specific deployment
→ Compare performance between commits
```

**Tags Added**:
- `git.commit.sha`: Full commit SHA
- `git.repository_url`: GitHub repository URL

---

### **4. Log Enrichment**

All logs include:
```json
{
  "git": {
    "commit_sha": "15de6e9...",
    "repository_url": "https://github.com/nuttea/genai-app-python"
  }
}
```

---

## 🧪 **Verification**

### **1. Check Startup Logs**

**Datadog Query**:
```
service:genai-adk-python "Source Code Integration enabled"
```

**Expected**:
```
📝 Datadog Source Code Integration enabled:
   Repository: https://github.com/nuttea/genai-app-python
   Commit: 15de6e9
```

---

### **2. Check APM Traces**

1. Go to **APM** → **Traces**
2. Click any trace for `genai-adk-python`
3. Look for git metadata in span tags:
   - `git.commit.sha`
   - `git.repository_url`

---

### **3. Test Error Link**

1. Trigger an error (or find existing error)
2. Go to **Error Tracking**
3. Click stack trace line
4. Should see "View in GitHub" button
5. Click → Opens exact file/line in GitHub

---

## ⚙️ **How It Works**

### **Build Time**

```
GitHub Actions → Build Docker
→ Pass git metadata as build args
→ Docker sets as environment variables
```

### **Runtime**

```
Service starts → Reads DD_GIT_* env vars
→ Datadog agent tags all traces/logs
→ Datadog backend enriches with git metadata
```

### **In Datadog UI**

```
User clicks trace → Datadog API calls GitHub
→ Returns source code at specific commit
→ Displays in-line in Datadog UI
```

---

## 🔗 **GitHub Integration Setup**

### **Required in Datadog UI**

To enable "View Code" buttons:

1. Go to **Organization Settings** → **Integrations**
2. Find "GitHub" and click "Configure"
3. Add repository:
   - Repository: `nuttea/genai-app-python`
   - Authentication: GitHub App or Personal Access Token
4. Grant permissions:
   - Read access to repositories
   - Read access to code

**Status**: ⚠️ **Needs to be configured in Datadog UI**

---

## 📈 **Benefits**

### **For Developers**

✅ **Faster Debugging**:
- Click from error directly to code
- No searching for files/lines

✅ **Better Context**:
- Know exact commit for each error
- Compare before/after deployments

✅ **Team Collaboration**:
- Share links to specific code lines
- Everyone sees the same version

---

### **For Operations**

✅ **Version Tracking**:
- Filter traces by commit SHA
- Identify problematic deployments

✅ **Root Cause Analysis**:
- See code changes that caused issues
- Compare performance metrics per commit

✅ **Rollback Decisions**:
- Quickly assess impact of changes
- Link incidents to specific commits

---

## 🚀 **Deployment**

### **Status**

**Commit**: `15de6e9`  
**GitHub Actions**: In progress

**Workflows**:
- ⏳ Code Quality
- ⏳ ADK Python Service CI/CD

**ETA**: ~3-4 minutes

---

### **What Happens After Deployment**

1. **Service Starts**:
   ```
   📝 Datadog Source Code Integration enabled:
      Repository: https://github.com/nuttea/genai-app-python
      Commit: 15de6e9
   ```

2. **All Traces Tagged**:
   ```
   @git.commit.sha:15de6e9...
   @git.repository_url:https://github.com/...
   ```

3. **Logs Enriched**:
   ```json
   {"git": {"commit_sha": "15de6e9...", ...}}
   ```

4. **Links Work** (after GitHub integration):
   - Click stack traces → Opens GitHub
   - Shows code at deployed commit

---

## 📊 **Monitoring Queries**

### **Verify Integration**

```
service:genai-adk-python "Source Code Integration enabled"
```

### **Check Git Tags**

```
service:genai-adk-python @git.commit.sha:*
```

### **Filter by Commit**

```
service:genai-adk-python @git.commit.sha:15de6e9*
```

### **Track Deployments**

```
service:genai-adk-python @git.commit.sha:* | unique_count(@git.commit.sha)
```

---

## 🔍 **Troubleshooting**

### **"View Code" Button Not Showing**

**Cause**: GitHub integration not configured in Datadog UI

**Fix**: 
1. Configure GitHub integration in Datadog
2. Grant repository access
3. Refresh page

---

### **Git Metadata Not in Logs**

**Cause**: Environment variables not set

**Check**:
```
service:genai-adk-python "Source Code Integration enabled"
```

**If not found**: Redeploy with correct build args

---

### **Wrong Commit Shown**

**Cause**: Cached Docker image

**Fix**:
1. Build with `--no-cache`
2. Or push new commit to trigger fresh build

---

## 🎯 **Next Steps**

### **1. Configure GitHub Integration** ⚠️

In Datadog UI:
- Add GitHub repository
- Grant read access
- Test "View Code" links

### **2. Verify in Production**

After deployment:
- Check logs for git commit
- Test APM trace links
- Verify error tracking links

### **3. Team Training**

Show team how to:
- Click from traces to code
- Filter by commit SHA
- Use for debugging

---

## 📚 **Documentation**

**Created**: `services/adk-python/DATADOG_SOURCE_CODE_INTEGRATION.md`
- Complete setup guide
- Verification steps
- Troubleshooting
- Datadog queries

---

## ✅ **Summary**

| Feature | Status |
|---------|--------|
| **Git Metadata in Dockerfile** | ✅ Implemented |
| **Git Metadata Logging** | ✅ Implemented |
| **APM Trace Tagging** | ✅ Automatic (via ddtrace) |
| **Log Enrichment** | ✅ Automatic (via ddtrace) |
| **GitHub Integration** | ⚠️ Needs Datadog UI config |
| **"View Code" Links** | ⚠️ After GitHub integration |
| **Deployment** | ⏳ In progress |

---

**Status**: ✅ **Source Code Integration Configured**

**Impact**: Click from any trace or error directly to GitHub source code! 🎉

**Next**: Configure GitHub integration in Datadog UI to enable "View Code" buttons.

---

**Test after deployment**:
```
service:genai-adk-python "Source Code Integration enabled"
```

Expected: Shows repository URL and commit SHA in logs! 📝✨

