# Datadog APM and LLM Observability Setup

Complete guide for setting up Datadog monitoring for the GenAI Application Platform.

## Overview

This application supports two types of Datadog monitoring:

1. **APM (Application Performance Monitoring)** - Track all requests, errors, and performance
2. **LLM Observability** - Monitor AI model calls, tokens, costs, and quality

## Prerequisites

- Datadog account (free trial available)
- Datadog API key
- Application deployed or running locally

## Quick Setup

### 1. Get Your Datadog API Key

```bash
# Get from: https://app.datadoghq.com/organization-settings/api-keys
export DD_API_KEY=your-datadog-api-key-here
```

### 2. Configure Environment Variables

**For Local Docker:**

```bash
# Add to your .env file
DD_API_KEY=your-api-key-here
DD_SITE=datadoghq.com
DD_SERVICE=genai-fastapi-backend
DD_ENV=development
DD_VERSION=0.1.0

# Optional: Enable LLM Observability
DD_LLMOBS_ML_APP=genai-vote-extractor
DD_LLMOBS_ENABLED=1
```

**For Cloud Run:**

```bash
# Set environment variables before deploying
export DD_API_KEY=your-api-key-here
export DD_SITE=datadoghq.com
export DD_SERVICE=genai-fastapi-backend
export DD_ENV=production
export DD_VERSION=1.0.0
export DD_LLMOBS_ML_APP=genai-vote-extractor
export DD_LLMOBS_ENABLED=1

# Deploy
cd infra/cloud-run
./deploy-backend.sh
```

### 3. Restart Services

**Local Docker:**
```bash
docker-compose down
docker-compose up -d
```

**Cloud Run:**
```bash
cd infra/cloud-run
./deploy-backend.sh
```

### 4. Verify in Datadog

After generating some traffic:

- **APM Traces**: https://app.datadoghq.com/apm/traces
- **LLM Observability**: https://app.datadoghq.com/llm/traces
- **Service Map**: https://app.datadoghq.com/apm/map
- **Logs**: https://app.datadoghq.com/logs

## Environment Variables Reference

### Required for APM

| Variable | Description | Example |
|----------|-------------|---------|
| `DD_API_KEY` | Your Datadog API key | `abc123...` |
| `DD_SERVICE` | Service name | `genai-fastapi-backend` |
| `DD_ENV` | Environment | `production`, `staging`, `dev` |
| `DD_VERSION` | Service version | `1.0.0`, `git-sha` |

### Optional APM Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `DD_SITE` | Datadog site | `datadoghq.com` |
| `DD_LOGS_INJECTION` | Inject trace IDs into logs | `true` |
| `DD_TRACE_SAMPLE_RATE` | Trace sampling rate (0-1) | `1.0` |
| `DD_TRACE_ENABLED` | Enable/disable tracing | `1` |
| `DD_PROFILING_ENABLED` | Enable continuous profiling | `true` |

### LLM Observability

| Variable | Description | Required |
|----------|-------------|----------|
| `DD_LLMOBS_ML_APP` | ML application name | Yes (for LLMObs) |
| `DD_LLMOBS_ENABLED` | Enable LLM Observability | `1` to enable |

## Features

### APM (Application Performance Monitoring)

When enabled, you get:

✅ **Request Tracing**
- Every API request traced end-to-end
- Timing breakdown by service, database, external calls
- Automatic instrumentation for FastAPI, httpx, etc.

✅ **Error Tracking**
- Automatic error capture
- Stack traces with context
- Error rate monitoring

✅ **Performance Metrics**
- Request rate (requests/second)
- Latency (p50, p75, p95, p99)
- Error rate
- Apdex scores

✅ **Service Map**
- Visual service dependencies
- Request flow visualization
- Performance bottleneck identification

✅ **Profiling**
- CPU usage by function
- Memory allocation
- Lock contention

### LLM Observability

When enabled, you get:

✅ **LLM Call Tracking**
- Every Gemini API call traced
- Input prompts and outputs
- Model parameters (temperature, max_tokens, etc.)

✅ **Token Usage**
- Input tokens
- Output tokens
- Total tokens per request
- Cost estimation

✅ **Quality Metrics**
- Response time
- Success/failure rates
- Model performance

✅ **Prompt Management**
- Track prompt templates
- Version control
- A/B testing support

## Implementation Details

### Automatic Instrumentation

The application uses `ddtrace-run` for automatic instrumentation:

