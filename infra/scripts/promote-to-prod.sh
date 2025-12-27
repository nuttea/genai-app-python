#!/bin/bash
# Helper script to promote main branch to production via Pull Request

set -e

echo "🚀 Promote to Production"
echo "======================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Ensure we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: You're on branch '$CURRENT_BRANCH', not 'main'"
    read -p "Switch to main branch? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

# Pull latest changes
echo "📥 Pulling latest changes from main..."
git pull origin main

# Check if prod branch exists
if ! git rev-parse --verify prod > /dev/null 2>&1; then
    echo "⚠️  prod branch doesn't exist locally"
    read -p "Fetch prod branch from remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git fetch origin prod:prod
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

# Show diff between main and prod
echo ""
echo "📊 Changes to be promoted:"
echo "=========================="
git log prod..main --oneline --no-decorate | head -20

COMMIT_COUNT=$(git log prod..main --oneline | wc -l | tr -d ' ')
echo ""
echo "Total commits: $COMMIT_COUNT"
echo ""

# Confirm promotion
read -p "Create Pull Request to promote these changes to production? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

# Get PR title and body
echo ""
echo "📝 Pull Request Details"
echo "======================="
read -p "PR Title (default: 'Release: Deploy to production'): " PR_TITLE
PR_TITLE=${PR_TITLE:-"Release: Deploy to production"}

echo "PR Description (optional, press Enter to skip):"
read -p "> " PR_BODY

if [ -z "$PR_BODY" ]; then
    # Generate automatic description
    PR_BODY="## 🚀 Production Deployment

### Changes
\`\`\`
$(git log prod..main --oneline --no-decorate | head -10)
\`\`\`

### Checklist
- [ ] All tests passing on main
- [ ] Code reviewed
- [ ] No known issues
- [ ] Ready for production

### Commits
$COMMIT_COUNT commits from main branch

### Monitoring
- Datadog: env:prod
- Cloud Run: revision tag 'prod'
"
fi

# Create Pull Request
echo ""
echo "📤 Creating Pull Request..."
PR_URL=$(gh pr create \
    --base prod \
    --head main \
    --title "$PR_TITLE" \
    --body "$PR_BODY")

echo ""
echo "✅ Pull Request created!"
echo "🔗 URL: $PR_URL"
echo ""
echo "📋 Next steps:"
echo "  1. Review the PR: $PR_URL"
echo "  2. Ensure all checks pass"
echo "  3. Get approval (if required)"
echo "  4. Merge the PR"
echo "  5. Monitor deployment in GitHub Actions"
echo "  6. Verify production URLs:"
echo "     - Backend:  https://genai-fastapi-backend-prod-HASH.run.app"
echo "     - Frontend: https://genai-streamlit-frontend-prod-HASH.run.app"
echo ""
echo "🔍 Monitor in Datadog with: env:prod"

