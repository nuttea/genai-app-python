# Google Gemini Models API - Key Findings

## Summary

After extensive testing, we discovered why `client.models.list()` returns 0 models and why our **static model list approach is the correct solution** for production.

## Key Discoveries

### 1. REST API vs Python SDK Behavior

| Method | Approach | Result | Authentication |
|--------|----------|--------|----------------|
| **REST API** | Direct HTTP call to `https://generativelanguage.googleapis.com/v1beta/models` | ✅ **Returns 50 models** | API Key (GEMINI_API_KEY) |
| **Python SDK** | `google-genai` with `client.models.list()` | ❌ **Returns 0 models or fails** | OAuth2 (even with API key) |

### 2. The Underlying Issue

**Even when using the `google-genai` SDK without `vertexai=True`, the `.list()` method still routes to the Vertex AI backend**, NOT the public Google AI API!

```python
# What we expected:
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
models = list(client.models.list())  # Expected to use Google AI API

# What actually happens:
# The SDK routes to: google.cloud.aiplatform.v1beta1.ModelGardenService.ListPublisherModels
# This endpoint requires OAuth2, not API keys!
# Error: "API keys are not supported by this API. Expected OAuth2 access token..."
```

### 3. Test Results

#### ✅ REST API Test (WORKS)

```bash
$ curl "https://generativelanguage.googleapis.com/v1beta/models?key=${GEMINI_API_KEY}"
```

**Result:** Returns 50 models including:
- `models/gemini-2.5-flash`
- `models/gemini-2.5-pro`
- `models/gemini-2.0-flash`
- `models/gemini-2.0-flash-exp`
- `models/gemini-exp-1206`
- And 45+ more models (embeddings, Gemma, etc.)

#### ❌ Python SDK Test (FAILS)

```python
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
models = list(client.models.list())  # Returns 0 or raises 401 error
```

**Error:**
```
google.genai.errors.ClientError: 401 UNAUTHENTICATED
'API keys are not supported by this API. Expected OAuth2 access token...'
Method: google.cloud.aiplatform.v1beta1.ModelGardenService.ListPublisherModels
```

### 4. Why Vertex AI `models.list()` Returns Empty

Both `google-genai` (with `vertexai=True`) and `google-cloud-aiplatform` SDKs' `.list()` methods are designed to:
- List **user-created/imported models** in Model Registry
- List **tuned models** (custom fine-tuned versions)
- **NOT** list Google's first-party foundation models (Gemini, PaLM, etc.)

This is by design - first-party models are accessed by name, not discovered via API.

## Our Solution: Static Model List ✅

For our application using Vertex AI (`vertexai=True`) with GCP authentication, we use a **curated static list** in the backend's `/models` endpoint:

```python
gemini_models = [
    {
        "name": "gemini-2.5-flash",
        "display_name": "Gemini 2.5 Flash",
        "description": "Fast and versatile multimodal model...",
        "context_window": 1_048_576,
        "output_tokens": 65_536,
    },
    # ... more models
]
```

### Why This Is the Best Approach

1. **Reliability**: No dependency on external API calls that may timeout or fail
2. **Performance**: Instant response, no network latency
3. **Control**: We decide which models to expose to users
4. **Consistency**: Same models across all environments (dev, prod)
5. **Simplicity**: No complex authentication just for listing
6. **Production-Ready**: Works seamlessly with Vertex AI for actual inference

### Alternative: Use REST API for Dynamic Listing

If we wanted a dynamic model list, we could:

```python
import requests

def get_dynamic_model_list():
    """Fetch models from Google AI API REST endpoint."""
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    response = requests.get(url)
    response.raise_for_status()
    return response.json()["models"]
```

**But this adds complexity:**
- Requires managing `GEMINI_API_KEY` separately from GCP auth
- Adds external API dependency
- Potential timeout/failure points
- API key rotation and security concerns
- Uses different authentication than Vertex AI inference

## Conclusion

✅ **Our static model list approach is validated as the correct production solution.**

The REST API *can* list models dynamically, but:
- It requires a separate API key
- The Python SDK doesn't properly support it (routes to wrong backend)
- It adds unnecessary complexity
- Static list is simpler, faster, and more reliable

## References

- **REST API Endpoint**: https://generativelanguage.googleapis.com/v1beta/models
- **Google AI API Docs**: https://ai.google.dev/api/rest/generativelanguage/models/list
- **Vertex AI Models**: https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini

## Test Scripts

All test scripts are available in the project root:
- `test_rest_api_models.py` - Direct REST API test (✅ works)
- `test_google_ai_api.py` - Python SDK test (❌ fails/routes to wrong endpoint)
- `test_both_sdk_approaches.py` - Compares Vertex AI vs Google AI API
- `test_gemini_models_api.py` - Original Vertex AI test

All scripts now automatically load `.env` file for easy testing.