```dockerfile
CMD ["ddtrace-run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

This automatically instruments:
- ✅ FastAPI routes
- ✅ HTTP clients (httpx, aiohttp)
- ✅ Database calls (if any)
- ✅ Redis/cache (if any)
- ✅ Custom spans

### Manual Instrumentation (Optional)

For custom tracking:

```python
from ddtrace import tracer

@tracer.wrap(service="custom-service", resource="custom-operation")
def my_function():
    # Your code
    pass

# Or use context manager
with tracer.trace("custom.operation", service="my-service") as span:
    span.set_tag("custom.tag", "value")
    # Your code
```

### Log-Trace Correlation

With `DD_LOGS_INJECTION=true`, logs automatically include:
- `dd.trace_id` - Link to APM trace
- `dd.span_id` - Specific span
- `dd.service` - Service name
- `dd.env` - Environment
- `dd.version` - Version

Example log with trace correlation:
```json
{
  "message": "Processing request",
  "level": "INFO",
  "dd.trace_id": "1234567890",
  "dd.span_id": "9876543210",
  "dd.service": "genai-fastapi-backend",
  "dd.env": "production"
}
```

## Local Development with Datadog

### Option 1: Direct to Datadog (Agentless)

Already configured! Just set environment variables:

```bash
# Add to .env
DD_API_KEY=your-api-key
DD_SERVICE=genai-fastapi-backend
DD_ENV=development
DD_VERSION=0.1.0

# Restart
docker-compose restart fastapi-backend
```

### Option 2: With Datadog Agent (Advanced)

Add Datadog Agent container to docker-compose.yml:

```yaml
datadog-agent:
  image: gcr.io/datadoghq/agent:latest
  container_name: datadog-agent
  environment:
    - DD_API_KEY=${DD_API_KEY}
    - DD_SITE=${DD_SITE:-datadoghq.com}
    - DD_APM_ENABLED=true
    - DD_APM_NON_LOCAL_TRAFFIC=true
    - DD_LOGS_ENABLED=true
    - DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - /proc/:/host/proc/:ro
    - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro
  networks:
    - genai-network

# Then update backend to use agent
fastapi-backend:
  environment:
    - DD_AGENT_HOST=datadog-agent
    - DD_TRACE_AGENT_PORT=8126
```

## Cloud Run Deployment with Datadog

### Method 1: Agentless (Recommended for Cloud Run)

Already configured in deployment scripts!

```bash
# Set environment variables
export DD_API_KEY=your-api-key
export DD_SERVICE=genai-fastapi-backend
export DD_ENV=production
export DD_VERSION=1.0.0
export DD_LLMOBS_ML_APP=genai-vote-extractor
export DD_LLMOBS_ENABLED=1

# Deploy
cd infra/cloud-run
./deploy-backend.sh
```

The script automatically adds all Datadog environment variables to Cloud Run.

### Method 2: With Serverless-Init Sidecar (Advanced)

For advanced monitoring with log correlation:

```yaml
# cloud-run-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: genai-fastapi-backend
spec:
  template:
    spec:
      containers:
        # Main application container
        - name: fastapi-backend
          image: gcr.io/PROJECT_ID/genai-fastapi-backend
          env:
            - name: DD_SERVICE
              value: "genai-fastapi-backend"
            - name: DD_ENV
              value: "production"
            - name: DD_VERSION
              value: "1.0.0"
            - name: DD_LOGS_INJECTION
              value: "true"
          volumeMounts:
            - mountPath: /var/log/app
              name: logs

        # Datadog serverless-init sidecar
        - name: datadog-sidecar
          image: gcr.io/datadoghq/serverless-init:latest
          env:
            - name: DD_API_KEY
              value: "YOUR_API_KEY"
            - name: DD_SITE
              value: "datadoghq.com"
            - name: DD_SERVICE
              value: "genai-fastapi-backend"
            - name: DD_ENV
              value: "production"
            - name: DD_VERSION
              value: "1.0.0"
            - name: DD_SERVERLESS_LOG_PATH
              value: "/var/log/app/*.log"
            - name: DD_SOURCE
              value: "python"
          volumeMounts:
            - mountPath: /var/log/app
              name: logs

      volumes:
        - name: logs
          emptyDir:
            medium: Memory
            sizeLimit: 512Mi
