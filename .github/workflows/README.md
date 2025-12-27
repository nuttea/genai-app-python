# GitHub Actions Workflows

CI/CD workflows for automated testing and deployment.

## Workflow Structure

```
.github/workflows/
├── fastapi-backend.yml      # FastAPI Backend CI/CD
├── streamlit-frontend.yml   # Streamlit Frontend CI/CD
├── code-quality.yml         # Code quality checks (all components)
└── README.md               # This file
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

### 2. Streamlit Frontend (`streamlit-frontend.yml`)

**Triggers:**
- Push to `main`/`develop` → `frontend/streamlit/**`
- Pull requests → `frontend/streamlit/**`
- Manual dispatch

**Jobs:**
- Lint (Black, Ruff)
- Build (Docker image)
- Deploy (Cloud Run - main only)

**Service**: `genai-streamlit-frontend`

### 3. Code Quality (`code-quality.yml`)

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
- `fastapi-backend.yml` - FastAPI backend service
- `streamlit-frontend.yml` - Streamlit frontend service

### Future Services

When adding new services, follow this pattern:

```
services/
├── fastapi-backend/           → .github/workflows/fastapi-backend.yml
├── mcp-server/                → .github/workflows/mcp-server.yml
└── nextjs-frontend/           → .github/workflows/nextjs-frontend.yml

frontend/
├── streamlit/                 → .github/workflows/streamlit-frontend.yml
└── nextjs/                    → .github/workflows/nextjs-frontend.yml (alternative)
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

**streamlit-frontend.yml:**
```yaml
paths:
  - 'frontend/streamlit/**'
  - '.github/workflows/streamlit-frontend.yml'
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
![Frontend CI](https://github.com/YOUR_ORG/genai-app-python/actions/workflows/streamlit-frontend.yml/badge.svg)
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

## Future Services

### MCP Server (TypeScript)

Create `.github/workflows/mcp-server.yml`:

```yaml
name: MCP Server CI/CD

on:
  push:
    paths:
      - 'services/mcp-server/**'
      - '.github/workflows/mcp-server.yml'

jobs:
  test:
    # Node.js testing
  lint:
    # TypeScript linting
  build:
    # Docker build
  deploy:
    # Cloud Run deployment
```

### Next.js Frontend

Create `.github/workflows/nextjs-frontend.yml`:

```yaml
name: Next.js Frontend CI/CD

on:
  push:
    paths:
      - 'frontend/nextjs/**'
      - '.github/workflows/nextjs-frontend.yml'

jobs:
  test:
    # Next.js testing
  build:
    # Docker build
  deploy:
    # Cloud Run deployment
```

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workload Identity Setup](../../docs/deployment/workload-identity-federation.md)
- [Quick Start Guide](../../GITHUB_ACTIONS_QUICKSTART.md)

---

**Workflows**: 3 (1 per service + code quality)
**Path-based**: ✅ Only affected services run
**Secure**: ✅ Workload Identity (no keys)
**Ready**: ✅ Add secrets and push to deploy!
