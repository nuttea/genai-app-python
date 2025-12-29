# 🚀 GitHub Actions CI/CD - Quick Start

Get automated deployments working in 15 minutes!

## What You Get

✅ **Automated Testing** - Every PR and push
✅ **Automated Deployment** - Push to main → deploys to Cloud Run
✅ **Path-based Triggers** - Only affected services rebuild
✅ **No Service Account Keys** - Workload Identity Federation
✅ **Security Scanning** - Trivy + Datadog Static Analysis
✅ **Notifications** - Slack alerts on deploy success/failure

## 15-Minute Setup

### Step 1: Setup Workload Identity (10 minutes)

```bash
export GITHUB_ORG=your-github-username
export GITHUB_REPO=genai-app-python

cd infra/cloud-run
./setup-workload-identity.sh
```

**Output will show values for GitHub Secrets** - save them!

### Step 2: Add GitHub Secrets (3 minutes)

Go to: `https://github.com/YOUR_ORG/genai-app-python/settings/secrets/actions`

Add these secrets (from Step 1 output):

**Required:**
- `GCP_PROJECT_ID`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT_EMAIL`
- `GCP_REGION`

**Optional (but recommended):**
- `DD_API_KEY` - For Datadog monitoring
- `DD_APP_KEY` - For Datadog static analysis
- `DD_SITE` - datadoghq.com
- `DD_RUM_CLIENT_TOKEN` - For frontend RUM
- `DD_RUM_APPLICATION_ID` - For frontend RUM
- `SLACK_WEBHOOK_URL` - For deployment notifications

### Step 3: Test It! (2 minutes)

```bash
# Test backend workflow
echo "# Test CI/CD" >> services/fastapi-backend/README.md
git add .
git commit -m "test: trigger fastapi-backend workflow"
git push origin main

# Or test frontend workflow
echo "# Test CI/CD" >> frontend/streamlit/README.md
git add .
git commit -m "test: trigger streamlit-frontend workflow"
git push origin main

# Watch the magic happen!
open https://github.com/YOUR_ORG/genai-app-python/actions
```

## 🎯 What Happens Automatically

### On Pull Request

```
1. Code quality checks run
2. Tests run (if changes in service)
3. Linting checks
4. Security scan
5. ✅ or ❌ status on PR
```

### On Push to Main

```
1. All checks run
2. Docker images built
3. Pushed to Container Registry
4. Deployed to Cloud Run
5. Smoke tests run
6. Slack notification sent
```

### Path-Based Triggers

**Backend changes** (`services/fastapi-backend/**`):
- ✅ Backend workflow runs
- ❌ Frontend workflow skipped

**Frontend changes** (`frontend/streamlit/**`):
- ✅ Frontend workflow runs
- ❌ Backend workflow skipped

**Both changed**:
- ✅ Both workflows run

## 🔧 Workflows

### Backend CI/CD

**File**: `.github/workflows/backend-ci-cd.yml`

**Jobs:**
1. Test (pytest with coverage)
2. Lint (Black, Ruff, Mypy)
3. Security (Trivy scan)
4. Build (Docker image)
5. Deploy (Cloud Run)

**Triggers:**
- Push/PR to `services/fastapi-backend/**`
- Manual dispatch

### Frontend CI/CD

**File**: `.github/workflows/frontend-ci-cd.yml`

**Jobs:**
1. Lint (Black, Ruff)
2. Build (Docker image)
3. Deploy (Cloud Run)

**Triggers:**
- Push/PR to `frontend/streamlit/**`
- Manual dispatch

### Code Quality

**File**: `.github/workflows/code-quality.yml`

**Jobs:**
1. Pre-commit hooks
2. Datadog Static Analysis
3. Dependency review
4. Security scan

**Triggers:**
- All PRs
- Push to main/develop

## 💡 Usage Examples

### Manual Workflow Trigger

```
1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Choose branch
5. Run
```

### Skip CI

```bash
# Add [skip ci] to commit message
git commit -m "docs: update readme [skip ci]"
```

### Test Specific Service

```bash
# Only backend
git add services/fastapi-backend/
git commit -m "feat: update backend"
git push  # Only backend workflow runs

# Only frontend
git add frontend/streamlit/
git commit -m "feat: update frontend"
git push  # Only frontend workflow runs
```

## 🐛 Troubleshooting

### Workflow Not Triggering

**Check:**
- Changes in correct path (`services/fastapi-backend/**`)
- Workflow file syntax valid
- Branch is not ignored

**Fix:**
```bash
# Validate workflow
gh workflow view backend-ci-cd

# Trigger manually
gh workflow run backend-ci-cd
```

### Authentication Failed

**Check:**
- Workload Identity setup complete
- GitHub secrets configured
- Service account has permissions

**Fix:**
```bash
# Re-run setup
./setup-workload-identity.sh

# Verify secrets in GitHub
# Settings → Secrets → Actions
```

### Tests Failing

**Check logs:**
```
GitHub Actions → Select run → Click failed job
```

**Run locally:**
```bash
cd services/fastapi-backend
poetry run pytest -v
```

### Deployment Failed

**Check Cloud Run logs:**
```bash
gcloud run services logs read SERVICE_NAME --region us-central1 --limit 100
```

**Rollback:**
```bash
gcloud run services update-traffic SERVICE_NAME \
    --to-revisions PREVIOUS_REVISION=100 \
    --region us-central1
```

## 📊 Monitoring CI/CD

### View Workflow Status

**GitHub UI:**
- Actions tab → See all workflows
- Each workflow shows history
- Click run for details

**GitHub CLI:**
```bash
# List workflow runs
gh run list

# View specific run
gh run view RUN_ID

# Watch current run
gh run watch
```

### Notifications

**Slack:**
- Deploy success: Green notification
- Deploy failure: Red notification with link

**Email:**
- GitHub sends on workflow failure (configure in settings)

## 🎓 Best Practices

### 1. Branch Protection

Setup in GitHub:
```
Settings → Branches → Add rule for `main`
- Require PR reviews (1+)
- Require status checks (all workflows)
- Require up to date branch
- Include administrators
```

### 2. Environment Secrets

For staging vs production:
```
Settings → Environments → New environment
- Name: production
- Add protection rules
- Add environment-specific secrets
```

### 3. Caching

Already configured:
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pypoetry
    key: poetry-${{ hashFiles('**/poetry.lock') }}
```

### 4. Matrix Testing

Test multiple Python versions:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
```

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Auth Action](https://github.com/google-github-actions/auth)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)

---

**Quick Setup**: `./setup-workload-identity.sh` → Add secrets → Push code → Done! 🎉
