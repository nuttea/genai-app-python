# Troubleshooting: ddtrace Import Errors

**Issue**: `ImportError: cannot import name 'workflow' from 'ddtrace.llmobs'`  
**Component**: Jupyter Notebook, ddtrace SDK  
**Date**: January 4, 2026

---

## Problem Description

When attempting to import the `workflow` decorator from `ddtrace.llmobs`, the following error occurs:

```python
from ddtrace.llmobs import workflow

# ❌ Error:
# ImportError: cannot import name 'workflow' from 'ddtrace.llmobs'
```

---

## Root Cause

The `workflow` decorator (and other span decorators) are located in the `ddtrace.llmobs.decorators` module, **not** directly in `ddtrace.llmobs`.

The `ddtrace.llmobs` module only exposes the main `LLMObs` class for core functionality like:
- `LLMObs.enable()`
- `LLMObs.annotate()`
- `LLMObs.submit_evaluation()`
- `LLMObs.export_span()`
- `LLMObs.create_dataset()`
- `LLMObs.pull_dataset()`

---

## Solution

### ✅ Correct Imports

```python
# ✅ CORRECT: Import LLMObs class directly
from ddtrace.llmobs import LLMObs

# ✅ CORRECT: Import decorators from decorators module
from ddtrace.llmobs.decorators import workflow, task, agent, tool, embedding, retrieval, llm
```

### ❌ Incorrect Imports

```python
# ❌ WRONG: Decorators are not in ddtrace.llmobs
from ddtrace.llmobs import workflow  # ImportError!
from ddtrace.llmobs import task      # ImportError!
from ddtrace.llmobs import agent     # ImportError!
```

---

## Complete Import Reference

### Main LLMObs Class

```python
from ddtrace.llmobs import LLMObs

# Used for:
LLMObs.enable(ml_app="my-app", api_key="...", site="...")
LLMObs.annotate(input_data=..., output_data=..., metadata=..., tags=...)
LLMObs.submit_evaluation(span=..., label=..., metric_type=..., value=...)
LLMObs.export_span(span=None)  # Get current span context
LLMObs.create_dataset(name="...", description="...")
LLMObs.pull_dataset(dataset_name="...", project_name="...")
```

### Span Decorators (for Tracing)

```python
from ddtrace.llmobs.decorators import (
    workflow,   # Top-level workflow (root span)
    task,       # Individual task within a workflow
    agent,      # Agent operation
    tool,       # Tool/function call
    embedding,  # Embedding generation
    retrieval,  # Retrieval operation
    llm,        # LLM API call
)

# Usage:
@workflow
def my_workflow():
    ...

@task
def my_task():
    ...
```

---

## Common Import Patterns

### Pattern 1: Basic Tracing Setup

```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow, task

# Enable LLMObs
LLMObs.enable(
    ml_app="vote-extractor",
    api_key=os.getenv("DD_API_KEY"),
    site=os.getenv("DD_SITE", "datadoghq.com"),
)

# Define workflow
@workflow
def extract_votes(images):
    ...
```

### Pattern 2: Experiments and Datasets

```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow
from typing import Dict, Any

# Create/load dataset
dataset = LLMObs.pull_dataset(
    dataset_name="my-dataset",
    project_name="my-project",
)

# Define task for experiments
@workflow
def task_function(input_data: Dict[str, Any]) -> Dict[str, Any]:
    ...
```

### Pattern 3: Evaluations and Feedback

```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow

@workflow
def my_workflow():
    # ... do work ...
    
    # Get span context
    span_context = LLMObs.export_span(span=None)
    
    # Submit evaluation
    LLMObs.submit_evaluation(
        span=span_context,
        label="accuracy",
        metric_type="score",
        value=0.95,
    )
```

---

## Fix Applied

### File: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`

**Cell 20 (Task Function) - FIXED**:

```python
# Before (❌ INCORRECT):
import httpx
from ddtrace.llmobs import workflow  # ImportError!

# After (✅ CORRECT):
import httpx
from ddtrace.llmobs.decorators import workflow

# FastAPI backend URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

@workflow
def vote_extraction_task(input_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Task function that extracts vote data from election form images."""
    ...
```

