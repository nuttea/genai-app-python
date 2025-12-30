# ADK Service Rename & Workflow Setup - Complete ✅

This document summarizes the renaming of the ADK service and creation of CI/CD workflows.

## 📝 Changes Summary

### 1. Service Renamed: `adk-content-creator` → `adk-python`

**Directory Changes:**
- ✅ `services/adk-content-creator/` → `services/adk-python/`
- ✅ `services/adk-python/agents/` → `services/adk-python/content-creator-agent/`

**Why?**
- More generic service name for future ADK agents
- Clear separation of agent logic (content-creator-agent) from service infrastructure

### 2. Docker Compose Updates

**File**: `docker-compose.yml`

**Changes:**
- Service name: `content-creator` → `adk-python`
- Container name: `genai-content-creator` → `genai-adk-python`
- Build context: `./services/adk-content-creator` → `./services/adk-python`
- DD_SERVICE: `adk-content-creator` → `adk-python`
- Volume mounts updated to reflect new paths
- Service references updated in other services (nextjs-frontend depends_on)

**Environment Variables:**
```yaml
- DD_SERVICE=adk-python  # Updated
- CONTENT_CREATOR_API_URL=http://adk-python:8002  # Updated in nextjs
```

### 3. Code Updates

**File**: `services/adk-python/main_adk.py`

**Changes:**
- Default DD_SERVICE: `adk-content-creator` → `adk-python`
- LLMObs ml_app: `datadog-content-creator` → `adk-python-content-creator`
- Import statement: `from agents.agent` → `from content_creator_agent.agent`
- Log messages updated to "ADK Python Service"

**Files**: `services/adk-python/content-creator-agent/*.py`

**Changes:**
- All imports updated: `from agents.` → `from content_creator_agent.`
- Applied recursively to all Python files in the agent directory

### 4. GitHub Actions Workflows Created

**File**: `.github/workflows/adk-python.yml`

**Triggers:**
- Push to `main`/`develop` → `services/adk-python/**`
- Pull requests
- Manual dispatch

**Jobs:**
1. **Lint**: Black (check only), Ruff
2. **Deploy**: Build Docker, Push to GCR, Deploy to Cloud Run (dev)

**Service**: `genai-adk-python`
**Port**: 8002
**Resources**: 2Gi RAM, 2 CPU
**Timeout**: 600s (10 minutes for LLM operations)

**Environment Variables (Cloud Run):**
- GOOGLE_CLOUD_PROJECT (from secrets)
- GOOGLE_GENAI_USE_VERTEXAI=True
- VERTEX_AI_LOCATION=us-central1
- DEFAULT_MODEL=gemini-2.5-flash
- DD_SERVICE=genai-adk-python
- DD_ENV=dev
- DD_VERSION={github.sha}
- DD_TRACE_ENABLED=true
- DD_API_KEY (from Secret Manager)

**Smoke Tests:**
- `/health` endpoint check
- `/list-apps` endpoint check (ADK-specific)

---

**File**: `.github/workflows/adk-python-prod.yml`

**Triggers:**
- Push to `prod` branch

**Jobs:**
1. **Deploy**: Build Docker, Push to GCR, Deploy to Cloud Run with `prod` tag (no-traffic)

**Environment**: `prod` (DD_ENV=prod)
**Min Instances**: 1 (high availability for production)

**Traffic Shifting:**
Production deployments use `--tag prod --no-traffic`, requiring manual traffic shift:

```bash
gcloud run services update-traffic genai-adk-python \
  --region us-central1 \
  --to-tags prod=100
```

### 5. Documentation Updates

**File**: `.github/workflows/README.md`

**Updates:**
- Added `adk-python.yml` and `adk-python-prod.yml` to workflow structure
- Added ADK Python Service section (Section 2) with features list
- Updated service counts: 3 → 4 services
- Updated workflow counts: 7 → 9 workflows
- Added path filters example for adk-python
- Added status badge for ADK Python CI
- Updated "Future Services" section to show all services implemented

## 🚀 How to Use

### Local Development

```bash
# Start services with new names
docker-compose up -d adk-python

# Check logs
docker logs genai-adk-python --tail 100

# Verify agent discovery
curl http://localhost:8002/list-apps

# Test health
curl http://localhost:8002/health
```

### Deploying to Cloud Run

**Development (main branch):**
```bash
# Commit changes to adk-python service
git add services/adk-python/
git commit -m "feat: Update ADK Python service"
git push origin main

# Workflow automatically:
# 1. Lints code
# 2. Builds Docker image
# 3. Deploys to Cloud Run (dev)
```

**Production (prod branch):**
```bash
# Merge to production
git checkout prod
git merge main
git push origin prod

# Workflow creates tagged revision
# Manual traffic shift required:
gcloud run services update-traffic genai-adk-python \
  --region us-central1 \
  --to-tags prod=100
```

