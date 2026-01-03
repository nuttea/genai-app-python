# Validation Trace Context Fix

## Problem

The `validate_extraction` task was creating a **separate trace** instead of being part of the same trace as the main extraction request.

### Symptoms
- In Datadog LLMObs, the validation task appeared as a separate trace
- The validation span was not grouped with the extraction workflow span
- Made it difficult to see the complete end-to-end flow of a single request

### Root Cause

```python
# services/fastapi-backend/app/services/vote_extraction_service.py
@workflow  # Creates trace ID: abc123
async def extract_from_images(...):
    # ... extraction logic ...
    return result

@task  # ❌ Creates NEW trace ID: xyz789 (separate trace!)
async def validate_extraction(data):
    # ... validation logic ...
    return is_valid, error_msg
```

The `validate_extraction` method was decorated with `@task`, which creates its own span. However, it was being called from the **endpoint** (`_parse_extraction_results`), which is **outside** the `@workflow` span context:

```python
# services/fastapi-backend/app/api/v1/endpoints/vote_extraction.py
async def extract_votes(...):
    # Inside workflow trace context
    result = await vote_extraction_service.extract_from_images(...)  # Trace ID: abc123
    
    # Outside workflow trace context (in endpoint)
    extracted_reports, warnings = await _parse_extraction_results(result, ...)
    # ↓
    # Inside _parse_extraction_results
    is_valid, error_msg = await vote_extraction_service.validate_extraction(data)
    # ❌ This creates a NEW trace because @task decorator creates a new span
    #    without parent context (Trace ID: xyz789)
```

### Why This Happened

When `@task` (or `@workflow`) decorators are used, they:
1. Create a new LLMObs span
2. **If there's a parent span in the current context**, they attach as a child
3. **If there's NO parent span**, they create a **new trace** (new trace ID)

The problem: The endpoint code (`_parse_extraction_results`) is **outside** the workflow span, so when `validate_extraction` is called from there, it has no parent context → creates a new trace.

## Solution

**Remove the `@task` decorator** from `validate_extraction` to make it a regular method. It will automatically inherit the parent trace context from the HTTP request span.

### Before (Separate Traces)

```python
@task  # ❌ Creates separate trace
async def validate_extraction(data):
    validation_checks = []
    # ... validation logic ...
```

### After (Same Trace)

```python
async def validate_extraction(data):  # ✅ Inherits parent trace context
    """
    Validate extracted vote data for consistency.
    
    This validation is called as part of the extraction workflow,
    so it inherits the parent workflow trace context.
    """
    validation_checks = []
    # ... validation logic ...
```

### Trace Hierarchy After Fix

```
HTTP Request (FastAPI)          [Trace ID: abc123]
├── extract_from_images         [Workflow Span]
│   ├── Gemini API Call         [LLM Span]
│   └── Annotation              [Metadata]
└── _parse_extraction_results   [HTTP span continues]
    └── validate_extraction     [✅ Part of same trace: abc123]
        ├── _validate_ballot_statistics
        └── Annotation          [Metadata]
```

## Changes Made

1. **Removed `@task` decorator** from `validate_extraction` method
2. **Updated docstring** to clarify that it inherits parent trace context
3. **Removed unused import** of `task` from `ddtrace.llmobs.decorators`

### Files Changed

- `services/fastapi-backend/app/services/vote_extraction_service.py`
  - Removed `@task` decorator from `validate_extraction` (line 541)
  - Updated docstring (line 546-550)
  - Removed `task` from imports (line 20)

## Benefits

✅ **Single unified trace**: All operations (extraction + validation) are in one trace  
✅ **Better observability**: Can see complete request flow in Datadog  
✅ **Correct span hierarchy**: Validation is properly nested under HTTP request  
✅ **Easier debugging**: All related spans grouped together with same trace ID  
✅ **Cleaner code**: Simpler implementation without unnecessary decorator  

## Alternative Approaches (Not Used)

### Option 1: Call validation inside workflow
Move validation logic into the `extract_from_images` workflow so it's executed before returning.

**Pros**: Validation would be part of the workflow span  
**Cons**: Would require significant refactoring; workflow should focus on extraction, not parsing  

### Option 2: Manual span context propagation
Pass the span context from the workflow to the validation method.

**Pros**: Keeps `@task` decorator  
**Cons**: Complex, error-prone, requires manual context management  

### Option 3: Remove decorator (Chosen)
Remove `@task` decorator and let validation inherit the parent HTTP request span.

**Pros**: Simple, clean, works automatically  
**Cons**: Validation doesn't get its own named span (but it's not needed for a simple validation function)  

## Verification

To verify the fix is working:

1. **Make an extraction request**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/vote-extraction/extract \
     -F "images=@test_page1.jpg" \
     -F "images=@test_page2.jpg"
   ```

2. **Check Datadog LLMObs**:
   - Go to: https://app.datadoghq.com/apm/traces
   - Search for: `service:vote-extractor`
   - Expected result: **One trace** containing:
     - HTTP request span
     - `extract_from_images` workflow span
     - Gemini API call span
     - All within the same trace ID ✅

3. **Before the fix**, you would see:
   - Trace 1: HTTP request + extract_from_images
   - Trace 2: validate_extraction (separate trace) ❌

4. **After the fix**, you see:
   - Trace 1: HTTP request + extract_from_images + validation (all together) ✅

## Testing

```bash
# Restart backend
docker-compose restart fastapi-backend

# Test extraction
cd scripts/tests
python test_vote_extraction.py

# Check logs
docker-compose logs fastapi-backend --tail 50 | grep -i "trace_id\|span_id\|llmobs"
```

## Related Documentation

- [Vote Extraction LLMObs Spans](../features/VOTE_EXTRACTION_LLMOBS_SPANS.md)
- [LLMObs Instrumentation Guide](../../guides/llmobs/sources/01_INSTRUMENTING_SPANS.md)
- [User Feedback Implementation](../features/USER_FEEDBACK_LLMOBS_IMPLEMENTATION_SUMMARY.md)

## Key Takeaway

**Only use `@task` or `@workflow` decorators when you want to create a NEW top-level span or a child span within an existing LLMObs span hierarchy.** 

For regular methods called during a request that should just inherit the parent trace context, **don't use any decorator** - they will automatically be part of the parent trace.

