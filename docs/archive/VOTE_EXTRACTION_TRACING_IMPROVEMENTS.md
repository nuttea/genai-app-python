# 🔧 Vote Extraction Service - Tracing Improvements

**Applied best practices to vote_extraction_service.py**

---

## 📊 Current vs Improved Implementation

### 1. Error Handling Improvement

**❌ Current** (`_handle_extraction_error`):
```python
def _handle_extraction_error(self, error: Exception, error_type: str) -> None:
    """Handle extraction errors with logging and LLMObs annotation."""
    if not self._llmobs_enabled or not DDTRACE_AVAILABLE:
        return

    try:
        LLMObs.annotate(
            parameters={
                "error_type": error_type,
                "error_message": str(error),
            },
        )
        logger.error(f"Extraction error: {error_type} - {error}")
    except Exception as e:
        logger.warning(f"Failed to annotate extraction error: {e}")
```

**✅ Improved**:
```python
from ddtrace import tracer

def _handle_extraction_error(self, error: Exception, error_type: str, context: dict = None) -> None:
    """
    Handle extraction errors with comprehensive trace tagging.
    
    Args:
        error: The exception that occurred
        error_type: Classification of the error
        context: Additional context (file count, model, etc.)
    """
    # Get current span
    current_span = tracer.current_span()
    
    if current_span:
        # Mark span as error (CRITICAL for APM error tracking!)
        current_span.set_tag("error", True)
        current_span.set_tag("error.type", error_type)
        current_span.set_tag("error.message", str(error))
        current_span.set_tag("error.stack", traceback.format_exc())
        
        # Add context tags
        if context:
            for key, value in context.items():
                current_span.set_tag(f"error.context.{key}", str(value))
        
        # Error metrics for alerting
        current_span.set_metric("error.count", 1)
        current_span.set_tag("extraction.success", False)
    
    # LLMObs annotation (if enabled)
    if self._llmobs_enabled and DDTRACE_AVAILABLE:
        try:
            LLMObs.annotate(
                parameters={
                    "error": True,
                    "error_type": error_type,
                    "error_message": str(error),
                    "error_context": context or {},
                },
            )
        except Exception as e:
            logger.warning(f"Failed to annotate LLMObs error: {e}")
    
    # Structured logging
    logger.error(
        f"Extraction error: {error_type}",
        extra={
            "error_type": error_type,
            "error_message": str(error),
            "error_context": context or {},
            "has_trace": current_span is not None,
        },
        exc_info=True
    )
```

---

### 2. Extract From Images - Complete Tracing

**✅ Improved Implementation**:

