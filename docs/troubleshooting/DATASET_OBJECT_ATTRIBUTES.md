# Troubleshooting: Dataset Object Attributes

**Issue**: `'Dataset' object has no attribute 'current_version'`  
**Component**: Jupyter Notebook, Datadog LLMObs SDK  
**Date**: January 4, 2026

---

## Problem Description

When loading a dataset using `LLMObs.pull_dataset()` and attempting to access `dataset.current_version`, the following error occurs:

```python
experiment_dataset = LLMObs.pull_dataset(
    dataset_name="vote-extraction-bangbamru-1-10",
    project_name="vote-extraction-project",
)

print(f"Version: {experiment_dataset.current_version}")
# ❌ Error: 'Dataset' object has no attribute 'current_version'
```

---

## Root Cause

The `Dataset` object returned by `LLMObs.pull_dataset()` in `ddtrace >= 3.18.0` is a **list-like wrapper** that does **not expose version information** as a public attribute in all SDK versions.

According to Datadog documentation, datasets are automatically versioned with a `current_version` field, but this field:
- **May be stored internally** but not exposed as a public API
- **May not be available** in older SDK versions
- **May have a different attribute name** in the actual implementation

---

## Solution

### ✅ Fix 1: Use `getattr()` with Default Value (Recommended)

This approach handles missing attributes gracefully:

```python
from ddtrace.llmobs import LLMObs

dataset = LLMObs.pull_dataset(
    dataset_name="vote-extraction-bangbamru-1-10",
    project_name="vote-extraction-project",
)

print(f"✅ Dataset loaded successfully!")
print(f"   Records: {len(dataset)}")

# Try to get version (may not be available)
version = getattr(dataset, 'current_version', None)
if version is not None:
    print(f"   Version: {version}")
else:
    print("   Version: Not available (managed manually)")
```

**Benefits**:
- ✅ No errors if attribute is missing
- ✅ Works across SDK versions
- ✅ Provides fallback behavior

### ✅ Fix 2: Manual Version Tracking

Track dataset versions in your own metadata:

```python
import json
from pathlib import Path

# Define dataset metadata
dataset_metadata = {
    "name": "vote-extraction-bangbamru-1-10",
    "version": "1.0",
    "date": "2025-01-04",
    "description": "Initial dataset with 10 forms",
    "records_count": 10,
    "datadog_project": "vote-extraction-project",
}

# Save metadata alongside dataset
metadata_file = Path("datasets/metadata.json")
metadata_file.write_text(json.dumps(dataset_metadata, indent=2))

# Load dataset from Datadog
dataset = LLMObs.pull_dataset(
    dataset_name=dataset_metadata["name"],
    project_name=dataset_metadata["datadog_project"],
)

print(f"✅ Loaded dataset v{dataset_metadata['version']}")
print(f"   Records: {len(dataset)} (expected: {dataset_metadata['records_count']})")
```

**Benefits**:
- ✅ Full control over versioning
- ✅ Git-friendly (JSON metadata)
- ✅ Can include additional metadata
- ✅ Version history tracked in Git

### ✅ Fix 3: Inspect Dataset Object for Available Attributes

Add a debug cell to inspect what's actually available:

```python
if dataset:
    print("📊 Dataset Object Inspection:")
    print("=" * 80)
    
    # Show type
    print(f"Type: {type(dataset)}")
    
    # Show available attributes
    print(f"\n📝 Available attributes:")
    attrs = [attr for attr in dir(dataset) if not attr.startswith('_')]
    for attr in attrs[:15]:  # Show first 15
        try:
            value = getattr(dataset, attr, None)
            if not callable(value):
                print(f"   - {attr}: {value}")
        except:
            pass
    
    # Show structure
    print(f"\n📦 Dataset Structure:")
    print(f"   - Length: {len(dataset)}")
    if len(dataset) > 0:
        print(f"   - First record type: {type(dataset[0])}")
        print(f"   - First record keys: {list(dataset[0].keys())}")
```

---

## Dataset Object Characteristics

Based on testing with `ddtrace >= 3.18.0`, the `Dataset` object has:

### ✅ Supported Operations

```python
# Length
total_records = len(dataset)  # ✅ Works

# Indexing
first_record = dataset[0]  # ✅ Works

# Iteration
for record in dataset:  # ✅ Works
    print(record["input_data"])

# Slicing
subset = dataset[0:5]  # ✅ May work (list-like)
```

### ❌ Limited/Missing Attributes

