# ✅ LLM Judge - Updated to Use Vertex AI

**Updated LLM-as-Judge evaluator to use Vertex AI (same as main extraction service)**

---

## 🔄 What Changed

### Before: Gemini API with API Key
```python
# ❌ OLD: Required separate API key
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
```

### After: Vertex AI with Application Default Credentials
```python
# ✅ NEW: Uses same GCP auth as main app
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("VERTEX_AI_LOCATION", "us-central1")

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location,
)
```

---

## ✅ Benefits

### 1. **Consistent Authentication**
- ✅ Uses same GCP setup as main extraction service
- ✅ No need for separate `GEMINI_API_KEY`
- ✅ Application Default Credentials (ADC)

### 2. **Simplified Configuration**
- ✅ No additional environment variables
- ✅ Works automatically if extraction works
- ✅ Single authentication flow

### 3. **Production Ready**
- ✅ Same auth as production extraction
- ✅ Cloud Run compatible
- ✅ Uses Workload Identity in GCP

### 4. **Better Integration**
- ✅ Follows same pattern as `vote_extraction_service.py`
- ✅ Consistent error handling
- ✅ Same logging format

---

## 📋 Prerequisites (Already Configured!)

Your project already has everything needed:

```bash
# These are already set in your docker-compose.yml
GOOGLE_CLOUD_PROJECT=datadog-sandbox        # ✅ Already configured
VERTEX_AI_LOCATION=us-central1              # ✅ Already configured
```

**Mounted Credentials:**
```yaml
volumes:
  - ${HOME}/.config/gcloud:/root/.config/gcloud:ro  # ✅ Already mounted
```

---

## 🚀 Usage (No Changes Required!)

### Automatic Operation

The LLM judge **works automatically** using the same GCP configuration:

```
1. Experiments run as normal
2. LLM judge uses Vertex AI (same as extraction)
3. Evaluates quality with gemini-3-pro-preview
4. Logs detailed reasoning
5. Returns scores to Datadog LLMObs
```

### Example: Run Experiments

**Via Streamlit:**
```
http://localhost:8501 → 🧪 Run Experiments
```

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [{"model": "gemini-2.5-flash", "temperature": 0.0}],
    "sample_size": 2
  }'
```

**LLM Judge runs automatically!** No configuration changes needed.

---

## 📝 Updated Code

### File: `services/fastapi-backend/app/services/experiments_service.py`

```python
def llm_judge_evaluator(input_data: Dict, output_data: Dict, expected_output: Dict) -> float:
    """
    LLM-as-Judge evaluator using gemini-3-pro-preview via Vertex AI.
    
    Uses Google GenAI SDK with Vertex AI (same as main extraction service).
    """
    import json
    from google import genai
    from google.genai import types
    
    try:
        # Get GCP configuration (same as extraction service)
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        
        if not project_id:
            logger.warning("LLM Judge: GOOGLE_CLOUD_PROJECT not set, skipping evaluation")
            return 0.0
        
        # Initialize Google GenAI client with Vertex AI
        # Uses Application Default Credentials (same as main extraction)
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )
        
        # Build evaluation prompt
        form_set_name = input_data.get("form_set_name", "Unknown")
        prompt = f"""..."""  # Full prompt
        
        # Call Gemini 3 Pro Preview as judge via Vertex AI
        logger.info(f"LLM Judge: Evaluating form {form_set_name} with gemini-3-pro-preview (Vertex AI)")
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
                max_output_tokens=4096,
            ),
        )
        
        # Parse and log results
        evaluation = json.loads(response.text)
        score = float(evaluation.get("score", 0.0))
        # ... (rest of the logic)
        
        return score
        
    except Exception as e:
        logger.error(f"LLM Judge: Error evaluating: {e}", exc_info=True)
        return 0.0
```

---

## 🔍 Pattern Consistency

### Main Extraction Service Pattern

```python
# vote_extraction_service.py
def _get_client(self) -> genai.Client:
    if self._client is None:
        self._client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.vertex_ai_location,
        )
    return self._client
```

### LLM Judge Pattern (Now Matches!)

```python
# experiments_service.py - llm_judge_evaluator()
client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location,
)
```

**✅ Same authentication method!**

---

## 📊 Verification

### Check Backend Logs

```bash
# Restart backend
docker-compose restart fastapi-backend

# Check startup
docker logs genai-fastapi-backend --tail 20

# Should see:
# ✅ GCP Project: datadog-sandbox
# ✅ Vertex AI Location: us-central1
```

### Test LLM Judge

```bash
# Run experiment (2 records for quick test)
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [{"model": "gemini-2.5-flash", "temperature": 0.0}],
    "sample_size": 2
  }'

# Check LLM judge logs
docker logs genai-fastapi-backend | grep "LLM Judge"

# Should see:
# INFO: LLM Judge: Evaluating form ... with gemini-3-pro-preview (Vertex AI)
```

---

## ⚠️ Error Handling

### Missing GCP Project

```python
if not project_id:
    logger.warning("LLM Judge: GOOGLE_CLOUD_PROJECT not set, skipping evaluation")
    return 0.0  # Score 0 instead of neutral 0.5
```

**Result:** 
- Warning logged
- Score: 0.0
- Other evaluators continue

### Vertex AI API Error

```python
except Exception as e:
    logger.error(f"LLM Judge: Error evaluating: {e}", exc_info=True)
    return 0.0
```

**Result:**
- Full stack trace logged
- Score: 0.0
- Experiment continues

---

## 💰 Cost (Unchanged)

**Billing:**
- ✅ Charges to same GCP project
- ✅ Same billing as extraction service
- ✅ ~$0.01 per evaluation

**No Additional Costs:**
- ❌ No separate API key charges
- ❌ No additional setup fees

---

## 🎯 Next Steps

### 1. Verify (Optional)

```bash
# Check GCP configuration
docker exec genai-fastapi-backend env | grep -E "GOOGLE_CLOUD|VERTEX_AI"

# Should show:
# GOOGLE_CLOUD_PROJECT=datadog-sandbox
# VERTEX_AI_LOCATION=us-central1
```

### 2. Run Experiments

Go to http://localhost:8501 → 🧪 Run Experiments and test!

### 3. Check Logs

```bash
docker logs genai-fastapi-backend | grep "LLM Judge"
```

You should see: `"LLM Judge: Evaluating form ... with gemini-3-pro-preview (Vertex AI)"`

---

## 📚 Related Documentation

- **Main Guide**: `LLM_JUDGE_EVALUATOR.md` (updated)
- **Extraction Service**: `services/fastapi-backend/app/services/vote_extraction_service.py`
- **Experiments**: `RUN_EXPERIMENTS_IMPLEMENTATION.md`

---

## ✅ Summary

**Changed:**
- ✅ LLM judge now uses Vertex AI
- ✅ Same auth as main extraction service
- ✅ No separate API key required
- ✅ Pattern consistent with vote_extraction_service.py

**Impact:**
- ✅ Simplified configuration
- ✅ Better production alignment
- ✅ Consistent authentication
- ✅ No user action required

**Migration:**
- ✅ No changes to experiments API
- ✅ No changes to Streamlit UI
- ✅ No changes to dataset format
- ✅ Works automatically!

---

**LLM Judge now uses Vertex AI!** 🤖✨

Same authentication, simpler setup, production-ready! 🚀

