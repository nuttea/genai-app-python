# Use Python 3.11 slim image
FROM python:3.11-slim

# Datadog Source Code Integration - Git metadata
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy Datadog serverless-init for Cloud Run APM
COPY --from=datadog/serverless-init:1 /datadog-init /app/datadog-init

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
# Extract and install production dependencies from pyproject.toml
RUN uv pip install --system \
    "fastapi>=0.109.0" \
    "uvicorn[standard]>=0.27.0" \
    "python-multipart>=0.0.9" \
    "google-cloud-aiplatform>=1.42.1" \
    "google-auth>=2.27.0" \
    "google-genai>=0.2.0" \
    "pydantic>=2.5.3" \
    "pydantic-settings>=2.1.0" \
    "python-dotenv>=1.0.0" \
    "httpx>=0.26.0" \
    "aiohttp>=3.9.1" \
    "python-json-logger>=2.0.7" \
    "structlog>=24.1.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    "ddtrace>=2.0.0" \
    "opentelemetry-api>=1.20.0" \
    "slowapi>=0.1.9"

# Install Datadog tracer to specific directory for serverless-init
RUN pip install --target /dd_tracer/python/ ddtrace

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FASTAPI_HOST=0.0.0.0 \
    FASTAPI_PORT=8000 \
    PATH=/usr/local/bin:$PATH \
    DD_LOGS_ENABLED=true \
    DD_LOGS_INJECTION=true \
    DD_SOURCE=python \
    DD_TRACE_SAMPLE_RATE=1.0 \
    DD_PROFILING_ENABLED=true

# IMPORTANT: Use serverless-init as ENTRYPOINT for Cloud Run
ENTRYPOINT ["/app/datadog-init"]

# Run application with ddtrace-run for automatic instrumentation
CMD ["/dd_tracer/python/bin/ddtrace-run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
