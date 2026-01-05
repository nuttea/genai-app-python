# 📊 Datadog Tracing - Quick Reference

**Quick copy-paste patterns for Python tracing**

---

## 🚀 Basic Patterns

### Simple Operation
```python
from ddtrace import tracer

with tracer.trace("operation", service="vote-extractor") as span:
    span.set_tag("operation.type", "extraction")
    result = await do_work()
    span.set_tag("success", True)
    return result
```

### With Error Handling
```python
with tracer.trace("operation", service="vote-extractor") as span:
    try:
        result = await do_work()
        span.set_tag("success", True)
        return result
    except Exception as e:
        span.set_tag("error", True)
        span.set_tag("error.type", type(e).__name__)
        span.set_tag("error.message", str(e))
        raise
```

---

## 🎯 LLMObs Decorators

### Workflow (Parent)
```python
from ddtrace.llmobs.decorators import workflow

@workflow
async def main_workflow(files: List):
    result1 = await step1(files)  # Child
    result2 = await step2(result1)  # Child
    return result2
```

### Task (Child)
```python
from ddtrace.llmobs.decorators import task

@task
async def process_step(data):
    with tracer.trace("processing", service="vote-extractor") as span:
        span.set_tag("step.name", "process")
        return await process(data)
```

### Tool (External Call)
```python
from ddtrace.llmobs.decorators import tool

@tool
async def call_api(endpoint: str):
    with tracer.trace("api.call", service="vote-extractor") as span:
        span.set_tag("api.endpoint", endpoint)
        response = await client.post(endpoint)
        span.set_metric("api.status_code", response.status_code)
        return response.json()
```

---

## ❌ Error Tagging

### Required Tags
```python
span.set_tag("error", True)  # ✅ CRITICAL!
span.set_tag("error.type", "ValueError")
span.set_tag("error.message", str(exception))
```

### Full Error Context
```python
import traceback

span.set_tag("error", True)
span.set_tag("error.type", type(e).__name__)
span.set_tag("error.message", str(e))
span.set_tag("error.stack", traceback.format_exc())
span.set_tag("operation.success", False)
span.set_metric("error.count", 1)

# Context
span.set_tag("error.context.user_id", user_id)
span.set_tag("error.context.file_count", len(files))
```

---

## 📏 Tags vs Metrics

### Tags (Strings)
```python
span.set_tag("llm.model_name", "gemini-2.5-flash")
span.set_tag("operation.type", "extraction")
span.set_tag("success", True)  # Boolean as string
```

### Metrics (Numbers)
```python
span.set_metric("llm.tokens.total", 1234)
span.set_metric("duration_ms", 567.89)
span.set_metric("file_count", 5)
span.set_metric("error.count", 1)
```

---

## 🏗️ Parent-Child Hierarchy

### Pattern 1: Workflow as Parent
```python
@workflow
async def parent_workflow():
    # This creates the parent span
    await child_task_1()  # Child span
    await child_task_2()  # Child span
    return result
```

### Pattern 2: Explicit Parent
```python
with tracer.trace("parent", service="vote-extractor") as parent_span:
    parent_span.set_tag("workflow.name", "extraction")
    
    # Child 1
    with tracer.trace("child1", service="vote-extractor") as child1:
        await do_step1()
    
    # Child 2
    with tracer.trace("child2", service="vote-extractor") as child2:
        await do_step2()
    
    parent_span.set_tag("success", True)
```

---

## 🔍 Current Span Access

### Get Current Span
```python
from ddtrace import tracer

current_span = tracer.current_span()

if current_span:
    current_span.set_tag("custom.tag", "value")
```

### In Context Manager
```python
with tracer.trace("operation") as span:
    # 'span' is the current span
    span.set_tag("key", "value")
```

---

## ⚙️ Common Tag Patterns

### LLM Operation
```python
span.set_tag("llm.model_name", "gemini-2.5-flash")
span.set_tag("llm.model_provider", "google")
span.set_tag("llm.temperature", 0.0)
span.set_tag("llm.max_tokens", 16384)

span.set_metric("llm.tokens.prompt", 100)
span.set_metric("llm.tokens.completion", 200)
span.set_metric("llm.tokens.total", 300)
```

### File Processing
```python
span.set_tag("input.format", "image/jpeg")
span.set_metric("input.file_count", 5)
span.set_metric("input.total_size_mb", 12.5)

span.set_tag("output.format", "json")
span.set_metric("output.records_count", 2)
```

### API Call
```python
span.set_tag("api.endpoint", "/api/v1/extract")
span.set_tag("api.method", "POST")
span.set_tag("api.auth", "api_key")

span.set_metric("api.response.status_code", 200)
span.set_metric("api.response.size_bytes", 4096)
span.set_metric("api.duration_ms", 1234)
```

### Operation Result
```python
span.set_tag("operation.type", "extraction")
span.set_tag("operation.status", "success")
span.set_tag("success", True)

span.set_metric("operation.duration_ms", span.duration * 1000)
span.set_metric("operation.records_processed", 10)
```

---

## 🛠️ Helper Functions

### Error Tagger
```python
def tag_span_error(span, exception: Exception, context: dict = None):
    """Tag span with error info."""
    span.set_tag("error", True)
    span.set_tag("error.type", type(exception).__name__)
    span.set_tag("error.message", str(exception))
    span.set_tag("error.stack", traceback.format_exc())
    
    if context:
        for key, value in context.items():
            span.set_tag(f"error.context.{key}", str(value))
    
    span.set_metric("error.count", 1)

# Usage
try:
    result = await do_work()
except Exception as e:
    tag_span_error(span, e, context={"user_id": "123"})
    raise
```

### Success Tagger
```python
def tag_span_success(span, metrics: dict = None, tags: dict = None):
    """Tag span with success info."""
    span.set_tag("success", True)
    
    if tags:
        for key, value in tags.items():
            span.set_tag(key, str(value))
    
    if metrics:
        for key, value in metrics.items():
            span.set_metric(key, value)

# Usage
tag_span_success(span, 
    tags={"operation": "extraction"},
    metrics={"records_processed": 10, "duration_ms": 123}
)
```

---

## 🔄 Async Tracing

### Async Function
```python
async def async_operation():
    with tracer.trace("async.op", service="vote-extractor") as span:
        result = await some_async_call()
        span.set_tag("success", True)
        return result
```

### Parallel Operations
```python
async def process_parallel(files: List):
    with tracer.trace("parallel.processing") as parent_span:
        parent_span.set_metric("parallel.task_count", len(files))
        
        # Create tasks (each gets own span)
        tasks = [process_file(f) for f in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        successes = sum(1 for r in results if not isinstance(r, Exception))
        parent_span.set_metric("parallel.successes", successes)
        
        return results
```

---

## ✅ Checklist

Before merging code with tracing:

- [ ] All operations have spans
- [ ] Exceptions set `error=True` tag
- [ ] Error type and message tagged
- [ ] Success/failure explicitly tagged
- [ ] Metrics use `set_metric()`, not `set_tag()`
- [ ] LLMObs decorators used correctly
- [ ] Parent-child hierarchy maintained
- [ ] No sensitive data in tags
- [ ] Tested in Datadog APM UI

---

## 📚 Full Guides

- **Comprehensive**: `DATADOG_TRACING_BEST_PRACTICES.md`
- **Implementation**: `VOTE_EXTRACTION_TRACING_IMPROVEMENTS.md`
- **Official Docs**: https://docs.datadoghq.com/tracing/

---

**Copy, paste, and trace!** 📊✨

