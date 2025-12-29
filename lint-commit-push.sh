#!/bin/bash
# Cursor Custom Command: Lint, Commit, and Push
# Usage: ./lint-commit-push.sh "your commit message"

set -e

COMMIT_MSG="${1:-chore: Update code}"

echo "🎨 Step 1/4: Formatting code with Black..."
echo ""

# Format backend
echo "  📦 Formatting backend..."
cd services/fastapi-backend
poetry run black app/
cd ../..

# Format frontend
echo "  📦 Formatting frontend..."
cd frontend/streamlit
poetry run black .
cd ../..

echo "✅ Formatting complete!"
echo ""

echo "🔧 Step 2/4: Linting and fixing with Ruff..."
echo ""

# Lint backend
echo "  🔍 Linting backend..."
cd services/fastapi-backend
poetry run ruff check --fix app/ || echo "  ⚠️  Some linting issues remain"
cd ../..

# Lint frontend
echo "  🔍 Linting frontend..."
cd frontend/streamlit
poetry run ruff check --fix . || echo "  ⚠️  Some linting issues remain"
cd ../..

echo "✅ Linting complete!"
echo ""

echo "📝 Step 3/4: Committing changes..."
echo "  Message: $COMMIT_MSG"
git add -A
git commit -m "$COMMIT_MSG" || {
    echo "❌ Commit failed. Maybe no changes to commit?"
    exit 1
}
echo "✅ Committed!"
echo ""

echo "🚀 Step 4/4: Pushing to remote..."
git push origin main
echo "✅ Pushed to main!"
echo ""

echo "======================================"
echo "✅ ALL DONE!"
echo "======================================"
echo ""
echo "📊 Latest commit:"
git log -1 --oneline
echo ""
echo "🌐 Check CI/CD: https://github.com/nuttea/genai-app-python/actions"

