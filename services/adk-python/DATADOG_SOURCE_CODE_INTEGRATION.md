# Datadog Source Code Integration

**Status**: ✅ Enabled  
**Service**: `genai-adk-python`  
**Feature**: Links traces, logs, and errors directly to source code in GitHub

---

## 📝 **What is Source Code Integration?**

Datadog Source Code Integration enriches APM traces, logs, and error tracking with:
- **Direct links** to source code in GitHub
- **Line-level precision** for stack traces
- **Commit information** for each deployment
- **One-click navigation** from Datadog to GitHub

### **Benefits**

✅ **Faster Debugging**: Click from error to source code  
✅ **Better Context**: See exact commit for each deployment  
✅ **Team Collaboration**: Share links to specific code lines  
✅ **Version Tracking**: Know which code is running

---

## 🔧 **Implementation**

### **Files Modified**

**1. `Dockerfile.cloudrun`**:
- Added `ARG DD_GIT_REPOSITORY_URL` and `ARG DD_GIT_COMMIT_SHA`
- Set as environment variables for runtime

**2. `main_adk.py`**:
- Added logging for git metadata on startup
- Verifies Source Code Integration is configured

**3. `.github/workflows/adk-python.yml`** (Already configured):
- Passes git metadata as build arguments

---

## 📊 **Configuration**

### **Build Arguments** (GitHub Actions)

```yaml
build-args: |
  DD_GIT_REPOSITORY_URL=${{ github.repositoryUrl }}
  DD_GIT_COMMIT_SHA=${{ github.sha }}
```

### **Environment Variables** (Dockerfile)

```dockerfile
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL} \
    DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}
```

### **Runtime Logging** (main_adk.py)

```python
if DD_GIT_REPOSITORY_URL and DD_GIT_COMMIT_SHA:
    logger.info(f"📝 Datadog Source Code Integration enabled:")
    logger.info(f"   Repository: {DD_GIT_REPOSITORY_URL}")
    logger.info(f"   Commit: {DD_GIT_COMMIT_SHA[:8]}")
```

---

## 🧪 **Verification**

### **1. Check Startup Logs**

After deployment, check logs for:

```
📝 Datadog Source Code Integration enabled:
   Repository: https://github.com/nuttea/genai-app-python
   Commit: 73a58ff9
```

**Datadog Query**:
```
service:genai-adk-python "Source Code Integration enabled"
```

---

### **2. Verify Environment Variables**

SSH into the container (or check logs):

```bash
echo $DD_GIT_REPOSITORY_URL
# Expected: https://github.com/nuttea/genai-app-python

echo $DD_GIT_COMMIT_SHA
# Expected: 73a58ff9... (full commit SHA)
```

---

### **3. Check Datadog APM**

1. Go to **APM** → **Traces**
2. Click on any trace for `genai-adk-python`
3. Look for:
   - **Git commit** tag
   - **Repository URL** in metadata
   - **"View Code"** button in stack traces

---

### **4. Test Error Linking**

When an error occurs:
1. Go to **Error Tracking**
2. Click on the error
3. Look for **"View in GitHub"** link
4. Should open the exact file and line in GitHub

---

## 🔗 **Datadog Integration Setup**

### **In Datadog Console**

1. Navigate to **Organization Settings** → **Source Code Integration**
2. Add GitHub integration:
   - Repository: `nuttea/genai-app-python`
   - Authentication: GitHub App or OAuth

3. Verify connection:
   - Datadog should show "Connected" status
   - Test by clicking a stack trace link

---

## 📈 **What Gets Tagged**

### **APM Traces**

```yaml
span_tags:
  git.commit.sha: "73a58ff9e1234567890abcdef"
  git.repository_url: "https://github.com/nuttea/genai-app-python"
```

### **Logs**

```json
{
  "git": {
    "commit_sha": "73a58ff9e1234567890abcdef",
    "repository_url": "https://github.com/nuttea/genai-app-python"
  }
}
```

### **Error Tracking**

