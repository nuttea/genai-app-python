# 🧪 Run Model Experiments - Complete Implementation

**Status**: ✅ Implemented  
**Date**: January 4, 2026  
**Features**: FastAPI Backend API, Streamlit UI, GitHub Actions Workflow

---

## 📋 Overview

This implementation provides three ways to run LLM model experiments with Datadog LLMObs:

1. **FastAPI Backend API** - RESTful endpoints for programmatic access
2. **Streamlit UI** - Interactive web interface for manual experiment runs
3. **GitHub Actions Workflow** - Automated CI/CD experiments

All three methods support:
- Multiple model configurations in a single run
- Configurable experiment settings (sample size, parallel jobs, etc.)
- Automatic result tracking in Datadog LLMObs
- Direct comparison URLs for side-by-side analysis

---

## 🎯 Features

### Core Capabilities

- ✅ Run experiments with multiple model configurations
- ✅ Pull datasets from Datadog LLMObs
- ✅ Execute vote extraction tasks with custom evaluators
- ✅ Track results in Datadog dashboard
- ✅ Generate comparison URLs automatically
- ✅ Support both sync and async execution
- ✅ CI/CD integration with GitHub Actions

### Evaluators

**Per-Record Evaluators**:
- `exact_form_match`: Check if form_info matches exactly
- `ballot_accuracy_score`: Calculate ballot statistics accuracy
- `vote_results_quality`: Calculate vote results accuracy
- `has_no_errors`: Check if extraction had no errors

**Summary Evaluators**:
- `overall_accuracy`: Overall accuracy across all metrics
- `success_rate`: Success rate (no errors)
- `avg_ballot_accuracy`: Average ballot accuracy

---

## 📂 Files Created

### 1. FastAPI Backend

| File | Purpose |
|------|---------|
| `services/fastapi-backend/app/models/experiments.py` | Pydantic models for requests/responses |
| `services/fastapi-backend/app/services/experiments_service.py` | Core experiment logic |
| `services/fastapi-backend/app/api/v1/endpoints/experiments.py` | API endpoints |
| `services/fastapi-backend/app/api/v1/router.py` | Router registration (updated) |

### 2. Streamlit Frontend

| File | Purpose |
|------|---------|
| `frontend/streamlit/pages/3_🧪_Run_Experiments.py` | Interactive experiment UI |

### 3. GitHub Actions

| File | Purpose |
|------|---------|
| `.github/workflows/run-experiments.yml` | Automated CI/CD workflow |

### 4. Documentation

| File | Purpose |
|------|---------|
| `RUN_EXPERIMENTS_IMPLEMENTATION.md` | This file - complete guide |

---

## 🚀 Usage

### Option 1: Streamlit UI (Recommended for Manual Testing)

1. **Start Streamlit**:
   ```bash
   docker compose up streamlit-frontend
   # or
   cd frontend/streamlit
   streamlit run app.py
   ```

2. **Navigate to Experiments Page**:
   - Open http://localhost:8501
   - Go to "🧪 Run Experiments" page

3. **Configure Settings**:
   - **LLMObs Settings**: Set ML app name, Datadog site, project name
   - **Dataset Settings**: Select dataset name and version
   - **Experiment Settings**: Set sample size, parallel jobs, error handling

4. **Add Model Configurations**:
   - Click "➕ Add Model Configuration" to add models
   - Or use **Quick Presets**:
     - 🎯 Baseline Comparison
     - 🌡️ Temperature Test
     - 🚀 Quick CI Test

5. **Run Experiments**:
   - Click "▶️ Run Experiments (Sync)" to wait for results
   - Or "⏱️ Run Experiments (Async)" for background execution

6. **View Results**:
   - See metrics and comparison URL
   - Download results as JSON
   - Click comparison URL to view in Datadog

---

### Option 2: FastAPI Backend API (Programmatic Access)

#### Endpoint: `POST /api/v1/experiments/run`

**Authentication**: Requires `X-API-Key` header

