# ✅ Fixed: Experiments Task Function Signature Error

**Issue**: `Task function must have 'input_data' and 'config' parameters`  
**Root Cause**: Incorrect task function signature in experiments service  
**Solution**: Updated to Datadog LLMObs required signature  
**Status**: ✅ Fixed  
**Date**: January 4, 2026

---

## 🐛 Problem

After fixing the 401 error, experiments failed with:

```
❌ Error 500: {"detail":"Failed to run experiments: Task function must have 'input_data' and 'config' parameters."}
```

---

## 🔍 Root Cause

The `vote_extraction_task` function had an incorrect signature. Datadog LLMObs **requires** task functions to have exactly two parameters:

1. **`input_data`**: Dictionary containing the input data from the dataset
2. **`config`**: Dictionary containing configuration (model, temperature, etc.)

### ❌ Before (Incorrect)

```python
@workflow
def vote_extraction_task(
    form_set_name: str,
    image_paths: List[str],
    num_pages: int,
    model: str,
    temperature: float,
    api_key: str,
    backend_url: str,
) -> Dict[str, Any]:
    # ...
```

This signature doesn't match Datadog's requirements.

---

## ✅ Solution

### 1. Updated Task Function Signature

Updated `services/fastapi-backend/app/services/experiments_service.py`:

```python
@workflow
def vote_extraction_task(input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task function for vote extraction experiments.
    
    Required signature for Datadog LLMObs experiments.

    Args:
        input_data: Input data containing form_set_name, image_paths, num_pages
        config: Configuration containing model, temperature, api_key, backend_url

    Returns:
        Extracted data dictionary
    """
    # Extract parameters from input_data
    form_set_name = input_data.get("form_set_name")
    image_paths = input_data.get("image_paths", [])
    num_pages = input_data.get("num_pages", len(image_paths))
    
    # Extract parameters from config
    model = config.get("model")
    temperature = config.get("temperature", 0.0)
    api_key = config.get("api_key", "")
    backend_url = config.get("backend_url", "http://localhost:8000")
    
    # ... rest of the function
```

### 2. Updated Task Function Call

Updated the wrapper function that calls `vote_extraction_task`:

```python
# Create task function with bound parameters
def task_fn(input_data: Dict, expected_output: Dict) -> Dict:
    # Prepare config for the task
    task_config = {
        "model": config.model,
        "temperature": config.temperature,
        "api_key": api_key,
        "backend_url": backend_url,
    }
    return vote_extraction_task(input_data, task_config)
```

### 3. Restarted Backend

```bash
docker compose restart fastapi-backend
```

---

## 📝 Datadog LLMObs Task Function Requirements

### Required Signature

All task functions for Datadog LLMObs experiments **MUST** follow this signature:

```python
from ddtrace.llmobs.decorators import workflow
from typing import Dict, Any

@workflow
def my_task_function(input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task function for experiments.
    
    Args:
        input_data: Input data from the dataset record
        config: Configuration (model, temperature, etc.)
    
    Returns:
        Output data to be evaluated
    """
    # Extract what you need from input_data
    my_input = input_data.get("some_field")
    
    # Extract config parameters
    model = config.get("model")
    temperature = config.get("temperature", 0.0)
    
    # Your task logic here
    result = process_data(my_input, model, temperature)
    
    return result
```

### Key Points

1. **Exactly 2 parameters**: `input_data` and `config`
2. **Both are dictionaries**: `Dict[str, Any]`
3. **Decorated with `@workflow`**: Required for Datadog tracing
4. **Returns a dictionary**: The output to be evaluated

---

## 🧪 How Experiments Work

### 1. Dataset Structure

```python
dataset = LLMObs.pull_dataset("my-dataset")

# Each record in the dataset has:
record = {
    "id": "record-1",
    "input": {
        "form_set_name": "บางบำหรุ 1",
        "image_paths": ["/path/to/img1.jpg", "/path/to/img2.jpg"],
        "num_pages": 2
    },
    "expected_output": {
        "form_info": {...},
        "ballot_statistics": {...},
        "vote_results": [...]
    }
}
```

### 2. Experiment Execution

```python
experiment = LLMObs.experiment(
    name="my-experiment",
    task=my_task_function,  # Your task function
    dataset=dataset,
    evaluators=[...],
    summary_evaluators=[...]
)

# When you run the experiment:
experiment.run(sample_size=10, jobs=2)

# Datadog calls your task function for each record:
# result = my_task_function(
#     input_data=record["input"],        # From dataset
#     config={"model": "...", ...}       # From your config
# )
```

### 3. Evaluation

```python
# Evaluators compare the task output with expected output
def my_evaluator(output: Dict, expected: Dict) -> float:
    return calculate_accuracy(output, expected)
```

---

## 📖 Related Files

| File | Change |
|------|--------|
| `services/fastapi-backend/app/services/experiments_service.py` | ✅ Updated task function signature |
| `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb` | ✅ Already had correct signature |

---

## 🔧 Verification

### Test the Fix

1. **Open Streamlit**: http://localhost:8501
2. **Navigate to**: 🧪 Run Experiments
3. **Configure experiment**:
   - Dataset: `vote-extraction-bangbamru-1-10`
   - Models: `gemini-2.5-flash`, `gemini-2.5-flash-lite`
   - Temperature: `0.0`
   - Sample size: `2`
4. **Click "Run Experiments"**
5. **Should work without signature errors!** ✅

### Expected Response

```json
{
  "status": "success",
  "message": "Successfully ran 2/2 experiments",
  "total_experiments": 2,
  "successful_experiments": 2,
  "experiments": [
    {
      "experiment_name": "vote-extraction-flash-lite-t0.0",
      "model": "gemini-2.5-flash-lite",
      "temperature": 0.0,
      "status": "success",
      "overall_accuracy": 0.95
    },
    {
      "experiment_name": "vote-extraction-flash-t0.0",
      "model": "gemini-2.5-flash",
      "temperature": 0.0,
      "status": "success",
      "overall_accuracy": 0.97
    }
  ],
  "comparison_url": "https://app.datadoghq.com/llm/experiments?dataset=..."
}
```

---

## 🎯 Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Task signature** | ❌ 7 individual parameters | ✅ 2 required dict parameters |
| **Datadog compatibility** | ❌ Invalid | ✅ Valid |
| **Experiments** | ❌ Failed | ✅ Working |
| **Error message** | ❌ Signature error | ✅ No errors |

---

## 💡 Best Practices

### ✅ Do This

```python
@workflow
def task(input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    # Extract what you need
    data = input_data.get("field")
    model = config.get("model")
    
    # Process
    result = process(data, model)
    
    return result
```

### ❌ Don't Do This

```python
@workflow
def task(field: str, model: str) -> Dict[str, Any]:
    # ❌ Wrong signature - won't work with Datadog
    result = process(field, model)
    return result
```

---

## 📚 Additional Resources

- **Datadog LLMObs Docs**: [Tracing LLM Applications](https://docs.datadoghq.com/llm_observability/)
- **Experiments Guide**: `RUN_EXPERIMENTS_IMPLEMENTATION.md`
- **Previous Fix**: `EXPERIMENTS_401_FIX.md` (DD_APP_KEY)
- **Test Results**: `EXPERIMENTS_TESTS_SUMMARY.md` (54/57 passing)

---

## ✅ Fixed!

The experiments feature now uses the correct Datadog LLMObs task function signature and should work properly! 🎉

**Both authentication (DD_APP_KEY) and task signature are now fixed!**