```
Stack Trace:
  File "/app/main_adk.py", line 150
    └─ [View in GitHub] → https://github.com/nuttea/genai-app-python/blob/73a58ff9/services/adk-python/main_adk.py#L150
```

---

## 🎯 **Usage Examples**

### **1. Debug a Trace**

```
APM Trace → Click span → "View Code"
→ Opens GitHub at exact commit and file
```

### **2. Investigate an Error**

```
Error Tracking → Click error → Stack trace → "View in GitHub"
→ Opens the exact line that caused the error
```

### **3. Compare Versions**

```
APM → Filter by git.commit.sha
→ Compare performance between commits
```

---

## 🔍 **Troubleshooting**

### **Issue**: "Source Code Integration not configured"

**Cause**: Git environment variables not set

**Fix**:
1. Check GitHub Actions workflow passes build args
2. Verify Dockerfile accepts ARGs
3. Ensure ARGs are set as ENV

---

### **Issue**: "View Code" button missing

**Cause**: GitHub integration not configured in Datadog

**Fix**:
1. Go to Datadog → Settings → Source Code Integration
2. Add GitHub repository
3. Authorize Datadog to access repository

---

### **Issue**: Links go to wrong commit

**Cause**: `DD_GIT_COMMIT_SHA` is incorrect

**Fix**:
1. Verify `${{ github.sha }}` in workflow
2. Check logs for correct commit SHA
3. Redeploy if needed

---

## 🚀 **Deployment**

### **Automatic in CI/CD**

Source Code Integration is automatically configured when:
1. Code is pushed to `main` branch
2. GitHub Actions builds Docker image
3. Git metadata passed as build args
4. Image deployed to Cloud Run

### **Manual Deployment**

If deploying manually:

```bash
# Build with git metadata
docker build \
  --build-arg DD_GIT_REPOSITORY_URL=https://github.com/nuttea/genai-app-python \
  --build-arg DD_GIT_COMMIT_SHA=$(git rev-parse HEAD) \
  -f Dockerfile.cloudrun \
  -t genai-adk-python .

# Deploy to Cloud Run
gcloud run deploy genai-adk-python --image genai-adk-python ...
```

---

## 📊 **Datadog Queries**

### **Check Integration Status**

```
service:genai-adk-python "Source Code Integration"
```

### **Filter by Commit**

```
service:genai-adk-python @git.commit.sha:73a58ff9*
```

### **Find Errors by Commit**

```
service:genai-adk-python status:error @git.commit.sha:*
```

### **Compare Commits**

```
service:genai-adk-python @git.commit.sha:(abc123 OR def456)
```

---

## 🔒 **Security Considerations**

### **Public vs Private Repositories**

- **Public Repo**: Links work for everyone with access
- **Private Repo**: Users need GitHub access + Datadog permissions

### **Sensitive Information**

- ✅ Git metadata is non-sensitive (commit SHA, repo URL)
- ✅ No source code is sent to Datadog
- ✅ Links only work for authorized users

---

## 📚 **References**

- [Datadog Source Code Integration](https://docs.datadoghq.com/integrations/guide/source-code-integration/)
- [Git Integration Best Practices](https://docs.datadoghq.com/tracing/service_catalog/setup/#git-integration)
- [APM Source Code Links](https://docs.datadoghq.com/tracing/error_tracking/explorer/?tab=python#source-code-integration)

---

## ✅ **Summary**

| Feature | Status |
|---------|--------|
| **Git Metadata in Traces** | ✅ Enabled |
| **Git Metadata in Logs** | ✅ Enabled |
| **Error Stack Trace Links** | ✅ Enabled |
| **GitHub Integration** | ⚠️ Needs setup in Datadog UI |
| **View Code Button** | ⚠️ Requires GitHub integration |

---

**Next Steps**:
1. ✅ Deploy with git metadata (automatic)
2. ⚠️ Configure GitHub integration in Datadog UI
3. ✅ Verify logs show git commit
4. ✅ Test "View Code" links in APM traces

---

**Status**: ✅ **Source Code Integration Configured**

**Benefit**: Click from any trace or error directly to the source code in GitHub! 🎉

