# 🧪 Run Model Experiments - Quick Reference

**Status**: ✅ Implemented  
**Date**: January 4, 2026

---

## 🎯 Quick Start

### 1. Streamlit UI (Easiest)

```bash
# Start services
docker compose up -d

# Open browser
open http://localhost:8501

# Navigate to "🧪 Run Experiments" page
# Configure and click "▶️ Run Experiments"
```

---

### 2. FastAPI API (Programmatic)

```bash
# Quick test
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {"model": "gemini-2.5-flash-lite", "temperature": 0.0},
      {"model": "gemini-2.5-flash", "temperature": 0.0}
    ],
    "sample_size": 4,
    "jobs": 2
  }'
```

---

### 3. GitHub Actions (CI/CD)

```bash
# Manual trigger:
# 1. Go to Actions → Run LLM Experiments
# 2. Click "Run workflow"
# 3. Configure inputs (dataset: vote-extraction-bangbamru-1-10, sample: 4)
# 4. Click "Run workflow"

# Or schedule: Runs every Monday at 8am UTC
```

---

## 📋 Features

| Feature | Streamlit | API | GitHub Actions |
|---------|-----------|-----|----------------|
| **Multiple models** | ✅ | ✅ | ✅ |
| **Custom sample size** | ✅ | ✅ | ✅ |
| **Parallel jobs** | ✅ | ✅ | ✅ |
| **Quick presets** | ✅ | ❌ | ✅ |
| **Results visualization** | ✅ | ❌ | ❌ |
| **Comparison URL** | ✅ | ✅ | ✅ |
| **Async execution** | ✅ | ✅ | ❌ |

---

## 🚀 Quick Presets (Streamlit Only)

| Preset | Models | Purpose |
|--------|--------|---------|
| **🎯 Baseline Comparison** | flash + lite | Compare standard vs. cost-optimized |
| **🌡️ Temperature Test** | flash (T=0.0, 0.1, 0.2) | Test temperature impact |
| **🚀 Quick CI Test** | flash-lite + flash | Fast CI/CD test (4 samples) |

---

## 🔧 Required Configuration

### Environment Variables

```bash
# .env file
DD_API_KEY=your-dd-api-key        # Required
DD_SITE=datadoghq.com              # Required
API_KEY=your-api-key               # Required
GOOGLE_CLOUD_PROJECT=your-project  # Required
```

### GitHub Secrets (for CI/CD)

- `DD_API_KEY`: Datadog API key
- `DD_APP_KEY`: Datadog Application key
- `GCP_SA_KEY`: GCP service account key
- `GCP_PROJECT_ID`: GCP project ID

---

## 📊 Example Results

```json
{
  "status": "success",
  "message": "Successfully ran 2 experiments",
  "total_experiments": 2,
  "successful_experiments": 2,
  "experiments": [
    {
      "model": "gemini-2.5-flash",
      "overall_accuracy": 0.95,
      "success_rate": 1.0,
      "experiment_url": "https://app.datadoghq.com/..."
    }
  ],
  "comparison_url": "https://app.datadoghq.com/llm/experiments?dataset=..."
}
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not configured" | Set `API_KEY` in `.env` |
| "Failed to load dataset" | Check dataset exists in Datadog |
| "Connection refused" | Start backend: `docker compose up -d` |
| "401 Unauthorized" | Verify `X-API-Key` header is set |

---

## 📖 Full Documentation

See [RUN_EXPERIMENTS_IMPLEMENTATION.md](./RUN_EXPERIMENTS_IMPLEMENTATION.md) for complete guide.

---

## ✨ Summary

**Three Ways to Run Experiments**:
1. **Streamlit UI** - Interactive, visual, easy presets
2. **FastAPI API** - Programmatic, flexible, automation-ready
3. **GitHub Actions** - Automated CI/CD, scheduled runs

**Key Benefits**:
- ✅ Compare multiple models in one run
- ✅ Track results in Datadog LLMObs
- ✅ Get direct comparison URLs
- ✅ Flexible configuration (sample size, parallel jobs, etc.)
- ✅ Production-ready with authentication

**Get Started**: `docker compose up -d` → http://localhost:8501 → "🧪 Run Experiments"

---

**Implementation Complete!** 🎉

