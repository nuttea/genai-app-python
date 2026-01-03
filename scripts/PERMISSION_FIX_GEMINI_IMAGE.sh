#!/bin/bash

# Fix Permission Denied Error for Gemini 3 Pro Image Model
# This script grants the required IAM permission to the Cloud Run service account

set -e

PROJECT_ID="datadog-ese-sandbox"
SERVICE_ACCOUNT="449012790678-compute@developer.gserviceaccount.com"
ROLE="roles/aiplatform.user"

echo "🔐 Granting Vertex AI User permission to Cloud Run service account..."
echo "   Project: $PROJECT_ID"
echo "   Service Account: $SERVICE_ACCOUNT"
echo "   Role: $ROLE"
echo ""

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="$ROLE" \
  --condition=None

echo ""
echo "✅ Permission granted successfully!"
echo ""
echo "📊 Verifying permissions..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT AND bindings.role:$ROLE" \
  --format="table(bindings.role)"

echo ""
echo "🎉 Done! The service can now access Gemini 3 Pro Image model."
echo ""
echo "🧪 Test by making an image generation request."
echo "   The traces will now show HTTP 503 (Service Unavailable) instead of 200 if there are permission issues."

