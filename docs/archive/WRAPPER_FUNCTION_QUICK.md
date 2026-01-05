# 🚀 Wrapper Function - Quick Reference

**Function**: `run_model_experiments()`  
**Location**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` → Section 6  
**Status**: ✅ Ready to use

---

## 💡 What It Does

Runs multiple LLM experiments with different models/temperatures in a single function call.

**Features**:
- ✅ Automatic LLMObs initialization
- ✅ Multiple model configurations
- ✅ Temperature comparisons
- ✅ Parallel processing
- ✅ Automatic comparison table
- ✅ Best performer identification

---

## 🚀 Quick Start

### Simplest Usage (3 Default Models)

```python
results = run_model_experiments(
    sample_size=10,
    jobs=2,
    raise_errors=True
)
```

**Runs**: gemini-2.5-flash, flash-lite, 3-pro-preview (all at T=0.0)

---

## 📋 Common Patterns

### Pattern 1: Temperature Comparison

```python
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0},
        {"model": "gemini-2.5-flash", "temperature": 0.1},
        {"model": "gemini-2.5-flash", "temperature": 0.2}
    ],
    sample_size=10,
    jobs=2
)
```

### Pattern 2: Cost vs. Quality

```python
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash-lite", "temperature": 0.0},  # Low cost
        {"model": "gemini-2.5-flash", "temperature": 0.0},       # Medium
        {"model": "gemini-3-pro-preview", "temperature": 0.0}    # High cost
    ]
)
```

### Pattern 3: Fast Iteration

```python
# Quick test on 3 records
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0}
    ],
    sample_size=3,
    jobs=1
)
```

---

## ⚙️ Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model_configs` | 3 models | List of models to test |
| `sample_size` | All | Number of records (None = all) |
| `jobs` | `2` | Parallel processing |
| `raise_errors` | `True` | Stop on first error |
| `show_comparison` | `True` | Print comparison table |

---

## 📊 Output

```
🔧 INITIALIZING DATADOG LLMOBS
✅ LLMObs enabled

📊 Loading dataset: vote-extraction-bangbamru-1-10
✅ Dataset loaded: 10 records

🚀 RUNNING 3 EXPERIMENTS
────────────────────────────────────────────────────────────
🧪 Experiment 1/3: gemini-2.5-flash (T=0.0)
✅ Created: vote-extraction-flash-t0
⏱️  Running...
✅ Completed! Processed 10 records
────────────────────────────────────────────────────────────

📊 EXPERIMENT COMPARISON
Experiment              Model                 Temp  Accuracy  Success
vote-extraction-flash   gemini-2.5-flash     0.0   98.5%     100%
vote-extraction-lite    flash-lite           0.0   96.8%     100%
vote-extraction-pro     3-pro-preview        0.0   99.1%     100%

🔍 Compare all experiments side-by-side:
   https://app.datadoghq.com/llm/experiments?dataset=241bfded...&project=vote-extraction-project

🏆 BEST PERFORMER:
   Model: gemini-3-pro-preview
   Temperature: 0.0
   Overall Accuracy: 99.1%
```

---

## 📤 Return Value

```python
{
    "experiments": [
        {
            "experiment_name": "vote-extraction-flash-t0",
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "summary_metrics": {"overall_accuracy": 98.5, ...},
            "url": "https://app.datadoghq.com/...",
            "status": "success"
        },
        ...
    ],
    "total_experiments": 3,
    "successful_experiments": 3,
    "failed_experiments": 0,
    "comparison_url": "https://app.datadoghq.com/llm/experiments?dataset=...&project=...",
    "dataset_id": "241bfded-e79d-4d2d-bbc4-a74bb06d85f9"
}
```

---

## 💡 Pro Tips

### 1. Start Small
```python
# Test with sample first
results = run_model_experiments(sample_size=3)

# Then run full dataset
results = run_model_experiments(sample_size=None)
```

### 2. Custom Naming
```python
model_configs=[
    {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "name_suffix": "prod-v1-baseline"  # Custom name
    }
]
```

### 3. Continue on Errors
```python
# Don't stop if one fails
results = run_model_experiments(
    raise_errors=False
)
```

### 4. Use Comparison URL
```python
results = run_model_experiments(...)

# Open in browser for side-by-side comparison
import webbrowser
if 'comparison_url' in results:
    webbrowser.open(results['comparison_url'])
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "DD_API_KEY not found" | Set in `.env` or pass as parameter |
| "Dataset not found" | Check `dataset_name` parameter |
| Experiment fails | Check `raise_errors` setting |
| Slow execution | Reduce `sample_size` or increase `jobs` |

---

## 📚 Full Documentation

See [WRAPPER_FUNCTION_COMPLETE.md](WRAPPER_FUNCTION_COMPLETE.md) for:
- Complete parameter reference
- Advanced examples
- Error handling
- Best practices

---

**Ready!** 🎉 Open the notebook and call `run_model_experiments()`!

