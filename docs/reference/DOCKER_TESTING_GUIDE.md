# 🐳 Docker Testing Guide - Content Creator

Quick reference for testing the Datadog Content Creator service locally with Docker Compose.

---

## 🚀 Quick Start

### 1. Build All Images
```bash
make docker-build
```

### 2. Start All Services
```bash
make docker-up
```

### 3. Check Status
```bash
make docker-ps
```

### 4. View Logs
```bash
# All services
make docker-logs

# Specific service
make docker-logs-content-creator
make docker-logs-backend
make docker-logs-frontend
```

### 5. Stop Services
```bash
make docker-down
```

---

## 🎯 Service Endpoints

Once services are running:

| Service | Port | Health Check | API Docs |
|---------|------|--------------|----------|
| **FastAPI Backend** | 8000 | http://localhost:8000/health | http://localhost:8000/docs |
| **Content Creator** | 8002 | http://localhost:8002/health | http://localhost:8002/info |
| **Streamlit Frontend** | 8501 | http://localhost:8501/_stcore/health | http://localhost:8501 |

---

## 📋 Common Commands

### Build Commands

```bash
# Build all images
make docker-build

# Build specific service
make docker-build-backend
make docker-build-frontend
make docker-build-content-creator
```

### Start Commands

```bash
# Start all services
make docker-up

# Start only backend services (FastAPI + Content Creator)
make docker-up-backend

# Start all services including frontend
make docker-up-full
```

### Stop Commands

```bash
# Stop all services
make docker-down

# Clean up everything (containers, volumes, networks)
make docker-clean
```

### Log Commands

```bash
# View all logs (follow mode)
make docker-logs

# View specific service logs
make docker-logs-backend
make docker-logs-frontend
make docker-logs-content-creator
```

### Debug Commands

```bash
# Open shell in container
make docker-shell-backend
make docker-shell-frontend
make docker-shell-content-creator

# Show running containers
make docker-ps

# Show resource usage
make docker-stats

# Restart specific service
make docker-restart-content-creator
```

---

## 🧪 Testing the Content Creator

### 1. Check Health
```bash
curl http://localhost:8002/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "adk-content-creator",
  "version": "0.1.0"
}
```

### 2. Get Service Info
```bash
curl http://localhost:8002/info
```

**Expected Response:**
```json
{
  "service": "adk-content-creator",
  "version": "0.1.0",
  "environment": "development",
  "llm_model": "gemini-2.5-flash",
  "capabilities": [
    "blog_post_generation",
    "video_script_generation",
    "social_media_posts",
    "video_processing",
    "image_analysis"
  ],
  "supported_inputs": [
    "text",
    "markdown",
    "video (mp4, mov, avi)",
    "images (png, jpg, jpeg)"
  ],
  "supported_outputs": [
    "blog_post (markdown, html)",
    "video_script (60s)",
    "social_media (linkedin, twitter, instagram)"
  ]
}
```

### 3. Check Root Endpoint
```bash
curl http://localhost:8002/
```

**Expected Response:**
```json
{
  "service": "adk-content-creator",
  "version": "0.1.0",
  "status": "running",
  "environment": "development"
}
```

---

## 🔍 Troubleshooting

### Services Won't Start

**Check logs:**
```bash
make docker-logs-content-creator
```

**Common issues:**
- GCP credentials not mounted: Check `$HOME/.config/gcloud` exists
- Port already in use: Stop conflicting services or change ports
- Build failed: Run `make docker-build-content-creator` and check for errors

### Cannot Connect to Service

**Check if service is running:**
```bash
make docker-ps
```

**Check health:**
```bash
curl http://localhost:8002/health
```

**Restart service:**
```bash
make docker-restart-content-creator
```

### Hot Reload Not Working

**Verify volume mounts in docker-compose.yml:**
```yaml
volumes:
  - ./services/adk-content-creator/app:/app/app:ro
```

**Restart service:**
```bash
make docker-restart-content-creator
```

### Out of Memory / High CPU

**Check resource usage:**
```bash
make docker-stats
```

**Solution:**
- Increase Docker memory limit in Docker Desktop
- Stop unused services
- Use `make docker-up-backend` instead of `make docker-up`

---

## 🛠️ Development Workflow

### Typical Development Cycle

1. **Make code changes** in `services/adk-content-creator/app/`

2. **Hot reload** automatically picks up changes (no rebuild needed)

3. **Test changes:**
   ```bash
   curl http://localhost:8002/health
   ```

4. **View logs** to debug:
   ```bash
   make docker-logs-content-creator
   ```

5. **If Dockerfile changes**, rebuild:
   ```bash
   make docker-build-content-creator
   make docker-restart-content-creator
   ```

### Testing API Changes

1. **Start services:**
   ```bash
   make docker-up-backend
   ```

2. **Test with curl:**
   ```bash
   # Health check
   curl http://localhost:8002/health
   
   # Service info
   curl http://localhost:8002/info
   
   # API docs
   open http://localhost:8002/docs  # Or visit in browser
   ```

3. **View logs in real-time:**
   ```bash
   make docker-logs-content-creator
   ```

---

## 📊 Service Architecture

```
┌─────────────────────────────────────────────────┐
│            Docker Network: genai-network         │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────────┐                            │
│  │  fastapi-backend │  Port: 8000                │
│  │  (existing)      │  Container: genai-fastapi-backend
│  └──────────────────┘                            │
│                                                   │
│  ┌──────────────────┐                            │
│  │ content-creator  │  Port: 8002                │
│  │  (NEW)           │  Container: genai-content-creator
│  │  - Video process │                            │
│  │  - Blog generate │                            │
│  │  - Script create │                            │
│  └──────────────────┘                            │
│                                                   │
│  ┌──────────────────┐                            │
│  │streamlit-frontend│  Port: 8501                │
│  │  (existing)      │  Container: genai-streamlit-frontend
│  └──────────────────┘                            │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 🔐 Environment Variables

Required for Content Creator:

```bash
# In your .env file or shell
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1
export CLOUD_STORAGE_BUCKET=content-uploads  # Optional
```

Optional:
```bash
# API Key
export API_KEY=your-api-key

# Datadog
export DD_API_KEY=your-dd-api-key
export DD_ENV=development
```

---

## 📝 Next Steps

1. **Phase 2**: Implement file upload API
   - Test with: `curl -X POST http://localhost:8002/api/v1/upload`

2. **Phase 3**: Add content generation
   - Test with: `curl -X POST http://localhost:8002/api/v1/generate`

3. **Phase 4**: Build Streamlit UI
   - Access at: http://localhost:8501

---

## 🎯 Quick Commands Summary

| Task | Command |
|------|---------|
| Build all | `make docker-build` |
| Start all | `make docker-up` |
| Stop all | `make docker-down` |
| View logs | `make docker-logs-content-creator` |
| Open shell | `make docker-shell-content-creator` |
| Check health | `curl http://localhost:8002/health` |
| Restart | `make docker-restart-content-creator` |
| Clean up | `make docker-clean` |

---

**Created**: December 30, 2024  
**Last Updated**: December 30, 2024  
**Service Version**: 0.1.0 (Phase 1 Complete)

