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
uv sync --all-extras --no-install-project >/dev/null 2>&1 || true
if [ -d .venv ]; then
    .venv/bin/black app/ || uv run black app/
else
    uv run black app/
fi
cd ../..

# Format frontend
echo "  📦 Formatting frontend..."
cd frontend/streamlit
uv sync --all-extras --no-install-project >/dev/null 2>&1 || true
if [ -d .venv ]; then
    .venv/bin/black . || uv run black .
else
    uv run black .
fi
cd ../..

echo "✅ Formatting complete!"
echo ""

echo "🔧 Step 2/4: Linting and fixing with Ruff..."
echo ""

# Lint backend
echo "  🔍 Linting backend..."
cd services/fastapi-backend
uv sync --all-extras --no-install-project >/dev/null 2>&1 || true
if [ -d .venv ]; then
    .venv/bin/ruff check --fix app/ || uv run ruff check --fix app/ || echo "  ⚠️  Some linting issues remain"
else
    uv run ruff check --fix app/ || echo "  ⚠️  Some linting issues remain"
fi
cd ../..

# Lint frontend
echo "  🔍 Linting frontend..."
cd frontend/streamlit
uv sync --all-extras --no-install-project >/dev/null 2>&1 || true
if [ -d .venv ]; then
    .venv/bin/ruff check --fix . || uv run ruff check --fix . || echo "  ⚠️  Some linting issues remain"
else
    uv run ruff check --fix . || echo "  ⚠️  Some linting issues remain"
fi
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

