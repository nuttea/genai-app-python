# Next.js Frontend GitHub Actions Workflows - Setup Complete ✅

This document summarizes the GitHub Actions CI/CD workflows created for the Next.js frontend.

## 📦 Files Created

### 1. Production Dockerfile

**File**: `frontend/nextjs/Dockerfile.cloudrun`

- Multi-stage build for optimized image size
- Standalone Next.js output
- Non-root user for security
- Health check endpoint integration
- Datadog source code integration support

### 2. Health API Endpoint

**File**: `frontend/nextjs/app/api/health/route.ts`

- Returns service health status
- Used by Cloud Run health checks
- Returns service info and timestamp

### 3. Development Workflow

**File**: `.github/workflows/nextjs-frontend.yml`

**Triggers**:

- Push to `main`/`develop` branches
- Pull requests
- Manual dispatch

**Jobs**:

1. **Lint and Test**: ESLint, TypeScript type checking, Prettier formatting check, Build test
2. **Deploy**: Build Docker image, push to GCR, deploy to Cloud Run (dev environment)

**Environment**: `dev` (DD_ENV=dev)

### 4. Production Workflow

**File**: `.github/workflows/nextjs-frontend-prod.yml`

**Triggers**:

- Push to `prod` branch

**Jobs**:

1. **Deploy**: Build Docker image with `prod-latest` tag, deploy to Cloud Run with `prod` revision tag (no-traffic)

**Environment**: `prod` (DD_ENV=prod)

### 5. Updated Documentation

**File**: `.github/workflows/README.md`

- Added Next.js Frontend workflows to documentation
- Updated workflow structure diagram
- Updated service listings
- Updated status badges

## 🚀 How It Works

### Development Workflow (main branch)

```
Push to main → Lint & Test → Build Docker → Deploy to Cloud Run (dev)
                ↓
            - ESLint
            - TypeScript
            - Prettier
            - Build test
```

**Deployment**:

- **Service**: `genai-nextjs-frontend`
- **Region**: `us-central1`
- **Environment**: `dev`
- **Traffic**: 100% (immediate deployment)
- **Min Instances**: 0 (cost-optimized)

### Production Workflow (prod branch)

```
Push to prod → Build Docker → Deploy with 'prod' tag (no-traffic)
                ↓
            Tagged revision ready for manual traffic shifting
```

**Deployment**:

- **Service**: `genai-nextjs-frontend`
- **Region**: `us-central1`
- **Environment**: `prod`
- **Traffic**: 0% (tagged revision, manual promotion)
- **Min Instances**: 1 (high availability)

## 🔧 Configuration

### Environment Variables

The workflows automatically configure these environment variables:

**Build-time**:

- `DD_GIT_REPOSITORY_URL`: Source code repository URL
- `DD_GIT_COMMIT_SHA`: Git commit SHA for tracking

**Runtime**:

- `VOTE_EXTRACTOR_API_URL`: Backend API URL (auto-detected)
- `CONTENT_CREATOR_API_URL`: Content Creator API URL (auto-detected)
- `NODE_ENV`: `production`
- `NEXT_TELEMETRY_DISABLED`: `1`
- `NEXT_PUBLIC_APP_NAME`: "Datadog GenAI Platform"
- `NEXT_PUBLIC_APP_VERSION`: Git commit SHA
- `NEXT_PUBLIC_DD_*`: Datadog RUM configuration
- `NEXT_PUBLIC_API_KEY`: From Secret Manager (`api-key:latest`)

### Secrets Required

Make sure these secrets are configured in GitHub:

**GCP Authentication**:

