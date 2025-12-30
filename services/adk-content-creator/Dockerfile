# Local development Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies (uv will create a virtual environment)
RUN uv sync

# Copy application code
COPY app/ ./app/

# Create uploads directory
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8002

# Expose port
EXPOSE 8002

# Run the application with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]

