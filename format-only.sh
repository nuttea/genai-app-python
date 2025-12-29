#!/bin/bash
# Cursor Custom Command: Format Only (No Commit)
# Usage: ./format-only.sh

set -e

echo "🎨 Formatting all code with Black..."
echo ""

# Format backend
echo "📦 Formatting backend..."
cd services/fastapi-backend
poetry run black app/
cd ../..

# Format frontend
echo "📦 Formatting frontend..."
cd frontend/streamlit
poetry run black .
cd ../..

echo ""
echo "✅ All code formatted!"
echo ""
echo "💡 Next steps:"
echo "  1. Review the changes"
echo "  2. Run: git add -A"
echo "  3. Run: git commit -m 'your message'"
echo "  4. Run: git push"
echo ""
echo "Or use: ./lint-commit-push.sh 'your message'"

