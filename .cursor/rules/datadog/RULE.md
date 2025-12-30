# Datadog Observability Rules

## Scope
**Paths**: All application code, Dockerfiles, GitHub Actions workflows

## Datadog Integration

### Required Environment Variables

```yaml
# All services must set:
DD_SITE: datadoghq.com
DD_SERVICE: service-name          # e.g., "fastapi-backend", "streamlit-frontend"
DD_ENV: environment              # "development", "dev", "prod"
DD_VERSION: git-sha              # Git commit SHA
DD_LOGS_ENABLED: "true"
DD_LOGS_INJECTION: "true"
DD_SOURCE: python
DD_TRACE_SAMPLE_RATE: "1.0"      # 100% sampling
DD_PROFILING_ENABLED: "true"
DD_CODE_ORIGIN_FOR_SPANS_ENABLED: "true"  # Links spans to code
```

### Dockerfile Integration

```dockerfile
# ✅ Good - Source Code Integration
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA

ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

# Copy serverless-init for Cloud Run
COPY --from=datadog/serverless-init:1 /datadog-init /app/datadog-init

# Install ddtrace
RUN pip install --target /dd_tracer/python/ ddtrace

# Set entrypoint
ENTRYPOINT ["/app/datadog-init"]
CMD ["/dd_tracer/python/bin/ddtrace-run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ❌ Bad - No Datadog integration
ENTRYPOINT ["uvicorn", "app.main:app"]
```

### Structured Logging

```python
# ✅ Good - JSON logging with extra fields
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Processing request",
    extra={
        "user_id": user_id,
        "request_id": request_id,
        "operation": "vote_extraction",
        "file_count": len(files),
        "model": model_name
    }
)

# ❌ Bad - Plain string logging
logger.info(f"Processing request for user {user_id}")
```

### APM Span Tags

```python
# ✅ Good - Rich span tags
from ddtrace import tracer

with tracer.trace("custom.operation", service="fastapi-backend") as span:
    # Operation metadata
    span.set_tag("operation.type", "llm_generation")
    span.set_tag("operation.name", "vote_extraction")

    # Input metadata
    span.set_tag("input.file_count", len(files))
    span.set_tag("input.total_size_mb", total_size / (1024*1024))

    # LLM metadata
    span.set_tag("llm.model", model_name)
    span.set_tag("llm.temperature", temperature)

    # Metrics
    span.set_metric("llm.tokens.input", input_tokens)
    span.set_metric("llm.tokens.output", output_tokens)
    span.set_metric("processing.duration_ms", duration_ms)

    result = await process()

# ❌ Bad - No tags
with tracer.trace("operation"):
    result = await process()
```

### LLM Observability

```python
# ✅ Good - LLMObs annotation
from ddtrace.llmobs import LLMObs
from ddtrace import tracer

# Enable LLMObs
LLMObs.enable(
    ml_app="vote-extraction",
    site="datadoghq.com",
    api_key=dd_api_key,
    env=environment
)

# Annotate LLM operation
with tracer.trace("llm.generation", service="fastapi-backend") as span:
    span.set_tag("llm.model_name", "gemini-2.5-flash")
    span.set_tag("llm.model_provider", "google")
    span.set_tag("llm.temperature", 0.0)
    span.set_tag("llm.max_tokens", 16384)

    span.set_metric("llm.tokens.prompt", input_tokens)
    span.set_metric("llm.tokens.completion", output_tokens)
    span.set_metric("llm.tokens.total", input_tokens + output_tokens)

    response = await generate(prompt)

# ❌ Bad - No LLMObs
response = await generate(prompt)
```

### RUM Integration (Frontend)

```javascript
// ✅ Good - Full RUM setup
window.DD_RUM.init({
    clientToken: 'CLIENT_TOKEN',
    applicationId: 'APP_ID',
    site: 'datadoghq.com',
    service: 'streamlit-frontend',
    env: 'production',
    version: 'git-sha',
    sessionSampleRate: 100,
    sessionReplaySampleRate: 20,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: 'mask-user-input'
})

// ❌ Bad - Minimal setup
window.DD_RUM.init({
    clientToken: 'CLIENT_TOKEN',
    applicationId: 'APP_ID'
})
```

### Error Tracking

```python
# ✅ Good - Structured error tracking
try:
    result = await process()
except ValueError as e:
    logger.error(
        "Validation error",
        extra={
            "error.type": "validation",
            "error.message": str(e),
            "input.size": len(data),
            "dd.trace_id": tracer.current_trace_context().trace_id
        },
        exc_info=True
    )
    raise HTTPException(status_code=422, detail=str(e))

# ❌ Bad - Generic error logging
try:
    result = await process()
except Exception as e:
    logger.error(str(e))
    raise
```

