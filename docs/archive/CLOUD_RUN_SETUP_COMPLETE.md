# ✅ Cloud Run Deployment Setup Complete!

## 🎉 What Was Created

### Deployment Scripts (`infra/cloud-run/`)

1. **`deploy-backend.sh`** - Deploy FastAPI backend
   - Enables required GCP APIs
   - Builds Docker image with Cloud Build
   - Deploys to Cloud Run
   - Configures environment variables
   - Optional Datadog LLMObs integration

2. **`deploy-frontend.sh`** - Deploy Streamlit frontend
   - Builds and deploys frontend
   - Auto-discovers backend URL
   - Configures API connection

3. **`deploy-all.sh`** - Deploy everything at once
   - Deploys backend first
   - Then deploys frontend with backend URL
   - Shows complete deployment summary

### CI/CD Configuration

1. **`services/fastapi-backend/cloudbuild.yaml`**
   - Automatic deployment on git push
   - Build, test, and deploy pipeline
   - Container image versioning

2. **`frontend/streamlit/cloudbuild.yaml`**
   - Frontend auto-deployment
   - Backend URL auto-discovery
   - Production configuration

### Build Optimization

1. **`.gcloudignore` files**
   - Excludes unnecessary files from deployment
   - Faster uploads
   - Smaller images

### Documentation

1. **`docs/CLOUD_RUN_DEPLOYMENT.md`** (500+ lines)
   - Complete deployment guide
   - Configuration options
   - Troubleshooting
   - Cost optimization
   - Security best practices

2. **`DEPLOY_QUICKSTART.md`**
   - 5-minute quick start
   - Essential commands
   - Quick troubleshooting

## 🚀 How to Deploy

### Quick Deploy (5 minutes)

```bash
# 1. Set your project
export GOOGLE_CLOUD_PROJECT=your-project-id

# 2. Deploy everything
cd infra/cloud-run
./deploy-all.sh

# 3. Access your application
# URLs will be shown after deployment
```

### Manual Deploy

```bash
# Deploy backend
cd infra/cloud-run
./deploy-backend.sh

# Deploy frontend (after backend is ready)
./deploy-frontend.sh
```

### With Datadog Monitoring

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export DD_LLMOBS_ML_APP=your-ml-app-name
export DD_API_KEY=your-datadog-api-key

cd infra/cloud-run
./deploy-all.sh
```

## 📊 Deployment Configuration

### Backend (FastAPI)

**Resources:**
- Memory: 2 GB
- CPU: 2 vCPU
- Timeout: 300 seconds
- Max instances: 10
- Min instances: 0 (scales to zero)

**Environment Variables:**
- `GOOGLE_CLOUD_PROJECT` - Your GCP project
- `VERTEX_AI_LOCATION` - GCP region (us-central1)
- `FASTAPI_ENV` - production
- `LOG_LEVEL` - info
- `CORS_ORIGINS` - * (all origins allowed)
- `DD_LLMOBS_ML_APP` - (optional) Datadog app name
- `DD_API_KEY` - (optional) Datadog API key

### Frontend (Streamlit)

**Resources:**
- Memory: 1 GB
- CPU: 1 vCPU
- Timeout: 300 seconds
- Max instances: 10
- Min instances: 0 (scales to zero)

**Environment Variables:**
- `API_BASE_URL` - Backend URL (auto-configured)
- `FASTAPI_ENV` - production

## 💰 Cost Estimates

### Free Tier (per month)
- 2 million requests
- 360,000 vCPU-seconds
- 180,000 GB-seconds

### After Free Tier
- **Backend**: ~$0.10-0.50 per 1000 requests
- **Frontend**: ~$0.05-0.25 per 1000 requests
- **Idle cost**: $0 (scales to zero)

### Example Costs
- **Low traffic** (1,000 requests/day): ~$5-10/month
- **Medium traffic** (10,000 requests/day): ~$50-100/month
- **High traffic** (100,000 requests/day): ~$500-1000/month

## 🔧 Management Commands

### View Service Status

```bash
# List services
gcloud run services list --region us-central1

# Describe service
gcloud run services describe genai-fastapi-backend --region us-central1
```

### View Logs

```bash
# Real-time logs
gcloud run services logs read genai-fastapi-backend --region us-central1 --follow

# Recent logs
gcloud run services logs read genai-streamlit-frontend --region us-central1 --limit 100
```

### Update Services

```bash
# Update environment variable
gcloud run services update genai-fastapi-backend \
    --region us-central1 \
    --set-env-vars NEW_VAR=VALUE

# Update resources
gcloud run services update genai-fastapi-backend \
    --region us-central1 \
    --memory 4Gi \
    --cpu 4
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service genai-fastapi-backend --region us-central1

