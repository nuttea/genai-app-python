# Setup Google AI API Key (Optional)

Guide to get a GEMINI_API_KEY for testing the Google AI API (non-Vertex AI approach).

## Why You Might Want This

The Google AI API **CAN list models** dynamically:
```python
from google import genai
client = genai.Client()  # Uses GEMINI_API_KEY
models = client.models.list()  # ✅ Returns full list!
```

While Vertex AI **CANNOT**:
```python
client = genai.Client(vertexai=True, project=..., location=...)
models = client.models.list()  # ❌ Returns empty
```

## Quick Setup (2 minutes)

### 1. Get Your API Key

Visit: https://aistudio.google.com/apikey

1. Sign in with your Google account
2. Click "Create API key"
3. Select a Google Cloud project (or create new)
4. Copy the API key

### 2. Set Environment Variable

**Option A: Temporary (current terminal session)**
```bash
export GEMINI_API_KEY=your-api-key-here
```

**Option B: Add to .env file** (recommended for testing)
```bash
# Add to .env
echo "GEMINI_API_KEY=your-api-key-here" >> .env
```

**Option C: Add to shell profile** (permanent)
```bash
# For zsh (macOS default)
echo 'export GEMINI_API_KEY=your-api-key-here' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export GEMINI_API_KEY=your-api-key-here' >> ~/.bashrc
source ~/.bashrc
```

### 3. Test It

```bash
cd /Users/nuttee.jirattivongvibul/Projects/genai-app-python
python test_google_ai_api.py
```

Should output:
```
✅ SUCCESS! Found 10+ models

📋 All Available Models:
1. gemini-2.5-flash
   Display Name: Gemini 2.5 Flash
   ...
```

## Google AI API vs Vertex AI

### Google AI API ✅
```python
# Setup
export GEMINI_API_KEY=abc123

# Code
from google import genai
client = genai.Client()  # Uses API key
models = client.models.list()  # Works! Returns models
```

**Pros:**
- ✅ Can list models dynamically
- ✅ Simple setup (just API key)
- ✅ Good for development/testing
- ✅ No GCP project needed

**Cons:**
- ❌ API key management (rotation, secrets)
- ❌ Less integrated with GCP
- ❌ Not ideal for production

### Vertex AI (Current) ✅
```python
# Setup
export GOOGLE_CLOUD_PROJECT=my-project
gcloud auth application-default login

# Code
from google import genai
client = genai.Client(vertexai=True, project=..., location=...)
models = client.models.list()  # Empty, but inference works!
```

**Pros:**
- ✅ GCP authentication (no API keys)
- ✅ Integrated with GCP services
- ✅ Better for production
- ✅ IAM and audit logging
- ✅ Models work perfectly for generation

**Cons:**
- ❌ Cannot list models dynamically
- ❌ Must use static list

## Our Decision

We use **Vertex AI** because:

1. **Production-ready** - GCP authentication, no API keys to manage
2. **Better security** - IAM roles, audit logs
3. **GCP integration** - Works with other GCP services
4. **Models work** - Even though list() is empty, generation works perfectly

We accept the trade-off:
- ❌ Cannot list models dynamically
- ✅ Use curated static list instead
- ✅ Update list manually when new models release

## Testing Both Approaches

### Test Google AI API (with GEMINI_API_KEY)
```bash
export GEMINI_API_KEY=your-key
python test_google_ai_api.py
```

### Test Vertex AI (with GCP auth)
```bash
export GOOGLE_CLOUD_PROJECT=your-project
python test_gemini_models_api.py
```

### Compare Both
```bash
export GEMINI_API_KEY=your-key
export GOOGLE_CLOUD_PROJECT=your-project
python test_both_sdk_approaches.py
```

## API Key Best Practices

If using GEMINI_API_KEY:

### 1. Keep it Secret
```bash
# DON'T commit to git
echo "GEMINI_API_KEY" >> .gitignore
```

### 2. Rotate Regularly
- Create new key every 90 days
- Revoke old keys
- Update .env file

### 3. Use Secrets Manager (Production)
```python
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
secret = client.access_secret_version(name="projects/*/secrets/gemini-api-key/versions/latest")
api_key = secret.payload.data.decode("UTF-8")
```

### 4. Limit Permissions
- Create API key with minimal scope
- Restrict to specific IPs if possible
- Monitor usage in Google Cloud Console

## Cleanup

If you're done testing:

```bash
# Remove from environment
unset GEMINI_API_KEY

# Remove from .env
sed -i '/GEMINI_API_KEY/d' .env

# Revoke key in console
# Visit: https://console.cloud.google.com/apis/credentials
# Find your API key and click "Delete"
```

---

**For production, stick with Vertex AI!** This API key setup is just for testing/comparison. 🔐

