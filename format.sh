#!/bin/bash
# Simple script to format code with Black before commit
# Designed to work with scfw/poetry setup
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
    scfw run poetry run black app/
    echo "✅ Backend formatted"
    cd ../..
}

format_frontend() {
    echo "📦 Formatting frontend..."
    cd frontend/streamlit
    scfw run poetry run black .
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