# Rollback to previous revision
gcloud run services update-traffic genai-fastapi-backend \
    --region us-central1 \
    --to-revisions REVISION_NAME=100
```

## 🔐 Security Features

✅ **Automatic HTTPS** - SSL certificates provisioned automatically
✅ **IAM Authentication** - Control who can access services
✅ **Secret Management** - Integration with Cloud Secret Manager
✅ **VPC Connectivity** - Optional private networking
✅ **Service Accounts** - Least-privilege access

## 📈 Monitoring

### Built-in Monitoring

- **Cloud Logging** - All application logs
- **Cloud Monitoring** - Metrics and dashboards
- **Error Reporting** - Automatic error detection
- **Cloud Trace** - Request tracing

### Datadog (Optional)

If configured with DD_* environment variables:
- **LLM Observability** - Track all Gemini API calls
- **APM** - Application performance monitoring
- **Custom Metrics** - Track business metrics
- **Alerts** - Automated alerting

### Access Monitoring

```bash
# Cloud Console
https://console.cloud.google.com/run

# Cloud Logging
https://console.cloud.google.com/logs

# Cloud Monitoring
https://console.cloud.google.com/monitoring
```

## 🎯 Next Steps

### 1. Deploy to Production

```bash
cd infra/cloud-run
export GOOGLE_CLOUD_PROJECT=your-project-id
./deploy-all.sh
```

### 2. Setup Custom Domain (Optional)

```bash
gcloud beta run domain-mappings create \
    --service genai-streamlit-frontend \
    --domain your-domain.com \
    --region us-central1
```

### 3. Setup CI/CD (Optional)

See [docs/CLOUD_RUN_DEPLOYMENT.md](docs/CLOUD_RUN_DEPLOYMENT.md#cicd-with-cloud-build)

### 4. Configure Monitoring

- Setup budget alerts
- Configure uptime checks
- Create custom dashboards

### 5. Optimize Costs

- Set appropriate max-instances
- Adjust memory/CPU based on actual usage
- Enable request compression
- Use Cloud CDN for static assets

## 🐛 Troubleshooting

### Deployment Fails

```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log BUILD_ID

# Common fixes:
# - Enable required APIs
# - Check IAM permissions
# - Verify Dockerfile syntax
```

### Service Not Starting

```bash
# Check service logs
gcloud run services logs read SERVICE_NAME --region us-central1 --limit 100

# Common fixes:
# - Verify environment variables
# - Check port configuration (8000 for backend, 8501 for frontend)
# - Increase memory/timeout if needed
```

### Connection Issues

```bash
# Test backend directly
curl https://your-backend-url.run.app/health

# Check frontend env vars
gcloud run services describe genai-streamlit-frontend --region us-central1

# Update backend URL if needed
gcloud run services update genai-streamlit-frontend \
    --region us-central1 \
    --set-env-vars API_BASE_URL=NEW_URL
```

## 📚 Documentation

- 🚀 [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md) - 5-minute quick start
- 📖 [docs/CLOUD_RUN_DEPLOYMENT.md](docs/CLOUD_RUN_DEPLOYMENT.md) - Complete guide
- 🗳️ [VOTE_EXTRACTOR_GUIDE.md](VOTE_EXTRACTOR_GUIDE.md) - Feature guide
- 📋 [PROJECT_PLAN.md](PROJECT_PLAN.md) - Architecture overview

## 🎉 Success Checklist

After deployment, verify:

- [ ] Backend health check: `curl BACKEND_URL/health`
- [ ] Frontend loads: Open frontend URL in browser
- [ ] API docs accessible: `BACKEND_URL/docs`
- [ ] Vote extraction works: Upload test images
- [ ] Logs are visible in Cloud Console
- [ ] Services scale to zero when idle
- [ ] HTTPS certificates are valid

## 💡 Pro Tips

1. **Use Cloud Build triggers** for automatic deployments on git push
2. **Set up budget alerts** to avoid unexpected costs
3. **Enable Cloud CDN** for frontend static assets
4. **Use Secret Manager** for sensitive configuration
5. **Implement health checks** for better reliability
6. **Monitor cold start times** and optimize if needed
7. **Use traffic splitting** for gradual rollouts

## 🆘 Getting Help

1. **Check service logs** first
2. **Review deployment guide**: [docs/CLOUD_RUN_DEPLOYMENT.md](docs/CLOUD_RUN_DEPLOYMENT.md)
3. **Google Cloud Run docs**: https://cloud.google.com/run/docs
4. **Check GCP Status**: https://status.cloud.google.com/

---

**Deployment Date**: December 27, 2024
**Status**: ✅ Ready for Deployment
**Estimated Setup Time**: 5-10 minutes
**Estimated Cost**: $0-50/month (depends on usage)