**Request Body**:
```json
{
  "ml_app": "vote-extractor",
  "site": "datadoghq.com",
  "agentless_enabled": true,
  "project_name": "vote-extraction-project",
  "dataset_name": "vote-extraction-bangbamru-1-10",
  "dataset_version": null,
  "model_configs": [
    {
      "model": "gemini-2.5-flash",
      "temperature": 0.0,
      "name_suffix": "baseline",
      "metadata": {"purpose": "baseline test"}
    },
    {
      "model": "gemini-2.5-flash-lite",
      "temperature": 0.0,
      "name_suffix": "lite",
      "metadata": {"purpose": "cost optimization"}
    }
  ],
  "sample_size": 10,
  "jobs": 2,
  "raise_errors": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Successfully ran 2 experiments",
  "total_experiments": 2,
  "successful_experiments": 2,
  "failed_experiments": 0,
  "experiments": [
    {
      "experiment_id": "exp_123",
      "experiment_name": "vote-extraction-baseline",
      "experiment_url": "https://app.datadoghq.com/llm/experiments/exp_123",
      "model": "gemini-2.5-flash",
      "temperature": 0.0,
      "status": "success",
      "total_records": 10,
      "successful_records": 10,
      "failed_records": 0,
      "overall_accuracy": 0.95,
      "success_rate": 1.0,
      "avg_ballot_accuracy": 0.98
    }
  ],
  "dataset_name": "vote-extraction-bangbamru-1-10",
  "dataset_size": 10,
  "project_name": "vote-extraction-project",
  "comparison_url": "https://app.datadoghq.com/llm/experiments?dataset=abc123&project=vote-extraction-project",
  "dataset_id": "abc123"
}
```

**Example using cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "name_suffix": "baseline"
      }
    ],
    "sample_size": 10,
    "jobs": 2
  }'
```

**Example using Python**:
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/experiments/run",
    json={
        "dataset_name": "vote-extraction-bangbamru-1-10",
        "model_configs": [
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.0,
                "name_suffix": "baseline",
            }
        ],
        "sample_size": 10,
        "jobs": 2,
    },
    headers={"X-API-Key": "your-api-key"},
    timeout=600.0,
)

result = response.json()
print(f"Comparison URL: {result['comparison_url']}")
```

#### Async Endpoint: `POST /api/v1/experiments/run-async`

For long-running experiments, use the async endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/experiments/run-async \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {"model": "gemini-2.5-flash", "temperature": 0.0}
    ],
    "sample_size": 100,
    "jobs": 4
  }'
```

**Response** (202 Accepted):
```json
{
  "status": "accepted",
  "message": "Experiments started in background",
  "task_id": "not-implemented",
  "note": "Results will be available in Datadog LLMObs dashboard"
}
```

#### Health Check: `GET /api/v1/experiments/health`

Check if experiments service is configured:

```bash
curl http://localhost:8000/api/v1/experiments/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "experiments",
  "datadog_configured": true,
  "api_key_configured": true,
  "note": "Experiments require Datadog API key and backend API key"
}
```

---

### Option 3: GitHub Actions Workflow (CI/CD)

#### Manual Trigger

1. Go to **Actions** → **Run LLM Experiments**
2. Click "Run workflow"
3. Configure inputs:
   - **Dataset name**: `vote-extraction-bangbamru-1-10`
   - **Sample size**: `4`
   - **Project name**: `vote-extraction-project`
4. Click "Run workflow"

#### Scheduled Run

The workflow runs automatically every Monday at 8am UTC:

```yaml
schedule:
  - cron: '0 8 * * 1'