```

Deploy with:
```bash
gcloud run services replace cloud-run-service.yaml
```

## Monitoring Dashboard

### Key Metrics to Monitor

**APM:**
- Request rate (requests/second)
- Latency (p50, p95, p99)
- Error rate
- Apdex score

**LLM Observability:**
- Token usage (input/output)
- Model latency
- Cost per request
- Error rate

**Infrastructure:**
- Container CPU usage
- Container memory usage
- Cold start frequency
- Instance count

### Creating Dashboards

1. Go to https://app.datadoghq.com/dashboard/lists
2. Create a new dashboard
3. Add widgets for:
   - Request rate: `trace.fastapi.request.hits`
   - Latency: `trace.fastapi.request.duration`
   - Errors: `trace.fastapi.request.errors`
   - LLM tokens: `llm.token.count`

## Alerts

### Recommended Alerts

1. **High Error Rate**
   ```
   avg(last_5m):sum:trace.fastapi.request.errors{service:genai-fastapi-backend}.as_count() > 10
   ```

2. **High Latency**
   ```
   avg(last_5m):p95:trace.fastapi.request.duration{service:genai-fastapi-backend} > 5s
   ```

3. **High Token Usage** (Cost Alert)
   ```
   sum(last_1h):sum:llm.token.count{service:genai-fastapi-backend} > 1000000
   ```

4. **Service Down**
   ```
   avg(last_5m):sum:trace.fastapi.request.hits{service:genai-fastapi-backend}.as_count() < 1
   ```

### Create Alerts

1. Go to https://app.datadoghq.com/monitors/create
2. Choose "APM" or "Metric" monitor type
3. Configure thresholds
4. Set notification channels (email, Slack, PagerDuty)

## Testing Datadog Integration

### Generate Test Traffic

```bash
# Health check
curl https://your-service.run.app/health

# Generate test traces
for i in {1..10}; do
  curl -X POST https://your-service.run.app/api/v1/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Test prompt '$i'", "model": "gemini-2.5-flash"}'
  sleep 1
done
```

### Verify in Datadog

1. **Check APM Traces**:
   - Go to https://app.datadoghq.com/apm/traces
   - Filter by `service:genai-fastapi-backend`
   - Should see traces appearing within 1-2 minutes

2. **Check LLM Traces** (if LLMObs enabled):
   - Go to https://app.datadoghq.com/llm/traces
   - Filter by application name
   - Should see Gemini API calls

3. **Check Service Map**:
   - Go to https://app.datadoghq.com/apm/map
   - Should see your service and dependencies

4. **Check Logs**:
   - Go to https://app.datadoghq.com/logs
   - Filter by `service:genai-fastapi-backend`
   - Logs should have trace correlation

## Troubleshooting

### No Traces Appearing

**Check:**
1. ✅ DD_API_KEY is set correctly
2. ✅ Service is receiving traffic
3. ✅ DD_TRACE_ENABLED=1
4. ✅ Application started with `ddtrace-run`

**Debug:**
```bash
# Check environment variables
docker-compose exec fastapi-backend env | grep DD_

# Check logs for Datadog startup messages
docker-compose logs fastapi-backend | grep -i datadog

# Enable debug logging
export DD_TRACE_DEBUG=true
docker-compose restart fastapi-backend
```

### Traces Not Linking to Logs

**Solution:**
1. Set `DD_LOGS_INJECTION=true`
2. Use structured logging (JSON format)
3. Restart application

### High Costs

**Optimize:**
1. Reduce sample rate: `DD_TRACE_SAMPLE_RATE=0.1` (10%)
2. Filter noisy endpoints
3. Use ingestion controls in Datadog UI
4. Set up budgets and alerts

## Best Practices

### Unified Service Tagging

Always set these three variables together:
```bash
DD_SERVICE=genai-fastapi-backend
DD_ENV=production
DD_VERSION=1.0.0
```

Benefits:
- Consistent service identification
- Easy filtering in dashboards
- Deployment tracking
- Version comparison

### Service Naming

Use consistent naming:
- `genai-fastapi-backend` - Backend API
- `genai-streamlit-frontend` - Frontend UI
- `genai-vote-extraction` - Specific feature

### Tagging Strategy

Add custom tags for better filtering:

```python
from ddtrace import tracer

@tracer.wrap()
def process_request():
    span = tracer.current_span()
    span.set_tag("user.type", "admin")
    span.set_tag("feature", "vote-extraction")
    span.set_tag("document.pages", 3)
