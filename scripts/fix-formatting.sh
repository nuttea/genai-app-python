#!/bin/bash
# Quick fix script to format code with Black

set -e

echo "🎨 Formatting code to fix CI/CD failure..."
echo ""

# Format backend
echo "📦 Formatting backend..."
cd services/fastapi-backend
if command -v uv &> /dev/null; then
    uv run black app/
else
    python3 -m black app/
fi
cd ../..
echo "✅ Backend formatted"

# Format frontend
echo "📦 Formatting frontend..."
cd frontend/streamlit
if command -v uv &> /dev/null; then
    uv run black .
else
    python3 -m black .
fi
cd ../..
echo "✅ Frontend formatted"

echo ""
echo "✅ All code formatted!"
echo ""
echo "Now run:"
echo "  git add -A"
echo "  git commit -m 'fix: Apply Black formatting to pass CI/CD checks'"
echo "  git push"
