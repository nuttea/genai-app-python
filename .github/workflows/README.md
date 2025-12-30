# GitHub Actions Workflows

CI/CD workflows for automated testing and deployment.

## Workflow Structure

```
.github/workflows/
├── fastapi-backend.yml          # FastAPI Backend CI/CD
├── fastapi-backend-prod.yml     # FastAPI Backend Production Deploy
├── adk-python.yml               # ADK Python Service CI/CD
├── adk-python-prod.yml          # ADK Python Service Production Deploy
├── streamlit-frontend.yml       # Streamlit Frontend CI/CD
├── streamlit-frontend-prod.yml  # Streamlit Frontend Production Deploy
├── nextjs-frontend.yml          # Next.js Frontend CI/CD
├── nextjs-frontend-prod.yml     # Next.js Frontend Production Deploy
├── code-quality.yml             # Code quality checks (all components)
└── README.md                    # This file
```

## Workflows

### 1. FastAPI Backend (`fastapi-backend.yml`)

**Triggers:**
- Push to `main`/`develop` → `services/fastapi-backend/**`
- Pull requests → `services/fastapi-backend/**`
- Manual dispatch

**Jobs:**
- Test (pytest with coverage)
- Lint (Black, Ruff, Mypy)
- Security (Trivy)
- Build (Docker image)
- Deploy (Cloud Run - main only)

**Service**: `genai-fastapi-backend`

### 2. ADK Python Service (`adk-python.yml`)

**Triggers:**
- Push to `main`/`develop` → `services/adk-python/**`
- Pull requests → `services/adk-python/**`
- Manual dispatch

**Jobs:**
- Lint (Black, Ruff)
- Build (Docker image)
- Deploy (Cloud Run - main only)

**Service**: `genai-adk-python`

**Features:**
- Google ADK Multi-Agent Framework
- Content Creator Agent
- Datadog LLM Observability
- Vertex AI / Gemini Integration

### 3. Streamlit Frontend (`streamlit-frontend.yml`)

**Triggers:**
- Push to `main`/`develop` → `frontend/streamlit/**`
- Pull requests → `frontend/streamlit/**`
- Manual dispatch

**Jobs:**
- Lint (Black, Ruff)
- Build (Docker image)
- Deploy (Cloud Run - main only)

**Service**: `genai-streamlit-frontend`

### 4. Next.js Frontend (`nextjs-frontend.yml`)

**Triggers:**
- Push to `main`/`develop` → `frontend/nextjs/**`
- Pull requests → `frontend/nextjs/**`
- Manual dispatch

**Jobs:**
- Lint and Test (ESLint, TypeScript, Prettier)
- Build (Docker image)
- Deploy (Cloud Run - main only)

**Service**: `genai-nextjs-frontend`

### 5. Production Deployments (`*-prod.yml`)

**Triggers:**
- Push to `prod` branch

**Jobs:**
- Build and deploy with `prod` tag (no-traffic)
- Smoke tests
- Deployment summary with traffic shifting instructions

**Services:**
- `genai-fastapi-backend`
- `genai-adk-python`
- `genai-streamlit-frontend`
- `genai-nextjs-frontend`

### 6. Code Quality (`code-quality.yml`)

**Triggers:**
- All pull requests
- Push to `main`/`develop`

**Jobs:**
- Pre-commit hooks
- Datadog Static Analysis
- Dependency review
- Security scan (Trivy)

**Applies to**: All code

## Naming Convention

### Current Services
- `fastapi-backend.yml` - FastAPI backend service (vote extraction)
- `adk-python.yml` - ADK Python service (multi-agent content creation)
- `streamlit-frontend.yml` - Streamlit frontend service
- `nextjs-frontend.yml` - Next.js frontend service

### Service Structure

Actual structure:

```
services/
├── fastapi-backend/           → .github/workflows/fastapi-backend.yml
└── adk-python/                → .github/workflows/adk-python.yml

frontend/
├── streamlit/                 → .github/workflows/streamlit-frontend.yml
└── nextjs/                    → .github/workflows/nextjs-frontend.yml
```

**Pattern**: `{service-name}.yml` matching the directory name

## Path Filters

Each workflow only runs when its service changes:

**fastapi-backend.yml:**
```yaml
paths:
  - 'services/fastapi-backend/**'
  - '.github/workflows/fastapi-backend.yml'
```

**adk-python.yml:**
```yaml
paths:
  - 'services/adk-python/**'
  - '.github/workflows/adk-python.yml'
```

**streamlit-frontend.yml:**
```yaml
paths:
  - 'frontend/streamlit/**'
  - '.github/workflows/streamlit-frontend.yml'
```

