# 🐕 Datadog APM - Quick Start

Enable complete observability for your GenAI application in 2 minutes!

## What You Get

✅ **APM (Application Performance Monitoring)**
- Request tracing (every API call)
- Performance metrics (latency, throughput)
- Error tracking with stack traces
- Service map and dependencies

✅ **LLM Observability**
- Track all Gemini API calls
- Token usage and costs
- Model performance
- Prompt/response monitoring

✅ **Log Correlation**
- Logs linked to traces
- Easy debugging
- Full request context

## 2-Minute Setup

### 1. Get API Key

Get your Datadog API key from:
https://app.datadoghq.com/organization-settings/api-keys

### 2. Local Development

```bash
# Add to .env file
cat >> .env <<EOF
DD_API_KEY=your-datadog-api-key-here
DD_SITE=datadoghq.com
DD_SERVICE=genai-fastapi-backend
DD_ENV=development
DD_VERSION=0.1.0
DD_LLMOBS_ML_APP=genai-vote-extractor
DD_LLMOBS_ENABLED=1
EOF

# Restart services
docker-compose down
docker-compose up -d
```

### 3. Cloud Run Deployment

**Option A: Setup Secrets (Recommended)**

```bash
# Set your API key
export DD_API_KEY=your-datadog-api-key-here

# Store in Secret Manager
cd infra/cloud-run
./setup-datadog-secrets.sh

# Deploy
./deploy-backend.sh
```

**Option B: Direct Environment Variable**

```bash
export DD_API_KEY=your-datadog-api-key-here
export DD_SERVICE=genai-fastapi-backend
export DD_ENV=production
export DD_VERSION=1.0.0
export DD_LLMOBS_ML_APP=genai-vote-extractor
export DD_LLMOBS_ENABLED=1

cd infra/cloud-run
./deploy-backend.sh
```

## Verify It's Working

### 1. Generate Traffic

```bash
# Local
curl http://localhost:8000/health

# Cloud Run
curl https://your-service.run.app/health
```

### 2. Check Datadog

Within 1-2 minutes, visit:

- **APM**: https://app.datadoghq.com/apm/traces
- **LLM**: https://app.datadoghq.com/llm/traces
- **Logs**: https://app.datadoghq.com/logs

Filter by `service:genai-fastapi-backend`

## Environment Variables

### Required

```bash
DD_API_KEY=your-api-key          # Your Datadog API key
DD_SERVICE=genai-fastapi-backend # Service name
DD_ENV=production                # Environment (dev/staging/prod)
DD_VERSION=1.0.0                 # Version/git SHA
```

### Optional (but recommended)

```bash
DD_SITE=datadoghq.com           # Datadog site (US1)
DD_LOGS_INJECTION=true          # Link logs to traces
DD_TRACE_SAMPLE_RATE=1.0        # Sample 100% of traces
DD_PROFILING_ENABLED=true       # Enable profiling

# LLM Observability
DD_LLMOBS_ML_APP=your-ml-app    # ML app name
DD_LLMOBS_ENABLED=1             # Enable LLMObs
```

## What Gets Traced

✅ **Automatic (via ddtrace-run)**
- All FastAPI endpoints
- HTTP client calls (httpx)
- Google GenAI API calls
- Database queries (if any)

✅ **Custom (in vote_extraction_service.py)**
- LLM model calls
- Token usage
- Extraction results

## Troubleshooting

### No traces in Datadog

```bash
# Check env vars are set
docker-compose exec fastapi-backend env | grep DD_

# Check logs for Datadog startup
docker-compose logs fastapi-backend | grep -i datadog

# Enable debug mode
export DD_TRACE_DEBUG=true
docker-compose restart fastapi-backend
```

### Traces not linked to logs

```bash
# Ensure logs injection is enabled
export DD_LOGS_INJECTION=true
docker-compose restart fastapi-backend
```

### High costs

```bash
# Reduce sampling
export DD_TRACE_SAMPLE_RATE=0.1  # 10% sampling
docker-compose restart fastapi-backend
```

## Quick Commands

```bash
# Local with Datadog
docker-compose up -d

# Deploy to Cloud Run with Datadog
cd infra/cloud-run
export DD_API_KEY=your-key
./deploy-backend.sh

# Setup Secret Manager
./setup-datadog-secrets.sh

# View traces in browser
open https://app.datadoghq.com/apm/traces?query=service:genai-fastapi-backend
```

## Cost Estimates

**APM**: ~$31/host/month + $0.002/span  
**LLMObs**: Based on token volume  
**Free Trial**: 14 days full features  

Most small applications stay under $50/month.

## Full Documentation

- 📖 [DATADOG_SETUP.md](docs/DATADOG_SETUP.md) - Complete setup guide
- 🚀 [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md) - Cloud Run deployment
- 📋 [PROJECT_PLAN.md](PROJECT_PLAN.md) - Architecture overview

---

**Need help?** See [docs/DATADOG_SETUP.md](docs/DATADOG_SETUP.md) for detailed troubleshooting.

