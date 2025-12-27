# Production Deployment Strategy

## Overview

This project uses a **two-environment strategy** with Cloud Run revision tags:

- **`main` branch** → `DD_ENV=dev` (Development/Testing)
- **`prod` branch** → `DD_ENV=prod` (Production with `prod` tag URL)

## Environment Architecture

### Main Branch (Development)
```
main branch
    ↓ (push)
GitHub Actions
    ↓
Deploy to Cloud Run
    ↓
Latest revision (no tag)
    ↓
URL: https://SERVICE-HASH.run.app
Environment: DD_ENV=dev
```

### Prod Branch (Production)
```
main branch
    ↓ (Pull Request)
prod branch
    ↓ (merge PR)
GitHub Actions
    ↓
Deploy to Cloud Run
    ↓
Tagged revision: 'prod'
    ↓
URL: https://SERVICE-prod-HASH.run.app
Environment: DD_ENV=prod
```

## URLs

### Backend URLs
- **Dev (main)**: `https://genai-fastapi-backend-HASH.run.app`
- **Prod (prod)**: `https://genai-fastapi-backend-prod-HASH.run.app`

### Frontend URLs
- **Dev (main)**: `https://genai-streamlit-frontend-HASH.run.app`
- **Prod (prod)**: `https://genai-streamlit-frontend-prod-HASH.run.app`

## Cloud Run Revision Tags

### What are Revision Tags?
Cloud Run revision tags create stable URLs for specific revisions:
- Each revision can have multiple tags
- Tags route traffic to specific revisions
- Enables blue/green, canary deployments
- Provides stable prod URLs

### Tag Strategy
- **No tag (main)**: Latest/dev version
- **`prod` tag**: Stable production version

## Setting Up Production Branch

### 1. Create Production Branch

```bash
# From main branch
git checkout main
git pull origin main

# Create prod branch
git checkout -b prod
git push -u origin prod
```

### 2. Configure Branch Protection

Go to GitHub: **Settings** → **Branches** → **Branch protection rules**

Create rule for `prod` branch:

#### Required Settings:
- ✅ **Require a pull request before merging**
  - ✅ Require approvals (minimum: 1)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Required checks:
    - `Code Quality`
    - `Fastapi Backend CI/CD / lint`
    - `Fastapi Backend CI/CD / test`
    - `Streamlit Frontend CI/CD / lint`

- ✅ **Require conversation resolution before merging**

- ✅ **Do not allow bypassing the above settings**

#### Optional Settings:
- ✅ **Require linear history**
- ✅ **Include administrators** (enforce rules for admins)

### 3. Configure Workload Identity for Prod

The same Workload Identity Federation setup works for both branches.
No additional configuration needed.

## Deployment Workflow

### Development Flow (main branch)

```bash
# 1. Make changes
git checkout main
git add .
git commit -m "feat: new feature"
git push origin main

# 2. Automatic deployment
# GitHub Actions deploys to Cloud Run (dev)
# URL: https://SERVICE-HASH.run.app
# DD_ENV: dev
```

### Production Flow (prod branch)

```bash
# 1. Ensure main is tested and stable
# Tests pass on main branch ✅

# 2. Create Pull Request
gh pr create \
  --base prod \
  --head main \
  --title "Release: Deploy to production" \
  --body "Deploy tested changes from main to production"

# 3. Review and approve PR
# - Code review
- Tests passing
# - All checks green

# 4. Merge PR
gh pr merge --merge

# 5. Automatic deployment
# GitHub Actions deploys to Cloud Run (prod)
# URL: https://SERVICE-prod-HASH.run.app
# DD_ENV: prod
# Traffic: 100% to 'prod' tag
```

## Quick Commands

### Check Current Deployments

```bash
# List all revisions for backend
gcloud run revisions list \
  --service genai-fastapi-backend \
  --region us-central1

# List all revisions for frontend
gcloud run revisions list \
  --service genai-streamlit-frontend \
  --region us-central1
```

### View Traffic Splits

```bash
# Backend traffic
gcloud run services describe genai-fastapi-backend \
  --region us-central1 \
  --format 'value(status.traffic)'

# Frontend traffic
gcloud run services describe genai-streamlit-frontend \
  --region us-central1 \
  --format 'value(status.traffic)'
```

### Get URLs

```bash
# Get dev URL (latest revision)
gcloud run services describe genai-fastapi-backend \
  --region us-central1 \
  --format 'value(status.url)'

# Get prod URL (prod tag)
gcloud run services describe genai-fastapi-backend \
  --region us-central1 \
  --format 'value(status.traffic[0].url)'
```

## Rollback Strategy

### Rollback Production

If production deployment has issues:

```bash
# 1. List revisions
gcloud run revisions list \
  --service genai-fastapi-backend \
  --region us-central1

# 2. Find previous stable revision
# Example: genai-fastapi-backend-00042-abc

# 3. Update 'prod' tag to previous revision
gcloud run services update-traffic genai-fastapi-backend \
  --region us-central1 \
  --to-revisions genai-fastapi-backend-00042-abc=100 \
  --tag prod

# 4. Verify
gcloud run services describe genai-fastapi-backend \
  --region us-central1 \
  --format 'value(status.traffic)'
```

## Monitoring in Datadog

### Filter by Environment

```
# View dev deployments
env:dev

# View prod deployments
env:prod

# Compare environments
env:dev vs env:prod
```

### Create Environment-Specific Monitors

```yaml
# Example: Production error rate
Monitor: High Error Rate in Production
Query: sum:trace.http.request.errors{env:prod,service:genai-fastapi-backend}
Threshold: > 10 errors in 5 minutes
Alert: PagerDuty, Slack #incidents
```

## Best Practices

1. **Always test on main first**
   - Let main run for a while
   - Monitor for errors
   - Validate functionality

2. **Use Pull Requests for prod**
   - Never push directly to prod
   - Require reviews
   - Ensure tests pass

3. **Monitor after deployment**
   - Watch Datadog for errors
   - Check Cloud Run logs
   - Validate URLs working

4. **Keep prod stable**
   - Only promote tested code
   - Have rollback plan ready
   - Document changes

5. **Tag releases**
   ```bash
   git tag -a v1.0.0 -m "Production release 1.0.0"
   git push origin v1.0.0
   ```

## Troubleshooting

### Prod deployment failed

1. Check GitHub Actions logs
2. Verify secrets are set
3. Check Cloud Run quota
4. Verify Workload Identity permissions

### Wrong traffic routing

```bash
# Force traffic to prod tag
gcloud run services update-traffic SERVICE_NAME \
  --region us-central1 \
  --to-tags prod=100
```

### Need to test prod before routing traffic

The workflows deploy with `--no-traffic` then route 100%.
To test first:

```bash
# Don't run update-traffic command
# Test the tagged URL manually
# Then route traffic when ready
gcloud run services update-traffic SERVICE_NAME \
  --region us-central1 \
  --to-tags prod=100
```

## Summary

**Two-branch strategy:**
- `main` = dev environment (latest features)
- `prod` = production environment (stable, tested)

**Deployment method:**
- Both deploy to same Cloud Run services
- Prod uses revision tag for stable URL
- Clear separation in Datadog monitoring

**Safety:**
- Branch protection on prod
- PR required for production changes
- Easy rollback with revision tags

