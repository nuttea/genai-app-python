#!/bin/bash
# Setup Workload Identity Federation for GitHub Actions

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
GITHUB_ORG="${GITHUB_ORG:-}"
GITHUB_REPO="${GITHUB_REPO:-genai-app-python}"
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-provider"
SA_NAME="github-actions"

echo "🔐 Setting up Workload Identity Federation for GitHub Actions"
echo "=============================================================="
echo "Project: ${PROJECT_ID}"
echo "GitHub: ${GITHUB_ORG}/${GITHUB_REPO}"
echo ""

# Check required variables
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT is not set"
    exit 1
fi

if [ -z "$GITHUB_ORG" ]; then
    echo "❌ Error: GITHUB_ORG is not set"
    echo "   Set it with: export GITHUB_ORG=your-github-username"
    exit 1
fi

# Enable APIs
echo "📋 Enabling required APIs..."
gcloud services enable \
    iamcredentials.googleapis.com \
    cloudresourcemanager.googleapis.com \
    sts.googleapis.com \
    --project="${PROJECT_ID}"

# Create Workload Identity Pool
echo "🏊 Creating Workload Identity Pool..."
if gcloud iam workload-identity-pools describe ${POOL_NAME} \
    --project="${PROJECT_ID}" \
    --location="global" > /dev/null 2>&1; then
    echo "   Pool already exists"
else
    gcloud iam workload-identity-pools create ${POOL_NAME} \
        --project="${PROJECT_ID}" \
        --location="global" \
        --display-name="GitHub Actions Pool"
    echo "   ✅ Pool created"
fi

# Get pool ID
POOL_ID=$(gcloud iam workload-identity-pools describe ${POOL_NAME} \
    --project="${PROJECT_ID}" \
    --location="global" \
    --format="value(name)")

# Create Workload Identity Provider
echo "🔗 Creating Workload Identity Provider..."
if gcloud iam workload-identity-pools providers describe ${PROVIDER_NAME} \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_NAME}" > /dev/null 2>&1; then
    echo "   Provider already exists"
else
    gcloud iam workload-identity-pools providers create-oidc ${PROVIDER_NAME} \
        --project="${PROJECT_ID}" \
        --location="global" \
        --workload-identity-pool="${POOL_NAME}" \
        --display-name="GitHub Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --issuer-uri="https://token.actions.githubusercontent.com"
    echo "   ✅ Provider created"
fi

# Get provider ID
PROVIDER_ID=$(gcloud iam workload-identity-pools providers describe ${PROVIDER_NAME} \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_NAME}" \
    --format="value(name)")

# Create Service Account
echo "👤 Creating Service Account..."
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe ${SA_EMAIL} --project="${PROJECT_ID}" > /dev/null 2>&1; then
    echo "   Service account already exists"
else
    gcloud iam service-accounts create ${SA_NAME} \
        --project="${PROJECT_ID}" \
        --description="Service account for GitHub Actions deployments" \
        --display-name="GitHub Actions"
    echo "   ✅ Service account created"
fi

# Grant IAM Permissions
echo "🔓 Granting IAM permissions..."

ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/cloudbuild.builds.editor"
    "roles/storage.admin"
    "roles/secretmanager.secretAccessor"
)

for ROLE in "${ROLES[@]}"; do
    echo "   Granting ${ROLE}..."
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="${ROLE}" \
        --condition=None \
        > /dev/null 2>&1 || echo "   (already granted)"
done

echo "   ✅ Permissions granted"

# Allow GitHub to impersonate Service Account
echo "🔐 Configuring Workload Identity binding..."
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"

echo "   ✅ Binding configured"

# Display results
echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Add these secrets to your GitHub repository:"
echo "https://github.com/${GITHUB_ORG}/${GITHUB_REPO}/settings/secrets/actions"
echo ""
echo "GCP_PROJECT_ID=${PROJECT_ID}"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER=${PROVIDER_ID}"
echo "GCP_SERVICE_ACCOUNT_EMAIL=${SA_EMAIL}"
echo "GCP_REGION=us-central1"
echo ""
echo "Additional secrets needed:"
echo "- DD_API_KEY (from Datadog)"
echo "- DD_APP_KEY (from Datadog)"
echo "- DD_SITE (datadoghq.com)"
echo "- DD_RUM_CLIENT_TOKEN (from Datadog RUM app)"
echo "- DD_RUM_APPLICATION_ID (from Datadog RUM app)"
echo "- SLACK_WEBHOOK_URL (optional, for notifications)"
echo ""
echo "Test the setup:"
echo "  1. Add secrets to GitHub"
echo "  2. Push a change to services/fastapi-backend/"
echo "  3. Check GitHub Actions tab"
echo ""
