# ✅ Wrapper Function: run_model_experiments()

**Feature**: Comprehensive wrapper function for running multiple LLM experiments  
**Status**: ✅ Complete  
**Date**: January 4, 2026

---

## 🎯 Overview

Added a powerful wrapper function `run_model_experiments()` that makes it easy to run multiple LLM experiments with custom configurations in a single function call.

**Location**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` → Section 6

---

## ✨ Key Features

### 1. LLMObs Configuration
- Configure `ml_app`, `api_key`, `site`, `agentless_enabled`, `project_name`
- Automatic initialization and error handling
- Falls back to environment variables

### 2. Model Configuration
- Test multiple models in one run
- Custom temperature settings per model
- Flexible metadata and naming

### 3. Run Configuration
- Set `sample_size`, `jobs`, `raise_errors`
- Parallel processing support
- Error handling options

### 4. Automated Results
- Automatic comparison table
- Best performer identification
- Detailed result dictionary

---

## ⚠️ Important Note

The function uses `tags` (not `metadata`) for the `LLMObs.experiment()` call, as required by the Datadog LLMObs SDK. All metadata values are automatically converted to strings for tag compatibility.

## 📖 Function Signature

```python
def run_model_experiments(
    # LLMObs Configuration
    ml_app: str = "vote-extractor",
    api_key: str = None,
    site: str = "datadoghq.com",
    agentless_enabled: bool = True,
    project_name: str = "vote-extraction-project",
    
    # Dataset Configuration
    dataset_name: str = "vote-extraction-bangbamru-1-10",
    dataset_version: Optional[int] = None,
    
    # Models and Temperatures to Test
    model_configs: Optional[List[Dict[str, Any]]] = None,
    
    # Task Function
    task_function: Optional[Callable] = None,
    
    # Evaluators
    evaluators: Optional[List[Callable]] = None,
    summary_evaluators: Optional[List[Callable]] = None,
    
    # Run Configuration
    sample_size: Optional[int] = None,
    jobs: int = 2,
    raise_errors: bool = True,
    
    # Options
    show_comparison: bool = True,
    return_results: bool = True
) -> Dict[str, Any]
```

---

## 🚀 Quick Start

### Example 1: Simplest Usage (Defaults)

```python
# Run with defaults: 3 models (flash, flash-lite, pro) at T=0.0
results = run_model_experiments(
    sample_size=10,
    jobs=2,
    raise_errors=True
)
```

**Output**:
```
🔧 INITIALIZING DATADOG LLMOBS
✅ LLMObs enabled
📊 Loading dataset: vote-extraction-bangbamru-1-10
✅ Dataset loaded: 10 records

🚀 RUNNING 3 EXPERIMENTS
────────────────────────────────────────────────────────────────────────────────
🧪 Experiment 1/3: gemini-2.5-flash (T=0.0)
✅ Created: vote-extraction-flash-t0
⏱️  Running...
✅ Completed! Processed 10 records
📈 Summary Metrics:
   - overall_accuracy: 98.5
   - success_rate: 100.0
   - avg_ballot_accuracy: 99.2
────────────────────────────────────────────────────────────────────────────────
... (2 more experiments)

📊 EXPERIMENT COMPARISON
Experiment                  Model                   Temperature  Status   Accuracy  Success  Ballot
vote-extraction-flash-t0    gemini-2.5-flash       0.0          success  98.5%     100%     99.2%
vote-extraction-lite-t0     gemini-2.5-flash-lite  0.0          success  96.8%     100%     97.5%
vote-extraction-pro-t0      gemini-3-pro-preview   0.0          success  99.1%     100%     99.8%

🏆 BEST PERFORMER:
   Model: gemini-3-pro-preview
   Temperature: 0.0
   Overall Accuracy: 99.1%