```python
from ddtrace import tracer
from ddtrace.llmobs.decorators import workflow
import traceback

@workflow
async def extract_from_images(
    self,
    image_files: list[UploadFile | bytes | str],
    image_filenames: list[str] | None = None,
    llm_config: LLMConfig | None = None,
) -> list[dict[str, Any]]:
    """
    Extract vote data from images with comprehensive tracing.
    
    This workflow creates a parent span for the entire extraction process.
    All nested operations will be children of this span.
    """
    # Create explicit parent span for the entire workflow
    with tracer.trace("vote_extraction.workflow", service="vote-extractor") as workflow_span:
        # Tag workflow metadata
        workflow_span.set_tag("workflow.name", "vote_extraction")
        workflow_span.set_tag("workflow.type", "extraction")
        workflow_span.set_metric("workflow.image_count", len(image_files))
        workflow_span.set_tag("workflow.model", llm_config.model if llm_config else "default")
        workflow_span.set_tag("workflow.temperature", llm_config.temperature if llm_config else 0.0)
        
        try:
            # Step 1: Process images (child span)
            with tracer.trace("vote_extraction.preprocess", service="vote-extractor") as preprocess_span:
                preprocess_span.set_tag("step.name", "preprocess_images")
                preprocess_span.set_metric("step.input_count", len(image_files))
                
                try:
                    content_parts = self._process_images_to_content_parts(image_files, image_filenames)
                    
                    # Tag success
                    preprocess_span.set_tag("step.success", True)
                    preprocess_span.set_metric("step.output_count", len(content_parts))
                    
                except ExtractionException as e:
                    # Tag error on preprocess span
                    preprocess_span.set_tag("error", True)
                    preprocess_span.set_tag("error.type", "ExtractionException")
                    preprocess_span.set_tag("error.message", str(e))
                    preprocess_span.set_tag("step.success", False)
                    
                    # Also tag workflow span
                    workflow_span.set_tag("error", True)
                    workflow_span.set_tag("error.step", "preprocess")
                    workflow_span.set_tag("workflow.success", False)
                    
                    raise
            
            # Step 2: Build prompt (child span)
            with tracer.trace("vote_extraction.build_prompt", service="vote-extractor") as prompt_span:
                prompt_span.set_tag("step.name", "build_prompt")
                
                prompt_text, prompt_metadata, schema_version, schema_hash = \
                    self._build_prompt_and_metadata()
                
                prompt_span.set_tag("step.success", True)
                prompt_span.set_tag("prompt.version", prompt_metadata.get("version", "auto"))
                prompt_span.set_tag("prompt.id", prompt_metadata.get("id", "unknown"))
                prompt_span.set_metric("prompt.length", len(prompt_text))
            
            # Step 3: Call LLM (child span)
            with tracer.trace("vote_extraction.llm_call", service="vote-extractor") as llm_span:
                llm_span.set_tag("step.name", "call_llm")
                llm_span.set_tag("llm.model_name", llm_config.model if llm_config else "default")
                llm_span.set_tag("llm.model_provider", "google")
                llm_span.set_tag("llm.temperature", llm_config.temperature if llm_config else 0.0)
                llm_span.set_tag("llm.max_tokens", llm_config.max_tokens if llm_config else 16384)
                
                try:
                    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                    response = self._call_gemini_api(client, content_parts, llm_config, prompt_metadata)
                    result = json.loads(response.text)
                    
                    # Tag LLM response metrics
                    llm_span.set_tag("step.success", True)
                    llm_span.set_metric("llm.response_length", len(response.text))
                    
                    # Token usage (if available)
                    if hasattr(response, 'usage_metadata'):
                        usage = response.usage_metadata
                        llm_span.set_metric("llm.tokens.prompt", usage.prompt_token_count)
                        llm_span.set_metric("llm.tokens.completion", usage.candidates_token_count)
                        llm_span.set_metric("llm.tokens.total", usage.total_token_count)
                    
                except (ValueError, TypeError, json.JSONDecodeError) as e:
                    # Tag parse error
                    llm_span.set_tag("error", True)
                    llm_span.set_tag("error.type", "ParseError")
                    llm_span.set_tag("error.message", str(e))
                    llm_span.set_tag("step.success", False)
                    
                    # Tag workflow
                    workflow_span.set_tag("error", True)
                    workflow_span.set_tag("error.step", "llm_call")
                    workflow_span.set_tag("workflow.success", False)
                    
                    # Handle error with context
                    self._handle_extraction_error(e, "ParseError", context={
                        "model": llm_config.model if llm_config else "default",
                        "file_count": len(image_files),
                        "response_length": len(response.text) if 'response' in locals() else 0,
                    })
                    
                    raise ExtractionException(f"Invalid extraction response: {e}") from e
                
                except Exception as e:
                    # Tag unexpected error
                    llm_span.set_tag("error", True)
                    llm_span.set_tag("error.type", type(e).__name__)
                    llm_span.set_tag("error.message", str(e))
                    llm_span.set_tag("step.success", False)
                    
                    workflow_span.set_tag("error", True)
                    workflow_span.set_tag("error.step", "llm_call")
                    workflow_span.set_tag("workflow.success", False)
                    
                    self._handle_extraction_error(e, type(e).__name__, context={
                        "model": llm_config.model if llm_config else "default",
                        "file_count": len(image_files),
                    })
                    
                    raise ExtractionException(f"Extraction failed: {e}") from e
            
            # Step 4: Validate (child span)
            with tracer.trace("vote_extraction.validate", service="vote-extractor") as validate_span:
                validate_span.set_tag("step.name", "validate_extraction")
                validate_span.set_metric("step.form_count", len(result) if isinstance(result, list) else 1)
                
                try:
                    await self._validate_within_workflow(result)
                    
                    validate_span.set_tag("step.success", True)
                    validate_span.set_tag("validation.passed", True)
                    
                except Exception as e:
                    validate_span.set_tag("error", True)
                    validate_span.set_tag("error.type", "ValidationError")
                    validate_span.set_tag("error.message", str(e))
                    validate_span.set_tag("step.success", False)
                    validate_span.set_tag("validation.passed", False)
                    
                    # Note: Validation errors might be warnings, not fatal
                    workflow_span.set_tag("validation.warning", str(e))
            
            # Step 5: Annotate success
            with tracer.trace("vote_extraction.annotate", service="vote-extractor") as annotate_span:
                annotate_span.set_tag("step.name", "annotate_success")
                
                self._annotate_extraction_success(
                    result, response.text, image_files, image_filenames,
                    llm_config, prompt_text, schema_version, schema_hash, prompt_metadata
                )
                
                annotate_span.set_tag("step.success", True)
            
            # Step 6: Capture span context for feedback
            self._capture_workflow_span_context()
            
            # Tag overall workflow success
            workflow_span.set_tag("workflow.success", True)
            workflow_span.set_tag("extraction.success", True)
            workflow_span.set_metric("workflow.forms_extracted", len(result) if isinstance(result, list) else 1)
            workflow_span.set_metric("workflow.duration_ms", workflow_span.duration * 1000)
            
            logger.info(
                "Vote extraction workflow completed successfully",
                extra={
                    "image_count": len(image_files),
                    "forms_extracted": len(result) if isinstance(result, list) else 1,
                    "model": llm_config.model if llm_config else "default",
                    "duration_ms": workflow_span.duration * 1000,
                }
            )
            
            return result
            
        except ExtractionException:
            # Already tagged and logged
            raise
            
        except Exception as e:
            # Unexpected error at workflow level
            workflow_span.set_tag("error", True)
            workflow_span.set_tag("error.type", type(e).__name__)
            workflow_span.set_tag("error.message", str(e))
            workflow_span.set_tag("error.stack", traceback.format_exc())
            workflow_span.set_tag("workflow.success", False)
            
            logger.critical(
                f"Unexpected error in vote extraction workflow: {e}",
                extra={
                    "image_count": len(image_files),
                    "model": llm_config.model if llm_config else "default",
                },
                exc_info=True
            )
            
            raise ExtractionException(f"Extraction workflow failed: {e}") from e
```

