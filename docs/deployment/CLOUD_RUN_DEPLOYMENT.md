# Google Cloud Run Deployment Guide

Complete guide for deploying the GenAI Application Platform to Google Cloud Run.

## Overview

This guide covers deploying both services to Cloud Run:
- **FastAPI Backend** - API server with Vertex AI integration
- **Streamlit Frontend** - Interactive web interface

## Prerequisites

### Required
- ✅ Google Cloud Platform account with billing enabled
- ✅ gcloud CLI installed and configured
- ✅ Docker installed (for local building)
- ✅ Project with Vertex AI API enabled

### Setup gcloud

```bash
# Install gcloud CLI (if not installed)
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install

# Initialize gcloud
gcloud init

# Set your project
export GOOGLE_CLOUD_PROJECT=your-project-id
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Authenticate
gcloud auth login
gcloud auth application-default login
```

## Quick Deployment

### Option 1: Deploy Everything (Recommended)

```bash
# Navigate to deployment scripts
cd infra/cloud-run

# Set your project
export GOOGLE_CLOUD_PROJECT=your-project-id

# Optional: Set Datadog credentials
export DD_LLMOBS_ML_APP=your-ml-app
export DD_API_KEY=your-datadog-api-key

# Deploy both services
./deploy-all.sh
```

This will:
1. ✅ Enable required Google Cloud APIs
2. ✅ Build and push Docker images
3. ✅ Deploy FastAPI backend
4. ✅ Deploy Streamlit frontend
5. ✅ Configure environment variables
6. ✅ Set up service URLs

### Option 2: Deploy Individually

**Deploy Backend Only:**
```bash
cd infra/cloud-run
export GOOGLE_CLOUD_PROJECT=your-project-id
./deploy-backend.sh
```

**Deploy Frontend Only:**
```bash
cd infra/cloud-run
export GOOGLE_CLOUD_PROJECT=your-project-id
export BACKEND_URL=https://your-backend-url.run.app
./deploy-frontend.sh
```

## Manual Deployment

### Step 1: Enable APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com
```

### Step 2: Deploy FastAPI Backend

```bash
# Navigate to backend directory
cd services/fastapi-backend

# Build and push image
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/genai-fastapi-backend

# Deploy to Cloud Run
gcloud run deploy genai-fastapi-backend \
    --image gcr.io/$GOOGLE_CLOUD_PROJECT/genai-fastapi-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
    --set-env-vars VERTEX_AI_LOCATION=us-central1 \
    --set-env-vars FASTAPI_ENV=production \
    --set-env-vars LOG_LEVEL=info \
    --set-env-vars CORS_ORIGINS=*

# Get backend URL
BACKEND_URL=$(gcloud run services describe genai-fastapi-backend \
    --region us-central1 \
    --format 'value(status.url)')

echo "Backend deployed at: $BACKEND_URL"
```

### Step 3: Deploy Streamlit Frontend

```bash
# Navigate to frontend directory
cd frontend/streamlit

# Build and push image
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/genai-streamlit-frontend

# Deploy to Cloud Run
gcloud run deploy genai-streamlit-frontend \
    --image gcr.io/$GOOGLE_CLOUD_PROJECT/genai-streamlit-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --set-env-vars API_BASE_URL=$BACKEND_URL \
    --set-env-vars FASTAPI_ENV=production

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe genai-streamlit-frontend \
    --region us-central1 \
    --format 'value(status.url)')

echo "Frontend deployed at: $FRONTEND_URL"
```

## CI/CD with Cloud Build

### Automatic Deployment on Git Push

1. **Setup Cloud Build triggers:**

```bash
# Connect your GitHub/GitLab repository
gcloud alpha builds triggers create github \
    --repo-name=genai-app-python \
    --repo-owner=your-username \
    --branch-pattern="^main$" \
    --build-config=services/fastapi-backend/cloudbuild.yaml

gcloud alpha builds triggers create github \
    --repo-name=genai-app-python \
    --repo-owner=your-username \
    --branch-pattern="^main$" \
    --build-config=frontend/streamlit/cloudbuild.yaml
```

2. **Grant permissions to Cloud Build:**

```bash
# Get Cloud Build service account
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format='value(projectNumber)')
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member=serviceAccount:${CLOUD_BUILD_SA} \
    --role=roles/run.admin

# Grant Service Account User role
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member=serviceAccount:${CLOUD_BUILD_SA} \
    --role=roles/iam.serviceAccountUser
```

3. **Push to trigger deployment:**

```bash
git push origin main
```

## Configuration

### Environment Variables

**Backend:**
- `GOOGLE_CLOUD_PROJECT` - Your GCP project ID (required)
- `VERTEX_AI_LOCATION` - GCP region (default: us-central1)
- `FASTAPI_ENV` - Environment (production/development)
- `LOG_LEVEL` - Logging level (info/debug/warning/error)
- `CORS_ORIGINS` - Allowed CORS origins (* for all)
- `DEFAULT_MODEL` - Default Gemini model (gemini-pro)
- `DD_LLMOBS_ML_APP` - Datadog ML app name (optional)
- `DD_API_KEY` - Datadog API key (optional)

**Frontend:**
- `API_BASE_URL` - Backend API URL (required)
- `FASTAPI_ENV` - Environment (production/development)

### Update Environment Variables

```bash
# Update backend
gcloud run services update genai-fastapi-backend \
    --region us-central1 \
    --set-env-vars KEY=VALUE

# Update frontend
gcloud run services update genai-streamlit-frontend \
    --region us-central1 \
    --set-env-vars API_BASE_URL=NEW_URL
