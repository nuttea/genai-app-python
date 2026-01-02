#!/bin/bash

# Quick Fix for Gemini 3 Pro Image Permission Error
# Run these commands to grant the necessary IAM permissions

set -e

echo "🔍 Getting Cloud Run service account..."
SERVICE_ACCOUNT=$(gcloud run services describe genai-adk-python \
  --region us-central1 \
  --project datadog-ese-sandbox \
  --format 'value(spec.template.spec.serviceAccountName)')

if [ -z "$SERVICE_ACCOUNT" ]; then
  echo "⚠️  No custom service account found, using default compute service account"
  PROJECT_NUMBER=$(gcloud projects describe datadog-ese-sandbox \
    --format='value(projectNumber)')
  SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
fi

echo "📧 Service Account: $SERVICE_ACCOUNT"

echo "✅ Granting Vertex AI User role..."
gcloud projects add-iam-policy-binding datadog-ese-sandbox \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/aiplatform.user"

echo "✅ Done! Waiting 60 seconds for IAM propagation..."
sleep 60

echo "🧪 Testing image generation..."
curl -X POST https://genai-adk-python-cn4wkmlbva-uc.a.run.app/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A simple test image of a happy robot",
    "image_type": "illustration",
    "aspect_ratio": "1:1",
    "session_id": "test_fix"
  }' | jq '.'

echo "✅ Fix complete! Check the response above."

