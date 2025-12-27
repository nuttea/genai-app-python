#!/bin/bash
# Deploy FastAPI backend to Google Cloud Run

set -e

source ../../.env

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="genai-fastapi-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# API Key Configuration
API_KEY_REQUIRED="${API_KEY_REQUIRED:-false}"

# Datadog APM and LLMObs (optional)
DD_API_KEY="${DD_API_KEY:-}"
DD_SITE="${DD_SITE:-datadoghq.com}"
DD_SERVICE="${DD_SERVICE:-genai-fastapi-backend}"
DD_ENV="${DD_ENV:-production}"
DD_VERSION="${DD_VERSION:-$(git rev-parse --short HEAD 2>/dev/null || echo '0.1.0')}"
DD_LLMOBS_ML_APP="${DD_LLMOBS_ML_APP:-}"
DD_LLMOBS_ENABLED="${DD_LLMOBS_ENABLED:-0}"

echo "🚀 Deploying FastAPI Backend to Cloud Run"
echo "=========================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_NAME}"
echo ""

# Check if project is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT is not set"
    echo "   Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

# Set gcloud project
gcloud config set project "${PROJECT_ID}"

# Enable required APIs
echo "📋 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    --project="${PROJECT_ID}"

echo "✅ APIs enabled"
echo ""

# Build and push Docker image
echo "🐳 Building Docker image..."
cd ../../services/fastapi-backend
gcloud builds submit \
    --tag "${IMAGE_NAME}" \
    --project="${PROJECT_ID}"

echo "✅ Image built and pushed"
echo ""

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."

# Build the deploy command
DEPLOY_CMD="gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID} \
    --set-env-vars VERTEX_AI_LOCATION=${REGION} \
    --set-env-vars FASTAPI_ENV=production \
    --set-env-vars LOG_LEVEL=info \
    --set-env-vars CORS_ORIGINS=* \
    --set-env-vars DEFAULT_MODEL=gemini-2.5-flash \
    --set-env-vars DEFAULT_TEMPERATURE=0.0 \
    --set-env-vars DEFAULT_MAX_TOKENS=32768 \
    --project=${PROJECT_ID}"

# Add Datadog APM configuration
DD_SECRET_EXISTS=false
if gcloud secrets describe dd-api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
    DD_SECRET_EXISTS=true
fi

if [ "$DD_SECRET_EXISTS" = "true" ] || [ -n "$DD_API_KEY" ]; then
    echo "📊 Datadog APM enabled"
    echo "   Service: ${DD_SERVICE}"
    echo "   Environment: ${DD_ENV}"
    echo "   Version: ${DD_VERSION}"

    # Always set Datadog configuration env vars
    DEPLOY_CMD="${DEPLOY_CMD} \
        --set-env-vars DD_SITE=${DD_SITE} \
        --set-env-vars DD_SERVICE=${DD_SERVICE} \
        --set-env-vars DD_ENV=${DD_ENV} \
        --set-env-vars DD_VERSION=${DD_VERSION} \
        --set-env-vars DD_LOGS_ENABLED=true \
        --set-env-vars DD_LOGS_INJECTION=true \
        --set-env-vars DD_SOURCE=python \
        --set-env-vars DD_TRACE_SAMPLE_RATE=1.0 \
        --set-env-vars DD_TRACE_ENABLED=1 \
        --set-env-vars DD_PROFILING_ENABLED=true \
        --set-env-vars DD_CODE_ORIGIN_FOR_SPANS_ENABLED=true"

    # Always use Secret Manager for DD_API_KEY
    if [ "$DD_SECRET_EXISTS" = "true" ]; then
        echo "   🔐 Using DD_API_KEY from Secret Manager"
        DEPLOY_CMD="${DEPLOY_CMD} --set-secrets=DD_API_KEY=dd-api-key:latest"
    else
        echo "   ⚠️  DD_API_KEY secret not found in Secret Manager"
        echo "   Creating dd-api-key secret..."
        if [ -n "$DD_API_KEY" ]; then
            echo -n "${DD_API_KEY}" | gcloud secrets create dd-api-key \
                --data-file=- \
                --replication-policy="automatic" \
                --project="${PROJECT_ID}"

            # Grant access
            PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')
            COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
            gcloud secrets add-iam-policy-binding dd-api-key \
                --member="serviceAccount:${COMPUTE_SA}" \
                --role="roles/secretmanager.secretAccessor" \
                --project="${PROJECT_ID}"

            echo "   ✅ Created and using DD_API_KEY from Secret Manager"
            DEPLOY_CMD="${DEPLOY_CMD} --set-secrets=DD_API_KEY=dd-api-key:latest"
        else
            echo "   ❌ DD_API_KEY not provided and secret doesn't exist"
            echo "   Run: ./setup-datadog-secrets.sh"
            exit 1
        fi
    fi

    # Add LLMObs if configured
    if [ -n "$DD_LLMOBS_ML_APP" ]; then
        echo "   LLMObs ML App: ${DD_LLMOBS_ML_APP}"
        DEPLOY_CMD="${DEPLOY_CMD} \
            --set-env-vars DD_LLMOBS_ML_APP=${DD_LLMOBS_ML_APP} \
            --set-env-vars DD_LLMOBS_ENABLED=1"
    fi
else
    echo "ℹ️  Datadog APM not configured"
    echo "   To enable: export DD_API_KEY=your-key && ./setup-datadog-secrets.sh"
fi

# Add API key from Secret Manager if required
if [ "$API_KEY_REQUIRED" = "true" ]; then
    if gcloud secrets describe api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
        echo "🔐 Using API_KEY from Secret Manager"
        DEPLOY_CMD="${DEPLOY_CMD} --set-secrets=API_KEY=api-key:latest"
    else
        echo "❌ Error: API_KEY_REQUIRED=true but api-key secret not found"
        echo "   Create the secret first:"
        echo "   ./setup-api-key.sh"
        exit 1
    fi
fi

# Note: DD_API_KEY is already added above in the Datadog APM configuration section

# Execute deployment
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
echo "Service URL: ${SERVICE_URL}"
echo "API Docs: ${SERVICE_URL}/docs"
echo "Health Check: ${SERVICE_URL}/health"
echo ""
echo "Test the deployment:"
echo "  curl ${SERVICE_URL}/health"
echo ""
echo "To view logs:"
echo "  gcloud run services logs read ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "To update environment variables:"
echo "  gcloud run services update ${SERVICE_NAME} --region ${REGION} --set-env-vars KEY=VALUE"
echo ""

# Save the URL to a file for the frontend deployment
echo "${SERVICE_URL}" > /tmp/backend-url.txt
echo "Backend URL saved for frontend deployment"
