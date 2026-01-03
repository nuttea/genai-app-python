# GitHub Variables Setup

**Date**: 2026-01-02  
**Commit**: `16dc09d`  
**Change**: Converted GCP_PROJECT_ID from secret to variable  
**Status**: ✅ Code updated, variables need to be created

---

## 🎯 **What Changed**

### **Before**
```yaml
gcr.io/${{ secrets.GCP_PROJECT_ID }}/service-name
```

### **After**
```yaml
gcr.io/${{ vars.GCP_PROJECT_ID }}/service-name
```

---

## 📋 **Why Use Variables Instead of Secrets?**

| Aspect | Secrets | Variables |
|--------|---------|-----------|
| **Use For** | Sensitive data (API keys, tokens) | Non-sensitive config (project ID, region) |
| **Visibility** | Hidden in logs (***) | Visible in logs |
| **Best Practice** | ✅ Passwords, keys | ✅ Project IDs, regions |
| **GitHub Access** | Secrets tab | Variables tab |

**Project IDs are not sensitive** → Use variables! ✅

---

## 🚀 **Required Actions**

### **Step 1: Create GitHub Variable**

#### **Using GitHub UI**

1. Go to your repository: https://github.com/nuttea/genai-app-python
2. Click **Settings** (top navigation)
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click the **Variables** tab (not Secrets!)
5. Click **New repository variable**
6. Fill in:
   - **Name**: `GCP_PROJECT_ID`
   - **Value**: `datadog-ese-sandbox`
7. Click **Add variable**

---

#### **Using GitHub CLI** (Faster)

```bash
# Create GCP_PROJECT_ID variable
gh variable set GCP_PROJECT_ID --body "datadog-ese-sandbox"

# Verify it was created
gh variable list

# Expected output:
# GCP_PROJECT_ID  datadog-ese-sandbox
```

---

### **Step 2: (Optional) Create GCP_REGION Variable**

If you want to add GCP_REGION for future use:

**GitHub UI**:
1. Same steps as above
2. **Name**: `GCP_REGION`
3. **Value**: `us-central1`

**GitHub CLI**:
```bash
gh variable set GCP_REGION --body "us-central1"
```

---

### **Step 3: (Optional) Clean Up Old Secret**

After confirming workflows work with variables:

**GitHub UI**:
1. Go to **Secrets** tab (not Variables)
2. Find `GCP_PROJECT_ID` secret
3. Click **Remove**

**GitHub CLI**:
```bash
gh secret delete GCP_PROJECT_ID
```

**⚠️ Only delete after confirming workflows work!**

---

## ✅ **Verification**

### **Check Variables**

```bash
# List all variables
gh variable list

# Expected:
# GCP_PROJECT_ID  datadog-ese-sandbox
# (GCP_REGION     us-central1)  # If created
```

---

### **Test Workflows**

After creating the variable, workflows should work:

```bash
# Check recent runs
gh run list --limit 5

# Watch a running workflow
gh run watch
```

---

## 📊 **Files Updated**

All GitHub Actions workflows now use `vars.GCP_PROJECT_ID`:

### **Development Workflows**
- ✅ `.github/workflows/adk-python.yml`
- ✅ `.github/workflows/fastapi-backend.yml`
- ✅ `.github/workflows/nextjs-frontend.yml`
- ✅ `.github/workflows/streamlit-frontend.yml`

### **Production Workflows**
- ✅ `.github/workflows/adk-python-prod.yml`
- ✅ `.github/workflows/fastapi-backend-prod.yml`
- ✅ `.github/workflows/nextjs-frontend-prod.yml`
- ✅ `.github/workflows/streamlit-frontend-prod.yml`

### **Reusable Workflow**
- ✅ `.github/workflows/_reusable-cloudrun-deploy.yml`

---

## 🔍 **What Each Workflow Uses It For**

### **Docker Image Tags**
```yaml
gcr.io/${{ vars.GCP_PROJECT_ID }}/service-name:${{ github.sha }}
```

Example:
```
gcr.io/datadog-ese-sandbox/genai-adk-python:abc123
```

---

### **Cloud Run Deployment**
```yaml
--image gcr.io/${{ vars.GCP_PROJECT_ID }}/service-name:${{ github.sha }}
```

---

### **Environment Variables**
```yaml
--set-env-vars GOOGLE_CLOUD_PROJECT=${{ vars.GCP_PROJECT_ID }}
--set-env-vars GCP_PROJECT_ID=${{ vars.GCP_PROJECT_ID }}
```

---

## 🧪 **Testing**

### **Test 1: Check Variable Exists**

```bash
gh variable get GCP_PROJECT_ID

# Expected output:
# datadog-ese-sandbox
```

---

### **Test 2: Trigger a Workflow**

```bash
# Make a small change and push
git commit --allow-empty -m "test: Verify GitHub variables work"
git push

# Watch the workflow
gh run watch
```

**Expected**: Workflow succeeds ✅

---

### **Test 3: Check Workflow Logs**

```bash
# Get latest run
gh run view --log

# Search for GCP_PROJECT_ID usage
gh run view --log | grep "gcr.io/datadog-ese-sandbox"
```

**Expected**: See project ID in image tags ✅

---

## 🚨 **Troubleshooting**

### **Error: "Context access might be invalid: vars.GCP_PROJECT_ID"**

**Cause**: Variable not created yet

**Fix**: Create the variable (Step 1 above)

---

### **Error: "Image not found: gcr.io//service-name"**

**Cause**: Variable is empty or not found

**Fix**: 
1. Check variable exists: `gh variable list`
2. Check variable value: `gh variable get GCP_PROJECT_ID`
3. Re-create if needed: `gh variable set GCP_PROJECT_ID --body "datadog-ese-sandbox"`

---

### **Workflows Still Failing**

**Check**:
1. Variable name is exact: `GCP_PROJECT_ID` (case-sensitive)
2. Variable value is correct: `datadog-ese-sandbox` (no spaces)
3. Variable is repository-level (not environment-specific)

---

## 📚 **GitHub Documentation**

- [Using variables in workflows](https://docs.github.com/en/actions/learn-github-actions/variables)
- [Managing variables](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository)
- [Contexts (vars context)](https://docs.github.com/en/actions/learn-github-actions/contexts#vars-context)

---

## ✅ **Summary**

**What You Need to Do**:

1. **Create variable** (required):
   ```bash
   gh variable set GCP_PROJECT_ID --body "datadog-ese-sandbox"
   ```

2. **Verify it works** (recommended):
   ```bash
   gh variable list
   ```

3. **Test a workflow** (optional):
   ```bash
   git commit --allow-empty -m "test: Verify variables"
   git push
   gh run watch
   ```

4. **Clean up old secret** (optional, after confirming):
   ```bash
   gh secret delete GCP_PROJECT_ID
   ```

---

## 🎯 **Quick Commands**

```bash
# All-in-one setup
gh variable set GCP_PROJECT_ID --body "datadog-ese-sandbox"
gh variable set GCP_REGION --body "us-central1"
gh variable list

# Expected output:
# GCP_PROJECT_ID  datadog-ese-sandbox
# GCP_REGION      us-central1
```

---

**Status**: 🟡 **Code Ready, Variables Needed**

Create the GitHub variables and workflows will work! 🚀✨