```

#### Configuration

Edit `.github/workflows/run-experiments.yml` to customize:

**Model Configurations** (line ~150):
```python
model_configs = [
    {
        'model': 'gemini-2.5-flash-lite',
        'temperature': 0.0,
        'name_suffix': 'ci-lite',
        'metadata': {'purpose': 'ci-test'},
    },
    {
        'model': 'gemini-2.5-flash',
        'temperature': 0.0,
        'name_suffix': 'ci-flash',
        'metadata': {'purpose': 'ci-test'},
    },
]
```

**Required Secrets**:
- `DD_API_KEY`: Datadog API key
- `DD_APP_KEY`: Datadog Application key
- `DD_SITE`: Datadog site (default: `datadoghq.com`)
- `GCP_SA_KEY`: GCP service account key (for Vertex AI)
- `GCP_PROJECT_ID`: GCP project ID
- `VERTEX_AI_LOCATION`: Vertex AI location (default: `us-central1`)

---

## 🔧 Configuration

### Environment Variables

**Required**:
- `DD_API_KEY`: Datadog API key for LLMObs
- `DD_SITE`: Datadog site (default: `datadoghq.com`)
- `API_KEY`: FastAPI backend API key (for authentication)
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `VERTEX_AI_LOCATION`: Vertex AI location

**Optional**:
- `DD_APP_KEY`: Datadog Application key (for API access)
- `API_BASE_URL`: Backend URL (default: `http://localhost:8000`)
- `DD_ENV`: Environment tag (default: `development`)
- `DD_SERVICE`: Service name (default: `vote-extractor`)

### `.env` File Example

```bash
# Datadog
DD_API_KEY=your-dd-api-key
DD_APP_KEY=your-dd-app-key
DD_SITE=datadoghq.com
DD_ENV=development
DD_SERVICE=vote-extractor

# Backend API
API_KEY=your-api-key
API_BASE_URL=http://localhost:8000

# GCP
GOOGLE_CLOUD_PROJECT=your-gcp-project
VERTEX_AI_LOCATION=us-central1
```

---

## 📊 Example Workflows

### Quick CI Test (2 models, 4 samples)

**Streamlit**: Use "🚀 Quick CI Test" preset

**API**:
```bash
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {"model": "gemini-2.5-flash-lite", "temperature": 0.0, "name_suffix": "ci-lite"},
      {"model": "gemini-2.5-flash", "temperature": 0.0, "name_suffix": "ci-flash"}
    ],
    "sample_size": 4,
    "jobs": 2
  }'
```

**GitHub Actions**: Trigger workflow with `sample_size=4`

---

### Baseline Comparison (2 models, 10 samples)

**Streamlit**: Use "🎯 Baseline Comparison" preset

**API**:
```bash
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {"model": "gemini-2.5-flash", "temperature": 0.0, "name_suffix": "baseline"},
      {"model": "gemini-2.5-flash-lite", "temperature": 0.0, "name_suffix": "lite"}
    ],
    "sample_size": 10,
    "jobs": 2
  }'
```

---

### Temperature Test (3 temperatures, full dataset)

**Streamlit**: Use "🌡️ Temperature Test" preset

**API**:
```bash
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {"model": "gemini-2.5-flash", "temperature": 0.0, "name_suffix": "t0.0"},
      {"model": "gemini-2.5-flash", "temperature": 0.1, "name_suffix": "t0.1"},
      {"model": "gemini-2.5-flash", "temperature": 0.2, "name_suffix": "t0.2"}
    ],
    "jobs": 2
  }'
```

---

## 🧪 Testing

### Local Testing

1. **Start services**:
   ```bash
   docker compose up -d
   ```

2. **Test API health**:
   ```bash
   curl http://localhost:8000/api/v1/experiments/health
   ```

3. **Run a quick test**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/experiments/run \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $API_KEY" \
     -d '{
       "dataset_name": "vote-extraction-bangbamru-1-10",
       "model_configs": [
         {"model": "gemini-2.5-flash", "temperature": 0.0}
       ],
       "sample_size": 2,
       "jobs": 1
     }'
   ```

4. **Test Streamlit UI**:
   - Open http://localhost:8501
   - Navigate to "🧪 Run Experiments"
   - Configure and run a test experiment

### CI/CD Testing

1. **Manual workflow trigger**:
   - Go to GitHub Actions → Run LLM Experiments
   - Click "Run workflow"
   - Monitor progress

2. **Verify results in Datadog**:
   - Open Datadog LLMObs dashboard
   - Find your project: `vote-extraction-project`
   - View experiment results

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "API key not configured"

**Problem**: Missing `API_KEY` environment variable

**Solution**:
```bash
# Add to .env
API_KEY=your-api-key

