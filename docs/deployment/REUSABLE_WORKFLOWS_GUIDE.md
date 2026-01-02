# GitHub Actions Reusable Workflows Guide

## 📋 Overview

This project uses **reusable workflows** to eliminate duplication and simplify maintenance of CI/CD pipelines. Reusable workflows are like functions - they can be called from other workflows with different parameters.

---

## 🏗️ Architecture

### Reusable Workflow Templates (Building Blocks)

```
.github/workflows/
├── _reusable-python-lint.yml      # Python linting (Black + Ruff)
├── _reusable-nodejs-lint.yml      # Node.js linting (ESLint + TypeScript + Prettier)
└── _reusable-cloudrun-deploy.yml  # Cloud Run deployment (Docker + gcloud)
```

**Naming Convention:** Prefix with `_` to indicate reusable templates

### Caller Workflows (Production - Using Reusables)

```
.github/workflows/
├── nextjs-frontend-prod-v2.yml       # ✨ NEW: Uses reusable workflows
├── fastapi-backend-prod-v2.yml       # ✨ NEW: Uses reusable workflows
└── adk-python-prod-v2.yml            # ✨ NEW: Uses reusable workflows
```

### Original Workflows (Still Active)

```
.github/workflows/
├── nextjs-frontend.yml               # Dev - no linting
├── nextjs-frontend-prod.yml          # Prod - full implementation
├── fastapi-backend.yml               # Dev - no linting
├── fastapi-backend-prod.yml          # Prod - full implementation
├── adk-python.yml                    # Dev - no linting
└── adk-python-prod.yml               # Prod - full implementation
```

---

## 🔧 Reusable Workflows Reference

### 1. Python Lint (`_reusable-python-lint.yml`)

**Purpose:** Run Black and Ruff linting on Python code

**Inputs:**
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `working_directory` | ✅ Yes | - | Working directory for the service |
| `python_version` | No | `'3.11'` | Python version |
| `run_black` | No | `true` | Run Black formatter check |
| `run_ruff` | No | `true` | Run Ruff linter |
| `black_path` | No | `'.'` | Path for Black to check |
| `ruff_path` | No | `'.'` | Path for Ruff to check |
| `sync_extras` | No | `'--all-extras'` | uv sync flags |

**Example Usage:**
```yaml
jobs:
  lint:
    uses: ./.github/workflows/_reusable-python-lint.yml
    with:
      working_directory: 'services/fastapi-backend'
      python_version: '3.11'
      black_path: 'app/'
      ruff_path: 'app/'
```

---

### 2. Node.js Lint (`_reusable-nodejs-lint.yml`)

**Purpose:** Run ESLint, TypeScript, Prettier, and build checks

**Inputs:**
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `working_directory` | ✅ Yes | - | Working directory for the service |
| `node_version` | No | `'20'` | Node.js version |
| `run_eslint` | No | `true` | Run ESLint |
| `run_typecheck` | No | `true` | Run TypeScript type checking |
| `run_prettier` | No | `true` | Run Prettier formatting check |
| `run_build` | No | `true` | Run build verification |
| `build_env_vars` | No | `'{}'` | Environment variables for build (JSON) |

**Example Usage:**
```yaml
jobs:
  lint:
    uses: ./.github/workflows/_reusable-nodejs-lint.yml
    with:
      working_directory: 'frontend/nextjs'
      node_version: '20'
      run_eslint: true
      run_typecheck: true
      run_prettier: true
      run_build: true
```

---

### 3. Cloud Run Deploy (`_reusable-cloudrun-deploy.yml`)

**Purpose:** Build Docker image and deploy to Google Cloud Run

**Inputs:**
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `service_name` | ✅ Yes | - | Cloud Run service name |
| `dockerfile_path` | ✅ Yes | - | Path to Dockerfile |
| `docker_context` | ✅ Yes | - | Docker build context directory |
| `region` | No | `'us-central1'` | GCP region |
| `deployment_tag` | No | `''` | Cloud Run revision tag |
| `no_traffic` | No | `false` | Deploy with --no-traffic |
| `environment` | No | `'dev'` | Environment (dev/prod) |
| `memory` | No | `'1Gi'` | Memory allocation |
| `cpu` | No | `'1'` | CPU allocation |
| `timeout` | No | `'300'` | Request timeout (seconds) |
| `max_instances` | No | `'10'` | Maximum instances |
| `min_instances` | No | `'0'` | Minimum instances |
| `port` | No | `'8000'` | Container port |
| `build_args` | No | `''` | Docker build arguments (multi-line) |
| `env_vars` | No | `''` | Environment variables (multi-line) |
| `secrets` | No | `''` | Secret Manager secrets (multi-line) |