---

### 3. Experiments Service - Parent-Child Traces

**✅ Improved `vote_extraction_task`**:

```python
from ddtrace import tracer
from ddtrace.llmobs.decorators import workflow

@workflow
def vote_extraction_task(input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task function for LLMObs experiments.
    
    Creates a workflow span that will be a child of the experiment span.
    All operations below will be children of this workflow span.
    """
    # Create explicit span for the experiment task
    with tracer.trace("experiment.task.vote_extraction", service="vote-extractor") as task_span:
        # Tag task metadata
        task_span.set_tag("task.type", "vote_extraction")
        task_span.set_tag("task.form_set", input_data.get("form_set_name"))
        task_span.set_metric("task.num_pages", input_data.get("num_pages", 0))
        task_span.set_tag("task.model", config.get("model"))
        task_span.set_tag("task.temperature", config.get("temperature", 0.0))
        
        try:
            # Extract parameters
            form_set_name = input_data.get("form_set_name")
            image_paths = input_data.get("image_paths", [])
            num_pages = input_data.get("num_pages", len(image_paths))
            
            model = config.get("model")
            temperature = config.get("temperature", 0.0)
            api_key = config.get("api_key", "")
            backend_url = config.get("backend_url", "http://localhost:8000")
            
            # Step 1: Read images (child span)
            with tracer.trace("experiment.task.read_images", service="vote-extractor") as read_span:
                read_span.set_metric("read.file_count", len(image_paths))
                
                files = []
                total_size = 0
                
                for path in image_paths:
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            data = f.read()
                            total_size += len(data)
                            files.append(("images", (os.path.basename(path), data, "image/jpeg")))
                
                read_span.set_metric("read.total_size_mb", total_size / 1024 / 1024)
                read_span.set_tag("read.success", True)
            
            # Step 2: Call backend API (child span)
            with tracer.trace("experiment.task.api_call", service="vote-extractor") as api_span:
                api_span.set_tag("api.url", f"{backend_url}/api/v1/vote-extraction/extract")
                api_span.set_tag("api.model", model)
                api_span.set_tag("api.temperature", temperature)
                
                with httpx.Client(timeout=120.0) as client:
                    # Prepare headers
                    headers = {}
                    if api_key:
                        headers["X-API-Key"] = api_key
                        api_span.set_tag("api.auth", "api_key")
                    
                    # Make request
                    response = client.post(
                        f"{backend_url}/api/v1/vote-extraction/extract",
                        files=files,
                        data={"model": model, "temperature": temperature},
                        headers=headers,
                    )
                    
                    # Tag response
                    api_span.set_metric("api.response.status_code", response.status_code)
                    api_span.set_metric("api.response.size_bytes", len(response.content))
                    
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    api_span.set_tag("api.success", True)
                    api_span.set_metric("api.forms_extracted", len(result) if isinstance(result, list) else 1)
            
            # Tag task success
            task_span.set_tag("task.success", True)
            task_span.set_metric("task.forms_extracted", len(result) if isinstance(result, list) else 1)
            task_span.set_metric("task.duration_ms", task_span.duration * 1000)
            
            return result
            
        except httpx.HTTPStatusError as e:
            # HTTP error
            task_span.set_tag("error", True)
            task_span.set_tag("error.type", "HTTPError")
            task_span.set_tag("error.message", str(e))
            task_span.set_metric("error.status_code", e.response.status_code)
            task_span.set_tag("task.success", False)
            
            logger.error(f"HTTP error in experiment task: {e}", exc_info=True)
            raise
            
        except Exception as e:
            # Unexpected error
            task_span.set_tag("error", True)
            task_span.set_tag("error.type", type(e).__name__)
            task_span.set_tag("error.message", str(e))
            task_span.set_tag("task.success", False)
            
            logger.error(f"Error in experiment task: {e}", exc_info=True)
            raise
```

