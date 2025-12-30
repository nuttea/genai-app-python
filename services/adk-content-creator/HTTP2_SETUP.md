# HTTP/2 Support with Hypercorn

## Overview

The Datadog Content Creator service uses **Hypercorn** instead of Uvicorn to support **HTTP/2** for better performance, especially when deployed to Google Cloud Run.

## Why HTTP/2?

### Benefits
- ✅ **Multiplexing**: Multiple requests over a single connection
- ✅ **Header compression**: Reduced bandwidth usage
- ✅ **Server push**: Proactive resource delivery
- ✅ **Binary protocol**: More efficient than HTTP/1.1
- ✅ **Better performance**: Especially for high-throughput APIs

### Cloud Run HTTP/2 Support
Google Cloud Run supports HTTP/2 natively, but requires an ASGI server that supports h2c (HTTP/2 Cleartext). Hypercorn is one of the few production-ready ASGI servers with full HTTP/2 support.

## Configuration

### Dependencies (`pyproject.toml`)
```toml
dependencies = [
    "hypercorn>=0.16.0",  # Replaced uvicorn[standard]
    # ... other dependencies
]
```

### Local Development (`Dockerfile`)
```dockerfile
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8002", "--worker-class", "asyncio"]
```

### Production (`Dockerfile.cloudrun`)
```dockerfile
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8080", "--worker-class", "asyncio"]
```

### Docker Compose
```yaml
command: ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8002", "--reload", "--worker-class", "asyncio"]
```

## Hypercorn vs Uvicorn

| Feature | Uvicorn | Hypercorn |
|---------|---------|-----------|
| HTTP/1.1 | ✅ | ✅ |
| HTTP/2 | ❌ | ✅ |
| WebSockets | ✅ | ✅ |
| ASGI 3.0 | ✅ | ✅ |
| Hot reload | ✅ | ✅ |
| Performance | Faster for HTTP/1.1 | Optimized for HTTP/2 |
| Cloud Run | Compatible | Native HTTP/2 support |

## Testing HTTP/2

### Local Testing (HTTP/1.1)
```bash
# Standard HTTP/1.1 request
curl -v http://localhost:8002/health
```

### Cloud Run (HTTP/2)
Once deployed to Cloud Run, the service will automatically use HTTP/2:

```bash
# Cloud Run automatically upgrades to HTTP/2
curl -v https://your-service.run.app/health

# Check HTTP version in response headers
# Look for: "HTTP/2 200"
```

### Verify HTTP/2 with httpie
```bash
# Install httpie
pip install httpie

# Test with HTTP/2
http --print=HhBb https://your-service.run.app/health
```

## Performance Comparison

### HTTP/1.1 (Uvicorn)
- Single request per connection
- Sequential processing
- Higher latency for multiple requests

### HTTP/2 (Hypercorn)
- Multiple requests per connection
- Parallel processing
- Lower latency for multiple requests
- Better resource utilization

## Cloud Run Deployment

### Enable HTTP/2 in Cloud Run
```bash
gcloud run deploy adk-content-creator \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --use-http2  # Enable HTTP/2
```

### Environment Variables
No special environment variables needed. Hypercorn automatically detects and uses HTTP/2 when available.

## Migration Notes

### Code Changes Required
- ✅ Updated `pyproject.toml` dependency
- ✅ Updated all Dockerfiles
- ✅ Updated `docker-compose.yml`
- ✅ Updated `app/main.py` if-main block

### No Changes Required
- ❌ FastAPI app code
- ❌ API endpoints
- ❌ Pydantic models
- ❌ Business logic

### Breaking Changes
- None! Hypercorn is fully compatible with FastAPI

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker logs genai-content-creator

# Common issues:
# 1. Port already in use
# 2. Missing hypercorn dependency
# 3. Configuration error
```

### HTTP/2 Not Working on Cloud Run
1. Verify service is deployed with `--use-http2` flag
2. Check Cloud Run logs for errors
3. Ensure HTTPS is enabled (HTTP/2 requires TLS)

### Performance Issues
- Check worker count (default: 1 worker)
- Monitor Cloud Run metrics
- Consider increasing resources

## Additional Resources

- [Hypercorn Documentation](https://pgjones.gitlab.io/hypercorn/)
- [Cloud Run HTTP/2](https://cloud.google.com/run/docs/configuring/http2)
- [HTTP/2 Explained](https://http2-explained.haxx.se/)

## Benchmarks

### Local Development
```bash
# Benchmark with wrk (HTTP/1.1)
wrk -t4 -c100 -d30s http://localhost:8002/health

# Expected: Similar to Uvicorn for single requests
```

### Cloud Run (HTTP/2)
```bash
# Benchmark with h2load (HTTP/2)
h2load -n10000 -c100 https://your-service.run.app/health

# Expected: Better performance for concurrent requests
```

## Configuration Options

### Advanced Hypercorn Config
```python
# app/main.py
from hypercorn.config import Config

config = Config()
config.bind = ["0.0.0.0:8002"]
config.worker_class = "asyncio"
config.workers = 4  # Multiple workers
config.backlog = 2048  # Connection queue size
config.keep_alive_timeout = 5  # Keep-alive timeout
```

### Environment Variables
```bash
# Hypercorn accepts these env vars:
HYPERCORN_BIND=0.0.0.0:8002
HYPERCORN_WORKERS=4
HYPERCORN_WORKER_CLASS=asyncio
```

---

**Status**: ✅ HTTP/2 support enabled with Hypercorn

**Compatibility**: Fully compatible with FastAPI and Cloud Run

**Performance**: Optimized for high-throughput, concurrent requests

