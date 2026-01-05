# ✅ ddtrace Import Error - Quick Fix

**Issue**: `ImportError: cannot import name 'workflow' from 'ddtrace.llmobs'`  
**Status**: ✅ Fixed  
**Date**: January 4, 2026

---

## 🎯 Problem

```python
# ❌ This caused ImportError:
from ddtrace.llmobs import workflow

# Error:
# ImportError: cannot import name 'workflow' from 'ddtrace.llmobs'
```

---

## ✅ Solution

```python
# ✅ CORRECT: Import from decorators module
from ddtrace.llmobs.decorators import workflow
```

---

## 📝 Quick Reference

### Correct Imports

| What | Correct Import | Wrong Import |
|------|---------------|--------------|
| Main class | `from ddtrace.llmobs import LLMObs` | ✅ Correct as-is |
| `workflow` decorator | `from ddtrace.llmobs.decorators import workflow` | ❌ `from ddtrace.llmobs import workflow` |
| `task` decorator | `from ddtrace.llmobs.decorators import task` | ❌ `from ddtrace.llmobs import task` |
| `agent` decorator | `from ddtrace.llmobs.decorators import agent` | ❌ `from ddtrace.llmobs import agent` |
| `tool` decorator | `from ddtrace.llmobs.decorators import tool` | ❌ `from ddtrace.llmobs import tool` |

---

## 🔧 What Was Fixed

### File: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`

**Cell 20** - Updated import:

```python
# Before (❌):
from ddtrace.llmobs import workflow

# After (✅):
from ddtrace.llmobs.decorators import workflow
```

---

## 🧪 Test the Fix

### Option 1: Test in Python REPL

```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow

print("✅ Imports successful!")
```

### Option 2: Re-run Notebook Cell

```bash
cd notebooks/datasets
jupyter notebook 01_prepare_vote_extraction_dataset.ipynb

# Re-run Cell 20
# ✅ Should now work!
```

---

## 💡 Why This Happened

**The ddtrace package structure is:**

```
ddtrace/
├── llmobs/
│   ├── __init__.py         # Contains: LLMObs class
│   └── decorators.py       # Contains: workflow, task, agent, tool, etc.
```

- **`LLMObs` class**: Directly in `ddtrace.llmobs`
- **Decorators**: In `ddtrace.llmobs.decorators` submodule

---

## 📚 Complete Example

```python
# ✅ All correct imports for LLMObs experiments:
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow
from typing import Dict, Any

# Enable LLMObs
LLMObs.enable(
    ml_app="vote-extractor",
    api_key=os.getenv("DD_API_KEY"),
    site=os.getenv("DD_SITE", "datadoghq.com"),
)

# Load dataset
dataset = LLMObs.pull_dataset(
    dataset_name="my-dataset",
    project_name="my-project",
)

# Define task function
@workflow
def vote_extraction_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Task function for experiments."""
    return {"result": "success"}

print("✅ Ready to run experiments!")
```

---

## 🔗 Related Resources

- **Troubleshooting Guide**: [docs/troubleshooting/DDTRACE_IMPORT_ERRORS.md](docs/troubleshooting/DDTRACE_IMPORT_ERRORS.md)
- **LLMObs Guide**: [guides/llmobs/01_INSTRUMENTING_SPANS.md](guides/llmobs/01_INSTRUMENTING_SPANS.md)
- **Experiments Guide**: [guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md](guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md)

---

## ✨ Quick Tip

**Remember**: Only `LLMObs` is in `ddtrace.llmobs`. Everything else (decorators, span types) is in `ddtrace.llmobs.decorators`!

```python
# ✅ Main class
from ddtrace.llmobs import LLMObs

# ✅ All decorators
from ddtrace.llmobs.decorators import workflow, task, agent, tool, llm, embedding, retrieval
```

---

**Ready to use!** 🚀 Re-run Cell 20 in the notebook to verify!

