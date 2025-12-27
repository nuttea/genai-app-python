#!/bin/bash
# Setup Datadog secrets in Google Cloud Secret Manager

set -e

source ../../.env

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"

echo "🔐 Setting up Datadog Secrets in Google Cloud"
echo "=============================================="
echo "Project: ${PROJECT_ID}"
echo ""

# Check if project is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT is not set"
    exit 1
fi

# Check if DD_API_KEY is set
if [ -z "$DD_API_KEY" ]; then
    echo "❌ Error: DD_API_KEY environment variable is not set"
    echo ""
    echo "Please set your Datadog API key:"
    echo "  export DD_API_KEY=your-datadog-api-key"
    echo ""
    echo "Get your API key from:"
    echo "  https://app.datadoghq.com/organization-settings/api-keys"
    exit 1
fi

# Enable Secret Manager API
echo "📋 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project="${PROJECT_ID}"

# Create DD_API_KEY secret
echo "🔑 Creating dd-api-key secret..."
if gcloud secrets describe dd-api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
    echo "   Secret 'dd-api-key' already exists"
    read -p "   Update existing secret? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "${DD_API_KEY}" | gcloud secrets versions add dd-api-key \
            --data-file=- \
            --project="${PROJECT_ID}"
        echo "   ✅ Secret updated"
    fi
else
    echo -n "${DD_API_KEY}" | gcloud secrets create dd-api-key \
        --data-file=- \
        --replication-policy="automatic" \
        --project="${PROJECT_ID}"
    echo "   ✅ Secret created"
fi

# Grant access to Cloud Run service account
echo "🔓 Granting access to Cloud Run..."

# Get Cloud Run service account
SERVICE_ACCOUNT=$(gcloud iam service-accounts list \
    --filter="email:${PROJECT_ID}-compute@developer.gserviceaccount.com" \
    --format="value(email)" \
    --project="${PROJECT_ID}")

if [ -z "$SERVICE_ACCOUNT" ]; then
    # Use default compute service account
    PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')
    SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
fi

echo "   Service Account: ${SERVICE_ACCOUNT}"

gcloud secrets add-iam-policy-binding dd-api-key \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="${PROJECT_ID}"

echo "   ✅ Access granted"

# Grant access to Cloud Build service account (for CI/CD)
echo "🔓 Granting access to Cloud Build..."
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud secrets add-iam-policy-binding dd-api-key \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="${PROJECT_ID}"

echo "   ✅ Access granted"

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Secrets created:"
echo "  - dd-api-key"
echo ""
echo "Access granted to:"
echo "  - Cloud Run: ${SERVICE_ACCOUNT}"
echo "  - Cloud Build: ${CLOUD_BUILD_SA}"
echo ""
echo "Next steps:"
echo "  1. Deploy with secrets: cd infra/cloud-run && ./deploy-backend.sh"
echo "  2. Or update existing service:"
echo "     gcloud run services update genai-fastapi-backend \\"
echo "       --region us-central1 \\"
echo "       --set-secrets=DD_API_KEY=dd-api-key:latest"
echo ""