### Manual Workflow Trigger

```bash
# Using GitHub CLI
gh workflow run adk-python.yml
gh workflow run adk-python-prod.yml

# Or via GitHub UI:
# Actions tab → Select workflow → Run workflow
```

## 📊 Service Architecture

```
GenAI App Platform
├── services/
│   ├── fastapi-backend/          → Vote extraction backend
│   │   └── .github/workflows/fastapi-backend.yml
│   │       .github/workflows/fastapi-backend-prod.yml
│   └── adk-python/               → ADK multi-agent service
│       ├── content-creator-agent/  → Agent logic
│       │   ├── agent.py           (main orchestrator)
│       │   ├── loop_agents.py     (self-correcting agents)
│       │   ├── sub_agents/        (specialized workers)
│       │   ├── tools.py           (custom functions)
│       │   └── validation_tools.py
│       ├── main_adk.py            → FastAPI app with ADK
│       └── .github/workflows/adk-python.yml
│           .github/workflows/adk-python-prod.yml
│
└── frontend/
    ├── streamlit/                → Classic Streamlit UI
    │   └── .github/workflows/streamlit-frontend.yml
    │       .github/workflows/streamlit-frontend-prod.yml
    └── nextjs/                   → Modern Next.js UI
        └── .github/workflows/nextjs-frontend.yml
            .github/workflows/nextjs-frontend-prod.yml
```

## 🎯 Key Features

**ADK Python Service:**
- ✅ Google ADK Multi-Agent Framework
- ✅ Self-correcting loop agents (blog planner, writer, video script writer)
- ✅ Specialized sub-agents (editor, social media)
- ✅ Datadog LLM Observability (auto-instrumentation)
- ✅ Vertex AI / Gemini 2.5 Flash integration
- ✅ Media file analysis (images, videos)
- ✅ Content export (Markdown, JSON)
- ✅ Session management (SQLite or Cloud SQL)

## 📚 Related Documentation

- **Service Architecture**: `services/adk-python/ARCHITECTURE_SIMPLIFIED.md`
- **ADK Implementation**: `services/adk-python/FULL_ADK_ACTIVATED.md`
- **Agent Architecture**: `services/adk-python/AGENT_ARCHITECTURE.md`
- **Datadog Setup**: `services/adk-python/DATADOG_LLMOBS_SETUP.md`
- **Workflow Guide**: `.github/workflows/README.md`
- **Next.js Workflows**: `NEXTJS_WORKFLOWS_SETUP.md`

## 🔍 Verification

After deployment, verify the service:

```bash
# Get service URL
gcloud run services describe genai-adk-python \
  --region us-central1 \
  --format 'value(status.url)'

# Test endpoints
SERVICE_URL="https://genai-adk-python-xxx.run.app"

curl "${SERVICE_URL}/health"
# Expected: {"status":"healthy","service":"adk-python",...}

curl "${SERVICE_URL}/list-apps"
# Expected: Array of agent apps

curl "${SERVICE_URL}/"
# Expected: Service info with ADK details
```

## 🐛 Troubleshooting

### Issue: Import errors after rename

**Symptom**: `ModuleNotFoundError: No module named 'agents'`

**Fix**: Already applied! All imports updated from `agents.` to `content_creator_agent.`

```bash
# If you see this error, run:
cd services/adk-python/content-creator-agent
find . -name "*.py" -exec sed -i '' 's/from agents\./from content_creator_agent./g' {} \;
```

### Issue: Docker container can't find agent directory

**Symptom**: "Agent directory not found" in logs

**Fix**: Already applied! Volume mount updated in docker-compose.yml:

```yaml
- ./services/adk-python/content-creator-agent:/app/content-creator-agent:ro
```

### Issue: Next.js can't connect to content creator

**Symptom**: Connection refused or 404 errors

**Fix**: Already applied! URL updated in docker-compose.yml:

```yaml
- CONTENT_CREATOR_API_URL=http://adk-python:8002
```

## ✅ Checklist

All tasks completed:

- [x] Rename service directory: `adk-content-creator` → `adk-python`
- [x] Rename agents directory: `agents` → `content-creator-agent`
- [x] Update docker-compose.yml service references
- [x] Update main_adk.py imports and service names
- [x] Update all Python imports in agent files
- [x] Create GitHub Actions workflow (dev)
- [x] Create GitHub Actions workflow (prod)
- [x] Update workflow documentation

## 🚦 Status

**Status**: ✅ Complete
**Services**: 4 (FastAPI Backend, ADK Python, Streamlit, Next.js)
**Workflows**: 9 (4 services × 2 environments + code quality)
**Ready**: Yes - commit and push to deploy!

---

**Created**: $(date +%Y-%m-%d)
**Service**: `genai-adk-python`
**Port**: 8002
**Agent**: `content-creator-agent`
