FROM python:3.11-slim

# Datadog Source Code Integration - Git metadata
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Datadog serverless-init binary for Cloud Run APM
COPY --from=datadog/serverless-init:1 /datadog-init /app/datadog-init

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml README.md ./

# Install dependencies using uv
# Install from pyproject.toml (uses versions defined there, not hardcoded)
RUN uv pip install --system -e .

# Install Datadog tracer to specific directory for serverless-init
RUN pip install --target /dd_tracer/python/ ddtrace

# Copy application code
COPY . .

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /app/datadog-init

USER appuser

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Datadog tracing and logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DD_LOGS_ENABLED=true \
    DD_LOGS_INJECTION=true \
    DD_SOURCE=python \
    DD_TRACE_SAMPLE_RATE=1.0 \
    DD_TRACE_ENABLED=1 \
    PATH=/usr/local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# IMPORTANT: Use serverless-init as ENTRYPOINT for Cloud Run APM
ENTRYPOINT ["/app/datadog-init"]

# Run Streamlit with ddtrace-run for automatic instrumentation
CMD ["/dd_tracer/python/bin/ddtrace-run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
