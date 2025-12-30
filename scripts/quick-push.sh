#!/bin/bash
# Cursor Custom Command: Quick Push (Auto-generate commit message)
# Usage: ./quick-push.sh

set -e

echo "🎨 Formatting code with Black..."
cd services/fastapi-backend && uv run black app/ && cd ../..
cd frontend/streamlit && uv run black . && cd ../..
echo "✅ Formatted!"
echo ""

echo "📝 Generating commit message from changes..."
# Get list of changed files
CHANGED_FILES=$(git diff --name-only --staged 2>/dev/null || git diff --name-only)

if [ -z "$CHANGED_FILES" ]; then
    # Stage all changes if nothing staged
    git add -A
    CHANGED_FILES=$(git diff --name-only --staged)
fi

if [ -z "$CHANGED_FILES" ]; then
    echo "❌ No changes to commit!"
    exit 1
fi

# Generate commit message
if echo "$CHANGED_FILES" | grep -q "\.yml$\|\.yaml$"; then
    COMMIT_MSG="chore: Update workflow configuration"
elif echo "$CHANGED_FILES" | grep -q "\.md$"; then
    COMMIT_MSG="docs: Update documentation"
elif echo "$CHANGED_FILES" | grep -q "services/fastapi-backend"; then
    COMMIT_MSG="fix: Update backend code"
elif echo "$CHANGED_FILES" | grep -q "frontend/streamlit"; then
    COMMIT_MSG="fix: Update frontend code"
else
    COMMIT_MSG="chore: Update code"
fi

echo "  Message: $COMMIT_MSG"
echo ""

git add -A
git commit -m "$COMMIT_MSG"
git push origin main

echo ""
echo "✅ Pushed! Latest commit:"
git log -1 --oneline
