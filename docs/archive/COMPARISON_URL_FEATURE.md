# ✅ Datadog Comparison URL Feature

**Feature**: Automatic generation of Datadog experiment comparison URLs  
**Status**: ✅ Complete  
**Date**: January 4, 2026

---

## 🎯 What Was Added

The `run_model_experiments()` wrapper function now automatically generates a direct link to view all experiments side-by-side in Datadog's comparison view.

**URL Format**:
```
https://app.datadoghq.com/llm/experiments?dataset={dataset_id}&project={project_name}
```

---

## ✨ Features

### 1. Automatic Dataset ID Extraction

The function extracts the dataset ID from `dataset.url`:

```python
# Dataset URL: https://app.datadoghq.com/llm/datasets/241bfded-e79d-4d2d-bbc4-a74bb06d85f9
# Extracted ID: 241bfded-e79d-4d2d-bbc4-a74bb06d85f9
```

### 2. Comparison URL Generation

Combines dataset ID + project name:

```python
comparison_url = f"https://app.datadoghq.com/llm/experiments?dataset={dataset_id}&project={project_name}"
```

### 3. Multiple Access Methods

The comparison URL is available in three ways:

#### Console Output
```
🔍 Compare all experiments side-by-side:
   https://app.datadoghq.com/llm/experiments?dataset=241bfded...&project=vote-extraction-project
```

#### Return Dictionary
```python
results = run_model_experiments(...)
print(results['comparison_url'])
```

#### Programmatic Usage
```python
import webbrowser
results = run_model_experiments(...)
webbrowser.open(results['comparison_url'])
```

---

## 🔧 Implementation

### Code Changes

**File**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`

#### 1. Extract Dataset ID (After Loading)

```python
# Extract dataset ID from URL for comparison link
dataset_id = None
try:
    # Dataset URL format: https://app.datadoghq.com/llm/datasets/{dataset_id}
    if hasattr(dataset, 'url') and dataset.url:
        dataset_id = dataset.url.split('/datasets/')[-1]
        print(f"   Dataset ID: {dataset_id}")
except Exception as e:
    print(f"   ⚠️  Could not extract dataset ID: {e}")
```

#### 2. Print Comparison URL (In Comparison Section)

```python
# Generate comparison URL if dataset_id is available
if dataset_id:
    comparison_url = f"https://app.datadoghq.com/llm/experiments?dataset={dataset_id}&project={project_name}"
    print(f"\n🔍 Compare all experiments side-by-side:")
    print(f"   {comparison_url}")
    print(f"{'=' * 120}\n")
```

#### 3. Add to Return Dictionary

```python
result_dict = {
    "experiments": all_results,
    "total_experiments": len(all_results),
    "successful_experiments": len([r for r in all_results if r['status'] == 'success']),
    "failed_experiments": len([r for r in all_results if r['status'] == 'failed']),
    "dataset_name": dataset_name,
    "dataset_size": len(dataset),
    "project_name": project_name
}

# Add comparison URL if available
if dataset_id:
    result_dict["comparison_url"] = f"https://app.datadoghq.com/llm/experiments?dataset={dataset_id}&project={project_name}"
    result_dict["dataset_id"] = dataset_id

return result_dict
```

---

## 📊 Example Output

### Before (Individual Links Only)

```
🔗 View in Datadog:
   ✅ vote-extraction-flash-t0: https://app.datadoghq.com/llm/experiments/abc...
   ✅ vote-extraction-lite-t0: https://app.datadoghq.com/llm/experiments/def...
   ✅ vote-extraction-pro-t0: https://app.datadoghq.com/llm/experiments/ghi...
```

### After (With Comparison Link)

```
🔗 View in Datadog:
   ✅ vote-extraction-flash-t0: https://app.datadoghq.com/llm/experiments/abc...
   ✅ vote-extraction-lite-t0: https://app.datadoghq.com/llm/experiments/def...
   ✅ vote-extraction-pro-t0: https://app.datadoghq.com/llm/experiments/ghi...

🔍 Compare all experiments side-by-side:
   https://app.datadoghq.com/llm/experiments?dataset=241bfded...&project=vote-extraction-project
```

---

## 🚀 Usage Examples

### Example 1: Print Comparison URL

```python
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0},
        {"model": "gemini-2.5-flash-lite", "temperature": 0.0}
    ],
    sample_size=10
)

# Access comparison URL
if 'comparison_url' in results:
    print(f"🔍 Compare: {results['comparison_url']}")
```

### Example 2: Open in Browser

```python
import webbrowser

results = run_model_experiments(...)

# Open comparison view in browser
if 'comparison_url' in results:
    webbrowser.open(results['comparison_url'])
```

### Example 3: Share with Team

```python
results = run_model_experiments(...)

# Generate shareable link
if 'comparison_url' in results:
    comparison_link = results['comparison_url']
    
    # Send via email, Slack, etc.
    print(f"📧 Share this link with your team:")
    print(f"   {comparison_link}")
```

### Example 4: Save to File

```python
import json

results = run_model_experiments(...)

# Save results with comparison URL
with open('experiment_results.json', 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "comparison_url": results.get('comparison_url'),
        "summary": {
            "total": results['total_experiments'],
            "successful": results['successful_experiments']
        }
    }, f, indent=2)