---

### 4. Helper Functions

**Add these helper functions to your service:**

```python
import traceback
from typing import Optional
from ddtrace import tracer

def tag_span_error(
    span,
    exception: Exception,
    error_type: Optional[str] = None,
    context: Optional[dict] = None
) -> None:
    """
    Tag a span with comprehensive error information.
    
    Args:
        span: Datadog span object
        exception: The exception that occurred
        error_type: Optional classification of the error
        context: Additional context to add as tags
    """
    if not span:
        return
    
    span.set_tag("error", True)
    span.set_tag("error.type", error_type or type(exception).__name__)
    span.set_tag("error.message", str(exception))
    span.set_tag("error.stack", traceback.format_exc())
    
    if context:
        for key, value in context.items():
            span.set_tag(f"error.context.{key}", str(value))
    
    span.set_metric("error.count", 1)


def tag_span_success(
    span,
    metrics: Optional[dict] = None,
    tags: Optional[dict] = None
) -> None:
    """
    Tag a span with success information.
    
    Args:
        span: Datadog span object
        metrics: Numeric metrics to add
        tags: String tags to add
    """
    if not span:
        return
    
    span.set_tag("success", True)
    
    if tags:
        for key, value in tags.items():
            span.set_tag(key, str(value))
    
    if metrics:
        for key, value in metrics.items():
            span.set_metric(key, value)


def get_current_span_or_create(operation_name: str, service: str = "vote-extractor"):
    """
    Get current span or create a new one if none exists.
    
    Args:
        operation_name: Name of the operation
        service: Service name for the span
    
    Returns:
        Span context manager
    """
    current = tracer.current_span()
    
    if current:
        # Use current span
        return current
    else:
        # Create new span
        return tracer.trace(operation_name, service=service)
```

---

## 📋 Implementation Checklist

Apply these changes to your service:

### vote_extraction_service.py

- [ ] Update `_handle_extraction_error` to tag current span
- [ ] Add explicit span creation in `extract_from_images`
- [ ] Tag each step (preprocess, prompt, llm_call, validate)
- [ ] Add comprehensive error tagging for all exception types
- [ ] Add success metrics (duration, forms_extracted, etc.)
- [ ] Import `traceback` for stack traces
- [ ] Add helper functions: `tag_span_error`, `tag_span_success`

### experiments_service.py

- [ ] Update `vote_extraction_task` with explicit spans
- [ ] Tag each step (read_images, api_call)
- [ ] Add HTTP error handling with proper tags
- [ ] Add success metrics
- [ ] Ensure all spans are children of the task span

### General

- [ ] Ensure all `try-except` blocks set `error=True` tag
- [ ] Use `set_metric()` for numeric values
- [ ] Use `set_tag()` for string values
- [ ] Add `duration_ms` metrics to long-running operations
- [ ] Test trace hierarchy in Datadog APM UI
- [ ] Verify errors show up in Error Tracking

---

## 🧪 Testing

### 1. Verify Trace Hierarchy

Run an extraction and check Datadog APM:

```
vote_extraction.workflow
├── vote_extraction.preprocess
├── vote_extraction.build_prompt
├── vote_extraction.llm_call
├── vote_extraction.validate
└── vote_extraction.annotate
```

### 2. Verify Error Tagging

Trigger an error and check that:
- Span has `error: true` tag
- `error.type` and `error.message` are present
- Error shows in Datadog Error Tracking
- Error metrics are recorded

### 3. Verify Experiments

Run an experiment and check that:
- `experiment.task.vote_extraction` is a child of experiment span
- All steps are children of the task span
- Success/failure is properly tagged
- Metrics are recorded

---

## 🎯 Expected Improvements

After implementing these changes:

1. **Better Error Visibility**: All errors properly tagged and tracked
2. **Clear Trace Hierarchy**: Parent-child relationships visualized in APM
3. **Rich Metrics**: Quantitative data on performance and success rates
4. **Easier Debugging**: Stack traces and context in spans
5. **Better Alerting**: Can alert on `error.count` metric
6. **Performance Insights**: Duration metrics for each step

---

**Ready to implement!** 🚀