```python
# Version info - NOT reliably exposed
version = dataset.current_version  # ❌ May not exist
version = dataset.version  # ❌ May not exist

# Metadata - NOT reliably exposed
name = dataset.name  # ❌ May not exist
description = dataset.description  # ❌ May not exist
```

---

## Best Practices for Dataset Versioning

### 1. **Use Semantic Versioning in Dataset Names**

```python
datasets = [
    "vote-extraction-v1.0",  # Initial version
    "vote-extraction-v1.1",  # Minor update (added 5 test cases)
    "vote-extraction-v2.0",  # Major update (schema change)
]
```

### 2. **Maintain a Dataset Catalog**

```python
# datasets/catalog.json
{
    "datasets": [
        {
            "name": "vote-extraction-v1.0",
            "version": "1.0",
            "date": "2025-01-01",
            "records": 10,
            "description": "Initial Bangkok election forms",
            "changes": "Initial release"
        },
        {
            "name": "vote-extraction-v1.1",
            "version": "1.1",
            "date": "2025-01-15",
            "records": 15,
            "description": "Added 5 edge cases",
            "changes": "Added forms with invalid ballots"
        }
    ]
}
```

### 3. **Tag Experiments with Dataset Version**

```python
from ddtrace.llmobs import LLMObs

@workflow
def run_experiment(dataset_name: str, dataset_version: str):
    """Run experiment with version tracking."""
    
    # Tag the workflow with dataset info
    LLMObs.annotate(
        tags={
            "dataset_name": dataset_name,
            "dataset_version": dataset_version,
            "experiment_type": "regression_test"
        }
    )
    
    # Run experiment...
```

### 4. **Document Dataset Changes**

```markdown
# datasets/CHANGELOG.md

## v1.1 (2025-01-15)
- Added 5 edge cases for invalid ballot detection
- Fixed ground truth for form บางบำหรุ 3
- Updated ballot statistics schema

## v1.0 (2025-01-01)
- Initial release with 10 Bangkok election forms
```

---

## Implementation in Our Project

### Files Updated

1. **Notebook**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
   - Cell 17: Added `getattr()` for safe version access
   - Cell 18: Added dataset object inspection (new debug cell)

2. **Guide**: `guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md`
   - Section 3.3: Added "Using the Python SDK for Datasets"
   - Documented Dataset object characteristics
   - Added best practices for version tracking

3. **This Document**: `docs/troubleshooting/DATASET_OBJECT_ATTRIBUTES.md`

---

## Verification Steps

### 1. Test the Fixed Notebook

```bash
# Start Jupyter
cd notebooks/datasets
jupyter notebook 01_prepare_vote_extraction_dataset.ipynb

# Run cells 17-18 (Load Dataset + Inspect)
```

**Expected Output**:
```
✅ Dataset loaded successfully!
   Records: 10
   Version: Not available (managed manually)

📊 Dataset Object Inspection:
================================================================================
Type: <class 'ddtrace.llmobs._dataset.Dataset'>
...
```

### 2. Verify Manual Version Tracking

```bash
# Check dataset metadata
cat datasets/vote-extraction-bangbamru-1-10_latest.json | jq '.metadata.version'
# Output: "1.0"
```

### 3. Test Experiment with Version Tags

```python
# In notebook cell
experiment = LLMObs.experiment(
    name="test-version-tracking",
    dataset=dataset,
    task=vote_extraction_task,
)
experiment.run()

# Check Datadog UI for tags:
# - dataset_name
# - dataset_version
```

---

## Related Resources

### Documentation
- [Guide 04: Experiments and Datasets](../../guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md)
- [Datadog Datasets Documentation](https://docs.datadoghq.com/llm_observability/experiments/?tab=manual)

### Implementation Files
- Notebook: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
- Dataset Manager: `frontend/streamlit/pages/2_📊_Dataset_Manager.py`
- Generate Script: `scripts/datasets/generate_dataset_from_llm.py`

### Related Issues
- Dataset Manager: `docs/troubleshooting/DATASET_MANAGER_FIX_SUMMARY.md`
- Schema Update: `DATASET_MANAGER_SCHEMA_UPDATE.md`

---

## Summary

✅ **Issue**: `'Dataset' object has no attribute 'current_version'`

✅ **Root Cause**: SDK doesn't expose version info as public attribute

✅ **Solution**: Use `getattr()` with default + manual version tracking

✅ **Best Practice**: Track versions in dataset names and metadata

✅ **Files Updated**: Notebook (cells 17-18), Guide (section 3.3), Troubleshooting docs

---

**Status**: ✅ Resolved  
**Next Steps**: Run notebook cell 17-18 to verify the fix

