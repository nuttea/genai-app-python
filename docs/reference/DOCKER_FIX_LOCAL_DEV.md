# Docker Local Development Fix

## Issue

The Streamlit frontend container was failing to start with this error:
```
Error response from daemon: failed to create task for container: failed to create shim task: 
OCI runtime create failed: runc create failed: unable to start container process: 
error during container init: exec: "/app/datadog-init": stat /app/datadog-init: 
no such file or directory: unknown
```

## Root Cause

The Dockerfiles for both frontend and backend are optimized for **Cloud Run deployment** with Datadog serverless-init. This setup uses:
- `ENTRYPOINT ["/app/datadog-init"]` - Datadog serverless wrapper
- `CMD ["/dd_tracer/python/bin/ddtrace-run", ...]` - Datadog APM instrumentation

While this works perfectly on Cloud Run, it can cause issues in local Docker development.

## Solution

Override the `entrypoint` and `command` in `docker-compose.yml` for local development:

### Backend
```yaml
fastapi-backend:
  # Override entrypoint for local development (Cloud Run uses datadog-init)
  entrypoint: []
  command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Frontend
```yaml
streamlit-frontend:
  # Override entrypoint for local development (Cloud Run uses datadog-init)
  entrypoint: []
  command: ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Benefits

✅ **Local Development**: Works without Datadog serverless-init  
✅ **Hot Reload**: Backend has `--reload` flag for development  
✅ **Cloud Run**: Dockerfiles unchanged, optimized for production  
✅ **Consistent**: Same approach for both services  
✅ **No Tracing Overhead**: Lighter weight for local dev  

## Usage

### 1. Rebuild Containers

```bash
# Stop existing containers
docker-compose down -v

# Rebuild with the fix
docker-compose up -d --build
```

### 2. Verify Containers

```bash
# Check status
docker-compose ps

# Both should show "Up" and "healthy"
# - genai-fastapi-backend
# - genai-streamlit-frontend
```

### 3. Test Services

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend (open in browser)
open http://localhost:8501
```

## Datadog Observability

### Local Development
- **APM Tracing**: Disabled (DD_TRACE_ENABLED=0 for frontend)
- **RUM**: Still works (browser-side, not affected)
- **Logs**: Optional (can still send if DD_API_KEY set)

### Cloud Run Deployment
- **Full APM**: Enabled with serverless-init
- **Distributed Tracing**: Backend → Vertex AI
- **LLMObs**: Complete observability
- **Source Code Integration**: Working

## Alternative Approaches

### Option 1: Separate Local Dockerfile (Not Recommended)
Create `Dockerfile.local` without serverless-init.
- ❌ Maintains two Dockerfiles
- ❌ Risk of drift between local and production

### Option 2: Conditional Setup (Complex)
Use build args to conditionally include serverless-init.
- ❌ More complex Dockerfile
- ❌ Build-time vs runtime considerations

### Option 3: docker-compose Override (✅ Recommended)
Override entrypoint/command in docker-compose.
- ✅ Single Dockerfile
- ✅ Production-optimized
- ✅ Simple override for local dev
- ✅ Clear separation of concerns

## Technical Details

### Why Serverless-Init Fails Locally

The serverless-init binary (`/app/datadog-init`) is designed for serverless environments like:
- Google Cloud Run
- AWS Fargate
- Azure Container Instances

It expects specific runtime conditions that may not be met in local Docker:
- Process lifecycle management
- Signal handling
- Log forwarding
- Metrics collection

### What Gets Disabled Locally

By skipping serverless-init in local dev:
- ❌ APM automatic instrumentation (can be added back manually if needed)
- ❌ Serverless-specific metrics
- ✅ RUM still works (browser-based)
- ✅ Logs still work (stdout)
- ✅ Application functions normally

### Re-enabling APM for Local Dev (Optional)

If you want APM tracing in local dev:

```yaml
# docker-compose.yml
streamlit-frontend:
  command: [
    "ddtrace-run",  # Add ddtrace-run wrapper
    "streamlit", "run", "app.py",
    "--server.port=8501",
    "--server.address=0.0.0.0"
  ]
  environment:
    - DD_TRACE_ENABLED=1  # Enable tracing
    - DD_API_KEY=${DD_API_KEY}  # Must provide API key
```

Note: Requires DD_API_KEY to be set.

## Summary

| Environment | Setup | APM | RUM | Logs |
|------------|-------|-----|-----|------|
| **Local Dev** | docker-compose override | Optional | ✅ | ✅ |
| **Cloud Run** | Full serverless-init | ✅ | ✅ | ✅ |

---

**The fix is now applied! Containers should start successfully.** 🚀

