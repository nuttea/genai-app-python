# Authentication with Google Cloud

This guide covers different authentication methods for accessing Google Cloud services (Vertex AI).

## Recommended: Application Default Credentials (ADC)

For **local development**, we recommend using `gcloud` Application Default Credentials (ADC). This is the most secure and convenient method.

### Setup ADC

1. **Install gcloud CLI** (if not already installed):
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Initialize gcloud**:
   ```bash
   gcloud init
   ```

3. **Set your project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Login with Application Default Credentials**:
   ```bash
   gcloud auth application-default login
   ```

   This will:
   - Open a browser for authentication
   - Store credentials at `~/.config/gcloud/application_default_credentials.json`
   - Allow all Google Cloud SDKs to automatically use these credentials

5. **Verify authentication**:
   ```bash
   gcloud auth application-default print-access-token
   ```

### Using ADC with the Application

Once you've authenticated with `gcloud auth application-default login`, the application will automatically use these credentials.

**Local Development:**
```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Run the app - credentials are automatically detected
cd services/fastapi-backend
uvicorn app.main:app --reload
```

**Docker Development:**
```bash
# Set your project ID in .env
echo "GOOGLE_CLOUD_PROJECT=your-project-id" > .env

# Start with Docker - credentials are mounted from ~/.config/gcloud
docker-compose up
```

The `docker-compose.yml` automatically mounts your gcloud config:
```yaml
volumes:
  - ${HOME}/.config/gcloud:/root/.config/gcloud:ro
```

### Environment Variables for ADC

```bash
# Required
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Optional (these are detected automatically with ADC)
# export GOOGLE_APPLICATION_CREDENTIALS=""  # Not needed with ADC
export VERTEX_AI_LOCATION="us-central1"
```

## Alternative: Service Account Key (Production/CI/CD)

For **production** or **CI/CD environments**, use a service account key file.

### Create Service Account

1. **Create the service account**:
   ```bash
   gcloud iam service-accounts create genai-app \
       --project=YOUR_PROJECT_ID \
       --description="Service account for GenAI application" \
       --display-name="GenAI App"
   ```

2. **Grant permissions**:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:genai-app@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/aiplatform.user"
   ```

3. **Create and download key**:
   ```bash
   gcloud iam service-accounts keys create ~/genai-service-account.json \
       --iam-account=genai-app@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

   ⚠️ **Security Warning**: Keep this file secure and never commit it to version control!

### Using Service Account Key

**Local Development:**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/genai-service-account.json"

cd services/fastapi-backend
uvicorn app.main:app --reload
```

**Docker:**
```bash
# Update docker-compose.yml to mount the key file instead:
volumes:
  - ${GOOGLE_APPLICATION_CREDENTIALS}:/app/secrets/key.json:ro

environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/key.json
```

## Authentication Flow

The application follows this credential discovery order:

1. **GOOGLE_APPLICATION_CREDENTIALS** environment variable (if set)
   - Points to a service account key file

2. **Application Default Credentials** (automatic)
   - Checks `~/.config/gcloud/application_default_credentials.json`
   - Created by `gcloud auth application-default login`

3. **Cloud environment metadata** (when running in GCP)
   - Automatically available in Cloud Run, GKE, Compute Engine, etc.

## Required GCP Permissions

Your user account or service account needs these roles:

### Minimum Required:
- `roles/aiplatform.user` - Access to Vertex AI

### Recommended for Development:
- `roles/aiplatform.user` - Vertex AI access
- `roles/logging.logWriter` - Write logs (optional)
- `roles/monitoring.metricWriter` - Write metrics (optional)

### Grant Permissions

**For your user account:**
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your.email@example.com" \
    --role="roles/aiplatform.user"
```

**For service account:**
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:genai-app@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

## Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID

# Optional but useful APIs
gcloud services enable compute.googleapis.com --project=YOUR_PROJECT_ID
gcloud services enable storage.googleapis.com --project=YOUR_PROJECT_ID
gcloud services enable logging.googleapis.com --project=YOUR_PROJECT_ID
```

## Troubleshooting

### "Could not automatically determine credentials"

**Solution 1: Re-authenticate with ADC**
```bash
gcloud auth application-default login
```

**Solution 2: Check environment variables**
```bash
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_APPLICATION_CREDENTIALS
```

**Solution 3: Verify credentials file exists**
```bash
ls -la ~/.config/gcloud/application_default_credentials.json
```

### "Permission denied" or "403 Forbidden"

**Check your permissions:**
```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:user:your.email@example.com"
```

**Grant required role:**
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your.email@example.com" \
    --role="roles/aiplatform.user"
```

### "API not enabled"

```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### Docker: "Could not load credentials"

**Verify volume mount:**
```bash
# Check if gcloud config exists
ls -la ~/.config/gcloud/

# Test Docker mount
docker-compose exec fastapi-backend ls -la /root/.config/gcloud/
```

**Alternative: Use host network (macOS/Linux)**
```yaml
# In docker-compose.yml
network_mode: "host"
```

## Best Practices

### Development
✅ **Use Application Default Credentials** (gcloud auth application-default login)
✅ **Mount gcloud config** in Docker
✅ **Set GOOGLE_CLOUD_PROJECT** environment variable
✅ **Never commit credentials** to version control

### Production
✅ **Use service account keys** or Workload Identity
✅ **Store keys in secrets manager** (not in environment variables)
✅ **Use minimal IAM permissions** (principle of least privilege)
✅ **Rotate keys regularly**
✅ **Monitor API usage** and costs

### CI/CD
✅ **Use service account keys** stored in CI/CD secrets
✅ **Use Workload Identity** for GitHub Actions/Cloud Build
✅ **Audit access** regularly
✅ **Use separate accounts** for dev/staging/prod

## Security Considerations

1. **Never commit credentials** to version control
2. **Use .gitignore** to exclude credential files
3. **Rotate service account keys** every 90 days
4. **Use Workload Identity** in production (GKE, Cloud Run)
5. **Monitor for unauthorized access** in Cloud Audit Logs
6. **Delete unused service accounts** and keys
7. **Use service account impersonation** when possible

## Environment-Specific Setup

### Local Development
```bash
# One-time setup
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# Run application
make run-fastapi
```

### Docker Development
```bash
# One-time setup
gcloud auth application-default login

# Create .env file
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
EOF

# Run with Docker
make docker-up
```

### Cloud Run (Production)
```bash
# Deploy with default service account
gcloud run deploy genai-app \
    --source . \
    --project=YOUR_PROJECT_ID \
    --region=us-central1 \
    --allow-unauthenticated

# Or specify service account
gcloud run deploy genai-app \
    --source . \
    --service-account=genai-app@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Google Kubernetes Engine (GKE)
```bash
# Use Workload Identity (recommended)
gcloud iam service-accounts add-iam-policy-binding \
    genai-app@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:YOUR_PROJECT_ID.svc.id.goog[NAMESPACE/KSA_NAME]"
```

## Quick Reference

| Method | Use Case | Setup Command |
|--------|----------|---------------|
| **ADC** | Local Development | `gcloud auth application-default login` |
| **Service Account** | Production/CI/CD | Create key file + set env var |
| **Workload Identity** | GKE Production | Configure K8s + IAM binding |
| **Default Service Account** | Cloud Run/GCE | Automatic (no setup needed) |

## Additional Resources

- [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
- [Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Vertex AI Authentication](https://cloud.google.com/vertex-ai/docs/authentication)

---

**Recommended for this project**: Use **Application Default Credentials** for local development, and **service accounts** for production deployments.
