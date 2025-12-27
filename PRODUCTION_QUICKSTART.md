# Production Deployment Quick Start

## 🎯 Quick Commands

### Promote main to production

```bash
# Interactive script (recommended)
./infra/scripts/promote-to-prod.sh

# Or manually
gh pr create --base prod --head main \
  --title "Release: Deploy to production" \
  --body "Promote tested changes to production"
```

### Check deployment status

```bash
# Watch GitHub Actions
gh run list --limit 5

# Get production URLs
gcloud run services describe genai-fastapi-backend \
  --region us-central1 --format 'value(status.traffic[0].url)'

gcloud run services describe genai-streamlit-frontend \
  --region us-central1 --format 'value(status.traffic[0].url)'
```

### Rollback production

```bash
# List revisions
gcloud run revisions list --service genai-fastapi-backend --region us-central1

# Rollback to previous revision
gcloud run services update-traffic genai-fastapi-backend \
  --region us-central1 \
  --to-revisions REVISION_NAME=100 \
  --tag prod
```

## 📊 Environment Strategy

| Branch | Environment | URL Pattern | Traffic |
|--------|-------------|-------------|---------|
| `main` | `dev` | `SERVICE-HASH.run.app` | Latest |
| `prod` | `prod` | `SERVICE-prod-HASH.run.app` | 100% on `prod` tag |

## 🚀 Deployment Flow

```
1. Develop on main
   ├─ git push origin main
   └─ Deploys to dev (DD_ENV=dev)

2. Promote to production
   ├─ ./infra/scripts/promote-to-prod.sh
   ├─ Create PR: main → prod
   ├─ Review & approve
   ├─ Merge PR
   └─ Deploys to prod (DD_ENV=prod)

3. Monitor
   ├─ Datadog: env:prod
   ├─ Cloud Run logs
   └─ Production URLs
```

## 🔧 First Time Setup

### 1. Create prod branch

```bash
git checkout main
git pull origin main
git checkout -b prod
git push -u origin prod
```

### 2. Configure branch protection

Go to: **GitHub** → **Settings** → **Branches** → **Add rule**

**Branch name pattern**: `prod`

✅ **Require pull request before merging**
  - Require 1 approval
  - Dismiss stale reviews

✅ **Require status checks to pass**
  - Require branches to be up to date
  - Required checks: lint, test, Code Quality

✅ **Require conversation resolution**

### 3. Test production workflows

```bash
# Make a test change on main
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test: production workflow"
git push origin main

# Promote to prod
./infra/scripts/promote-to-prod.sh

# Merge PR
# Watch workflows deploy
gh run list --limit 3
```

## 📖 Full Documentation

See [docs/deployment/PRODUCTION_STRATEGY.md](docs/deployment/PRODUCTION_STRATEGY.md) for complete details.

## 🆘 Troubleshooting

### Workflows not triggering
- Check GitHub Actions are enabled
- Verify branch protection rules
- Check file paths in workflow triggers

### Deployment failed
- Check GitHub Actions logs
- Verify secrets are set
- Check GCP quotas

### Wrong traffic routing
```bash
# Force traffic to prod tag
gcloud run services update-traffic SERVICE_NAME \
  --region us-central1 \
  --to-tags prod=100
```

## 🔗 URLs

### Development (main branch)
- Backend: Get from Cloud Run console or `gcloud run services describe`
- Frontend: Get from Cloud Run console or `gcloud run services describe`

### Production (prod branch with tag)
- Backend: `https://genai-fastapi-backend-prod-HASH.run.app`
- Frontend: `https://genai-streamlit-frontend-prod-HASH.run.app`

## 📈 Monitoring

### Datadog Queries

```
# Production traffic only
env:prod

# Production errors
env:prod status:error

# Compare environments
env:dev vs env:prod
```

### Cloud Run Metrics

- **Console**: https://console.cloud.google.com/run
- **Metrics**: CPU, Memory, Request count, Latency
- **Logs**: Filtered by revision/tag

---

**Ready to deploy?** Run: `./infra/scripts/promote-to-prod.sh` 🚀

