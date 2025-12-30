# 🐳 Docker Compose Testing Guide - Next.js Frontend

## 📋 Prerequisites

- Docker and Docker Compose installed
- Google Cloud credentials configured (`gcloud auth application-default login`)
- `.env` file with required environment variables

## 🚀 Quick Start

### 1. Build the Next.js Frontend

```bash
# Build only Next.js frontend
make docker-build-nextjs

# Or build all services
make docker-build
```

### 2. Start Services

```bash
# Start all services (recommended)
make docker-up-full

# Or start specific services
docker-compose up -d fastapi-backend content-creator nextjs-frontend
```

### 3. Check Status

```bash
# View running containers
make docker-ps

# View logs
make docker-logs-nextjs

# Or follow all logs
make docker-logs
```

### 4. Access Services

- **Next.js Frontend**: http://localhost:3000
- **FastAPI Backend**: http://localhost:8000
- **Content Creator**: http://localhost:8002
- **Streamlit (legacy)**: http://localhost:8501

---

## 🧪 Testing Checklist

### ✅ Next.js Frontend

#### 1. Container Health

```bash
# Check if container is running
docker ps | grep nextjs-frontend

# Check logs for errors
docker-compose logs nextjs-frontend | grep -i error

# Check health status
docker inspect genai-nextjs-frontend --format='{{.State.Health.Status}}'
```

Expected: Container running, no errors, health status = "healthy"

#### 2. Homepage Load

```bash
# Test homepage
curl http://localhost:3000

# Check for Next.js response
curl -I http://localhost:3000
```

Expected: HTTP 200, HTML response with Next.js markup

#### 3. Sidebar Navigation

Open http://localhost:3000 in browser and verify:
- [ ] Sidebar visible with Datadog purple theme
- [ ] Dashboard, Vote Extractor, Content Creator menu items
- [ ] Mobile menu (hamburger) works on small screens
- [ ] Links navigate correctly

#### 4. API Proxy

Test API proxy routes:

```bash
# Test Vote Extractor proxy
curl http://localhost:3000/api/vote-extractor/health

# Test Content Creator proxy
curl http://localhost:3000/api/content-creator/health
```

Expected: Returns health check responses from backend services

#### 5. Hot Reload

Make a change to a component and verify:
```bash
# Watch logs for rebuild
docker-compose logs -f nextjs-frontend
```

Expected: Next.js detects changes and recompiles

---

### ✅ Backend Services Integration

#### 1. FastAPI Backend

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

Expected: Service healthy, Swagger docs accessible

#### 2. Content Creator

```bash
# Health check
curl http://localhost:8002/health

# Info endpoint
curl http://localhost:8002/info
```

Expected: Service healthy, info shows capabilities

#### 3. CORS Configuration

Test CORS from Next.js:
```bash
# Should allow Next.js origin
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     http://localhost:8000/api/v1/vote-extraction/extract
```

Expected: CORS headers present with localhost:3000 allowed

---

## 🔍 Troubleshooting

### Issue: Next.js container fails to start

**Check:**
```bash
# View logs
docker-compose logs nextjs-frontend

# Common issues:
# 1. node_modules not installed
# 2. Port 3000 already in use
# 3. Syntax errors in code
```

**Solution:**
```bash
# Rebuild with no cache
docker-compose build --no-cache nextjs-frontend

# Check port availability
lsof -i :3000

# Kill process on port 3000
kill -9 $(lsof -t -i:3000)
```

### Issue: Hot reload not working

**Check:**
```bash
# Verify volumes are mounted
docker inspect genai-nextjs-frontend | grep -A 10 Mounts
```

**Solution:**
```bash
# Ensure volumes in docker-compose.yml:
# - ./frontend/nextjs:/app:ro
# - /app/node_modules
# - /app/.next
```

### Issue: API calls fail (CORS or connection)