```

---

## 📋 Usage Examples

### Example 2: Custom Models and Temperatures

```python
results = run_model_experiments(
    model_configs=[
        {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "name_suffix": "flash-deterministic",
            "metadata": {"purpose": "Production baseline", "cost_tier": "medium"}
        },
        {
            "model": "gemini-2.5-flash",
            "temperature": 0.1,
            "name_suffix": "flash-tolerant",
            "metadata": {"purpose": "Tolerance test", "cost_tier": "medium"}
        },
        {
            "model": "gemini-2.5-flash",
            "temperature": 0.2,
            "name_suffix": "flash-varied",
            "metadata": {"purpose": "Variation test", "cost_tier": "medium"}
        },
        {
            "model": "gemini-2.5-flash-lite",
            "temperature": 0.0,
            "name_suffix": "lite-speed",
            "metadata": {"purpose": "High-volume test", "cost_tier": "low"}
        }
    ],
    sample_size=10,
    jobs=2,
    raise_errors=False  # Continue even if one fails
)
```

### Example 3: Full Configuration

```python
results = run_model_experiments(
    # LLMObs configuration
    ml_app="vote-extractor-advanced",
    api_key=os.getenv("DD_API_KEY"),
    site="datadoghq.com",
    agentless_enabled=True,
    project_name="vote-extraction-project",
    
    # Dataset configuration
    dataset_name="vote-extraction-bangbamru-1-10",
    dataset_version=None,  # Latest
    
    # Models to test
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0},
        {"model": "gemini-3-pro-preview", "temperature": 0.0}
    ],
    
    # Task and evaluators
    task_function=vote_extraction_task,
    evaluators=[exact_form_match, ballot_accuracy_score, vote_results_quality, has_no_errors],
    summary_evaluators=[overall_accuracy, success_rate, avg_ballot_accuracy],
    
    # Run configuration
    sample_size=10,
    jobs=2,
    raise_errors=True,
    
    # Display options
    show_comparison=True,
    return_results=True
)
```

---

## 📊 Model Configuration Format

Each model configuration is a dictionary with the following fields:

```python
{
    "model": str,              # Required: Model name (e.g., "gemini-2.5-flash")
    "temperature": float,      # Required: Temperature (0.0-1.0)
    "name_suffix": str,        # Optional: Custom experiment name suffix
    "metadata": dict          # Optional: Additional tags (converted to strings automatically)
}
```

**Note**: The `metadata` dict is converted to `tags` for the Datadog LLMObs experiment, with all values stringified.

### Examples

```python
# Minimal
{"model": "gemini-2.5-flash", "temperature": 0.0}

# With custom naming
{
    "model": "gemini-2.5-flash",
    "temperature": 0.0,
    "name_suffix": "prod-baseline"
}

# With full metadata
{
    "model": "gemini-2.5-flash-lite",
    "temperature": 0.0,
    "name_suffix": "lite-speed-test",
    "metadata": {
        "purpose": "High-volume processing",
        "cost_tier": "low",
        "use_case": "Production candidate"
    }
}
```

---

## 🎯 Parameters Reference

### LLMObs Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ml_app` | str | `"vote-extractor"` | Datadog LLMObs application name |
| `api_key` | str | `None` | Datadog API key (defaults to `DD_API_KEY` env var) |
| `site` | str | `"datadoghq.com"` | Datadog site (e.g., `datadoghq.eu`) |
| `agentless_enabled` | bool | `True` | Enable agentless mode |
| `project_name` | str | `"vote-extraction-project"` | LLMObs project name |

### Dataset Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_name` | str | `"vote-extraction-bangbamru-1-10"` | Dataset name in Datadog |
| `dataset_version` | int | `None` | Specific version (None = latest) |

### Models and Evaluators

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_configs` | List[Dict] | 3 default models | List of model configurations |
| `task_function` | Callable | `vote_extraction_task` | Task function to execute |
| `evaluators` | List[Callable] | Standard set | Per-record evaluators |
| `summary_evaluators` | List[Callable] | Standard set | Summary evaluators |

### Run Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sample_size` | int | `None` | Number of records (None = all) |
| `jobs` | int | `2` | Parallel jobs |
| `raise_errors` | bool | `True` | Stop on first error |

### Display Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `show_comparison` | bool | `True` | Print comparison table |
| `return_results` | bool | `True` | Return results dictionary |

---

## 📤 Return Value

Returns a dictionary with the following structure:

```python
{
    "experiments": [
        {
            "experiment_name": str,
            "model": str,
            "temperature": float,
            "sample_size": int,
            "summary_metrics": dict,
            "url": str,
            "status": str  # "success" or "failed"
        },
        ...
    ],
    "total_experiments": int,
    "successful_experiments": int,
    "failed_experiments": int,
    "dataset_name": str,
    "dataset_size": int,
    "project_name": str,
    "comparison_url": str,  # Datadog URL to compare all experiments side-by-side
    "dataset_id": str       # Dataset ID extracted from dataset.url
}
```

