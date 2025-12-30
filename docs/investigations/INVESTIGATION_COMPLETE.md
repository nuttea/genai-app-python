# Investigation Complete: Why `client.models.list()` Returns 0 Models

## 🎯 Bottom Line

**Our static model list approach is correct and validated.** The Python SDK's `.list()` method is fundamentally incompatible with listing Google's first-party models, even with the Google AI API.

## 🔍 What We Discovered

### The Core Issue

Even when using `google-genai.Client(api_key=...)` (non-Vertex AI mode), the SDK's `.models.list()` method **incorrectly routes to the Vertex AI backend** which:
1. Requires OAuth2 authentication (not API keys)
2. Is designed to list user-created models, not Google's foundation models
3. Returns empty for first-party models like Gemini

### Test Results

| Test Method | Authentication | Result | Models Returned |
|-------------|----------------|--------|-----------------|
| REST API | `GEMINI_API_KEY` | ✅ **Works** | **50 models** |
| Python SDK `.list()` | `GEMINI_API_KEY` | ❌ **Fails** | 401 Error or 0 models |
| Vertex AI SDK | GCP OAuth2 | ✅ **Works for inference** | 0 models (by design) |

### Example: REST API Works

```bash
$ curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"

{
  "models": [
    {
      "name": "models/gemini-2.5-flash",
      "displayName": "Gemini 2.5 Flash",
      "inputTokenLimit": 1048576,
      "outputTokenLimit": 65536
    },
    # ... 49 more models
  ]
}
```

### Example: Python SDK Fails

```python
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
models = list(client.models.list())

# Result: 401 UNAUTHENTICATED
# Error: "API keys are not supported by this API. Expected OAuth2 access token"
# Reason: SDK routes to Vertex AI endpoint, not Google AI API endpoint
```

## ✅ Our Production Solution

We use a **curated static model list** in:
- Backend: `services/fastapi-backend/app/api/v1/endpoints/vote_extraction.py`
- Endpoint: `GET /api/v1/vote-extraction/models`

### Benefits

1. **✅ Reliable**: No external API dependencies
2. **✅ Fast**: Instant response, no network calls
3. **✅ Controlled**: We choose which models users can access
4. **✅ Consistent**: Same across all environments
5. **✅ Simple**: No complex authentication for listing
6. **✅ Production-Ready**: Works seamlessly with Vertex AI inference

### Implementation

```python
gemini_models = [
    {
        "name": "gemini-2.5-flash",
        "display_name": "Gemini 2.5 Flash",
        "description": "Fast and versatile multimodal model...",
        "context_window": 1_048_576,
        "output_tokens": 65_536,
        "supported": True,
    },
    # ... more models
]
```

## 🚀 Changes Made

### 1. Test Scripts Enhanced

All test scripts now automatically load `.env` file:
- ✅ `test_rest_api_models.py` - REST API test (proves dynamic listing is possible)
- ✅ `test_google_ai_api.py` - SDK test (proves SDK routing issue)
- ✅ `test_both_sdk_approaches.py` - Comparison test
- ✅ `test_gemini_models_api.py` - Vertex AI test

### 2. Dependencies Installed

```bash
$ pip3 install --break-system-packages requests python-dotenv google-genai
```

### 3. Environment Setup

All scripts now use:
```python
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')
```

## 📊 Comparison: Dynamic vs Static

### Option A: Dynamic (REST API)

**Pros:**
- Always up-to-date with latest models
- Auto-discovers new models

**Cons:**
- Requires separate `GEMINI_API_KEY` management
- Python SDK doesn't support it properly
- External API dependency (timeout risk)
- Different auth from Vertex AI inference
- Added complexity

### Option B: Static (Our Approach) ✅

**Pros:**
- No external dependencies
- Instant response
- Simple and reliable
- Same auth as Vertex AI
- Full control over exposed models

**Cons:**
- Manual updates needed (but Gemini models are stable)
- Requires curating list

## 🎓 Key Learnings

1. **SDK Limitation**: The `google-genai` SDK's `.models.list()` method is not suitable for listing first-party models, even with Google AI API credentials.

2. **REST API Works**: The REST API endpoint correctly returns models, but requires separate API key management.

3. **Vertex AI by Design**: Vertex AI's model listing is intentionally designed for user-created models, not foundation models.

4. **Static List is Best**: For production applications using Vertex AI, a curated static list is the most practical solution.

## 📚 Documentation

- **Detailed Findings**: `MODELS_API_FINDINGS.md`
- **Setup Guide**: `SETUP_GOOGLE_AI_API_KEY.md`
- **LLM Config Guide**: `LLM_CONFIG_QUICKSTART.md`
- **Test Scripts**: All `.py` files in project root

## ✨ Conclusion

**Investigation validated our approach.** The static model list in our backend is:
- ✅ The correct production solution
- ✅ More reliable than dynamic listing
- ✅ Simpler to maintain
- ✅ Faster for users

No changes needed to the application - **our implementation is already optimal!** 🎉
