#!/bin/bash
# Deploy Streamlit frontend to Google Cloud Run

set -e

source ../../.env

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="genai-streamlit-frontend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Backend URL (can be provided or read from previous deployment)
if [ -f /tmp/backend-url.txt ]; then
    BACKEND_URL=$(cat /tmp/backend-url.txt)
else
    BACKEND_URL="${BACKEND_URL:-}"
fi

# Datadog Configuration (optional)
DD_API_KEY="${DD_API_KEY:-}"
DD_SITE="${DD_SITE:-datadoghq.com}"
DD_SERVICE="${DD_SERVICE:-genai-streamlit-frontend}"
DD_ENV="${DD_ENV:-production}"
DD_VERSION="${DD_VERSION:-$(git rev-parse --short HEAD 2>/dev/null || echo '0.1.0')}"

# Datadog RUM Configuration (optional)
DD_RUM_CLIENT_TOKEN="${DD_RUM_CLIENT_TOKEN:-}"
DD_RUM_APPLICATION_ID="${DD_RUM_APPLICATION_ID:-}"

echo "🚀 Deploying Streamlit Frontend to Cloud Run"
echo "=========================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_NAME}"
echo "Backend URL: ${BACKEND_URL}"
echo ""

# Check if project is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT is not set"
    echo "   Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

# Check if backend URL is set
if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  Warning: Backend URL not set"
    echo "   The frontend won't be able to connect to the backend"
    echo "   Set it with: export BACKEND_URL=https://your-backend-url.run.app"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set gcloud project
gcloud config set project "${PROJECT_ID}"

# Build and push Docker image
echo "🐳 Building Docker image..."
cd ../../frontend/streamlit
gcloud builds submit \
    --tag "${IMAGE_NAME}" \
    --project="${PROJECT_ID}"

echo "✅ Image built and pushed"
echo ""

# Check if API key is in Secret Manager
API_KEY_SECRET=""
if gcloud secrets describe api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
    echo "🔐 Using API_KEY from Secret Manager"
    API_KEY_SECRET="--set-secrets=API_KEY=api-key:latest"
else
    echo "⚠️  API key not found in Secret Manager"
    echo "   If API key validation is enabled on backend, frontend won't be able to connect"
    echo "   Setup API key: ./setup-api-key.sh"
fi

# Build the deploy command
DEPLOY_CMD="gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --set-env-vars API_BASE_URL=${BACKEND_URL} \
    --set-env-vars FASTAPI_ENV=production \
    ${API_KEY_SECRET} \
    --project=${PROJECT_ID}"

# Add Datadog configuration
DD_SECRET_EXISTS=false
if gcloud secrets describe dd-api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
    DD_SECRET_EXISTS=true
fi

DD_RUM_ENABLED=false
if [ -n "$DD_RUM_CLIENT_TOKEN" ] && [ -n "$DD_RUM_APPLICATION_ID" ]; then
    DD_RUM_ENABLED=true
fi

if [ "$DD_SECRET_EXISTS" = "true" ] || [ "$DD_RUM_ENABLED" = "true" ]; then
    echo "📊 Datadog enabled for frontend"
    echo "   Service: ${DD_SERVICE}"
    echo "   Environment: ${DD_ENV}"
    echo "   Version: ${DD_VERSION}"

    # Always set Datadog env vars
    DEPLOY_CMD="${DEPLOY_CMD} \
        --set-env-vars DD_SITE=${DD_SITE} \
        --set-env-vars DD_SERVICE=${DD_SERVICE} \
        --set-env-vars DD_ENV=${DD_ENV} \
        --set-env-vars DD_VERSION=${DD_VERSION}"

    # Add API key from Secret Manager if exists
    if [ "$DD_SECRET_EXISTS" = "true" ]; then
        echo "   🔐 Using DD_API_KEY from Secret Manager"
        DEPLOY_CMD="${DEPLOY_CMD} --set-secrets=DD_API_KEY=dd-api-key:latest"
    fi

    # Add RUM configuration if provided
    if [ "$DD_RUM_ENABLED" = "true" ]; then
        echo "   🌐 Datadog RUM enabled"
        echo "      Client Token: ${DD_RUM_CLIENT_TOKEN:0:10}..."
        echo "      Application ID: ${DD_RUM_APPLICATION_ID}"
        DEPLOY_CMD="${DEPLOY_CMD} \
            --set-env-vars DD_RUM_CLIENT_TOKEN=${DD_RUM_CLIENT_TOKEN} \
            --set-env-vars DD_RUM_APPLICATION_ID=${DD_RUM_APPLICATION_ID}"
    else
        echo "   ℹ️  Datadog RUM not configured"
        echo "      Set DD_RUM_CLIENT_TOKEN and DD_RUM_APPLICATION_ID to enable"
    fi
else
    echo "ℹ️  Datadog not configured for frontend"
    echo "   To enable logs: ./setup-datadog-secrets.sh"
    echo "   To enable RUM: Set DD_RUM_CLIENT_TOKEN and DD_RUM_APPLICATION_ID"
fi

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
eval $DEPLOY_CMD

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project="${PROJECT_ID}")

echo ""
echo "✅ Deployment complete!"
echo "=========================================="
echo "Frontend URL: ${SERVICE_URL}"
echo "Backend URL: ${BACKEND_URL}"
echo ""
echo "🎉 Your GenAI application is now live!"
echo ""
echo "Access the application:"
echo "  ${SERVICE_URL}"
echo ""
echo "To view logs:"
echo "  gcloud run services logs read ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "To update backend URL later:"
echo "  gcloud run services update ${SERVICE_NAME} --region ${REGION} --set-env-vars API_BASE_URL=NEW_URL"
echo ""