### Example

```python
results = run_model_experiments(...)

print(f"Total: {results['total_experiments']}")
print(f"Successful: {results['successful_experiments']}")

# Access individual experiments
for exp in results['experiments']:
    print(f"{exp['experiment_name']}: {exp['status']}")
    print(f"  Accuracy: {exp['summary_metrics'].get('overall_accuracy')}%")
    print(f"  URL: {exp['url']}")

# Compare all experiments side-by-side in Datadog
if 'comparison_url' in results:
    print(f"\n🔍 Compare all experiments:")
    print(f"   {results['comparison_url']}")
    # Opens: https://app.datadoghq.com/llm/experiments?dataset=241bfded-e79d-4d2d-bbc4-a74bb06d85f9&project=vote-extraction-project
```

---

## 💡 Use Cases

### 1. Temperature Comparison

```python
# Compare same model with different temperatures
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0},
        {"model": "gemini-2.5-flash", "temperature": 0.1},
        {"model": "gemini-2.5-flash", "temperature": 0.2},
    ],
    sample_size=10
)
```

### 2. Cost vs. Quality Analysis

```python
# Compare models across cost tiers
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash-lite", "temperature": 0.0},  # Low cost
        {"model": "gemini-2.5-flash", "temperature": 0.0},       # Medium cost
        {"model": "gemini-3-pro-preview", "temperature": 0.0}    # High cost
    ]
)
```

### 3. Fast Iteration (Sample)

```python
# Quick test on 3 records
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0}
    ],
    sample_size=3,  # Fast iteration
    jobs=1
)
```

### 4. Production Validation

```python
# Full dataset, all evaluators
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0}
    ],
    sample_size=None,  # All records
    jobs=2,
    raise_errors=True  # Fail fast
)
```

---

## 🔍 Comparison Output

The function automatically generates a comparison table and provides a direct link to view all experiments side-by-side in Datadog:

```
📊 EXPERIMENT COMPARISON
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
Experiment                    Model                   Temperature  Status   Records  Overall Accuracy  Success Rate  Avg Ballot Accuracy
vote-extraction-flash-t0      gemini-2.5-flash       0.0          success  10       98.5             100.0         99.2
vote-extraction-lite-t0       gemini-2.5-flash-lite  0.0          success  10       96.8             100.0         97.5
vote-extraction-pro-t0        gemini-3-pro-preview   0.0          success  10       99.1             100.0         99.8

════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
🔗 View in Datadog:
   ✅ vote-extraction-flash-t0: https://app.datadoghq.com/llm/experiments/...
   ✅ vote-extraction-lite-t0: https://app.datadoghq.com/llm/experiments/...
   ✅ vote-extraction-pro-t0: https://app.datadoghq.com/llm/experiments/...
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

🔍 Compare all experiments side-by-side:
   https://app.datadoghq.com/llm/experiments?dataset=241bfded-e79d-4d2d-bbc4-a74bb06d85f9&project=vote-extraction-project
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

🏆 BEST PERFORMER:
   Model: gemini-3-pro-preview
   Temperature: 0.0
   Overall Accuracy: 99.1%
```

---

## 🔗 Datadog Comparison URL

The function automatically generates a direct link to compare all experiments side-by-side in Datadog.

### URL Format

```
https://app.datadoghq.com/llm/experiments?dataset={dataset_id}&project={project_name}
```

**Where**:
- `dataset_id`: Extracted from `dataset.url` (e.g., `241bfded-e79d-4d2d-bbc4-a74bb06d85f9`)
- `project_name`: Your LLMObs project name (e.g., `vote-extraction-project`)

### Accessing the URL

The comparison URL is available in three ways:

#### 1. Printed in Console

```
🔍 Compare all experiments side-by-side:
   https://app.datadoghq.com/llm/experiments?dataset=...&project=...
```

#### 2. In Return Dictionary

```python
results = run_model_experiments(...)

if 'comparison_url' in results:
    print(results['comparison_url'])
    # Opens browser or shares with team
```

#### 3. Programmatically

```python
import webbrowser

results = run_model_experiments(...)

# Open comparison in browser
if 'comparison_url' in results:
    webbrowser.open(results['comparison_url'])
```

