# 🧪 Run Model Experiments - Architecture Overview

**Visual guide to the complete implementation**

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │
│  │              │   │              │   │              │          │
│  │  Streamlit   │   │  FastAPI     │   │  GitHub      │          │
│  │  UI 🎨       │   │  REST API    │   │  Actions ⚙️   │          │
│  │              │   │              │   │              │          │
│  │ Interactive  │   │ Programmatic │   │ Automated    │          │
│  │ Quick Presets│   │ Sync/Async   │   │ CI/CD Tests  │          │
│  │              │   │              │   │              │          │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │    FastAPI Backend                         │
        │    /api/v1/experiments/                    │
        │                                            │
        │  ┌──────────────────────────────────────┐ │
        │  │  Endpoints                           │ │
        │  │  • POST /run (sync)                  │ │
        │  │  • POST /run-async (background)      │ │
        │  │  • GET /health                       │ │
        │  └──────────────────────────────────────┘ │
        │                │                           │
        │                ▼                           │
        │  ┌──────────────────────────────────────┐ │
        │  │  Experiments Service                 │ │
        │  │  • run_experiments()                 │ │
        │  │  • vote_extraction_task()            │ │
        │  │  • Evaluators (4 per-record)         │ │
        │  │  • Summary Evaluators (3 summary)    │ │
        │  └──────────────────────────────────────┘ │
        │                │                           │
        └────────────────┼───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │    Datadog LLMObs                          │
        │                                            │
        │  ┌──────────────────────────────────────┐ │
        │  │  LLMObs.enable()                     │ │
        │  │  • Initialize tracking               │ │
        │  │  • Configure ML app                  │ │
        │  └──────────────────────────────────────┘ │
        │                │                           │
        │                ▼                           │
        │  ┌──────────────────────────────────────┐ │
        │  │  LLMObs.pull_dataset()               │ │
        │  │  • Load dataset from Datadog         │ │
        │  │  • Get test data                     │ │
        │  └──────────────────────────────────────┘ │
        │                │                           │
        │                ▼                           │
        │  ┌──────────────────────────────────────┐ │
        │  │  LLMObs.experiment()                 │ │
        │  │  • Create experiment                 │ │
        │  │  • Run with evaluators               │ │
        │  │  • Track results                     │ │
        │  └──────────────────────────────────────┘ │
        │                │                           │
        │                ▼                           │
        │  ┌──────────────────────────────────────┐ │
        │  │  Results & Comparison URL            │ │
        │  │  • Metrics per model                 │ │
        │  │  • Comparison dashboard link         │ │
        │  └──────────────────────────────────────┘ │
        │                                            │
        └────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │    Google Vertex AI                        │
        │                                            │
        │  ┌──────────────────────────────────────┐ │
        │  │  Gemini Models                       │ │
        │  │  • gemini-2.5-flash                  │ │
        │  │  • gemini-2.5-flash-lite             │ │
        │  │  • gemini-2.0-flash-exp              │ │
        │  │  • gemini-1.5-flash                  │ │
        │  │  • gemini-1.5-pro                    │ │
        │  └──────────────────────────────────────┘ │
        │                │                           │
        │                ▼                           │
        │  ┌──────────────────────────────────────┐ │
        │  │  Vote Extraction                     │ │
        │  │  • Process Thai election forms       │ │
        │  │  • Extract structured data           │ │
        │  │  • With thinking_config enabled      │ │
        │  └──────────────────────────────────────┘ │
        │                                            │
        └────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. User Initiates Experiment

```
User (Streamlit/API/GitHub Actions)
  ↓
  Sends: ExperimentRequest
    • dataset_name
    • model_configs []
    • sample_size
    • jobs
```

### 2. Backend Processes Request

```
FastAPI Backend
  ↓
  1. Validate request (Pydantic)
  2. Authenticate (API key)
  3. Call experiments_service.run_experiments()
```

### 3. LLMObs Initialization

```
LLMObs.enable()
  ↓
  Configure:
    • ml_app: "vote-extractor"
    • site: "datadoghq.com"
    • agentless_enabled: true
```

### 4. Dataset Loading

```
LLMObs.pull_dataset()
  ↓
  Returns: Dataset object
    • records []
    • url
    • current_version
```

### 5. Experiment Execution (Per Model)

```
For each model_config:
  ↓
  1. Create experiment
     LLMObs.experiment(
       name="vote-extraction-{suffix}",
       task=vote_extraction_task,
       dataset=dataset,
       evaluators=[...],
       tags={...}
     )
  
  ↓
  2. Run experiment
     experiment.run(
       sample_size=10,
       jobs=2,
       raise_errors=True
     )
  
  ↓
  3. Collect results
     • Per-record metrics
     • Summary metrics
     • Experiment URL
```

### 6. Results Aggregation

```
Aggregate all experiments:
  ↓
  • Total: 2
  • Successful: 2
  • Failed: 0
  • Comparison URL: https://app.datadoghq.com/...
```

### 7. Response to User

```
ExperimentResponse
  ↓
  • Status: "success"
  • Experiments: [...]
  • Comparison URL
  • Dataset info
```

