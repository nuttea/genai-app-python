# Workload Identity Federation Setup for GitHub Actions

Complete guide for setting up Workload Identity Federation to allow GitHub Actions to deploy to Google Cloud Run without service account keys.

## Overview

Workload Identity Federation allows GitHub Actions to authenticate to GCP using short-lived tokens instead of long-lived service account keys.

**Benefits:**
- ✅ No service account keys to manage
- ✅ Temporary credentials (short-lived)
- ✅ Audit trail in Cloud Audit Logs
- ✅ Automatic key rotation
- ✅ Least privilege access

## Architecture

```
GitHub Actions
    ↓ (OIDC Token)
Workload Identity Pool
    ↓ (Federation)
Workload Identity Provider
    ↓ (Impersonation)
Service Account
    ↓ (IAM Permissions)
GCP Resources (Cloud Run, Container Registry, etc.)
```

## Step-by-Step Setup

### 1. Enable Required APIs

```bash
export PROJECT_ID=your-project-id

gcloud services enable \
    iamcredentials.googleapis.com \
    cloudresourcemanger.googleapis.com \
    sts.googleapis.com \
    --project=${PROJECT_ID}
```

### 2. Create Workload Identity Pool

```bash
# Create the pool
gcloud iam workload-identity-pools create "github-actions-pool" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Get the pool ID
export POOL_ID=$(gcloud iam workload-identity-pools describe github-actions-pool \
    --project="${PROJECT_ID}" \
    --location="global" \
    --format="value(name)")

echo "Pool ID: ${POOL_ID}"
```

### 3. Create Workload Identity Provider

```bash
# Get your GitHub repository info
export GITHUB_ORG=nuttea
export GITHUB_REPO=genai-app-python

# Create the provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="github-actions-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --attribute-condition="assertion.repository_owner == '${GITHUB_ORG}'" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# Get the provider ID
export PROVIDER_ID=$(gcloud iam workload-identity-pools providers describe github-provider \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="github-actions-pool" \
    --format="value(name)")

echo "Provider ID: ${PROVIDER_ID}"
```

### 4. Create Service Account

```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create nuttee-gh-actions-sa \
    --project="${PROJECT_ID}" \
    --description="Service account for GitHub Actions deployments" \
    --display-name="GitHub Actions"

export SA_EMAIL="nuttee-gh-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Service Account: ${SA_EMAIL}"
```

### 5. Grant IAM Permissions

```bash
# Grant Cloud Run Admin (to deploy services)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

# Grant Service Account User (to act as service accounts)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

# Grant Cloud Build Editor (to build images)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/cloudbuild.builds.editor"

# Grant Storage Admin (for Container Registry)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

# Grant Secret Manager Secret Accessor (to read secrets)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"
```

### 6. Allow GitHub to Impersonate Service Account

```bash
# Allow GitHub Actions from your repository to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"
```

### 7. Get Values for GitHub Secrets

```bash
echo "Add these values to GitHub Secrets:"
echo ""
echo "GCP_PROJECT_ID: ${PROJECT_ID}"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER: ${PROVIDER_ID}"
echo "GCP_SERVICE_ACCOUNT_EMAIL: ${SA_EMAIL}"
echo "GCP_REGION: ${REGION}"
```

## Configure GitHub Secrets

### 1. Go to GitHub Repository Settings

```
https://github.com/YOUR_USERNAME/genai-app-python/settings/secrets/actions
```

### 2. Add Secrets

Click "New repository secret" and add each:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_PROJECT_ID` | your-project-id | GCP Project ID |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | projects/123.../providers/github-provider | Full provider path |
| `GCP_SERVICE_ACCOUNT_EMAIL` | github-actions@project.iam.gserviceaccount.com | Service account email |
| `GCP_REGION` | us-central1 | GCP region |
| `DD_API_KEY` | your-datadog-api-key | Datadog API key |
| `DD_APP_KEY` | your-datadog-app-key | Datadog App key |
| `DD_SITE` | datadoghq.com | Datadog site |
| `DD_RUM_CLIENT_TOKEN` | pub... | Datadog RUM client token |
| `DD_RUM_APPLICATION_ID` | uuid... | Datadog RUM app ID |
| `SLACK_WEBHOOK_URL` | https://hooks.slack.com/... | Slack webhook (optional) |

### 3. Environment Secrets (Optional)

For staging vs production separation:

**Staging environment:**
- `GCP_PROJECT_ID_STAGING`
- `DD_ENV=staging`

**Production environment:**
- `GCP_PROJECT_ID_PROD`
- `DD_ENV=production`

## Test the Setup

### Manual Workflow Dispatch

1. Go to Actions tab in GitHub
2. Select "Backend CI/CD" workflow
3. Click "Run workflow"
4. Select branch
5. Run

### Push to Trigger

```bash
# Make a small change
echo "# Test" >> services/fastapi-backend/README.md

# Commit and push
git add services/fastapi-backend/README.md
git commit -m "test: trigger workflow"
git push origin main

# Check GitHub Actions tab
```

## Troubleshooting

### "Permission denied" Errors

**Check IAM permissions:**
```bash
# List service account permissions
gcloud projects get-iam-policy ${PROJECT_ID} \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SA_EMAIL}"
```

**Grant missing permissions:**
```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/REQUIRED_ROLE"
```

### "Workload Identity Pool not found"

**Verify pool exists:**
```bash
gcloud iam workload-identity-pools list --location=global --project=${PROJECT_ID}
```

**Verify provider exists:**
```bash
gcloud iam workload-identity-pools providers list \
    --workload-identity-pool="github-actions-pool" \
    --location="global" \
    --project=${PROJECT_ID}
```

### "Token exchange failed"

**Check attribute mapping:**
```bash
gcloud iam workload-identity-pools providers describe github-provider \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="github-actions-pool"
```

**Verify GitHub repository is allowed:**
```bash
gcloud iam service-accounts get-iam-policy ${SA_EMAIL} \
    --project="${PROJECT_ID}"
```

## Security Best Practices

### 1. Least Privilege

Only grant necessary permissions:
```bash
# ✅ Good - specific role
--role="roles/run.admin"

# ❌ Bad - too broad
--role="roles/editor"
```

### 2. Repository Restrictions

Limit to specific repositories:
```bash
--member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"
```

### 3. Branch Restrictions

Limit to specific branches (in workflow):
```yaml
if: github.ref == 'refs/heads/main'
```

### 4. Audit Logging

Enable Cloud Audit Logs:
```bash
# View who deployed what
gcloud logging read "protoPayload.authenticationInfo.principalEmail:${SA_EMAIL}" \
    --limit 50
```

### 5. Regular Reviews

- Monthly: Review IAM permissions
- Quarterly: Audit deployments
- Yearly: Review architecture

## Advanced: Multiple Repositories

To allow multiple repositories:

```bash
# Create condition for multiple repos
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_ORG}/repo1" \
    --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_ORG}/repo2"
```

## Resources

- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions + GCP](https://github.com/google-github-actions/auth)
- [Best Practices](https://cloud.google.com/iam/docs/best-practices-for-using-workload-identity-federation)

---

**Quick Setup Script**: See `infra/cloud-run/setup-workload-identity.sh`
