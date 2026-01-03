# Datadog Logging with APM Trace Correlation

## Overview

Implemented structured JSON logging with automatic APM trace correlation for the FastAPI backend. This enables seamless navigation between logs and traces in Datadog, providing complete observability of the application.

**References:**
- [Datadog Python Log Collection](https://docs.datadoghq.com/logs/log_collection/python/)
- [Correlating Python Logs and Traces](https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/)

## How It Works

When `DD_LOGS_INJECTION=true`, the `ddtrace` library automatically injects trace correlation fields into log records:

- `dd.trace_id`: Links log to specific trace
- `dd.span_id`: Links log to specific span
- `dd.env`: Environment (dev, prod)
- `dd.service`: Service name
- `dd.version`: Service version

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Application                                         │
│ ├─ Configured with DatadogJsonFormatter                     │
│ └─ Uses python-json-logger for structured logs              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ ddtrace Auto-Instrumentation (DD_LOGS_INJECTION=true)      │
│ ├─ Automatically injects dd.trace_id into log records       │
│ ├─ Automatically injects dd.span_id into log records        │
│ └─ Adds dd.env, dd.service, dd.version                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ JSON Log Output (stdout)                                    │
│ {                                                            │
│   "timestamp": "2026-01-03 14:53:11",                       │
│   "level": "INFO",                                           │
│   "logger": "app.main",                                      │
│   "message": "Processing request",                           │
│   "dd.env": "development",                                   │
│   "dd.service": "vote-extractor",                            │
│   "dd.version": "0.1.0",                                     │
│   "dd.trace_id": "140031489178122457...",  ← Correlation!   │
│   "dd.span_id": "14484272564170044706",    ← Correlation!   │
│   "filename": "main.py",                                     │
│   "lineno": 42                                               │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Datadog Agent                                               │
│ ├─ Collects logs from stdout                                │
│ ├─ Automatically parses JSON structure                      │
│ └─ Correlates logs with APM traces via trace_id             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Datadog Platform                                            │
│ ├─ Logs appear in Log Explorer                              │
│ ├─ Traces appear in APM Trace Explorer                      │
│ └─ Navigate between logs ↔ traces seamlessly! ✅            │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Logging Configuration Module

**File**: `services/fastapi-backend/app/core/logging.py`

```python
from pythonjsonlogger import jsonlogger

class DatadogJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes Datadog trace correlation fields.
    
    Datadog trace fields (automatically injected by ddtrace):
    - dd.trace_id: Trace ID for correlation
    - dd.span_id: Span ID for correlation
    - dd.env: Environment (e.g., dev, prod)
    - dd.service: Service name
    - dd.version: Service version
    """
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["filename"] = record.filename
        log_record["lineno"] = record.lineno
        
        # ddtrace automatically adds trace fields when DD_LOGS_INJECTION=true
```

### 2. Application Initialization

**File**: `services/fastapi-backend/app/main.py`

```python
from app.core.logging import setup_logging

# Setup logging with JSON formatting and trace correlation
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

# Log startup info
logger.info(f"Starting {settings.api_title} v{settings.api_version}")
logger.info(f"✅ Datadog Logs Injection: {os.getenv('DD_LOGS_INJECTION')}")
```

### 3. Environment Configuration

**File**: `docker-compose.yml`

```yaml
services:
  fastapi-backend:
    environment:
      # Datadog APM
      - DD_SERVICE=vote-extractor
      - DD_ENV=development
      - DD_VERSION=0.1.0
      
      # Logs Configuration
      - DD_LOGS_ENABLED=true
      - DD_LOGS_INJECTION=true  # ← Enable automatic trace injection!
      - DD_SOURCE=python
      
      # Trace Configuration
      - DD_TRACE_ENABLED=1
      - DD_TRACE_AGENT_URL=http://datadog-agent:8126
```

### 4. Dependencies

**File**: `services/fastapi-backend/pyproject.toml`

```toml
dependencies = [
    "ddtrace>=4.0.0",              # Datadog APM tracing
    "python-json-logger>=2.0.7",   # JSON log formatting
    ...
]
```

## Log Output Examples

### Without Active Trace (Startup Logs)

```json
{
  "timestamp": "2026-01-03 14:53:11",
  "level": "INFO",
  "logger": "app.main",
  "message": "Starting GenAI FastAPI Backend v0.1.0",
  "dd.env": null,
  "dd.service": null,
  "dd.version": null,
  "dd.trace_id": null,
  "dd.span_id": null,
  "filename": "main.py",
  "lineno": 27
}
```

### With Active Trace (During Request)

```json
{
  "timestamp": "2026-01-03 15:10:42",
  "level": "INFO",
  "logger": "app.api.v1.endpoints.vote_extraction",
  "message": "✅ Extracting votes from 2 images",
  "dd.env": "development",
  "dd.service": "vote-extractor",
  "dd.version": "0.1.0",
  "dd.trace_id": "140031489178122457180989337003685814519",
  "dd.span_id": "14484272564170044706",
  "filename": "vote_extraction.py",
  "lineno": 340
}
```

## Usage in Code

### Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

# These logs will automatically include trace correlation when inside a request
logger.info("Processing vote extraction request")
logger.debug(f"Received {len(images)} images")
logger.error("Extraction failed", exc_info=True)
```

### With Extra Context

```python
logger.info(
    "Vote extraction completed",
    extra={
        "pages_processed": 5,
        "reports_extracted": 3,
        "duration_ms": 1234
    }
)
```

### Structured Logging

```python
# All extra fields are automatically included in JSON output
logger.info(
    "Validation result",
    extra={
        "validation_passed": True,
        "ballot_count": 1500,
        "candidate_count": 10
    }
)
```

## Datadog UI Integration

### 1. Navigate from Trace to Logs

In the APM Trace view:
1. Open any trace
2. Click on a span
3. Click "View Related Logs"
4. See all logs with matching `dd.trace_id` ✅

### 2. Navigate from Logs to Trace

In the Log Explorer:
1. Find a log entry
2. Click on the trace ID
3. Opens the corresponding trace view ✅

### 3. Query Logs by Trace

```
# Find all logs for a specific trace
@dd.trace_id:140031489178122457180989337003685814519

# Find logs for a specific service with errors
service:vote-extractor status:error

# Find logs with trace correlation
@dd.trace_id:* @dd.span_id:*
```

## Benefits

### ✅ Complete Request Context

Every log includes full trace context:
- Which request generated this log?
- What span was executing?
- What service, environment, version?

### ✅ Seamless Navigation

Navigate between logs and traces without manual correlation:
- Click trace ID in logs → View trace
- Click "View Logs" in trace → See all related logs

### ✅ Easier Debugging

When investigating issues:
1. Find error in logs
2. Click trace ID
3. See complete distributed trace
4. Understand full request flow

### ✅ Performance Analysis

Correlate slow operations:
- See which logs correspond to slow spans
- Identify bottlenecks with log timestamps
- Debug performance issues faster

### ✅ Better Alerts

Create alerts combining logs and traces:
- Alert on errors with specific trace attributes
- Monitor log patterns within traced operations
- Set up composite monitors

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DD_LOGS_INJECTION` | `false` | Enable automatic trace injection |
| `DD_LOGS_ENABLED` | `false` | Enable log collection |
| `DD_SOURCE` | - | Log source (set to `python`) |
| `DD_SERVICE` | - | Service name |
| `DD_ENV` | - | Environment name |
| `DD_VERSION` | - | Service version |

### Python Configuration

```python
from app.core.logging import configure_logging

# JSON logs with trace correlation (recommended)
configure_logging(
    level="INFO",
    json_logs=True,  # Use JSON formatting
    service_name="vote-extractor"
)

# Standard format with trace fields
configure_logging(
    level="INFO",
    json_logs=False,  # Use text formatting
    service_name="vote-extractor"
)
```

## Testing

### 1. Local Testing with Docker Compose

```bash
# Start services
docker-compose up -d

# Check logs with JSON formatting
docker-compose logs fastapi-backend --tail 20

# Make a request to generate traced logs
curl -X POST http://localhost:8000/api/v1/vote-extraction/extract \
  -F "images=@test_form.jpg"

# Check logs during request (should have trace IDs)
docker-compose logs fastapi-backend --tail 50 | grep trace_id
```

### 2. Verify Trace Correlation

Look for log entries with populated trace fields:
```json
{
  "dd.trace_id": "140031489178122457...",  // ← Should have value
  "dd.span_id": "14484272564170044706",    // ← Should have value
  ...
}
```

### 3. Datadog Verification

1. Go to Datadog Log Explorer
2. Search for: `service:vote-extractor`
3. Click on any log entry
4. Verify:
   - ✅ Trace ID is present
   - ✅ Click trace ID opens trace view
   - ✅ Log is correctly attributed to service

## Troubleshooting

### Logs Missing Trace IDs

**Problem**: Logs show `dd.trace_id: null`

**Solution**:
- Check `DD_LOGS_INJECTION=true` is set
- Verify `ddtrace` is installed and instrumentation is active
- Ensure logs are generated within a traced request/span

### JSON Formatter Not Working

**Problem**: Logs are in text format, not JSON

**Solution**:
```bash
# Install python-json-logger
cd services/fastapi-backend
uv pip install python-json-logger

# Or using docker-compose
docker-compose build fastapi-backend
```

### Logs Not Appearing in Datadog

**Problem**: Logs don't show up in Datadog

**Solution**:
- Check Datadog Agent is running: `docker-compose ps datadog-agent`
- Verify `DD_API_KEY` is set correctly
- Check Agent logs: `docker-compose logs datadog-agent`
- Ensure logs are written to stdout (which the Agent collects)

### Trace IDs in Wrong Format

**Problem**: Trace IDs don't match between logs and APM

**Solution**:
- Logs use decimal format (from ddtrace SDK)
- Datadog UI uses hexadecimal format
- Both are correct, just different representations
- The Agent handles conversion automatically

## Best Practices

### ✅ DO: Use Structured Logging

```python
# Good: Structured with extra fields
logger.info(
    "Request processed",
    extra={
        "duration_ms": 123,
        "status": "success"
    }
)
```

### ❌ DON'T: String Formatting in Message

```python
# Bad: Hard to query and analyze
logger.info(f"Request processed in {duration_ms}ms with status {status}")
```

### ✅ DO: Include Context

```python
# Good: Include relevant business context
logger.info(
    "Vote extraction completed",
    extra={
        "pages_processed": 5,
        "reports_extracted": 3,
        "validation_passed": True
    }
)
```

### ✅ DO: Use Appropriate Log Levels

```python
logger.debug("Detailed diagnostic info")      # Development debugging
logger.info("Important business events")       # Normal operations
logger.warning("Recoverable issues")           # Attention needed
logger.error("Operation failures", exc_info=True)  # Errors with stack traces
```

### ✅ DO: Log at Key Points

```python
# Start of operation
logger.info("Starting vote extraction", extra={"pages": len(images)})

# Intermediate steps
logger.debug("Processed page 1 of 5")

# Completion
logger.info("Vote extraction completed", extra={"duration_ms": 1234})

# Errors
logger.error("Extraction failed", exc_info=True, extra={"reason": "invalid_image"})
```

## Related Documentation

- [Datadog APM Setup](../monitoring/DATADOG_APM.md)
- [Datadog LLMObs](../monitoring/DATADOG_LLMOBS.md)
- [Vote Extraction LLMObs Spans](./VOTE_EXTRACTION_LLMOBS_SPANS.md)
- [Validation Custom Evaluations](./VALIDATION_CUSTOM_EVALUATIONS.md)

## Summary

✅ **JSON structured logging** for better parsing and analysis  
✅ **Automatic trace correlation** via `DD_LOGS_INJECTION=true`  
✅ **Seamless navigation** between logs and traces in Datadog UI  
✅ **Complete observability** of distributed requests  
✅ **Easy debugging** with full request context  

This implementation provides production-ready logging with complete APM trace correlation for comprehensive application observability! 🎯