### Custom Metrics

```python
# ✅ Good - Business metrics
from datadog import statsd

# Count operations
statsd.increment('vote_extraction.requests', tags=["model:gemini-2.5-flash"])

# Track duration
statsd.histogram('vote_extraction.duration', duration_ms, tags=["status:success"])

# Gauge for queue size
statsd.gauge('processing.queue_size', queue_length)

# ❌ Bad - No custom metrics
# (Missing important business metrics)
```

## Environment-Specific Configuration

### Development (DD_ENV=dev)
```yaml
DD_ENV: dev
DD_TRACE_SAMPLE_RATE: "1.0"      # 100% tracing
DD_PROFILING_ENABLED: "true"      # Full profiling
DD_LOGS_INJECTION: "true"         # Log correlation
```

### Production (DD_ENV=prod)
```yaml
DD_ENV: prod
DD_TRACE_SAMPLE_RATE: "1.0"      # 100% tracing
DD_PROFILING_ENABLED: "true"      # Full profiling
DD_LOGS_INJECTION: "true"         # Log correlation
```

## GitHub Actions Integration

```yaml
# ✅ Good - Build args for source code integration
- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    build-args: |
      DD_GIT_REPOSITORY_URL=${{ github.repositoryUrl }}
      DD_GIT_COMMIT_SHA=${{ github.sha }}
    # ...

# ✅ Good - Environment variables for Cloud Run
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy $SERVICE \
      --set-env-vars DD_SITE=datadoghq.com \
      --set-env-vars DD_SERVICE=$SERVICE_NAME \
      --set-env-vars DD_ENV=dev \
      --set-env-vars DD_VERSION=${{ github.sha }} \
      --set-env-vars DD_CODE_ORIGIN_FOR_SPANS_ENABLED=true \
      --set-secrets DD_API_KEY=dd-api-key:latest

# ❌ Bad - Missing DD_ environment variables
gcloud run deploy $SERVICE --image $IMAGE
```

## Monitoring Best Practices

### Dashboard Creation
1. **Service Overview**: Requests, errors, latency
2. **LLM Metrics**: Token usage, cost, latency by model
3. **Business Metrics**: Extractions, success rate, processing time
4. **Infrastructure**: CPU, memory, container count

### Alerts
```yaml
# ✅ Good - Meaningful alerts
- name: High Error Rate
  query: "errors per minute > 10"
  message: "Error rate elevated in {{service.name}}"

- name: LLM Token Limit
  query: "avg:llm.tokens.output > 60000"
  message: "Approaching token limit, may cause truncation"

- name: Slow Response Time
  query: "p95:trace.duration > 30s"
  message: "95th percentile latency exceeded 30s"

# ❌ Bad - Generic alerts
- name: Service Down
  query: "status != 200"
```

### Log Management

```python
# ✅ Good - Log levels
logger.debug("Detailed debug info")
logger.info("Important events", extra={...})
logger.warning("Potential issues", extra={...})
logger.error("Errors requiring attention", extra={...}, exc_info=True)

# ❌ Bad - Everything at INFO
logger.info("Debug message")
logger.info("Error occurred")
```

## Cost Optimization

### Sampling Strategy
```python
# For high-volume, low-value endpoints
DD_TRACE_SAMPLE_RATE = "0.1"  # 10% sampling

# For critical paths
DD_TRACE_SAMPLE_RATE = "1.0"  # 100% sampling (our choice)
```

### Log Filtering
```yaml
# Exclude noisy logs
DD_LOGS_CONFIG_PROCESSING_RULES: |
  [
    {"type": "exclude_at_match", "name": "exclude_healthchecks", "pattern": "/health"}
  ]
```

## Don't

- ❌ Don't skip DD_ENV, DD_SERVICE, DD_VERSION
- ❌ Don't use plain text logs (use JSON/structured)
- ❌ Don't forget to set DD_CODE_ORIGIN_FOR_SPANS_ENABLED
- ❌ Don't skip LLMObs for LLM operations
- ❌ Don't forget to add span tags for important operations
- ❌ Don't log sensitive data (PII, API keys)
- ❌ Don't set DD_TRACE_SAMPLE_RATE < 1.0 without understanding impact
- ❌ Don't deploy without Datadog in production