**nextjs-frontend.yml:**
```yaml
paths:
  - 'frontend/nextjs/**'
  - '.github/workflows/nextjs-frontend.yml'
```

**Benefits:**
- ✅ Faster CI/CD (only affected services)
- ✅ Parallel builds
- ✅ Independent deployments
- ✅ Clear history per service

## Required GitHub Secrets

### GCP Authentication
- `GCP_PROJECT_ID`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT_EMAIL`
- `GCP_REGION`

### Datadog
- `DD_API_KEY`
- `DD_APP_KEY`
- `DD_SITE`
- `DD_RUM_CLIENT_TOKEN` (frontend)
- `DD_RUM_APPLICATION_ID` (frontend)

### Notifications (Optional)
- `SLACK_WEBHOOK_URL`

See: [docs/deployment/workload-identity-federation.md](../../docs/deployment/workload-identity-federation.md)

## Adding New Service Workflow

### Template

```yaml
name: New Service CI/CD

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'services/new-service/**'
      - '.github/workflows/new-service.yml'
  pull_request:
    paths:
      - 'services/new-service/**'
  workflow_dispatch:

env:
  SERVICE_NAME: genai-new-service
  REGION: us-central1

jobs:
  # Add your jobs here (test, lint, build, deploy)
```

### Steps

1. Copy existing workflow (fastapi-backend.yml or streamlit-frontend.yml)
2. Rename file to match service
3. Update service name and paths
4. Adjust jobs for language/framework
5. Test with manual dispatch

## Manual Workflow Dispatch

Run workflows manually:

```bash
# Using GitHub CLI
gh workflow run fastapi-backend.yml
gh workflow run streamlit-frontend.yml

# Or via GitHub UI
# Actions tab → Select workflow → Run workflow
```

## Monitoring Workflows

### GitHub UI

- **Actions tab**: https://github.com/YOUR_ORG/genai-app-python/actions
- **Per workflow**: Click workflow name
- **Per run**: Click run for details

### GitHub CLI

```bash
# List recent runs
gh run list

# View specific run
gh run view RUN_ID

# Watch current run
gh run watch

# View logs
gh run view RUN_ID --log
```

### Status Badges

Add to README.md:

```markdown
![Backend CI](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/fastapi-backend.yml/badge.svg)
![ADK Python CI](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/adk-python.yml/badge.svg)
![Streamlit Frontend CI](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/streamlit-frontend.yml/badge.svg)
![Next.js Frontend CI](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/nextjs-frontend.yml/badge.svg)
![Code Quality](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/code-quality.yml/badge.svg)
```

## Workflow Dependencies

### Sequential Deployment

If frontend depends on backend URL:

```yaml
# frontend workflow
needs: [lint, build]
if: github.ref == 'refs/heads/main'

steps:
  - name: Get Backend URL
    run: |
      BACKEND_URL=$(gcloud run services describe genai-fastapi-backend ...)
```

### Parallel Deployment

Both services can deploy in parallel (current setup).

## Cost Optimization

### Workflow Caching

Already configured:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pypoetry
    key: poetry-${{ hashFiles('**/poetry.lock') }}
```

### Matrix Strategy

Test multiple versions efficiently:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
```

## Troubleshooting

### Workflow Not Triggering

**Check:**
- File path matches filter
- Syntax is valid
- Branch not ignored

**Test:**
```bash
# Validate syntax
yamllint .github/workflows/fastapi-backend.yml

# Check what would trigger
gh workflow view fastapi-backend.yml
```

### Permission Denied

**Check:**
- Workload Identity setup complete
- Service account has required roles
- GitHub secrets configured

**Fix:**
```bash
./setup-workload-identity.sh
```

## All Services Implemented ✅

All planned services now have CI/CD workflows:
- ✅ FastAPI Backend (Vote Extraction)
- ✅ ADK Python Service (Multi-Agent Content Creation)
- ✅ Streamlit Frontend
- ✅ Next.js Frontend

Each service has:
- Development workflow (main branch) → auto-deploy to dev
- Production workflow (prod branch) → tagged revision for manual traffic shifting

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workload Identity Setup](../../docs/deployment/workload-identity-federation.md)
- [Quick Start Guide](../../GITHUB_ACTIONS_QUICKSTART.md)

---

**Workflows**: 9 (4 services × 2 environments + code quality)
**Services**: FastAPI Backend, ADK Python, Streamlit Frontend, Next.js Frontend
**Path-based**: ✅ Only affected services run
**Secure**: ✅ Workload Identity (no keys)
**Ready**: ✅ Add secrets and push to deploy!