```

### Sampling

**Development:**
```bash
DD_TRACE_SAMPLE_RATE=1.0  # 100% - trace everything
```

**Production (low traffic):**
```bash
DD_TRACE_SAMPLE_RATE=1.0  # 100% - if < 1000 req/min
```

**Production (high traffic):**
```bash
DD_TRACE_SAMPLE_RATE=0.1  # 10% - if > 10000 req/min
```

## Cost Management

### Datadog Pricing (Approximate)

**APM:**
- Free: 1 host, 150 GB logs/month
- Pro: $31/host/month + $0.002/span
- Enterprise: Custom pricing

**LLM Observability:**
- Pricing based on token volume
- Check current pricing at https://www.datadoghq.com/pricing/

### Optimization Tips

1. **Sampling**: Reduce sample rate for high-traffic endpoints
2. **Filtering**: Exclude health checks from tracing
3. **Retention**: Adjust retention settings
4. **Budgets**: Set up budget alerts in Datadog

### Exclude Health Checks

```python
# In app/main.py
from ddtrace import config

# Don't trace health checks
config.fastapi["trace_query_string"] = False

@app.get("/health")
async def health():
    # Health checks won't be traced if you configure filtering
    pass
```

Or filter in deployment:
```bash
export DD_TRACE_HEALTH_METRICS_ENABLED=false
```

## Advanced Configuration

### Custom Spans

```python
from ddtrace import tracer

async def extract_votes(files):
    with tracer.trace("vote.extraction", service="vote-extractor") as span:
        span.set_tag("file.count", len(files))
        span.set_tag("extraction.type", "multi-page")

        # Your extraction logic
        result = await process_files(files)

        span.set_tag("extraction.success", True)
        span.set_tag("pages.processed", result.pages)

        return result
```

### Distributed Tracing

For frontend → backend → Gemini API:

```python
# Backend automatically propagates trace context
# to downstream services (Gemini API)
```

### Error Tracking

```python
from ddtrace import tracer

try:
    result = await risky_operation()
except Exception as e:
    span = tracer.current_span()
    span.set_tag("error.type", type(e).__name__)
    span.set_tag("error.message", str(e))
    span.set_tag("error.stack", traceback.format_exc())
    raise
```

## Datadog Dashboard Examples

### Create Vote Extraction Dashboard

```json
{
  "title": "GenAI Vote Extraction Monitoring",
  "widgets": [
    {
      "definition": {
        "type": "timeseries",
        "requests": [{
          "q": "sum:trace.fastapi.request.hits{service:genai-fastapi-backend,resource_name:post_/api/v1/vote-extraction/extract}.as_count()"
        }],
        "title": "Vote Extraction Requests"
      }
    },
    {
      "definition": {
        "type": "timeseries",
        "requests": [{
          "q": "avg:trace.fastapi.request.duration{service:genai-fastapi-backend,resource_name:post_/api/v1/vote-extraction/extract}"
        }],
        "title": "Extraction Latency"
      }
    },
    {
      "definition": {
        "type": "query_value",
        "requests": [{
          "q": "sum:llm.token.count{service:genai-fastapi-backend}.as_count()"
        }],
        "title": "Total Tokens Used"
      }
    }
  ]
}
```

## Security

### Protect API Keys

**Don't:**
- ❌ Commit DD_API_KEY to version control
- ❌ Print API key in logs
- ❌ Expose in public endpoints

**Do:**
- ✅ Use environment variables
- ✅ Use Cloud Secret Manager for production
- ✅ Rotate keys regularly
- ✅ Use least-privilege API keys

### Use Secret Manager (Cloud Run)

```bash
# Create secret
echo -n "your-dd-api-key" | gcloud secrets create dd-api-key --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding dd-api-key \
    --member=serviceAccount:YOUR_SERVICE_ACCOUNT \
    --role=roles/secretmanager.secretAccessor

# Deploy with secret
gcloud run services update genai-fastapi-backend \
    --region us-central1 \
    --set-secrets=DD_API_KEY=dd-api-key:latest
```

## Resources

- [Datadog APM Documentation](https://docs.datadoghq.com/tracing/)
- [Python Tracing](https://docs.datadoghq.com/tracing/trace_collection/automatic_instrumentation/dd_libraries/python/)
- [LLM Observability](https://docs.datadoghq.com/llm_observability/)
- [Cloud Run Integration](https://docs.datadoghq.com/serverless/google_cloud_run/)

---

**Quick Start**: Set `DD_API_KEY` and restart services to enable full Datadog monitoring! 🚀
