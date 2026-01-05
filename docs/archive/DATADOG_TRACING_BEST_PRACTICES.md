# 📊 Datadog APM Best Practices for Python

**Comprehensive guide for tracing, error handling, and LLMObs in the GenAI App**

---

## 📖 Table of Contents

1. [Exception Handling with Trace Errors](#1-exception-handling-with-trace-errors)
2. [LLMObs Parent-Child Trace Hierarchy](#2-llmobs-parent-child-trace-hierarchy)
3. [Span Tagging Best Practices](#3-span-tagging-best-practices)
4. [Error Handling Patterns](#4-error-handling-patterns)
5. [LLMObs Decorators](#5-llmobs-decorators)
6. [Async Tracing](#6-async-tracing)
7. [Testing Traces](#7-testing-traces)

---

## 1. Exception Handling with Trace Errors

### ✅ Best Practice: Mark Spans as Errors

When exceptions occur, **always** mark the span as an error:

```python
from ddtrace import tracer

async def extract_data(files: List):
    with tracer.trace("vote_extraction.extract", service="vote-extractor") as span:
        try:
            # Your code here
            result = await process_files(files)
            
            # Tag success metrics
            span.set_tag("extraction.success", True)
            span.set_metric("extraction.files_processed", len(files))
            
            return result
            
        except ValueError as e:
            # Mark span as error
            span.set_tag("error", True)  # ✅ Critical!
            span.set_tag("error.type", "ValueError")
            span.set_tag("error.message", str(e))
            span.set_tag("extraction.success", False)
            
            # Log for debugging
            logger.error(f"Validation error: {e}", exc_info=True)
            
            # Re-raise or convert to custom exception
            raise ExtractionException(f"Invalid data: {e}") from e
            
        except Exception as e:
            # Mark span as error
            span.set_tag("error", True)  # ✅ Critical!
            span.set_tag("error.type", type(e).__name__)
            span.set_tag("error.message", str(e))
            span.set_tag("extraction.success", False)
            span.set_metric("extraction.error_code", 500)
            
            logger.critical(f"Unexpected error: {e}", exc_info=True)
            raise
```

### 🔧 Helper Function for Error Tagging

```python
def tag_span_error(span, exception: Exception, context: dict = None):
    """
    Tag a span with error information.
    
    Args:
        span: Datadog span object
        exception: The exception that occurred
        context: Additional context to add as tags
    """
    span.set_tag("error", True)
    span.set_tag("error.type", type(exception).__name__)
    span.set_tag("error.message", str(exception))
    span.set_tag("error.stack", traceback.format_exc())
    
    if context:
        for key, value in context.items():
            span.set_tag(f"error.context.{key}", str(value))
    
    # Set error metric for alerting
    span.set_metric("error.count", 1)
```

**Usage:**

```python
with tracer.trace("operation") as span:
    try:
        result = await do_something()
    except Exception as e:
        tag_span_error(span, e, context={
            "user_id": user_id,
            "file_count": len(files),
            "operation": "extraction"
        })
        raise
```

---

## 2. LLMObs Parent-Child Trace Hierarchy

### ✅ Ensure All LLMObs Operations Share Parent Trace

**Problem**: LLMObs operations (`@workflow`, `@task`, `@tool`) might create separate traces instead of being nested under a parent.

**Solution**: Use `tracer.trace()` as the parent context.

### Pattern 1: Workflow as Parent

```python
from ddtrace import tracer
from ddtrace.llmobs.decorators import workflow, task, tool

@workflow
async def extract_vote_data(files: List[UploadFile]) -> dict:
    """
    Main workflow - automatically creates a parent span.
    All nested operations will be children of this span.
    """
    # This workflow creates the root span
    with tracer.current_span() as parent_span:
        parent_span.set_tag("workflow.name", "vote_extraction")
        parent_span.set_tag("workflow.file_count", len(files))
    
    # Preprocessing (child span)
    processed_files = await preprocess_images(files)
    
    # LLM extraction (child span)
    result = await call_llm(processed_files)
    
    # Validation (child span)
    validated = await validate_result(result)
    
    return validated


@task
async def preprocess_images(files: List[UploadFile]) -> List[bytes]:
    """
    Task is a child of the workflow span.
    """
    with tracer.trace("preprocessing.resize", service="vote-extractor") as span:
        span.set_tag("preprocessing.file_count", len(files))
        
        processed = []
        for file in files:
            data = await file.read()
            # Process image
            processed.append(data)
        
        span.set_metric("preprocessing.total_size_mb", sum(len(p) for p in processed) / 1024 / 1024)
        
        return processed


@tool
async def validate_result(result: dict) -> dict:
    """
    Tool is a child of the workflow span.
    """
    with tracer.trace("validation.check", service="vote-extractor") as span:
        span.set_tag("validation.has_data", bool(result))
        
        # Validation logic
        if not result.get("vote_results"):
            span.set_tag("error", True)
            span.set_tag("validation.error", "No vote results")
            raise ValueError("No vote results")
        
        span.set_tag("validation.success", True)
        return result
```

### Pattern 2: Explicit Parent Span

```python
from ddtrace import tracer
from ddtrace.llmobs import LLMObs

async def process_request(request: VoteExtractionRequest):
    """
    Create explicit parent span for the entire request.
    """
    # Create parent span for the entire operation
    with tracer.trace("vote_extraction.request", service="vote-extractor") as parent_span:
        parent_span.set_tag("request.id", request.id)
        parent_span.set_tag("request.user", request.user_id)
        parent_span.set_tag("request.file_count", len(request.files))
        
        try:
            # All operations below will be children of this span
            
            # Step 1: Upload files (child span)
            with tracer.trace("vote_extraction.upload") as upload_span:
                upload_span.set_tag("upload.count", len(request.files))
                file_paths = await upload_files(request.files)
            
            # Step 2: Extract with LLM (child span - using @workflow)
            with tracer.trace("vote_extraction.extract") as extract_span:
                extract_span.set_tag("llm.model", request.model)
                result = await extract_from_images(file_paths, request.model)
                extract_span.set_metric("llm.tokens.total", result.get("tokens", 0))
            
            # Step 3: Validate (child span)
            with tracer.trace("vote_extraction.validate") as validate_span:
                is_valid, error = await validate_extraction(result)
                validate_span.set_tag("validation.success", is_valid)
                if error:
                    validate_span.set_tag("validation.error", error)
            
            # Success tags on parent
            parent_span.set_tag("request.success", True)
            parent_span.set_metric("request.duration_ms", parent_span.duration * 1000)
            
            return result
            
        except Exception as e:
            # Error tags on parent span
            parent_span.set_tag("error", True)
            parent_span.set_tag("error.type", type(e).__name__)
            parent_span.set_tag("error.message", str(e))
            parent_span.set_tag("request.success", False)
            
            logger.error(f"Request failed: {e}", exc_info=True)
            raise
```

### Pattern 3: LLMObs with Manual Span Context

```python
from ddtrace.llmobs import LLMObs

async def run_experiment(dataset: Dataset, model: str):
    """
    Run an LLMObs experiment with proper span hierarchy.
    """
    # Create parent span
    with tracer.trace("experiment.run", service="vote-extractor") as parent_span:
        parent_span.set_tag("experiment.dataset", dataset.name)
        parent_span.set_tag("experiment.model", model)
        
        # Export parent span context
        parent_context = LLMObs.export_span(span=None)
        
        try:
            # Initialize LLMObs if not already done
            if not hasattr(LLMObs, '_instance'):
                LLMObs.enable(
                    ml_app="vote-extractor",
                    site="datadoghq.com",
                    api_key=os.getenv("DD_API_KEY")
                )
            
            # Create experiment (will be child of parent_span)
            experiment = LLMObs.experiment(
                name=f"vote-extraction-{model}",
                task=my_task_function,
                dataset=dataset,
                evaluators=[...]
            )
            
            # Run experiment
            results = experiment.run(sample_size=10, jobs=2)
            
            # Tag parent with results
            parent_span.set_metric("experiment.total_records", len(results))
            parent_span.set_metric("experiment.success_rate", results.get("success_rate", 0))
            parent_span.set_tag("experiment.status", "completed")
            
            return results
            
        except Exception as e:
            parent_span.set_tag("error", True)
            parent_span.set_tag("error.type", type(e).__name__)
            parent_span.set_tag("error.message", str(e))
            parent_span.set_tag("experiment.status", "failed")
            raise
```

---

## 3. Span Tagging Best Practices

### ✅ Naming Conventions

Follow Datadog's recommended tag naming:

```python
# ✅ Good - Structured tags
span.set_tag("llm.model_name", "gemini-2.5-flash")
span.set_tag("llm.model_provider", "google")
span.set_tag("llm.temperature", 0.0)
span.set_tag("llm.max_tokens", 16384)

span.set_metric("llm.tokens.prompt", input_tokens)
span.set_metric("llm.tokens.completion", output_tokens)
span.set_metric("llm.tokens.total", total_tokens)

span.set_tag("operation.type", "extraction")
span.set_tag("operation.status", "success")

span.set_tag("input.file_count", len(files))
span.set_tag("input.format", "image/jpeg")
span.set_metric("input.total_size_bytes", total_size)

span.set_tag("output.format", "json")
span.set_metric("output.records_count", len(records))

# ❌ Bad - Inconsistent naming
span.set_tag("model", "gemini-2.5-flash")
span.set_tag("temp", 0.0)
span.set_tag("tokens", 1000)  # Should be metric
span.set_tag("fileCount", len(files))  # Should use snake_case
```

### Tag Categories

| Category | Example Tags | Notes |
|----------|--------------|-------|
| **LLM** | `llm.model_name`, `llm.provider`, `llm.temperature` | LLM-specific config |
| **Metrics** | `llm.tokens.total`, `processing.duration_ms` | Use `set_metric()` |
| **Input** | `input.file_count`, `input.format`, `input.size_mb` | Request inputs |
| **Output** | `output.format`, `output.records_count` | Response outputs |
| **Operation** | `operation.type`, `operation.status` | What's happening |
| **Error** | `error`, `error.type`, `error.message` | Error details |
| **User** | `user.id`, `user.role` | User context |
| **Resource** | `resource.name`, `resource.type` | Resource info |

---

## 4. Error Handling Patterns

### Pattern 1: Graceful Degradation

```python
@workflow
async def extract_with_fallback(files: List[UploadFile], model: str):
    """
    Extract data with fallback to different model on error.
    """
    with tracer.trace("extraction.with_fallback", service="vote-extractor") as span:
        span.set_tag("extraction.model.primary", model)
        
        try:
            # Try primary model
            result = await extract_from_images(files, model)
            span.set_tag("extraction.model.used", model)
            span.set_tag("extraction.fallback_used", False)
            return result
            
        except Exception as e:
            # Log primary failure
            span.set_tag("extraction.primary.error", str(e))
            logger.warning(f"Primary model {model} failed, trying fallback")
            
            # Try fallback model
            fallback_model = "gemini-2.5-flash-lite"
            span.set_tag("extraction.model.fallback", fallback_model)
            
            try:
                result = await extract_from_images(files, fallback_model)
                span.set_tag("extraction.model.used", fallback_model)
                span.set_tag("extraction.fallback_used", True)
                span.set_tag("extraction.success", True)
                return result
                
            except Exception as fallback_error:
                # Both failed - mark as error
                span.set_tag("error", True)
                span.set_tag("error.type", "ExtractionFailure")
                span.set_tag("error.message", "Both primary and fallback failed")
                span.set_tag("extraction.primary.error", str(e))
                span.set_tag("extraction.fallback.error", str(fallback_error))
                span.set_tag("extraction.success", False)
                
                logger.error(f"Both models failed: {e} | {fallback_error}")
                raise ExtractionException("Extraction failed with all models") from fallback_error
```

### Pattern 2: Retry with Exponential Backoff

```python
import asyncio
from typing import Callable, TypeVar

T = TypeVar('T')

async def retry_with_trace(
    func: Callable[..., T],
    max_retries: int = 3,
    operation_name: str = "operation"
) -> T:
    """
    Retry function with exponential backoff and trace each attempt.
    """
    with tracer.trace(f"{operation_name}.with_retry", service="vote-extractor") as parent_span:
        parent_span.set_metric("retry.max_attempts", max_retries)
        
        for attempt in range(1, max_retries + 1):
            with tracer.trace(f"{operation_name}.attempt", service="vote-extractor") as attempt_span:
                attempt_span.set_metric("retry.attempt_number", attempt)
                
                try:
                    result = await func()
                    
                    # Success tags
                    attempt_span.set_tag("retry.success", True)
                    parent_span.set_metric("retry.attempts_used", attempt)
                    parent_span.set_tag("retry.success", True)
                    
                    return result
                    
                except Exception as e:
                    # Tag this attempt as failed
                    attempt_span.set_tag("error", True)
                    attempt_span.set_tag("error.type", type(e).__name__)
                    attempt_span.set_tag("error.message", str(e))
                    attempt_span.set_tag("retry.success", False)
                    
                    if attempt == max_retries:
                        # Final attempt failed
                        parent_span.set_tag("error", True)
                        parent_span.set_tag("error.type", "MaxRetriesExceeded")
                        parent_span.set_tag("error.final_error", str(e))
                        parent_span.set_metric("retry.attempts_used", attempt)
                        parent_span.set_tag("retry.success", False)
                        
                        logger.error(f"{operation_name} failed after {max_retries} attempts: {e}")
                        raise
                    
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** (attempt - 1)
                    attempt_span.set_metric("retry.wait_seconds", wait_time)
                    
                    logger.warning(f"{operation_name} attempt {attempt} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
```

---

## 5. LLMObs Decorators

### Decorator Hierarchy

```
@workflow  →  High-level business process (e.g., "extract vote data")
    ↓
@task      →  Discrete processing step (e.g., "preprocess images")
    ↓
@tool      →  External tool call (e.g., "call Gemini API")
```

### Complete Example

```python
from ddtrace.llmobs.decorators import workflow, task, tool
from ddtrace import tracer

@workflow
async def vote_extraction_workflow(
    files: List[UploadFile],
    model: str = "gemini-2.5-flash"
) -> dict:
    """
    Main workflow for vote extraction.
    This creates the root LLMObs span.
    """
    with tracer.current_span() as span:
        span.set_tag("workflow.name", "vote_extraction")
        span.set_tag("workflow.model", model)
        span.set_tag("workflow.file_count", len(files))
    
    # Step 1: Preprocess (task)
    processed_files = await preprocess_images_task(files)
    
    # Step 2: Extract with LLM (tool)
    raw_result = await call_gemini_tool(processed_files, model)
    
    # Step 3: Post-process (task)
    structured_result = await postprocess_result_task(raw_result)
    
    # Step 4: Validate (task)
    validated_result = await validate_result_task(structured_result)
    
    with tracer.current_span() as span:
        span.set_tag("workflow.success", True)
        span.set_metric("workflow.total_duration_ms", span.duration * 1000)
    
    return validated_result


@task
async def preprocess_images_task(files: List[UploadFile]) -> List[bytes]:
    """
    Task: Preprocess images before extraction.
    Child of workflow span.
    """
    with tracer.trace("preprocessing", service="vote-extractor") as span:
        span.set_tag("task.name", "preprocess_images")
        span.set_metric("task.input_count", len(files))
        
        processed = []
        total_size = 0
        
        for i, file in enumerate(files):
            data = await file.read()
            total_size += len(data)
            
            # Resize/optimize image
            processed_data = await resize_image(data)
            processed.append(processed_data)
        
        span.set_metric("task.output_count", len(processed))
        span.set_metric("task.total_size_mb", total_size / 1024 / 1024)
        span.set_tag("task.success", True)
        
        return processed


@tool
async def call_gemini_tool(images: List[bytes], model: str) -> str:
    """
    Tool: Call external LLM API.
    Child of workflow span.
    """
    with tracer.trace("llm.call", service="vote-extractor") as span:
        span.set_tag("tool.name", "call_gemini")
        span.set_tag("tool.provider", "google")
        span.set_tag("llm.model_name", model)
        span.set_metric("llm.input_images", len(images))
        
        try:
            # Call Gemini API
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            
            response = await client.aio.models.generate_content(
                model=model,
                contents=[...],  # Your content
            )
            
            # Tag response metrics
            span.set_metric("llm.tokens.prompt", response.usage_metadata.prompt_token_count)
            span.set_metric("llm.tokens.completion", response.usage_metadata.candidates_token_count)
            span.set_metric("llm.tokens.total", response.usage_metadata.total_token_count)
            span.set_tag("llm.finish_reason", response.candidates[0].finish_reason)
            span.set_tag("tool.success", True)
            
            return response.text
            
        except Exception as e:
            span.set_tag("error", True)
            span.set_tag("error.type", type(e).__name__)
            span.set_tag("error.message", str(e))
            span.set_tag("tool.success", False)
            raise


@task
async def validate_result_task(result: dict) -> dict:
    """
    Task: Validate extraction result.
    Child of workflow span.
    """
    with tracer.trace("validation", service="vote-extractor") as span:
        span.set_tag("task.name", "validate_result")
        
        validation_checks = []
        
        # Check 1: Has vote results
        if not result.get("vote_results"):
            span.set_tag("error", True)
            span.set_tag("validation.error", "No vote results")
            span.set_tag("task.success", False)
            raise ValueError("No vote results")
        
        validation_checks.append({"check": "has_results", "passed": True})
        
        # Check 2: Ballot statistics
        if result.get("ballot_statistics"):
            stats = result["ballot_statistics"]
            expected = stats["good_ballots"] + stats["bad_ballots"] + stats["no_vote_ballots"]
            
            if stats["ballots_used"] != expected:
                span.set_tag("validation.warning", "Ballot mismatch")
                validation_checks.append({
                    "check": "ballot_match",
                    "passed": False,
                    "error": f"Expected {expected}, got {stats['ballots_used']}"
                })
            else:
                validation_checks.append({"check": "ballot_match", "passed": True})
        
        # Summary
        checks_passed = sum(1 for c in validation_checks if c["passed"])
        total_checks = len(validation_checks)
        
        span.set_metric("validation.checks_passed", checks_passed)
        span.set_metric("validation.checks_total", total_checks)
        span.set_metric("validation.score", checks_passed / total_checks)
        span.set_tag("task.success", True)
        
        return result
```

---

## 6. Async Tracing

### ✅ Best Practices for Async Code

```python
import asyncio
from ddtrace import tracer

# Pattern 1: Async function with tracing
async def async_operation():
    with tracer.trace("async.operation", service="vote-extractor") as span:
        span.set_tag("operation.type", "async")
        
        # Async operations
        result = await some_async_call()
        
        span.set_tag("operation.success", True)
        return result


# Pattern 2: Parallel async operations
async def process_multiple_files(files: List[UploadFile]):
    with tracer.trace("processing.parallel", service="vote-extractor") as parent_span:
        parent_span.set_metric("parallel.task_count", len(files))
        
        # Create tasks
        tasks = []
        for i, file in enumerate(files):
            # Each task gets its own span
            task = process_single_file(file, index=i)
            tasks.append(task)
        
        # Wait for all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = len(results) - successes
        
        parent_span.set_metric("parallel.successes", successes)
        parent_span.set_metric("parallel.failures", failures)
        parent_span.set_tag("parallel.all_succeeded", failures == 0)
        
        return results


async def process_single_file(file: UploadFile, index: int):
    """Process single file with its own span."""
    with tracer.trace(f"processing.file_{index}", service="vote-extractor") as span:
        span.set_tag("file.index", index)
        span.set_tag("file.name", file.filename)
        
        try:
            data = await file.read()
            span.set_metric("file.size_bytes", len(data))
            
            result = await do_processing(data)
            
            span.set_tag("processing.success", True)
            return result
            
        except Exception as e:
            span.set_tag("error", True)
            span.set_tag("error.type", type(e).__name__)
            span.set_tag("processing.success", False)
            return e  # Return exception (handled by gather)
```

---

## 7. Testing Traces

### Verify Traces in Tests

```python
import pytest
from ddtrace import tracer

@pytest.fixture
def trace_buffer():
    """Capture traces for testing."""
    from ddtrace.internal.writer import TraceWriter
    
    # Create a test writer that captures traces
    writer = TraceWriter()
    tracer.configure(writer=writer)
    
    yield writer
    
    # Cleanup
    tracer.configure(writer=None)


async def test_extraction_creates_spans(trace_buffer):
    """Test that extraction creates proper spans."""
    # Run extraction
    result = await extract_from_images(test_files, model="gemini-2.5-flash")
    
    # Flush traces
    tracer.flush()
    
    # Get captured traces
    traces = trace_buffer.pop_traces()
    
    assert len(traces) > 0, "No traces captured"
    
    # Find the workflow span
    workflow_span = None
    for trace in traces:
        for span in trace:
            if span.name == "vote_extraction.workflow":
                workflow_span = span
                break
    
    assert workflow_span is not None, "Workflow span not found"
    
    # Verify tags
    assert workflow_span.get_tag("workflow.model") == "gemini-2.5-flash"
    assert workflow_span.get_tag("workflow.success") == "True"
    assert workflow_span.get_tag("error") is None, "Span should not have error tag"
    
    # Verify metrics
    assert workflow_span.get_metric("workflow.file_count") > 0


async def test_extraction_error_tagged(trace_buffer):
    """Test that errors are properly tagged."""
    with pytest.raises(ExtractionException):
        await extract_from_images([], model="gemini-2.5-flash")
    
    tracer.flush()
    traces = trace_buffer.pop_traces()
    
    # Find error span
    error_span = None
    for trace in traces:
        for span in trace:
            if span.get_tag("error") == "True":
                error_span = span
                break
    
    assert error_span is not None, "Error span not found"
    assert error_span.get_tag("error.type") is not None
    assert error_span.get_tag("error.message") is not None
```

---

## 🎯 Quick Reference

### Common Patterns

```python
# 1. Simple operation with error handling
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

# 2. Workflow with nested operations
@workflow
async def main_workflow():
    with tracer.current_span() as span:
        span.set_tag("workflow.name", "main")
    
    # All these will be children of the workflow span
    result1 = await step1()
    result2 = await step2(result1)
    return await step3(result2)

# 3. Metrics and tags
span.set_tag("string.tag", "value")  # String
span.set_metric("numeric.metric", 123.45)  # Number
span.set_tag("boolean.tag", True)  # Boolean (as string)

# 4. Error tagging
span.set_tag("error", True)  # Mark as error
span.set_tag("error.type", "ValueError")
span.set_tag("error.message", "Invalid input")
```

---

## 📚 Resources

- [Datadog APM Python](https://docs.datadoghq.com/tracing/trace_collection/dd_libraries/python/)
- [LLM Observability SDK](https://docs.datadoghq.com/llm_observability/instrumentation/sdk/?tab=python)
- [Custom Instrumentation](https://docs.datadoghq.com/tracing/trace_collection/custom_instrumentation/python/)
- [Error Tracking](https://docs.datadoghq.com/tracing/error_tracking/)

---

## ✅ Checklist

Use this checklist when implementing tracing:

- [ ] All async functions have proper span context
- [ ] Exceptions are caught and tagged with `error=True`
- [ ] Error messages and types are added as tags
- [ ] Success/failure is tagged explicitly
- [ ] Metrics use `set_metric()`, not `set_tag()`
- [ ] LLMObs decorators (`@workflow`, `@task`, `@tool`) are used correctly
- [ ] Parent-child relationships are maintained
- [ ] Resource names follow naming conventions
- [ ] Sensitive data is NOT added to spans
- [ ] Tests verify span creation and tagging

---

**Happy Tracing!** 📊✨