---

## 📊 Data Models

### ExperimentRequest

```python
{
  "ml_app": "vote-extractor",
  "site": "datadoghq.com",
  "project_name": "vote-extraction-project",
  "dataset_name": "vote-extraction-bangbamru-1-10",
  "dataset_version": null,
  "model_configs": [
    {
      "model": "gemini-2.5-flash",
      "temperature": 0.0,
      "name_suffix": "baseline",
      "metadata": {"purpose": "baseline"}
    }
  ],
  "sample_size": 10,
  "jobs": 2,
  "raise_errors": true
}
```

### ExperimentResponse

```python
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
      "experiment_url": "https://...",
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
  "comparison_url": "https://...",
  "dataset_id": "abc123"
}
```

---

## 🧩 Component Responsibilities

### 1. Streamlit UI (`pages/3_🧪_Run_Experiments.py`)

**Responsibilities**:
- User input collection
- Configuration validation
- Quick presets
- Results visualization
- Download functionality

**Key Features**:
- 4 quick presets
- Dynamic model config management
- JSON metadata editor
- Results caching

---

### 2. FastAPI Endpoints (`api/v1/endpoints/experiments.py`)

**Responsibilities**:
- Request validation
- Authentication
- Route to service layer
- Error handling
- Response formatting

**Endpoints**:
- `POST /run` - Synchronous execution
- `POST /run-async` - Background execution
- `GET /health` - Service health check

---

### 3. Experiments Service (`services/experiments_service.py`)

**Responsibilities**:
- LLMObs initialization
- Dataset loading
- Experiment orchestration
- Evaluator execution
- Results aggregation

**Key Functions**:
- `run_experiments()` - Main orchestrator
- `vote_extraction_task()` - Task wrapper
- Evaluators (7 total)

---

### 4. Pydantic Models (`models/experiments.py`)

**Responsibilities**:
- Request validation
- Response serialization
- Type safety
- Documentation

**Models**:
- `ModelConfig`
- `ExperimentRequest`
- `ExperimentSummary`
- `ExperimentResponse`

---

### 5. GitHub Actions (`.github/workflows/run-experiments.yml`)

**Responsibilities**:
- Automated testing
- CI/CD integration
- Scheduled runs
- Result reporting

**Triggers**:
- Manual (`workflow_dispatch`)
- Scheduled (Monday 8am UTC)
- Push (optional)

---

## 🎯 Use Case Matrix

| Use Case | Recommended Interface | Sample Size | Jobs |
|----------|----------------------|-------------|------|
| **Quick local test** | Streamlit UI | 2-4 | 1-2 |
| **Manual comparison** | Streamlit UI | 10+ | 2-4 |
| **Automated CI/CD** | GitHub Actions | 4-10 | 2 |
| **Integration tests** | FastAPI API | 2-10 | 1-2 |
| **Production validation** | FastAPI API (async) | Full | 4-8 |
| **Temperature tuning** | Streamlit UI (preset) | 10+ | 2-4 |
| **Cost optimization** | Streamlit UI (preset) | 10+ | 2-4 |
| **Scheduled monitoring** | GitHub Actions | 10+ | 2-4 |

---

## 🚀 Quick Access

### Start Services

```bash
docker compose up -d
```

### Access Points

| Interface | URL | Auth Required |
|-----------|-----|---------------|
| **Streamlit** | http://localhost:8501 | No |
| **API Docs** | http://localhost:8000/docs | No (for viewing) |
| **API Endpoint** | http://localhost:8000/api/v1/experiments/run | Yes (X-API-Key) |
| **Health Check** | http://localhost:8000/api/v1/experiments/health | No |

### Quick Commands

```bash
# Test API health
curl http://localhost:8000/api/v1/experiments/health

# Run quick test (requires API_KEY)
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {"model": "gemini-2.5-flash", "temperature": 0.0}
    ],
    "sample_size": 2
  }'

# Open Streamlit
open http://localhost:8501
```

---

## 📖 Documentation Links

| Document | Purpose | Best For |
|----------|---------|----------|
| [Implementation Guide](./RUN_EXPERIMENTS_IMPLEMENTATION.md) | Complete details | Deep dive |
| [Quick Reference](./RUN_EXPERIMENTS_QUICK.md) | Fast lookup | Quick tasks |
| [Summary](./RUN_EXPERIMENTS_SUMMARY.md) | High-level overview | Status check |
| [This File](./RUN_EXPERIMENTS_OVERVIEW.md) | Visual architecture | Understanding flow |

---

## ✨ Key Benefits

1. **Three Interfaces** - Choose what fits your workflow
2. **Production Ready** - Authentication, error handling, validation
3. **Datadog Integration** - Automatic tracking and comparison URLs
4. **Quick Presets** - Common use cases pre-configured
5. **CI/CD Ready** - GitHub Actions for automation
6. **Flexible Configuration** - Sample size, parallel jobs, error handling
7. **Comprehensive Documentation** - Guides for every use case

---

**Get Started**: `docker compose up -d` → http://localhost:8501 → "🧪 Run Experiments"

**All Ready to Use!** 🎉