- `GCP_PROJECT_ID`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT_EMAIL`

**Datadog RUM**:

- `DD_RUM_APPLICATION_ID`
- `DD_RUM_CLIENT_TOKEN`

**Notifications (Optional)**:

- `SLACK_WEBHOOK_URL`

### Cloud Run Configuration

**Development (main branch)**:

```bash
--memory 1Gi
--cpu 1
--timeout 300
--max-instances 10
--min-instances 0
--allow-unauthenticated
--port 3000
```

**Production (prod branch)**:

```bash
--memory 1Gi
--cpu 1
--timeout 300
--max-instances 10
--min-instances 1  # High availability
--allow-unauthenticated
--port 3000
--tag prod
--no-traffic  # Manual traffic shifting
```

## 📝 Usage

### Automatic Deployment (Development)

1. Make changes to `frontend/nextjs/**`
2. Commit and push to `main` branch:
   ```bash
   git add frontend/nextjs/
   git commit -m "feat: Update Next.js frontend"
   git push origin main
   ```
3. GitHub Actions automatically:
   - Runs linting and tests
   - Builds Docker image
   - Deploys to Cloud Run (dev)
   - Runs smoke tests

### Production Deployment

1. Merge `main` into `prod` branch:
   ```bash
   git checkout prod
   git merge main
   git push origin prod
   ```
2. GitHub Actions automatically:
   - Builds production Docker image
   - Deploys with `prod` tag (no traffic)
   - Runs smoke tests
3. **Manual traffic shift** (when ready):
   ```bash
   gcloud run services update-traffic genai-nextjs-frontend \
     --region us-central1 \
     --to-tags prod=100
   ```

### Manual Workflow Trigger

Using GitHub CLI:

```bash
# Development workflow
gh workflow run nextjs-frontend.yml

# Production workflow
gh workflow run nextjs-frontend-prod.yml
```

Using GitHub UI:

1. Go to **Actions** tab
2. Select **Next.js Frontend CI/CD** (or Production)
3. Click **Run workflow**

## 🔍 Monitoring

### GitHub Actions

**View workflow runs**:

```bash
# List recent runs
gh run list --workflow=nextjs-frontend.yml

# View specific run
gh run view RUN_ID --log

# Watch current run
gh run watch
```

**GitHub UI**:

- https://github.com/YOUR_ORG/genai-app-python/actions/workflows/nextjs-frontend.yml

### Cloud Run

**Check deployment**:

```bash
# Get service URL
gcloud run services describe genai-nextjs-frontend \
  --region us-central1 \
  --format 'value(status.url)'

# View revisions
gcloud run revisions list \
  --service genai-nextjs-frontend \
  --region us-central1

# View traffic split
gcloud run services describe genai-nextjs-frontend \
  --region us-central1 \
  --format 'value(status.traffic)'
```

### Datadog

The frontend automatically reports to Datadog RUM:

- Session Replay enabled
- 100% sampling (dev and prod)
- Traces enabled
- Service: `genai-nextjs-frontend`
- Environment: `dev` or `prod`

## 🧪 Testing

### Smoke Tests

The workflows include automated smoke tests:

**Development**:

```bash
curl -f https://genai-nextjs-frontend-dev.run.app/api/health
curl -f https://genai-nextjs-frontend-dev.run.app/
```

**Production**:

```bash
curl -f https://genai-nextjs-frontend-prod-HASH.run.app/api/health
curl -f https://genai-nextjs-frontend-prod-HASH.run.app/
```

### Local Testing

Test the production Dockerfile locally:

```bash
cd frontend/nextjs

# Build production image
docker build -f Dockerfile.cloudrun -t nextjs-frontend:local .

# Run container
docker run -p 3000:3000 \
  -e VOTE_EXTRACTOR_API_URL=http://localhost:8000 \
  -e CONTENT_CREATOR_API_URL=http://localhost:8002 \
  nextjs-frontend:local

# Test health endpoint
curl http://localhost:3000/api/health
```

## 🛠️ Troubleshooting

### Workflow Not Triggering

**Check**:

1. Changes are in `frontend/nextjs/**` path
2. Branch is `main` or `develop` (or `prod` for production)
3. Workflow file syntax is valid

**Test**:

```bash
# Validate YAML syntax
yamllint .github/workflows/nextjs-frontend.yml

# View workflow configuration
gh workflow view nextjs-frontend.yml
```

### Build Failures

**Common issues**:

1. **TypeScript errors**: Run `npm run type-check` locally
2. **Linting errors**: Run `npm run lint` locally
3. **Prettier errors**: Run `npx prettier --check .` locally

**Fix locally first**:

```bash
cd frontend/nextjs
npm run lint
npm run type-check
npx prettier --write "**/*.{ts,tsx,js,jsx,json,css,md}"
npm run build
```

### Deployment Failures

**Check**:

1. GCP secrets are configured correctly
2. Service account has required permissions
3. Backend services are deployed and accessible

**Verify secrets**:

```bash
# Check Secret Manager
gcloud secrets versions access latest --secret=api-key

# Verify service account permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL"
```

### Backend URL Not Found

If the workflow can't find backend URLs:

**Check services exist**:

```bash
gcloud run services list --region us-central1
```

**Deploy backends first**:

```bash
# Deploy FastAPI backend
git push origin main  # Triggers fastapi-backend.yml

# Deploy Content Creator
docker-compose up -d content-creator
# (Manual deployment or create workflow)
```

## 📊 Status Badge

Add to your README:

```markdown
[![Next.js Frontend CI](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/nextjs-frontend.yml/badge.svg)](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/nextjs-frontend.yml)
```

## 🎯 Next Steps

1. **Configure GitHub Secrets** (if not already done):
   - See `.github/workflows/README.md` for required secrets
   - Follow Workload Identity setup guide

2. **Test Development Workflow**:

   ```bash
   # Make a small change
   echo "# Test" >> frontend/nextjs/README.md
   git add -A
   git commit -m "test: Trigger Next.js workflow"
   git push origin main
   ```

3. **Monitor Deployment**:
   - Check GitHub Actions tab
   - Verify Cloud Run deployment
   - Test the deployed service
   - Check Datadog RUM for traces

4. **Test Production Workflow** (when ready):
   ```bash
   git checkout prod
   git merge main
   git push origin prod
   # Then manually shift traffic when ready
   ```

## 📚 Resources

- **GitHub Actions**: [Workflows README](.github/workflows/README.md)
- **Workload Identity**: See `docs/deployment/workload-identity-federation.md`
- **Next.js Config**: `frontend/nextjs/next.config.js`
- **Docker Config**: `frontend/nextjs/Dockerfile.cloudrun`

---

**Created**: $(date +%Y-%m-%d)
**Status**: ✅ Ready to use
**Services**: 3 (FastAPI Backend, Streamlit Frontend, Next.js Frontend)
**Environments**: 2 (dev, prod)
