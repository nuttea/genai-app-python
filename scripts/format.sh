#!/bin/bash
# Simple script to format code with Black before commit
# Designed to work with uv package manager
#
# Usage:
#   ./format.sh          - Format all code (backend + frontend)
#   ./format.sh backend  - Format only backend
#   ./format.sh frontend - Format only frontend

set -e

TARGET="${1:-all}"

format_backend() {
    echo "📦 Formatting backend..."
    cd services/fastapi-backend
    uv sync --all-extras --no-install-project >/dev/null 2>&1 || true
    if [ -d .venv ]; then
        .venv/bin/black app/ || uv run black app/
    else
        uv run black app/
    fi
    echo "✅ Backend formatted"
    cd ../..
}

format_frontend() {
    echo "📦 Formatting frontend..."
    cd frontend/streamlit
    uv sync --all-extras --no-install-project >/dev/null 2>&1 || true
    if [ -d .venv ]; then
        .venv/bin/black . || uv run black .
    else
        uv run black .
    fi
    echo "✅ Frontend formatted"
    cd ../..
}

echo "🎨 Formatting code with Black..."
echo ""

case "$TARGET" in
    backend)
        format_backend
        ;;
    frontend)
        format_frontend
        ;;
    all)
        format_backend
        format_frontend
        ;;
    *)
        echo "❌ Unknown target: $TARGET"
        echo "Usage: $0 [backend|frontend|all]"
        exit 1
        ;;
esac

echo ""
echo "✅ All requested code formatted successfully!"
echo "   You can now commit your changes."
