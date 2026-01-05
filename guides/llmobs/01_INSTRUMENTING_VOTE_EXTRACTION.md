# Part 01: Instrumenting Our Vote Extraction Application

This guide shows how we've implemented LLM Observability in our Thai election vote extraction application using Datadog's span kinds and annotations.

## Overview

Our vote extraction application processes election form images through multiple steps:
1. **Workflow**: Vote extraction orchestration
2. **Tasks**: Prompt building, metadata capture, error handling
3. **LLM Calls**: Gemini API for structured data extraction
4. **Tools**: External service calls and validations

We use Datadog LLMObs to trace each operation, providing visibility into performance, errors, and data flow.

---

## Architecture: How Our Application Uses Span Kinds

```
vote_extraction_workflow (workflow span - root)
├── _build_prompt_and_metadata (task span)
├── _call_gemini_api (llm span)
│   └── Gemini API call with thinking_config
├── _capture_workflow_span_context (task span)
└── _handle_extraction_error (task span - on error)

llm_judge_evaluator (workflow span - root)
├── llm_judge.initialize_client (custom APM span)
├── llm_judge.build_prompt (custom APM span)
├── llm_judge.api_call (custom APM span)
│   └── Retry logic with exponential backoff
├── llm_judge.parse_response (custom APM span)
└── llm_judge.log_results (custom APM span)
```

---

## Implementation Examples from Our Codebase

### 1. Workflow Span: Vote Extraction

**File**: `services/fastapi-backend/app/services/vote_extraction_service.py`

Our main vote extraction function is instrumented as a **workflow** because it orchestrates a fixed sequence of operations:

```python
from ddtrace.llmobs.decorators import workflow

@workflow
async def extract_from_images(
    images_input: Union[List[UploadFile], List[str]],
    form_set_name: str = "default",
    config: Optional[LLMConfig] = None,
) -> List[Dict[str, Any]]:
    """
    Extract election data from images using Google Gemini with LLMObs tracing.
    
    This is a workflow span - it orchestrates multiple steps:
    - Prompt building
    - LLM API call
    - Response parsing
    - Error handling
    """
    try:
        # Step 1: Build prompt and capture metadata (task span)
        prompt_parts, metadata = _build_prompt_and_metadata(
            images_input, form_set_name, config
        )
        
        # Step 2: Call Gemini API (llm span)
        response = await _call_gemini_api(prompt_parts, config, metadata)
        
        # Step 3: Capture workflow context (task span)
        _capture_workflow_span_context(response, metadata, config)
        
        # Parse and return results
        result = json.loads(response.text)
        return result
        
    except Exception as e:
        # Error handling (task span)
        _handle_extraction_error(e, form_set_name, metadata)
        raise
```

**Why `@workflow`?**
- ✅ Fixed sequence of operations
- ✅ High-level entry point for vote extraction
- ✅ Orchestrates multiple child spans
- ✅ Can be traced from start to finish

---

### 2. Task Span: Prompt Building

**File**: `services/fastapi-backend/app/services/vote_extraction_service.py`

Prompt building is a **task** because it's a standalone data transformation that doesn't call external services:

```python
from ddtrace.llmobs.decorators import task

@task
def _build_prompt_and_metadata(
    images_input: Union[List[UploadFile], List[str]],
    form_set_name: str,
    config: Optional[LLMConfig],
) -> Tuple[List, Dict[str, Any]]:
    """
    Build the prompt and collect metadata for LLM call.
    
    This is a task span - it performs data preparation without external calls.
    """
    metadata = {
        "form_set_name": form_set_name,
        "num_images": len(images_input),
        "model": config.model if config else settings.default_model,
        "temperature": config.temperature if config else settings.default_temperature,
    }
    
    prompt_parts = [EXTRACTION_PROMPT]
    
    # Process images
    for idx, image in enumerate(images_input, 1):
        if isinstance(image, str):
            # Load from file path
            img_data = Image.open(image)
        else:
            # Load from upload
            img_data = Image.open(image.file)
        
        prompt_parts.append(img_data)
    
    return prompt_parts, metadata
```

**Why `@task`?**
- ✅ Standalone data processing
- ✅ No external service calls
- ✅ Pure transformation logic
- ✅ Part of larger workflow

---

### 3. LLM Span: Gemini API Call

**File**: `services/fastapi-backend/app/services/vote_extraction_service.py`

While auto-instrumentation handles most LLM calls, we can also manually instrument custom LLM implementations:

```python
from ddtrace.llmobs.decorators import llm

@llm(model_name="gemini-2.5-flash", model_provider="google-vertex-ai")
async def _call_gemini_api(
    prompt_parts: List,
    config: LLMConfig,
    metadata: Dict[str, Any],
) -> Any:
    """
    Call Gemini API with structured schema and thinking config.
    
    This is an LLM span - it traces the actual model inference call.
    """
    client = _get_client()
    
    # Configure generation with thinking mode for better reasoning
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,  # Unlimited thinking for best accuracy
        ),
        response_mime_type="application/json",
        response_schema=ELECTION_DATA_SCHEMA,  # Structured output
        temperature=config.temperature,
        max_output_tokens=config.max_tokens,
    )
    
    # Make the LLM call
    response = await client.aio.models.generate_content(
        model=config.model,
        contents=prompt_parts,
        config=generate_content_config,
    )
    
    return response
```

**Why `@llm`?**
- ✅ Direct LLM inference call
- ✅ Tracks model, provider, config
- ✅ Captures tokens, latency
- ✅ Records prompts and completions

**Note**: In our actual implementation, we rely on **auto-instrumentation** for Gemini calls, so we don't use the `@llm` decorator. This example shows how you would manually instrument it if needed.

---

### 4. Custom APM Spans: LLM Judge Evaluator

**File**: `services/fastapi-backend/app/services/experiments_service.py`

For our LLM-as-judge evaluator, we use **custom APM spans** to trace each step without LLMObs-specific metadata:

```python
from ddtrace import tracer

def llm_judge_evaluator(
    input_data: Dict,
    output_data: Dict,
    expected_output: Dict,
) -> float:
    """
    Evaluate extraction quality using Gemini 3 Pro as a judge.
    
    Uses custom APM spans for detailed observability.
    """
    form_set_name = input_data.get("form_set_name", "unknown")
    
    with tracer.trace(
        "llm_judge.evaluate",
        service="vote-extractor",
        resource=f"evaluate_{form_set_name}"
    ) as eval_span:
        eval_span.set_tag("form_set_name", form_set_name)
        eval_span.set_tag("evaluator", "llm_judge")
        
        try:
            # Initialize client
            with tracer.trace("llm_judge.initialize_client", service="vote-extractor"):
                client = genai.Client(
                    vertexai=True,
                    project=settings.google_cloud_project,
                    location=settings.vertex_ai_location,
                )
            
            # Build evaluation prompt
            with tracer.trace("llm_judge.build_prompt", service="vote-extractor") as prompt_span:
                prompt = f"""Evaluate this election data extraction...
                Expected: {json.dumps(expected_output, ensure_ascii=False)}
                Actual: {json.dumps(output_data, ensure_ascii=False)}
                """
                prompt_span.set_metric("prompt_length", len(prompt))
            
            # Call LLM with retry logic
            response = None
            retry_delay = 1.0
            
            for attempt in range(1, 4):  # Max 3 retries
                with tracer.trace("llm_judge.api_call", service="vote-extractor") as api_span:
                    api_span.set_metric("attempt", attempt)
                    
                    # Debug response structure
                    response = client.models.generate_content(
                        model="gemini-3-pro-preview",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=EVALUATION_SCHEMA,
                            temperature=0.0,
                            max_output_tokens=4096,
                        ),
                    )
                    
                    # Log finish reason and candidates
                    finish_reason = getattr(response, 'finish_reason', 'N/A')
                    api_span.set_tag("finish_reason", str(finish_reason))
                    
                    if response and response.text:
                        api_span.set_tag("response_valid", True)
                        break  # Success!
                    else:
                        # Retry on empty response
                        api_span.set_tag("response_valid", False)
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
            
            # Parse response
            with tracer.trace("llm_judge.parse_response", service="vote-extractor"):
                if not response or not response.text:
                    return 0.0  # Failed after retries
                
                result = json.loads(response.text)
                score = float(result.get("score", 0.0))
            
            # Log results
            with tracer.trace("llm_judge.log_results", service="vote-extractor") as log_span:
                log_span.set_metric("final_score", score)
                log_span.set_tag("reasoning", result.get("reasoning", ""))
                
                logger.info(
                    f"LLM Judge: {form_set_name}",
                    extra={
                        "score": score,
                        "reasoning": result.get("reasoning"),
                        "errors_found": len(result.get("errors", [])),
                    }
                )
            
            return score
            
        except Exception as e:
            eval_span.set_tag("error", True)
            eval_span.set_tag("error.message", str(e))
            logger.error(f"LLM Judge Error: {e}")
            return 0.0
```

