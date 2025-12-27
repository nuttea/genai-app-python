#!/bin/bash
# Deploy both FastAPI backend and Streamlit frontend to Cloud Run

set -e

# Load environment variables if .env exists
if [ -f ../../.env ]; then
    source ../../.env
fi

echo "🚀 Deploying GenAI Application to Google Cloud Run"
echo "===================================================="
echo ""

# Check if project is set
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT is not set"
    echo "   Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION:-us-central1}"
echo ""

# Check for secrets
echo "🔍 Checking secrets..."
if gcloud secrets describe api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
    echo "   ✅ api-key secret exists"
else
    echo "   ⚠️  api-key secret not found (API key validation will be disabled)"
fi

if gcloud secrets describe dd-api-key --project="${PROJECT_ID}" > /dev/null 2>&1; then
    echo "   ✅ dd-api-key secret exists"
else
    echo "   ℹ️  dd-api-key secret not found (Datadog monitoring will be disabled)"
fi
echo ""

# Confirm deployment
read -p "Deploy to Cloud Run? This will incur costs. (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

# Deploy backend first
echo ""
echo "Step 1/2: Deploying Backend..."
echo "=============================="
./deploy-backend.sh

# Deploy frontend
echo ""
echo "Step 2/2: Deploying Frontend..."
echo "==============================="
./deploy-frontend.sh

# Get URLs
BACKEND_SERVICE="genai-fastapi-backend"
FRONTEND_SERVICE="genai-streamlit-frontend"
REGION="${REGION:-us-central1}"

BACKEND_URL=$(gcloud run services describe ${BACKEND_SERVICE} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project="${PROJECT_ID}" 2>/dev/null || echo "Not deployed")

FRONTEND_URL=$(gcloud run services describe ${FRONTEND_SERVICE} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project="${PROJECT_ID}" 2>/dev/null || echo "Not deployed")

echo ""
echo "🎉 Deployment Complete!"
echo "======================================================"
echo ""
echo "📊 Deployed Services:"
echo "   Backend:  ${BACKEND_URL}"
echo "   Frontend: ${FRONTEND_URL}"
echo ""
echo "🔗 Quick Links:"
echo "   Application:  ${FRONTEND_URL}"
echo "   API Docs:     ${BACKEND_URL}/docs"
echo "   Health Check: ${BACKEND_URL}/health"
echo ""
echo "📝 Management Commands:"
echo ""
echo "View Backend Logs:"
echo "  gcloud run services logs read ${BACKEND_SERVICE} --region ${REGION}"
echo ""
echo "View Frontend Logs:"
echo "  gcloud run services logs read ${FRONTEND_SERVICE} --region ${REGION}"
echo ""
echo "Update Backend:"
echo "  cd infra/cloud-run && ./deploy-backend.sh"
echo ""
echo "Update Frontend:"
echo "  cd infra/cloud-run && ./deploy-frontend.sh"
echo ""
echo "Delete Services (to avoid charges):"
echo "  gcloud run services delete ${BACKEND_SERVICE} --region ${REGION}"
echo "  gcloud run services delete ${FRONTEND_SERVICE} --region ${REGION}"
echo ""
echo "💰 Cost Optimization:"
echo "   - Services scale to zero when not in use"
echo "   - You only pay for actual usage"
echo "   - Set --max-instances to control costs"
echo ""