**Required Secrets:**
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT_EMAIL`
- `GCP_PROJECT_ID`

**Optional Secrets:**
- `SLACK_WEBHOOK_URL`
- `DD_RUM_APPLICATION_ID`
- `DD_RUM_CLIENT_TOKEN`
- `API_KEY`

**Outputs:**
- `service_url`: Deployed Cloud Run service URL

**Example Usage:**
```yaml
jobs:
  deploy:
    uses: ./.github/workflows/_reusable-cloudrun-deploy.yml
    with:
      service_name: genai-fastapi-backend
      dockerfile_path: services/fastapi-backend/Dockerfile.cloudrun
      docker_context: services/fastapi-backend
      deployment_tag: prod
      no_traffic: true
      environment: prod
      memory: 2Gi
      cpu: '2'
      port: '8000'
      env_vars: |
        DD_ENV=prod
        DD_SERVICE=genai-fastapi-backend
        LOG_LEVEL=INFO
      secrets: |
        DD_API_KEY=dd-api-key:latest
        API_KEY=api-key:latest
    secrets:
      GCP_WORKLOAD_IDENTITY_PROVIDER: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
      GCP_SERVICE_ACCOUNT_EMAIL: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}
      GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
```

---

## 📝 Complete Example: Production Workflow

Here's a complete example showing how to combine reusable workflows:

```yaml
name: My Service Production Deploy

on:
  push:
    branches:
      - prod

env:
  SERVICE_NAME: my-service
  REGION: us-central1

jobs:
  # Step 1: Run linting
  lint:
    name: Quality Gate
    uses: ./.github/workflows/_reusable-python-lint.yml
    with:
      working_directory: 'services/my-service'
      python_version: '3.11'
      black_path: 'app/'
      ruff_path: 'app/'

  # Step 2: Deploy to Cloud Run
  deploy:
    name: Deploy to Production
    needs: [lint]  # Wait for linting to pass
    uses: ./.github/workflows/_reusable-cloudrun-deploy.yml
    with:
      service_name: my-service
      dockerfile_path: services/my-service/Dockerfile.cloudrun
      docker_context: services/my-service
      deployment_tag: prod
      no_traffic: true
      environment: prod
      memory: 2Gi
      cpu: '2'
      port: '8000'
      env_vars: |
        DD_ENV=prod
        DD_SERVICE=my-service
      secrets: |
        DD_API_KEY=dd-api-key:latest
    secrets:
      GCP_WORKLOAD_IDENTITY_PROVIDER: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
      GCP_SERVICE_ACCOUNT_EMAIL: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}
      GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
```

---

## 🎯 Benefits of Reusable Workflows

### Before (Duplicated Code)
```yaml
# In every workflow:
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install uv
  run: pip install uv

- name: Install dependencies
  run: uv sync --all-extras

- name: Run Black
  run: uv run black --check app/

- name: Run Ruff
  run: uv run ruff check app/
```

**Duplicated across 3+ workflows = maintenance nightmare! 😱**

### After (Reusable Workflows)
```yaml
jobs:
  lint:
    uses: ./.github/workflows/_reusable-python-lint.yml
    with:
      working_directory: 'services/my-service'
