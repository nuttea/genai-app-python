# Datadog Trace Agent Configuration

## Overview

Configured all services to use the Datadog trace agent with custom port configuration for local development.

## Environment Variables

The following environment variables are now loaded from the root `.env` file and applied to all services:

```bash
DD_TRACE_AGENT_URL=http://localhost:8136
DD_AGENT_HOST=localhost
DD_TRACE_AGENT_PORT=8136
```

## Services Configured

### 1. FastAPI Backend (`genai-fastapi-backend`)
- Service: `genai-fastapi-backend`
- Port: 8000
- DD Trace Agent: ✅ Configured

### 2. Streamlit Frontend (`genai-streamlit-frontend`)
- Service: `genai-streamlit-frontend`
- Port: 8501
- DD Trace Agent: ✅ Configured

### 3. Content Creator (`adk-content-creator`)
- Service: `adk-content-creator`
- Port: 8002
- DD Trace Agent: ✅ Configured

### 4. Next.js Frontend (`nextjs-frontend`)
- Service: `nextjs-frontend`
- Port: 3000
- DD RUM: ✅ Configured (frontend monitoring)

## Configuration Files Updated

### 1. `docker-compose.yml`

Added to all Python services (backend, streamlit, content-creator):

```yaml
environment:
  # ... existing DD config ...
  # Datadog Trace Agent Configuration
  - DD_TRACE_AGENT_URL=${DD_TRACE_AGENT_URL:-http://localhost:8136}
  - DD_AGENT_HOST=${DD_AGENT_HOST:-localhost}
  - DD_TRACE_AGENT_PORT=${DD_TRACE_AGENT_PORT:-8136}
```

### 2. `.env.example`

Created/updated with DD trace agent configuration:

```bash
# Datadog Trace Agent Configuration (for local development)
DD_TRACE_AGENT_URL=http://localhost:8136
DD_AGENT_HOST=localhost
DD_TRACE_AGENT_PORT=8136
```

## How It Works

### Local Development

1. **Datadog Agent** runs on custom port `8136` (instead of default `8126`)
2. **All services** send traces to `http://localhost:8136`
3. **Environment variables** are loaded from root `.env` file
4. **Docker Compose** passes these to all containers

### Environment Variable Precedence

```
1. .env file (root directory)
   ↓
2. docker-compose.yml (with ${VAR:-default})
   ↓
3. Container environment
```

## Verification

### Check Environment Variables in Container

```bash
# Check Content Creator
docker exec genai-content-creator env | grep DD_

# Check FastAPI Backend
docker exec genai-fastapi-backend env | grep DD_

# Check Streamlit Frontend
docker exec genai-streamlit-frontend env | grep DD_
```

### Expected Output

```bash
DD_TRACE_AGENT_URL=http://localhost:8136
DD_AGENT_HOST=localhost
DD_TRACE_AGENT_PORT=8136
DD_SERVICE=adk-content-creator
DD_ENV=development
DD_VERSION=0.1.0
DD_TRACE_ENABLED=1
DD_CODE_ORIGIN_FOR_SPANS_ENABLED=true
# ... other DD vars ...
```

### Check Trace Agent Connection

```bash
# View logs for trace agent connection attempts
docker logs genai-content-creator --tail 50 | grep -i "datadog\|trace\|agent"
```

## Troubleshooting

### Issue: Traces not appearing in Datadog

**Check 1: Verify environment variables**
```bash
docker exec genai-content-creator env | grep DD_TRACE_AGENT
```

**Check 2: Verify Datadog Agent is running**
```bash
# Check if agent is listening on port 8136
netstat -an | grep 8136
# or
lsof -i :8136
```

**Check 3: Check container logs**
```bash
docker logs genai-content-creator --tail 100 | grep -E "DD_|trace|agent"
```

### Issue: Connection refused to localhost:8126

This means the service is trying to connect to the default port instead of 8136.

**Solution**: Ensure `.env` file in root directory contains:
```bash
DD_TRACE_AGENT_URL=http://localhost:8136
DD_AGENT_HOST=localhost
DD_TRACE_AGENT_PORT=8136
```

Then restart services:
```bash
docker-compose restart
```

### Issue: Environment variables not loading

**Solution 1**: Check `.env` file location
```bash
# Should be in project root
ls -la .env
```

**Solution 2**: Restart Docker Compose
```bash
docker-compose down
docker-compose up -d
```

## Production Deployment

### Cloud Run

For Cloud Run deployments, set these as **environment variables** in the Cloud Run service configuration:

```bash
# Via gcloud CLI
gcloud run services update adk-content-creator \
  --set-env-vars="DD_TRACE_AGENT_URL=http://localhost:8126" \
  --set-env-vars="DD_AGENT_HOST=localhost" \
  --set-env-vars="DD_TRACE_AGENT_PORT=8126"
```

**Note**: Cloud Run uses the default port `8126` when using Datadog serverless-init.

### GKE

For GKE deployments, add to your Kubernetes deployment manifest:

```yaml
env:
  - name: DD_TRACE_AGENT_URL
    value: "http://datadog-agent.datadog:8126"
  - name: DD_AGENT_HOST
    value: "datadog-agent.datadog"
  - name: DD_TRACE_AGENT_PORT
    value: "8126"
```

## Testing

### Test Trace Generation

```bash
# Generate a blog post (creates traces)
curl -X POST http://localhost:8002/api/v1/generate/blog-post \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Trace",
    "description": "Testing Datadog trace agent",
    "style": "professional",
    "target_audience": "developers"
  }'

# Check logs for trace submission
docker logs genai-content-creator --tail 50 | grep -i trace
```

### Verify in Datadog UI

1. Go to **APM → Traces**
2. Filter by service: `adk-content-creator`
3. Look for traces from the test request
4. Verify spans show up with correct timing

## Summary

✅ **Configured**: All services now use custom DD trace agent port (8136)  
✅ **Environment Variables**: Loaded from root `.env` file  
✅ **Docker Compose**: Updated for all Python services  
✅ **Documentation**: Created `.env.example` with DD config  
✅ **Verified**: Environment variables present in containers  

## Next Steps

1. ✅ Create/update `.env` file in project root with DD trace agent config
2. ✅ Restart services: `docker-compose restart`
3. 🔜 Verify traces appear in Datadog UI
4. 🔜 Test with real Datadog Agent running on port 8136

---

**Status**: ✅ Configuration Complete  
**Date**: December 30, 2025  
**Services**: All Python services configured

