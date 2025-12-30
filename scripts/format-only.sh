#!/bin/bash
# Format all Python code with Black
# Usage: ./scripts/format-only.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🎨 Formatting all code with Black..."
echo ""

# Format backend
echo "📦 Formatting backend..."
cd services/fastapi-backend
uv run black app/
cd ../..
echo "✅ Backend formatted!"
echo ""

# Format frontend
echo "📦 Formatting frontend..."
cd frontend/streamlit
uv run black .
cd ../..
echo "✅ Frontend formatted!"
echo ""

echo "✅ All code formatted!"
echo ""
echo "💡 Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Stage changes: git add -A"
echo "  3. Commit: git commit -m 'your message'"
echo "  4. Push: git push"
echo ""
echo "Or use: ./lint-commit-push.sh 'your message'"