```

### Secrets Management

For sensitive data, use Cloud Secret Manager:

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create MY_SECRET --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding MY_SECRET \
    --member=serviceAccount:YOUR_SERVICE_ACCOUNT \
    --role=roles/secretmanager.secretAccessor

# Use in Cloud Run
gcloud run services update genai-fastapi-backend \
    --region us-central1 \
    --set-secrets=DD_API_KEY=MY_SECRET:latest
```

## Monitoring & Logging

### View Logs

```bash
# Real-time logs
gcloud run services logs read genai-fastapi-backend \
    --region us-central1 \
    --follow

# Recent logs
gcloud run services logs read genai-streamlit-frontend \
    --region us-central1 \
    --limit 100
```

### Cloud Console

- **Logs**: https://console.cloud.google.com/logs
- **Cloud Run**: https://console.cloud.google.com/run
- **Metrics**: https://console.cloud.google.com/monitoring

### Datadog Integration

If you configured Datadog:
- LLM traces: https://app.datadoghq.com/llm/traces
- APM: https://app.datadoghq.com/apm
- Logs: https://app.datadoghq.com/logs

## Cost Management

### Pricing

Cloud Run pricing (approximate):
- **Backend (2 vCPU, 2GB RAM)**:
  - $0.00002400/vCPU-second
  - $0.00000250/GB-second
  - ~$0.10-0.50 per 1000 requests

- **Frontend (1 vCPU, 1GB RAM)**:
  - ~$0.05-0.25 per 1000 requests

- **Free Tier**:
  - 2 million requests/month
  - 360,000 vCPU-seconds/month
  - 180,000 GB-seconds/month

### Cost Optimization

1. **Scale to Zero**:
   ```bash
   --min-instances 0  # Already configured
   ```

2. **Set Maximum Instances**:
   ```bash
   gcloud run services update genai-fastapi-backend \
       --region us-central1 \
       --max-instances 5  # Limit concurrent instances
   ```

3. **Reduce Resources**:
   ```bash
   # For low-traffic applications
   gcloud run services update genai-fastapi-backend \
       --region us-central1 \
       --memory 1Gi \
       --cpu 1
   ```

4. **Set Budget Alerts**:
   ```bash
   # In Cloud Console > Billing > Budgets & alerts
   ```

## Custom Domains

### Add Custom Domain

```bash
# Map domain to service
gcloud beta run domain-mappings create \
    --service genai-streamlit-frontend \
    --domain your-domain.com \
    --region us-central1

# Follow DNS verification steps shown in output
```

### SSL Certificates

Cloud Run automatically provisions SSL certificates for custom domains.

## Security

### IAM & Authentication

**Make services private:**
```bash
# Remove public access
gcloud run services remove-iam-policy-binding genai-fastapi-backend \
    --region us-central1 \
    --member=allUsers \
    --role=roles/run.invoker

# Add specific users
gcloud run services add-iam-policy-binding genai-fastapi-backend \
    --region us-central1 \
    --member=user:example@example.com \
    --role=roles/run.invoker
```

**Service-to-service authentication:**
```bash
# Frontend calls backend with identity token
# Automatically handled by Cloud Run
```

### Best Practices

- ✅ Use Secret Manager for sensitive data
- ✅ Enable Cloud Audit Logs
- ✅ Set up VPC Service Controls (for high security)
- ✅ Use least privilege IAM roles
- ✅ Enable Binary Authorization (for production)
- ✅ Regular security scanning with Container Analysis

## Troubleshooting

### Deployment Fails

**Check build logs:**
```bash
gcloud builds list --limit 5
gcloud builds log BUILD_ID
```

**Common issues:**
- Insufficient IAM permissions
- API not enabled
- Dockerfile errors
- Out of memory during build

### Service Not Starting

**Check service logs:**
```bash
gcloud run services logs read SERVICE_NAME \
    --region us-central1 \
    --limit 100
```

**Common issues:**
- Port mismatch (must match Dockerfile EXPOSE)
- Missing environment variables
- Health check failures
- Startup timeout

### Connection Issues

**Frontend can't reach backend:**
1. Check backend URL in frontend env vars
2. Verify backend is deployed and healthy
3. Check CORS settings in backend

**502/504 Errors:**
1. Increase timeout: `--timeout 300`
2. Increase memory: `--memory 2Gi`
3. Check application logs for crashes

## Rollback

### Rollback to Previous Revision

```bash
# List revisions
gcloud run revisions list \
    --service genai-fastapi-backend \
    --region us-central1

# Rollback to specific revision
gcloud run services update-traffic genai-fastapi-backend \
    --region us-central1 \
    --to-revisions REVISION_NAME=100
```

### Traffic Splitting

```bash
# Gradual rollout (90% old, 10% new)
gcloud run services update-traffic genai-fastapi-backend \
    --region us-central1 \
    --to-revisions REVISION_OLD=90,REVISION_NEW=10
```

## Cleanup

### Delete Services

```bash
# Delete frontend
gcloud run services delete genai-streamlit-frontend \
    --region us-central1

# Delete backend
gcloud run services delete genai-fastapi-backend \
    --region us-central1

# Delete images
gcloud container images delete gcr.io/$GOOGLE_CLOUD_PROJECT/genai-fastapi-backend
gcloud container images delete gcr.io/$GOOGLE_CLOUD_PROJECT/genai-streamlit-frontend
```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

## Support

For issues specific to this deployment:
1. Check service logs
2. Review [Troubleshooting](#troubleshooting) section
3. Check Cloud Run quotas and limits
4. Review GCP Service Health Dashboard

---

**Last Updated**: December 27, 2024

