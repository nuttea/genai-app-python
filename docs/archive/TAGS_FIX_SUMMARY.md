# ✅ Tags Fix: LLMObs.experiment() Parameter

**Issue**: `TypeError: LLMObs.experiment() got an unexpected keyword argument 'metadata'`  
**Solution**: Use `tags` instead of `metadata`  
**Status**: ✅ Fixed  
**Date**: January 4, 2026

---

## 🎯 Problem

The wrapper function was using `metadata` parameter in `LLMObs.experiment()`, but the Datadog LLMObs SDK expects `tags`:

```python
# ❌ WRONG (Before)
experiment = LLMObs.experiment(
    name=experiment_name,
    task=task_function,
    dataset=dataset,
    evaluators=evaluators,
    summary_evaluators=summary_evaluators,
    metadata={  # ❌ TypeError!
        "model": model,
        "temperature": temperature,
        **extra_metadata
    }
)
```

**Error**:
```
TypeError: LLMObs.experiment() got an unexpected keyword argument 'metadata'
```

---

## ✅ Solution

Changed to use `tags` parameter with string values:

```python
# ✅ CORRECT (After)
# Prepare tags (combine model, temperature, and extra metadata)
tags = {
    "model": model,
    "temperature": str(temperature),  # Convert to string
    **{k: str(v) for k, v in extra_metadata.items()}  # Convert all to strings
}

experiment = LLMObs.experiment(
    name=experiment_name,
    task=task_function,
    dataset=dataset,
    evaluators=evaluators,
    summary_evaluators=summary_evaluators,
    tags=tags  # ✅ Correct parameter!
)
```

---

## 🔧 Key Changes

### 1. Use `tags` Instead of `metadata`

```python
# Before
metadata={"model": model, "temperature": temperature}

# After
tags={"model": model, "temperature": str(temperature)}
```

### 2. Convert All Values to Strings

Tags require string values, so we convert everything:

```python
tags = {
    "model": model,                    # Already a string
    "temperature": str(temperature),   # Convert float → string
    **{k: str(v) for k, v in extra_metadata.items()}  # Convert all metadata values
}
```

---

## 📝 Updated Code

**File**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` → Cell 46

**Changes**:

```python
# Create experiment
experiment_name = f"vote-extraction-{name_suffix}"

# Prepare tags (combine model, temperature, and extra metadata)
tags = {
    "model": model,
    "temperature": str(temperature),
    **{k: str(v) for k, v in extra_metadata.items()}
}

experiment = LLMObs.experiment(
    name=experiment_name,
    task=task_function,
    dataset=dataset,
    evaluators=evaluators,
    summary_evaluators=summary_evaluators,
    tags=tags  # ✅ Use tags parameter
)
```

---

## 🧪 Testing

### Before (Error)

```python
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0}
    ]
)
# TypeError: LLMObs.experiment() got an unexpected keyword argument 'metadata'
```

### After (Success)

```python
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0}
    ]
)
# ✅ Works! Creates experiment with tags
```

---

## 📊 Example Tags

### Input Configuration

```python
model_configs=[
    {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "name_suffix": "prod-baseline",
        "metadata": {
            "purpose": "Production baseline",
            "cost_tier": "medium",
            "version": 1.0
        }
    }
]
```

### Generated Tags

```python
tags = {
    "model": "gemini-2.5-flash",
    "temperature": "0.0",           # Float → String
    "purpose": "Production baseline",
    "cost_tier": "medium",
    "version": "1.0"                # Float → String
}
```

---

## 💡 Important Notes

### 1. All Tag Values Must Be Strings

Datadog tags require string values. The function automatically converts:
- `float` → `str` (e.g., `0.0` → `"0.0"`)
- `int` → `str` (e.g., `1` → `"1"`)
- `bool` → `str` (e.g., `True` → `"True"`)

### 2. Metadata Dict Still Works

You can still use `metadata` in your config dict:

```python
model_configs=[
    {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "metadata": {"purpose": "test", "version": 1}  # Still works!
    }
]
```

It's automatically converted to `tags` internally.

### 3. Tag Keys Are Preserved

Tag keys (like `model`, `temperature`, `purpose`) remain as-is. Only values are stringified.

---

## 📂 Files Updated

| File | Change |
|------|--------|
| `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` | ✅ Cell 46: Use `tags` instead of `metadata` |
| `WRAPPER_FUNCTION_COMPLETE.md` | ✅ Added note about tags usage |
| `TAGS_FIX_SUMMARY.md` | ✅ Fix documentation (this file) |

---

## 🔗 Related Information

### Datadog LLMObs SDK

The `LLMObs.experiment()` function signature:

```python
LLMObs.experiment(
    name: str,
    task: Callable,
    dataset: Dataset,
    evaluators: List[Callable] = None,
    summary_evaluators: List[Callable] = None,
    tags: Dict[str, str] = None  # ✅ Use 'tags', not 'metadata'
)
```

### Why Tags?

Datadog uses **tags** for filtering, grouping, and searching experiments:
- Filter by model: `tags.model:gemini-2.5-flash`
- Filter by temperature: `tags.temperature:0.0`
- Group by cost tier: `tags.cost_tier:*`

---

## ✨ Summary

| Aspect | Status |
|--------|--------|
| **Problem** | ✅ Identified: `metadata` parameter invalid |
| **Solution** | ✅ Changed to `tags` parameter |
| **String conversion** | ✅ All values converted to strings |
| **Backward compatible** | ✅ `metadata` dict still works in config |
| **Tested** | ✅ Fixed and verified |
| **Documented** | ✅ Updated docs |

---

**Fixed!** ✅ The wrapper function now correctly uses `tags` instead of `metadata` for LLMObs experiments.

**Usage remains the same**:
```python
results = run_model_experiments(
    model_configs=[
        {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "metadata": {"purpose": "test"}  # Still works!
        }
    ]
)
```

The function handles the `metadata` → `tags` conversion automatically! 🎉

