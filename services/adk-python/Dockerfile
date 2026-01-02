# Local development Dockerfile
FROM python:3.11-slim

# Install system dependencies
# Note: ffmpeg/OpenCV not needed - Gemini 2.5 Flash handles multimodal natively
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies using pip (simpler for Docker)
RUN uv pip install --system -e .

# Copy application code and ADK agents
COPY app/ ./app/
COPY content_creator_agent/ ./content_creator_agent/
COPY image_creator_agent/ ./image_creator_agent/
COPY main_adk.py ./

# Create uploads directory
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8002

# Expose port
EXPOSE 8002

# Run with hypercorn (supports HTTP/2)
# Hypercorn supports h2c (HTTP/2 Cleartext) by default
# Using full ADK with get_fast_api_app()
CMD ["hypercorn", "main_adk:app", "--bind", "0.0.0.0:8002", "--worker-class", "asyncio"]

