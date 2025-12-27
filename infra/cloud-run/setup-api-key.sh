#!/bin/bash
# Setup API key in Google Cloud Secret Manager

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"

echo "🔐 Setting up API Key in Google Cloud Secret Manager"
echo "====================================================="
echo "Project: ${PROJECT_ID}"
echo ""

# Check if project is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT is not set"
    exit 1
fi

# Generate or use provided API key
if [ -z "$API_KEY" ]; then
    echo "📝 Generating secure API key..."
    API_KEY=$(openssl rand -hex 32)
    echo "   Generated: ${API_KEY:0:8}...${API_KEY: -8}"
    echo ""
    echo "⚠️  SAVE THIS API KEY - you'll need it for the frontend!"
    echo "   API_KEY=${API_KEY}"
    echo ""
else
    echo "✅ Using provided API key"
fi

# Enable Secret Manager API
echo "📋 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project="${PROJECT_ID}"

# Create api-key secret
echo "🔑 Creating api-key secret..."
if gcloud secrets describe api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
    echo "   Secret 'api-key' already exists"
    read -p "   Update existing secret? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "${API_KEY}" | gcloud secrets versions add api-key \
            --data-file=- \
            --project="${PROJECT_ID}"
        echo "   ✅ Secret updated"
    fi
else
    echo -n "${API_KEY}" | gcloud secrets create api-key \
        --data-file=- \
        --replication-policy="automatic" \
        --project="${PROJECT_ID}"
    echo "   ✅ Secret created"
fi

# Grant access to Cloud Run service accounts
echo "🔓 Granting access to Cloud Run services..."

# Get project number
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')

# Default compute service account (used by Cloud Run)
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant backend access
echo "   Granting access to backend service..."
gcloud secrets add-iam-policy-binding api-key \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="${PROJECT_ID}"

# Grant frontend access
echo "   Granting access to frontend service..."
gcloud secrets add-iam-policy-binding api-key \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="${PROJECT_ID}"

# Grant access to Cloud Build (for CI/CD)
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
gcloud secrets add-iam-policy-binding api-key \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="${PROJECT_ID}"

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "API Key: ${API_KEY}"
echo ""
echo "⚠️  IMPORTANT: Save this API key securely!"
echo ""
echo "Secrets created:"
echo "  - api-key"
echo ""
echo "Access granted to:"
echo "  - Cloud Run (backend): ${COMPUTE_SA}"
echo "  - Cloud Run (frontend): ${COMPUTE_SA}"
echo "  - Cloud Build: ${CLOUD_BUILD_SA}"
echo ""
echo "Next steps:"
echo "  1. Deploy backend with API key:"
echo "     export API_KEY_REQUIRED=true"
echo "     cd infra/cloud-run && ./deploy-backend.sh"
echo ""
echo "  2. Deploy frontend with API key:"
echo "     ./deploy-frontend.sh"
echo ""
echo "  3. Test with API key:"
echo "     curl -H 'X-API-Key: ${API_KEY}' https://your-backend-url.run.app/health"
echo ""
