# Test Gemini Models API

Quick guide to test if the Gemini API models list is working with Vertex AI.

## Prerequisites

Make sure your `.env` file has:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
```

And you're authenticated with GCP:
```bash
gcloud auth application-default login
```

## Test Methods

### Method 1: Direct Python Script

```bash
# Load environment variables
source .env

# Run test script
python test_gemini_models_api.py
```

### Method 2: With Poetry (Backend Environment)

```bash
cd services/fastapi-backend
poetry run python ../../test_gemini_models_api.py
```

### Method 3: Quick One-Liner

```bash
cd services/fastapi-backend
poetry run python -c "
from google import genai
import os

client = genai.Client(
    vertexai=True,
    project=os.getenv('GOOGLE_CLOUD_PROJECT'),
    location=os.getenv('VERTEX_AI_LOCATION', 'us-central1')
)

print('Models supporting generateContent:')
for m in client.models.list():
    if 'generateContent' in m.supported_actions:
        print(f'  {m.base_model_id} - {m.display_name}')
"
```

### Method 4: Test Backend API Endpoint

```bash
# Make sure backend is running (docker-compose up)
curl http://localhost:8000/api/v1/vote-extraction/models | jq '.providers[0].models[] | {name, display_name}'
```

## Expected Output

If working correctly, you should see:

```
============================================================
Testing Gemini Models API with Vertex AI
============================================================
Project: your-project-id
Location: us-central1

✅ Client initialized successfully with Vertex AI

List of models that support generateContent:

  - models/gemini-2.5-flash
    Display: Gemini 2.5 Flash
    Base ID: gemini-2.5-flash
    Input Tokens: 1048576
    Output Tokens: 8192

  - models/gemini-2.0-flash-exp
    Display: Gemini 2.0 Flash (Experimental)
    ...

Total models supporting generateContent: 10+
```

## Current Configuration

### In Application

All components use **Vertex AI** as the backend:

**Backend Service** (`vote_extraction_service.py`):
```python
client = genai.Client(
    vertexai=True,
    project=settings.google_cloud_project,
    location=settings.vertex_ai_location,
)
```

**Models Endpoint** (`/api/v1/vote-extraction/models`):
- Uses `vote_extraction_service._get_client()`
- Fetches from Vertex AI
- Falls back to static list on timeout/error

**Frontend** (Streamlit):
- Calls backend `/models` endpoint
- 10 second timeout
- Falls back to static list

## Vertex AI vs Google AI API

### Vertex AI (Current - Production)
```python
client = genai.Client(
    vertexai=True,
    project="your-project",
    location="us-central1"
)
```

**Advantages**:
- ✅ Uses GCP project authentication
- ✅ Better for production
- ✅ Integrated with GCP services
- ✅ Supports custom models

### Google AI API (Alternative - Development)
```python
client = genai.Client()  # Uses GEMINI_API_KEY
```

**Advantages**:
- ✅ Simpler setup (just API key)
- ✅ Good for development
- ✅ No GCP project needed

## Troubleshooting

### Error: GOOGLE_CLOUD_PROJECT not set
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
# or add to .env file
```

### Error: Authentication failed
```bash
gcloud auth application-default login
```

### Error: Timeout
This is expected sometimes. The fallback list will be used:
- Backend: Returns static fallback models
- Frontend: Uses cached static list
- Extraction: Still works with any model name

### Error: Permission denied
Make sure your service account or user has:
- `aiplatform.endpoints.predict` permission
- `aiplatform.models.list` permission

## Performance Notes

- **API Call Speed**: Usually < 2 seconds
- **Timeout Setting**: 5 seconds backend, 10 seconds frontend
- **Fallback**: Always available if API fails
- **Caching**: Could be added for production

## Next Steps After Testing

1. **If API works fast (< 2s)**:
   - ✅ Keep dynamic fetching
   - Consider adding caching (Redis/memory)

2. **If API is slow (> 5s)**:
   - ⚠️ Use static list only
   - Or increase timeout
   - Or add background refresh

3. **If API fails**:
   - ✅ Fallback is already in place
   - Users still get models
   - Extraction works normally

---

**Test it now and let me know the results!** 🧪