```

**One call = DRY principle! ✨**

---

## 🚀 Migration Strategy

### Phase 1: Create Reusables ✅ COMPLETE
- ✅ Created `_reusable-python-lint.yml`
- ✅ Created `_reusable-nodejs-lint.yml`
- ✅ Created `_reusable-cloudrun-deploy.yml`

### Phase 2: Create V2 Workflows ✅ COMPLETE
- ✅ Created `*-prod-v2.yml` workflows using reusables
- ✅ Tested alongside original workflows

### Phase 3: Validation (CURRENT)
- ⏳ Test v2 workflows in production
- ⏳ Verify all features work correctly
- ⏳ Compare performance with original workflows

### Phase 4: Cutover (FUTURE)
- ⏳ Rename `*-prod-v2.yml` to `*-prod.yml`
- ⏳ Archive original workflows
- ⏳ Update documentation

### Phase 5: Expand (FUTURE)
- ⏳ Create reusable workflows for dev deployments
- ⏳ Add more reusable components (testing, security scans)
- ⏳ Create reusable workflows for other services

---

## 📊 Comparison: Original vs Reusable

### Lines of Code

| Workflow | Original | Reusable | Reduction |
|----------|----------|----------|-----------|
| Frontend Prod | ~240 lines | ~120 lines | **50%** ⬇️ |
| Backend Prod | ~140 lines | ~70 lines | **50%** ⬇️ |
| ADK Prod | ~170 lines | ~75 lines | **56%** ⬇️ |

**Total reduction: ~300 lines of duplicated code!**

### Maintainability

| Aspect | Original | Reusable |
|--------|----------|----------|
| **Update linting** | 6 files | 1 file |
| **Update deployment** | 6 files | 1 file |
| **Add new service** | Copy 200+ lines | Call 2 workflows |
| **Consistency** | Manual | Automatic |

---

## 🔍 Testing Reusable Workflows

### Local Testing (Not Possible)
❌ Reusable workflows cannot be tested locally with `act` or similar tools

### Testing Strategy

1. **Create V2 versions** (don't replace originals)
2. **Test on non-prod branch** first
3. **Monitor deployment logs** carefully
4. **Compare results** with original workflows
5. **Gradually roll out** to production

### Validation Checklist

- [ ] Linting runs and catches errors
- [ ] Docker build succeeds
- [ ] Cloud Run deployment works
- [ ] Environment variables set correctly
- [ ] Secrets mounted properly
- [ ] Service URL returned correctly
- [ ] Slack notifications work
- [ ] Deployment tags applied correctly

---

## 🛠️ Customization

### Adding New Parameters

**Example: Add timeout for linting**

1. Update `_reusable-python-lint.yml`:
```yaml
inputs:
  timeout_minutes:
    description: 'Job timeout in minutes'
    required: false
    type: number
    default: 30

jobs:
  lint:
    timeout-minutes: ${{ inputs.timeout_minutes }}
```

2. Use in caller workflow:
```yaml
jobs:
  lint:
    uses: ./.github/workflows/_reusable-python-lint.yml
    with:
      working_directory: 'services/my-service'
      timeout_minutes: 15
```

### Adding New Reusable Workflow

**Example: Create testing workflow**

```yaml
# _reusable-python-test.yml
name: Reusable Python Test

on:
  workflow_call:
    inputs:
      working_directory:
        required: true
        type: string
      python_version:
        required: false
        type: string
        default: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working_directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python_version }}
      - run: pip install uv
      - run: uv sync --all-extras
      - run: uv run pytest
```

---

## 🎓 Best Practices

### 1. **Naming Convention**
- ✅ Prefix reusable workflows with `_`
- ✅ Use descriptive names: `_reusable-<purpose>.yml`
- ❌ Don't use generic names like `_common.yml`

### 2. **Input Design**
- ✅ Make commonly changed values configurable
- ✅ Provide sensible defaults
- ✅ Use clear descriptions
- ❌ Don't hardcode values that might change

### 3. **Secret Handling**
- ✅ Pass secrets explicitly from caller
- ✅ Make secrets optional when possible
- ❌ Don't reference secrets directly in reusable workflows

### 4. **Documentation**
- ✅ Document all inputs/outputs
- ✅ Provide usage examples
- ✅ Explain complex logic
- ❌ Don't assume users know your intentions

### 5. **Error Handling**
- ✅ Fail fast on errors
- ✅ Provide clear error messages
- ✅ Use conditions for optional steps
- ❌ Don't silently ignore failures

---

## 📚 Additional Resources

- [GitHub Docs: Reusing Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Best Practices for Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows#best-practices)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

## 🎉 Summary

**Reusable workflows provide:**
- ✅ **50%+ reduction** in code duplication
- ✅ **Single source of truth** for common tasks
- ✅ **Easier maintenance** - update once, apply everywhere
- ✅ **Consistency** across all services
- ✅ **Faster onboarding** - simple to add new services

**Trade-offs:**
- ❌ Slightly more complex to understand initially
- ❌ Cannot test locally
- ❌ Requires careful parameter design

**Overall verdict: Highly recommended for projects with 3+ similar workflows! 🚀**