---

## Verification Steps

### 1. Test Import in Python

```python
# Test in Python REPL or Jupyter
import sys
print(f"Python version: {sys.version}")

# Test correct imports
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow

print("✅ Imports successful!")
print(f"LLMObs: {LLMObs}")
print(f"workflow: {workflow}")
```

### 2. Run Notebook Cell

```bash
cd notebooks/datasets
jupyter notebook 01_prepare_vote_extraction_dataset.ipynb

# Run Cell 20
# ✅ Should now work without ImportError
```

**Expected Output**:
```
✅ Task function defined: vote_extraction_task()
```

### 3. Check ddtrace Version

```python
import ddtrace
print(f"ddtrace version: {ddtrace.__version__}")

# Ensure >= 3.18.0 for dataset support
assert ddtrace.__version__ >= "3.18.0", "Update ddtrace to >= 3.18.0"
```

---

## Related Import Errors

### Error: `cannot import name 'task' from 'ddtrace.llmobs'`

**Solution**: Same fix - import from `decorators` module:

```python
# ✅ CORRECT:
from ddtrace.llmobs.decorators import task
```

### Error: `cannot import name 'agent' from 'ddtrace.llmobs'`

**Solution**: Same fix:

```python
# ✅ CORRECT:
from ddtrace.llmobs.decorators import agent
```

### Error: `module 'ddtrace.llmobs' has no attribute 'workflow'`

**Solution**: Same fix - use correct import path.

---

## Best Practices

### 1. **Always Import from Correct Module**

```python
# ✅ DO: Be explicit about module paths
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow, task

# ❌ DON'T: Try to import decorators from main module
from ddtrace.llmobs import workflow  # This will fail
```

### 2. **Use Type Hints**

```python
from typing import Dict, Any, Optional
from ddtrace.llmobs.decorators import workflow

@workflow
def my_function(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Properly typed function."""
    return {"result": "success"}
```

### 3. **Check Available Imports**

```python
# Inspect what's available in a module
import ddtrace.llmobs
print("Available in ddtrace.llmobs:")
print([attr for attr in dir(ddtrace.llmobs) if not attr.startswith('_')])

import ddtrace.llmobs.decorators
print("\nAvailable in ddtrace.llmobs.decorators:")
print([attr for attr in dir(ddtrace.llmobs.decorators) if not attr.startswith('_')])
```

---

## Summary

| Import | Module | Purpose |
|--------|--------|---------|
| `LLMObs` | `ddtrace.llmobs` | Main class for LLMObs functionality |
| `workflow` | `ddtrace.llmobs.decorators` | Decorator for workflow spans |
| `task` | `ddtrace.llmobs.decorators` | Decorator for task spans |
| `agent` | `ddtrace.llmobs.decorators` | Decorator for agent spans |
| `tool` | `ddtrace.llmobs.decorators` | Decorator for tool spans |
| `llm` | `ddtrace.llmobs.decorators` | Decorator for LLM spans |
| `embedding` | `ddtrace.llmobs.decorators` | Decorator for embedding spans |
| `retrieval` | `ddtrace.llmobs.decorators` | Decorator for retrieval spans |

---

## Related Resources

### Documentation
- [Guide 01: Instrumenting Spans](../../guides/llmobs/01_INSTRUMENTING_SPANS.md)
- [Guide 04: Experiments and Datasets](../../guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md)
- [Datadog LLMObs Python SDK](https://docs.datadoghq.com/llm_observability/setup/sdk/python/)

### Implementation Files
- Notebook: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
- Backend Service: `services/fastapi-backend/app/services/vote_extraction_service.py`

### Related Issues
- [Dataset Version Attribute Fix](DATASET_OBJECT_ATTRIBUTES.md)

---

**Status**: ✅ Fixed  
**Next Steps**: Re-run notebook Cell 20 to verify the import works correctly.