print("✅ Results saved with comparison URL!")
```

---

## 🎁 Benefits

### For Individual Use
- ✅ **Quick access** - One click to see all experiments
- ✅ **Visual comparison** - Side-by-side metrics and charts
- ✅ **Interactive filtering** - Filter by model, temperature, etc.
- ✅ **Historical tracking** - Revisit past comparisons

### For Teams
- ✅ **Easy sharing** - Share URL via email/Slack
- ✅ **Collaborative review** - Team members can view same comparison
- ✅ **Consistent view** - Everyone sees the same experiments
- ✅ **Documentation** - Include in reports and docs

### For Production
- ✅ **Decision making** - Compare models before deployment
- ✅ **Performance tracking** - Monitor improvements over time
- ✅ **Audit trail** - Keep links to all experiment comparisons
- ✅ **Reproducibility** - Reference specific experiment sets

---

## 📂 Files Updated

| File | Change |
|------|--------|
| `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` | ✅ Cell 46: Extract dataset ID<br>✅ Cell 46: Print comparison URL<br>✅ Cell 46: Add to return dict<br>✅ Cell 48: Show usage example |
| `WRAPPER_FUNCTION_COMPLETE.md` | ✅ Updated return value docs<br>✅ Added comparison URL section<br>✅ Added usage examples |
| `WRAPPER_FUNCTION_QUICK.md` | ✅ Updated output example<br>✅ Updated return value<br>✅ Added pro tip |
| `COMPARISON_URL_FEATURE.md` | ✅ Feature documentation (this file) |

---

## 🔍 URL Structure Explained

### Dataset URL (Source)
```
https://app.datadoghq.com/llm/datasets/241bfded-e79d-4d2d-bbc4-a74bb06d85f9
                                          └─────────────── dataset_id ──────────────┘
```

### Comparison URL (Generated)
```
https://app.datadoghq.com/llm/experiments?dataset=241bfded-e79d-4d2d-bbc4-a74bb06d85f9&project=vote-extraction-project
                                                   └──────────── dataset_id ────────────┘  └──── project_name ────┘
```

### URL Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| `dataset` | `241bfded...` | Extracted from `dataset.url` |
| `project` | `vote-extraction-project` | Function parameter `project_name` |

---

## ✨ Return Value Updates

### New Fields Added

```python
{
    # ... existing fields ...
    "project_name": str,        # NEW: Project name
    "comparison_url": str,      # NEW: Datadog comparison URL
    "dataset_id": str          # NEW: Extracted dataset ID
}
```

### Full Return Structure

```python
{
    "experiments": [...],
    "total_experiments": 3,
    "successful_experiments": 3,
    "failed_experiments": 0,
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "dataset_size": 10,
    "project_name": "vote-extraction-project",
    "comparison_url": "https://app.datadoghq.com/llm/experiments?dataset=241bfded...&project=vote-extraction-project",
    "dataset_id": "241bfded-e79d-4d2d-bbc4-a74bb06d85f9"
}
```

---

## 🧪 Testing

### Verify Extraction

```python
from ddtrace.llmobs import LLMObs

# Initialize and load dataset
LLMObs.enable(...)
dataset = LLMObs.pull_dataset(...)

# Check URL structure
print(f"Dataset URL: {dataset.url}")
# Output: https://app.datadoghq.com/llm/datasets/241bfded-e79d-4d2d-bbc4-a74bb06d85f9

# Extract ID
dataset_id = dataset.url.split('/datasets/')[-1]
print(f"Dataset ID: {dataset_id}")
# Output: 241bfded-e79d-4d2d-bbc4-a74bb06d85f9
```

### Verify Comparison URL

```python
results = run_model_experiments(...)

assert 'comparison_url' in results
assert 'dataset_id' in results
assert results['dataset_id'] in results['comparison_url']
assert results['project_name'] in results['comparison_url']

print("✅ All checks passed!")
```

---

## 💡 Tips

### 1. Bookmark Comparison URLs

Save frequently used comparison URLs as browser bookmarks for quick access.

### 2. Include in Documentation

Add comparison URLs to your experiment documentation:

```markdown
## Experiment Results (2026-01-04)

- Flash vs Flash-Lite: [Compare](https://app.datadoghq.com/llm/experiments?...)
- Temperature Study: [Compare](https://app.datadoghq.com/llm/experiments?...)
```

### 3. Automated Reporting

Generate weekly reports with comparison URLs:

```python
weekly_experiments = [
    run_model_experiments(config=config1),
    run_model_experiments(config=config2),
]

report = "# Weekly Experiment Report\n\n"
for i, exp in enumerate(weekly_experiments, 1):
    report += f"## Experiment Set {i}\n"
    report += f"- [View Comparison]({exp['comparison_url']})\n"
    report += f"- Best: {exp['experiments'][0]['model']}\n\n"

with open('weekly_report.md', 'w') as f:
    f.write(report)
```

---

## 🎯 Key Takeaways

✅ **Automatic generation** - No manual URL construction needed  
✅ **Multiple access methods** - Console, return dict, programmatic  
✅ **Team collaboration** - Easy sharing and viewing  
✅ **Production ready** - Documented and tested  
✅ **Backward compatible** - Gracefully handles missing dataset URLs  

---

## 🔗 Related Documentation

- **Complete Guide**: `WRAPPER_FUNCTION_COMPLETE.md`
- **Quick Reference**: `WRAPPER_FUNCTION_QUICK.md`
- **Notebook**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` → Section 6

---

**Ready!** 🚀 Run `run_model_experiments()` and get automatic comparison URLs for all your experiments!