**Why Custom APM Spans (not LLMObs decorators)?**
- ✅ More granular control over span hierarchy
- ✅ Track retry logic and debugging info
- ✅ Avoid `KeyError: 'Span kind not found'` from LLMObs
- ✅ Still get full APM visibility

**Key Patterns**:
- Hierarchical spans with `with tracer.trace()`
- Rich tagging with `set_tag()` and `set_metric()`
- Error tracking with `error=True`
- Structured logging with `extra={}`

---

## Annotation Best Practices

### Adding Context to Spans

Use `LLMObs.annotate()` to add custom data to any span:

```python
from ddtrace.llmobs import LLMObs

@workflow
async def extract_from_images(...):
    # ... your logic ...
    
    LLMObs.annotate(
        input_data={
            "form_set_name": form_set_name,
            "num_images": len(images_input),
            "model": config.model,
        },
        output_data={
            "forms_extracted": len(result),
            "total_votes": sum(form.get("total_votes", 0) for form in result),
        },
        metadata={
            "api_version": "v1",
            "schema_version": "2024-01",
            "thinking_enabled": True,
        },
        metrics={
            "extraction_time_ms": metadata.get("duration_ms"),
            "tokens_used": metadata.get("token_count"),
        },
        tags={
            "environment": settings.dd_env,
            "extraction_type": "election_forms",
        }
    )
```

### Span Tagging with Datadog Tracer

For custom APM spans (non-LLMObs), use Datadog tracer tags:

```python
from ddtrace import tracer

with tracer.trace("custom_operation", service="vote-extractor") as span:
    # Set string tags
    span.set_tag("operation_type", "validation")
    span.set_tag("form_name", form_set_name)
    
    # Set numeric metrics
    span.set_metric("validation_score", 0.95)
    span.set_metric("fields_validated", 25)
    
    # Mark errors
    if error_occurred:
        span.set_tag("error", True)
        span.set_tag("error.message", str(error))
        span.set_tag("error.type", type(error).__name__)
```

---

## Integration with Datadog APM

Our LLMObs traces are **automatically correlated** with APM traces, giving us:

### Service-Level Visibility
```python
# In main.py
from ddtrace import tracer

tracer.set_tags({
    "env": settings.dd_env,
    "service": "vote-extractor",
    "version": settings.dd_version,
})
```

### Request-Level Correlation
```python
# FastAPI endpoint automatically creates APM trace
@router.post("/extract")
async def extract_endpoint(request: ExtractionRequest):
    # This creates an APM trace that contains our LLMObs workflow
    result = await extract_from_images(...)
    return result
```

**Benefits**:
- 🔗 Link LLM operations to HTTP requests
- 📊 See full request latency including LLM calls
- 🔍 Trace errors from API → Workflow → LLM
- 📈 Track resource usage across services

---

## Real-World Observability Queries

### Find Slow Extractions
```
service:vote-extractor operation_name:extract_from_images @duration:>5000
```

### Find LLM Judge Failures
```
service:vote-extractor operation_name:llm_judge.evaluate @final_score:0.0
```

### Track Retry Attempts
```
service:vote-extractor operation_name:llm_judge.api_call @attempt:>1
```

### Find Empty LLM Responses
```
service:vote-extractor @finish_reason:SAFETY OR @response_valid:false
```

### Monitor Token Usage
```
service:vote-extractor operation_name:extract_from_images | stats sum(@tokens_used) by @model
```

---

## Key Takeaways

### ✅ Span Kind Selection
- **Workflow**: `extract_from_images` - orchestrates entire process
- **Task**: `_build_prompt_and_metadata` - data preparation
- **LLM**: Auto-instrumented Gemini calls
- **Custom APM**: `llm_judge_evaluator` - fine-grained control

### ✅ Instrumentation Patterns
- Use decorators for high-level operations
- Use `tracer.trace()` for granular control
- Add rich context with annotations
- Capture errors and retry logic

### ✅ Observability Benefits
- 🔍 Debug slow/failed extractions
- 📊 Monitor LLM performance and costs
- 🐛 Trace errors to root cause
- 📈 Optimize based on real usage data

---

## Next Steps

In **Part 02**, we'll explore:
- How to visualize these traces in Datadog
- Analyzing trace flamegraphs
- Using span details for debugging
- Setting up monitors and alerts

---

## Related Files

- **Implementation**: `services/fastapi-backend/app/services/vote_extraction_service.py`
- **Experiments**: `services/fastapi-backend/app/services/experiments_service.py`
- **Configuration**: `services/fastapi-backend/app/config.py`
- **Source Material**: `guides/llmobs/sources/01_INSTRUMENTING_SPANS.md`

---

**Last Updated**: January 5, 2026

