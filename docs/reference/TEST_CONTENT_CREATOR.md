# 🧪 Test Datadog Content Creator - Quick Guide

**Status**: Ready for local testing with Docker Compose ✅

---

## 🚀 Quick Test Commands

### 1. Build and Start
```bash
# Build the Docker image
make docker-build-content-creator

# Start the service
make docker-up

# Or start only backend services (FastAPI + Content Creator)
make docker-up-backend
```

### 2. Check if Running
```bash
# Check container status
make docker-ps

# View logs
make docker-logs-content-creator
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:8002/health

# Service info
curl http://localhost:8002/info

# Root endpoint
curl http://localhost:8002/
```

---

## ✅ Expected Responses

### Health Check
```bash
$ curl http://localhost:8002/health
```
```json
{
  "status": "healthy",
  "service": "adk-content-creator",
  "version": "0.1.0"
}
```

### Service Info
```bash
$ curl http://localhost:8002/info
```
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

---

## 🔍 Verify Installation

### Check All Services
```bash
$ make docker-ps
```

Expected output:
```
NAME                        STATUS         PORTS
genai-fastapi-backend       Up (healthy)   0.0.0.0:8000->8000/tcp
genai-content-creator       Up (healthy)   0.0.0.0:8002->8002/tcp
genai-streamlit-frontend    Up (healthy)   0.0.0.0:8501->8501/tcp
```

### Access Services
- **Content Creator**: http://localhost:8002
- **Content Creator API Docs**: http://localhost:8002/docs (when implemented)
- **FastAPI Backend**: http://localhost:8000
- **Streamlit Frontend**: http://localhost:8501

---

## 🛠️ Development Testing

### Test Hot Reload
1. Start the service:
   ```bash
   make docker-up-backend
   ```

2. Make a change in `services/adk-content-creator/app/main.py`

3. The service should automatically reload (check logs):
   ```bash
   make docker-logs-content-creator
   ```

4. Test the change:
   ```bash
   curl http://localhost:8002/health
   ```

### Debug with Logs
```bash
# Follow logs in real-time
make docker-logs-content-creator

# View last 100 lines
docker logs genai-content-creator --tail 100

# View logs with timestamps
docker logs genai-content-creator --timestamps
```

### Open Shell in Container
```bash
# Open bash shell
make docker-shell-content-creator

# Inside container:
python --version
pip list
ls -la /app
```

---

## 📊 Performance Testing

### Check Resource Usage
```bash
make docker-stats
```

Expected:
- **CPU**: < 5% idle, < 50% under load
- **Memory**: ~200-500 MB
- **Network**: Minimal when idle

---

## 🐛 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
make docker-logs-content-creator
```

**Common issues:**

1. **GCP credentials not found**
   ```
   Error: Could not load credentials
   ```
   **Fix**: Ensure `gcloud auth application-default login` is run

2. **Port already in use**
   ```
   Error: bind: address already in use
   ```
   **Fix**: Stop conflicting service or change port in docker-compose.yml

3. **Dependencies not installed**
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
   **Fix**: Rebuild image with `make docker-build-content-creator`

### Cannot Connect to Service

**Check if container is running:**
```bash
docker ps | grep content-creator
```

**Check health:**
```bash
curl -v http://localhost:8002/health
```

**Restart service:**
```bash
make docker-restart-content-creator
```

### Hot Reload Not Working

**Verify volume mount:**
```bash
docker inspect genai-content-creator | grep -A 10 Mounts
```

**Restart with rebuild:**
```bash
make docker-down
make docker-build-content-creator
make docker-up-backend
```

---

## 🎯 Next Steps After Testing

### Phase 2: Add Upload Endpoint
Once basic testing works, implement:
```bash
# Will be available at:
POST http://localhost:8002/api/v1/upload
```

### Phase 3: Add Content Generation
```bash
# Will be available at:
POST http://localhost:8002/api/v1/generate
```

### Phase 4: Test from Streamlit
Access Streamlit UI at http://localhost:8501 and use the new "Content Creator" page

---

## 📝 Test Checklist

- [ ] Build image successfully
- [ ] Start container successfully
- [ ] Health check returns 200 OK
- [ ] Service info shows correct capabilities
- [ ] Logs show no errors
- [ ] Hot reload works when changing code
- [ ] Container restarts automatically if crashed
- [ ] GCP credentials mounted correctly
- [ ] Can open shell in container
- [ ] Resource usage is reasonable

---

## 🔗 Resources

- **Full Docker Guide**: [DOCKER_TESTING_GUIDE.md](./DOCKER_TESTING_GUIDE.md)
- **Service README**: [services/adk-content-creator/README.md](./services/adk-content-creator/README.md)
- **Progress Tracker**: [DATADOG_CONTENT_CREATOR_PROGRESS.md](./DATADOG_CONTENT_CREATOR_PROGRESS.md)

---

## 📞 Quick Help

**Can't build?**
```bash
make docker-clean
make docker-build-content-creator
```

**Service crashed?**
```bash
make docker-logs-content-creator  # Check why
make docker-restart-content-creator  # Restart
```

**Want fresh start?**
```bash
make docker-down
make docker-clean
make docker-build
make docker-up
```

---

**Ready to test!** 🚀

Run: `make docker-up-backend && curl http://localhost:8002/health`

---

**Created**: December 30, 2024  
**Status**: Phase 1 Complete - Ready for Local Testing ✅

