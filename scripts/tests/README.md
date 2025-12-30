# Test Scripts

This directory contains test and debugging scripts for various components of the GenAI application.

## 🧪 Test Scripts

### Model Listing Tests

**[test_google_ai_api.py](./test_google_ai_api.py)**
- Tests Google AI API (non-Vertex AI) with API key
- Attempts to list models using Python SDK
- Shows SDK routing issue (routes to wrong endpoint)
- Requires: `GEMINI_API_KEY` in `.env`

**[test_rest_api_models.py](./test_rest_api_models.py)**
- Tests Google AI API REST endpoint directly
- Successfully lists 50+ models
- Validates that REST API works correctly
- Requires: `GEMINI_API_KEY` in `.env`

**[test_both_sdk_approaches.py](./test_both_sdk_approaches.py)**
- Compares `google-genai` vs `google-cloud-aiplatform` SDKs
- Tests both Vertex AI and Google AI API modes
- Shows both return 0 models (by design)
- Requires: `GOOGLE_CLOUD_PROJECT`, `GEMINI_API_KEY`

**[test_gemini_models_api.py](./test_gemini_models_api.py)**
- Tests Vertex AI model listing with `google-genai` SDK
- Shows that Vertex AI returns 0 first-party models
- Validates generation still works despite empty list
- Requires: `GOOGLE_CLOUD_PROJECT`

### Dynamic Features Tests

**[test_dynamic_models.py](./test_dynamic_models.py)**
- Tests dynamic model listing implementation
- Validates REST API integration
- Checks backend `/models` endpoint
- Shows cache behavior
- Requires: `GEMINI_API_KEY` in `.env`

### Debug Scripts

**[debug_models_api.py](./debug_models_api.py)**
- Debug script for troubleshooting model listing
- Lists all models without filtering
- Useful for investigating SDK behavior
- Requires: `GOOGLE_CLOUD_PROJECT`

### Shell Scripts

**[test_list_all_models.sh](./test_list_all_models.sh)**
- Quick bash script to list models via REST API
- Requires: `GEMINI_API_KEY` environment variable

## 🚀 Running Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip3 install --break-system-packages python-dotenv requests httpx google-genai
   ```

2. **Set up `.env` file** (project root):
   ```bash
   GOOGLE_CLOUD_PROJECT=your-project-id
   GEMINI_API_KEY=your-api-key
   VERTEX_AI_LOCATION=us-central1
   ```

3. **Authenticate with GCP** (for Vertex AI tests):
   ```bash
   gcloud auth application-default login
   ```

### Run Individual Tests

```bash
# Test Google AI API with Python SDK
python3 scripts/tests/test_google_ai_api.py

# Test REST API directly (most reliable)
python3 scripts/tests/test_rest_api_models.py

# Test dynamic model listing
python3 scripts/tests/test_dynamic_models.py

# Compare SDK approaches
python3 scripts/tests/test_both_sdk_approaches.py

# Test Vertex AI model listing
python3 scripts/tests/test_gemini_models_api.py
```

## 📊 Expected Results

| Script | Expected Result |
|--------|----------------|
| `test_rest_api_models.py` | ✅ Lists 50+ models successfully |
| `test_google_ai_api.py` | ❌ 401 error or 0 models (SDK issue) |
| `test_both_sdk_approaches.py` | ⚠️ 0 models (by design) |
| `test_gemini_models_api.py` | ⚠️ 0 models, but generation works |
| `test_dynamic_models.py` | ✅ 26+ models via backend |

## 🎯 Use Cases

### Investigate Model Listing
```bash
# Quick check - does REST API work?
python3 scripts/tests/test_rest_api_models.py

# Why does SDK return 0?
python3 scripts/tests/test_google_ai_api.py
```

### Validate Dynamic Listing
```bash
# Is backend returning models?
python3 scripts/tests/test_dynamic_models.py
```

### Compare Approaches
```bash
# Vertex AI vs Google AI API
python3 scripts/tests/test_both_sdk_approaches.py
```

## 📝 Notes

### Environment Loading
All Python test scripts automatically load `.env` from the project root:
```python
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')
```

### Authentication
- **Vertex AI tests**: Use Application Default Credentials (ADC)
- **Google AI API tests**: Use `GEMINI_API_KEY` from `.env`

### CI/CD
These scripts are for **local development and debugging only**, not part of the CI/CD pipeline.

## 🔗 Related Documentation

- [Investigation Findings](../../docs/investigations/) - What we learned
- [Troubleshooting](../../docs/troubleshooting/) - Common issues
- [Reference Docs](../../docs/reference/) - Implementation details

---

**Last Updated:** 2024-12-29