# Or set in environment
export API_KEY=your-api-key
```

#### 2. "Failed to load dataset"

**Problem**: Dataset not found in Datadog or wrong project name

**Solution**:
- Verify dataset exists in Datadog LLMObs
- Check `dataset_name` matches exactly
- Ensure `project_name` is correct
- Verify `DD_API_KEY` is set

#### 3. "Request Error: Connection refused"

**Problem**: Backend not running or wrong URL

**Solution**:
```bash
# Check backend is running
docker ps | grep fastapi-backend

# Or start it
docker compose up -d fastapi-backend

# Verify URL
echo $API_BASE_URL
```

#### 4. "HTTP 401 Unauthorized"

**Problem**: Missing or invalid API key

**Solution**:
```bash
# Verify API_KEY is set
echo $API_KEY

# Test with explicit key
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

#### 5. GitHub Actions failures

**Problem**: Missing secrets or GCP credentials

**Solution**:
- Verify all required secrets are set in GitHub
- Check GCP service account has necessary permissions
- Review workflow logs for specific error

---

## 📈 Best Practices

### 1. Sample Size

- **Development/Testing**: Use `sample_size=2-4` for quick feedback
- **CI/CD**: Use `sample_size=4-10` for automated testing
- **Production**: Use full dataset (`sample_size=None`) for comprehensive results

### 2. Parallel Jobs

- **Local**: `jobs=1-2` to avoid rate limits
- **CI/CD**: `jobs=2` for balance between speed and stability
- **Production**: `jobs=4-8` for faster processing

### 3. Error Handling

- **Development**: `raise_errors=True` to catch issues early
- **CI/CD**: `raise_errors=False` to continue testing other models
- **Production**: `raise_errors=True` for accurate results

### 4. Model Selection

- **Quick tests**: Use `gemini-2.5-flash-lite` for speed
- **Baseline**: Use `gemini-2.5-flash` as reference
- **Quality**: Use `gemini-1.5-pro` for best accuracy

### 5. Metadata Tags

Add descriptive metadata for easier filtering in Datadog:

```json
{
  "model": "gemini-2.5-flash",
  "temperature": 0.0,
  "metadata": {
    "purpose": "baseline",
    "environment": "production",
    "version": "v1.2.0",
    "commit": "abc123"
  }
}
```

---

## 🔗 Related Documentation

- **Notebook Implementation**: See `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
- **Wrapper Function**: See `WRAPPER_FUNCTION_COMPLETE.md`
- **Datadog LLMObs**: See official Datadog documentation
- **FastAPI Docs**: http://localhost:8000/docs

---

## ✨ Summary

| Component | Status | Endpoint/Path |
|-----------|--------|---------------|
| **FastAPI API** | ✅ Ready | `/api/v1/experiments/run` |
| **Streamlit UI** | ✅ Ready | `pages/3_🧪_Run_Experiments.py` |
| **GitHub Actions** | ✅ Ready | `.github/workflows/run-experiments.yml` |
| **Documentation** | ✅ Complete | This file |

**Key Features**:
- ✅ Multiple model comparison
- ✅ Configurable experiment settings
- ✅ Datadog LLMObs integration
- ✅ Automatic comparison URLs
- ✅ Sync and async execution
- ✅ CI/CD automation

**Next Steps**:
1. Configure environment variables
2. Start services with `docker compose up -d`
3. Access Streamlit UI at http://localhost:8501
4. Run your first experiment!
5. View results in Datadog LLMObs dashboard

---

**Implementation Complete!** 🎉

All three interfaces (API, UI, CI/CD) are ready to use. Choose the method that best fits your workflow.

