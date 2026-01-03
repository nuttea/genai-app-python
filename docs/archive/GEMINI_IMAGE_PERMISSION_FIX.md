# Gemini 3 Pro Image Permission Fix

## 🔍 **Issue Summary**

From Datadog logs and traces analysis:

```
403 PERMISSION_DENIED
Permission 'aiplatform.endpoints.predict' denied on resource 
'//aiplatform.googleapis.com/projects/datadog-sandbox/locations/global/publishers/google/models/gemini-3-pro-image-preview'
```

**Key Findings from Datadog**:
- **Service**: `genai-adk-python` (Cloud Run)
- **Project**: `datadog-ese-sandbox` (from GCR metadata)
- **Location**: `us-central1`
- **Model**: `gemini-3-pro-image-preview` at `global` location
- **Auth Method**: Cloud Run default service account (via GCE metadata service)
- **Timestamp**: 2026-01-02 16:14:47 UTC
- **Trace ID**: `3895988154444577359`

## 🎯 **Root Cause**

The Cloud Run service's **default compute service account** lacks the required IAM permissions to access Vertex AI Gemini 3 Pro Image model.

**From Trace Analysis**:
- Service successfully gets credentials from `computeMetadata/v1/instance/service-accounts/default/token`
- But the service account doesn't have `aiplatform.endpoints.predict` permission
- Request to Gemini API fails with 403 PERMISSION_DENIED

## ✅ **Solution**

Grant the Cloud Run service account the necessary Vertex AI permissions.

### **Option 1: Use Vertex AI User Role (Recommended)**

This role provides access to use Vertex AI models without administrative permissions.

```bash
# Get the service account email
SERVICE_ACCOUNT=$(gcloud run services describe genai-adk-python \
  --region us-central1 \
  --project datadog-ese-sandbox \
  --format 'value(spec.template.spec.serviceAccountName)')

echo "Service Account: $SERVICE_ACCOUNT"

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding datadog-ese-sandbox \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/aiplatform.user"
```

### **Option 2: Use Custom Role with Minimal Permissions**

For more granular control:

```bash
# Create custom role
gcloud iam roles create vertexAIImageGeneration \
  --project=datadog-ese-sandbox \
  --title="Vertex AI Image Generation" \
  --description="Minimal permissions for Gemini image generation" \
  --permissions="aiplatform.endpoints.predict,aiplatform.endpoints.get"

# Grant custom role
gcloud projects add-iam-policy-binding datadog-ese-sandbox \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="projects/datadog-ese-sandbox/roles/vertexAIImageGeneration"
```

### **Option 3: If Using Default Compute Service Account**

If the service is using the default compute service account:

```bash
# Default compute service account format
DEFAULT_SA="[PROJECT_NUMBER]-compute@developer.gserviceaccount.com"

# Get project number
PROJECT_NUMBER=$(gcloud projects describe datadog-ese-sandbox \
  --format='value(projectNumber)')

# Grant role
gcloud projects add-iam-policy-binding datadog-ese-sandbox \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## 🧪 **Verify the Fix**

### 1. Check IAM Permissions

```bash
gcloud projects get-iam-policy datadog-ese-sandbox \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT}" \
  --format="table(bindings.role)"
```

### 2. Test Image Generation

After granting permissions, test the endpoint:

```bash
curl -X POST https://genai-adk-python-cn4wkmlbva-uc.a.run.app/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A simple test image",
    "image_type": "illustration",
    "aspect_ratio": "1:1",
    "session_id": "test_session"
  }'
```

### 3. Monitor in Datadog

Check logs for success:

```bash
# In Datadog Log Explorer
service:genai-adk-python "Image generation completed"
```

## 📊 **Datadog Monitoring**

### Logs Query

```
service:genai-adk-python 
(status:error "PERMISSION_DENIED" OR "Image generation completed")
```

### Trace Query

```
service:genai-adk-python 
resource_name:"POST /api/v1/images/generate"
```

### Monitor Alert

Create a monitor to alert on permission errors:

```
service:genai-adk-python status:error PERMISSION_DENIED
```

## 🔐 **Security Best Practices**

### 1. Use Dedicated Service Account

Instead of the default compute service account, create a dedicated one:

```bash
# Create dedicated service account
gcloud iam service-accounts create adk-python-sa \
  --display-name="ADK Python Service Account" \
  --project=datadog-ese-sandbox

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding datadog-ese-sandbox \
  --member="serviceAccount:adk-python-sa@datadog-ese-sandbox.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Update Cloud Run service to use it
gcloud run services update genai-adk-python \
  --region us-central1 \
  --service-account=adk-python-sa@datadog-ese-sandbox.iam.gserviceaccount.com \
  --project=datadog-ese-sandbox
```

### 2. Principle of Least Privilege

Only grant necessary permissions:
- ✅ `roles/aiplatform.user` - Can use Vertex AI models
- ❌ `roles/aiplatform.admin` - Too broad, includes admin permissions

### 3. Enable Audit Logging

Track API usage:

```bash
# Enable Data Access audit logs for Vertex AI
# Go to Cloud Console > IAM & Admin > Audit Logs
# Enable "Data Read" for Vertex AI API
```

## 📝 **Related Files**

- **Image Generation Service**: `services/adk-python/app/services/image_generation.py`
- **Main ADK App**: `services/adk-python/main_adk.py`
- **Deployment Workflow**: `.github/workflows/adk-python.yml`

## 🔗 **References**

- [Vertex AI IAM Permissions](https://cloud.google.com/vertex-ai/docs/general/access-control)
- [Cloud Run Service Accounts](https://cloud.google.com/run/docs/securing/service-identity)
- [Gemini 3 Image Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)

## ⚠️ **Notes**

1. **Permission Propagation**: IAM changes may take up to 60 seconds to propagate
2. **Multiple Projects**: Ensure you're using the correct project (`datadog-ese-sandbox`, not `datadog-sandbox`)
3. **Model Availability**: Gemini 3 Pro Image Preview is in preview and requires allowlisting in some cases
4. **Location**: The model is accessed via `location="global"`, not regional endpoints

---

**Status**: Ready to apply
**Priority**: High - Service is currently non-functional for image generation
**Estimated Fix Time**: 2-3 minutes (IAM propagation)

