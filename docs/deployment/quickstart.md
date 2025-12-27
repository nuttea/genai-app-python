# 🚀 Cloud Run Deployment - Quick Start

Deploy your GenAI Application to Google Cloud Run in 5 minutes!

## Prerequisites

✅ GCP account with billing enabled  
✅ gcloud CLI installed  
✅ Project with Vertex AI API enabled  

## 1-Minute Setup

```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Authenticate
gcloud auth login
gcloud auth application-default login
```

## Deploy Everything

```bash
# Navigate to deployment directory
cd infra/cloud-run

# Deploy both services
./deploy-all.sh
```

That's it! ✨

## What Gets Deployed

- ✅ **FastAPI Backend** - API server with Vertex AI
- ✅ **Streamlit Frontend** - Interactive web UI
- ✅ **Auto-scaling** - Scales to zero when not in use
- ✅ **HTTPS** - Automatic SSL certificates
- ✅ **Monitoring** - Built-in logging and metrics

## Access Your Application

After deployment completes, you'll get URLs like:

```
Frontend:  https://genai-streamlit-frontend-xxxxx.run.app
Backend:   https://genai-fastapi-backend-xxxxx.run.app
API Docs:  https://genai-fastapi-backend-xxxxx.run.app/docs
```

## Optional: Add Datadog Monitoring

```bash
export DD_LLMOBS_ML_APP=your-ml-app-name
export DD_API_KEY=your-datadog-api-key

# Then deploy
./deploy-all.sh
```

## Cost Estimate

**Free Tier**: 2 million requests/month included

**After Free Tier**: ~$0.10-0.50 per 1000 requests

**Auto-scaling**: Pay only for actual usage, scales to $0 when idle

## Update Deployment

```bash
# Update backend
cd infra/cloud-run
./deploy-backend.sh

# Update frontend
./deploy-frontend.sh
```

## Delete Everything

```bash
gcloud run services delete genai-fastapi-backend --region us-central1
gcloud run services delete genai-streamlit-frontend --region us-central1
```

## Troubleshooting

**Issue**: Deployment fails

**Solution**: Check you have:
- Billing enabled
- Required APIs enabled
- Proper IAM permissions

**View logs:**
```bash
gcloud run services logs read genai-fastapi-backend --region us-central1 --limit 100
```

## Next Steps

- 📖 Full guide: [docs/CLOUD_RUN_DEPLOYMENT.md](docs/CLOUD_RUN_DEPLOYMENT.md)
- ⚙️ Setup CI/CD for automatic deployments
- 🔒 Configure custom domains
- 📊 Setup monitoring and alerts

---

**Need help?** See the [complete deployment guide](docs/CLOUD_RUN_DEPLOYMENT.md)

