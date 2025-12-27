#!/bin/bash
set -e

# Start FastAPI with Uvicorn
echo "Starting FastAPI backend..."
exec uvicorn app.main:app \
    --host "${FASTAPI_HOST:-0.0.0.0}" \
    --port "${FASTAPI_PORT:-8000}" \
    --log-level "${LOG_LEVEL:-info}" \
    "$@"
