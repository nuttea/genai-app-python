#!/bin/bash
# Helper script to build Docker images with Datadog Source Code Integration

set -e

# Get Git metadata
GIT_REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "unknown")
GIT_COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")

echo "🔍 Git Metadata:"
echo "  Repository: $GIT_REPO_URL"
echo "  Commit SHA: $GIT_COMMIT_SHA"
echo ""

# Export for docker-compose
export DD_GIT_REPOSITORY_URL="$GIT_REPO_URL"
export DD_GIT_COMMIT_SHA="$GIT_COMMIT_SHA"

# Build with docker-compose
echo "🐳 Building with Datadog Source Code Integration..."
docker-compose build "$@"

echo "✅ Build complete!"
echo ""
echo "💡 To run: docker-compose up"