**Check:**
```bash
# Backend reachable from Next.js container
docker-compose exec nextjs-frontend curl http://fastapi-backend:8000/health

# Content Creator reachable
docker-compose exec nextjs-frontend curl http://content-creator:8002/health
```

**Solution:**
```bash
# Verify CORS_ORIGINS includes http://localhost:3000
docker-compose exec fastapi-backend env | grep CORS

# Restart backend if needed
docker-compose restart fastapi-backend
```

### Issue: Datadog RUM not loading

**Check:**
```bash
# Check environment variables
docker-compose exec nextjs-frontend env | grep DD_
```

**Solution:**
- Ensure `DD_RUM_APPLICATION_ID` and `DD_RUM_CLIENT_TOKEN` are set
- Or set them to empty string to disable RUM (dev mode)

### Issue: Styles not loading / Tailwind not working

**Check:**
```bash
# Rebuild CSS
docker-compose exec nextjs-frontend npm run build
```

**Solution:**
```bash
# Rebuild container
docker-compose build --no-cache nextjs-frontend
docker-compose up -d nextjs-frontend
```

---

## 📊 Performance Testing

### Load Time

```bash
# Measure page load time
time curl -o /dev/null -s -w "%{time_total}\n" http://localhost:3000
```

Expected: < 2 seconds

### Memory Usage

```bash
# Check container memory
docker stats genai-nextjs-frontend --no-stream
```

Expected: < 500MB for development

### Build Time

```bash
# Time the build
time docker-compose build nextjs-frontend
```

Expected: 2-5 minutes (first build), < 1 minute (cached)

---

## 🧹 Cleanup

### Stop Services

```bash
# Stop all
make docker-down

# Stop only Next.js
docker-compose stop nextjs-frontend
```

### Remove Containers

```bash
# Remove all containers
docker-compose rm -f

# Clean everything
make docker-clean
```

### Free Up Space

```bash
# Remove dangling images
docker image prune -f

# Remove all unused images
docker image prune -a

# Clean build cache
docker builder prune -a
```

---

## 📝 Development Workflow

### 1. Make Code Changes

Edit files in `frontend/nextjs/`

### 2. Watch for Hot Reload

```bash
# Terminal 1: Follow logs
make docker-logs-nextjs

# Terminal 2: Make changes
# Next.js should auto-reload
```

### 3. Test Changes

Open browser: http://localhost:3000

### 4. Check Logs for Errors

```bash
# View recent errors
docker-compose logs nextjs-frontend | grep -i error | tail -20
```

### 5. Restart if Needed

```bash
# Restart Next.js only
make docker-restart-nextjs

# Or restart all
make docker-restart
```

---

## 🎯 Success Criteria

Your Next.js frontend is working correctly if:

- ✅ Container starts and passes health check
- ✅ Homepage loads at http://localhost:3000
- ✅ Sidebar navigation is visible and functional
- ✅ Datadog purple theme is applied
- ✅ Mobile menu works on small screens
- ✅ API proxy routes return backend responses
- ✅ Hot reload detects file changes
- ✅ No errors in container logs
- ✅ CORS allows requests from Next.js
- ✅ Backend services are accessible

---

## 📚 Related Commands

```bash
# See all available commands
make help

# Docker commands
make docker-build-nextjs    # Build Next.js image
make docker-logs-nextjs     # View Next.js logs
make docker-restart-nextjs  # Restart Next.js container
make docker-shell-nextjs    # Open shell in container

# Full stack
make docker-up-full         # Start all services
make docker-logs            # View all logs
make docker-ps              # Show running containers
make docker-stats           # Resource usage
```

---

## 🔗 Next Steps

1. ✅ Verify Next.js loads correctly
2. ✅ Test API integration with backends
3. 🚧 Implement Content Creator pages (Phase 4)
4. 🚧 Build Vote Extractor pages (Phase 5)
5. 🚧 Add dashboard analytics (Phase 6)

---

**Status**: ✅ Docker Compose configuration complete and ready for testing

**Last Updated**: December 30, 2024