### Benefits

✅ **Side-by-side comparison** - View all experiments in one page  
✅ **Interactive filtering** - Filter by model, temperature, metrics  
✅ **Visual charts** - Compare accuracy trends visually  
✅ **Easy sharing** - Share URL with team members  
✅ **Historical tracking** - Access past experiment comparisons  

---

## ⚠️ Error Handling

### Automatic Error Handling

- **Missing API Key**: Raises `ValueError` with clear message
- **Failed Experiment**: Marks as failed, continues if `raise_errors=False`
- **LLMObs Already Enabled**: Catches exception, continues gracefully

### Example with Error Handling

```python
# Continue even if some experiments fail
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0},
        {"model": "invalid-model", "temperature": 0.0},  # Will fail
        {"model": "gemini-2.5-flash-lite", "temperature": 0.0}
    ],
    raise_errors=False  # Don't stop on first error
)

# Check results
print(f"Failed: {results['failed_experiments']}")
for exp in results['experiments']:
    if exp['status'] == 'failed':
        print(f"❌ {exp['experiment_name']}: {exp.get('error')}")
```

---

## 📚 Complete Example

```python
# Complete workflow with wrapper function
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Run comprehensive experiments
results = run_model_experiments(
    # LLMObs setup
    ml_app="vote-extractor-comparison",
    project_name="vote-extraction-project",
    
    # Test configuration
    model_configs=[
        # Baseline
        {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "name_suffix": "baseline",
            "metadata": {"version": "v1", "purpose": "Production baseline"}
        },
        # Speed test
        {
            "model": "gemini-2.5-flash-lite",
            "temperature": 0.0,
            "name_suffix": "speed",
            "metadata": {"version": "v1", "purpose": "High-volume test"}
        },
        # Quality test
        {
            "model": "gemini-3-pro-preview",
            "temperature": 0.0,
            "name_suffix": "quality",
            "metadata": {"version": "v1", "purpose": "Maximum accuracy"}
        }
    ],
    
    # Run config
    sample_size=10,
    jobs=2,
    raise_errors=True
)

# Analyze results
print("\n📊 Analysis:")
best = max(
    results['experiments'],
    key=lambda x: x['summary_metrics'].get('overall_accuracy', 0)
)
print(f"🏆 Best: {best['model']} at T={best['temperature']}")
print(f"   Accuracy: {best['summary_metrics']['overall_accuracy']}%")

# Save results (optional)
import json
with open('experiment_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## 🎯 Best Practices

### 1. Start Small, Scale Up

```python
# Development: Test on sample
results = run_model_experiments(sample_size=3, jobs=1)

# Production: Run on full dataset
results = run_model_experiments(sample_size=None, jobs=2)
```

### 2. Use Meaningful Names

```python
model_configs=[
    {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "name_suffix": "prod-v1-baseline",  # Clear, versioned
        "metadata": {"date": "2026-01-04", "purpose": "Production baseline"}
    }
]
```

### 3. Handle Errors Appropriately

```python
# Development: Fail fast
results = run_model_experiments(raise_errors=True)

# Production validation: Continue on errors
results = run_model_experiments(raise_errors=False)
```

### 4. Document Metadata

```python
metadata={
    "purpose": "Production baseline",
    "version": "v1.0",
    "date": "2026-01-04",
    "cost_tier": "medium",
    "expected_qps": "100"
}
```

---

## 📂 Files Added

| File | Description |
|------|-------------|
| `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` | ✅ Section 6 added (7 new cells) |
| `WRAPPER_FUNCTION_COMPLETE.md` | ✅ Complete documentation (this file) |

---

## 🔗 Related Documentation

- **Experiments Guide**: `EXPERIMENTS_MODEL_COMPARISON.md`
- **Notebook**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
- **LLMObs Docs**: `docs/monitoring/DATADOG_LLMOBS_COMPLETE.md`

---

## ✨ Summary

✅ **Comprehensive wrapper function** for running multiple experiments  
✅ **Easy configuration** with sensible defaults  
✅ **Flexible model configs** with temperature control  
✅ **Automatic comparison** and best performer identification  
✅ **Error handling** with continue-on-error option  
✅ **Complete examples** from simple to advanced  

**Ready to use!** 🚀 Just call `run_model_experiments()` with your desired configuration!

