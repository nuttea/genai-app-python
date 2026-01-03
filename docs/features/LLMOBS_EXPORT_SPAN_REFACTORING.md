# LLMObs.export_span() Refactoring

## Overview

Refactored validation custom evaluations to use `LLMObs.export_span()` instead of manually passing `span_id` and `trace_id`, following [Datadog's official SDK pattern](https://docs.datadoghq.com/llm_observability/evaluations/external_evaluations#submitting-external-evaluations-with-the-sdk).

## Official Datadog Pattern

From the Datadog documentation:

```python
from ddtrace.llmobs import LLMObs

# joining an evaluation to a span via span ID and trace ID
span_context = LLMObs.export_span(span=None)
LLMObs.submit_evaluation(
    span = span_context,
    ml_app = "chatbot",
    label="harmfulness",
    metric_type="score",
    value=my_harmfulness_eval(completion),
    tags={"type": "custom"},
    timestamp_ms=1765990800016,
    assessment="pass",
    reasoning="it makes sense",
)
```

## Key Insight

**`LLMObs.export_span(span=None)`** automatically gets the current active span context. You don't need to manually capture and pass `span_id` and `trace_id` through your code!

## Before vs After

### Before: Manual Span Context Passing

```python
# ❌ OLD APPROACH - Manual span context management

# Endpoint Layer
async def extract_votes(...):
    result = await vote_extraction_service.extract_from_images(...)
    
    # Capture span context
    span_context = _get_span_context()
    span_id = span_context.span_id if span_context else None
    trace_id = span_context.trace_id if span_context else None
    
    # Pass through layers
    extracted_reports, warnings = await _parse_extraction_results(
        result=result,
        span_id=span_id,  # ← Pass manually
        trace_id=trace_id,  # ← Pass manually
    )

# Service Layer
async def _parse_extraction_results(
    result,
    span_id: str | None,  # ← Extra parameter
    trace_id: str | None,  # ← Extra parameter
):
    is_valid, error = await validate_extraction(
        data=data,
        span_id=span_id,  # ← Pass manually
        trace_id=trace_id,  # ← Pass manually
    )

async def validate_extraction(
    data,
    span_id: str | None,  # ← Extra parameter
    trace_id: str | None,  # ← Extra parameter
):
    _submit_validation_evaluation(
        span_id=span_id,  # ← Pass manually
        trace_id=trace_id,  # ← Pass manually
        is_valid=is_valid,
        ...
    )

def _submit_validation_evaluation(
    span_id: str | None,  # ← Extra parameter
    trace_id: str | None,  # ← Extra parameter
    is_valid,
    ...
):
    if not span_id or not trace_id:
        logger.warning("Missing span context")
        return
    
    # Manually construct span context
    span_context = {
        "span_id": span_id,
        "trace_id": trace_id,
    }
    
    LLMObs.submit_evaluation(span=span_context, ...)
```

### After: Automatic Span Detection

```python
# ✅ NEW APPROACH - Official SDK pattern

# Endpoint Layer
async def extract_votes(...):
    result = await vote_extraction_service.extract_from_images(...)
    
    # Parse and validate
    # Validation uses LLMObs.export_span() internally
    extracted_reports, warnings = await _parse_extraction_results(
        result=result
        # ← No span params needed!
    )
    
    # Only capture span context for feedback submission
    span_context = _get_span_context()

# Service Layer
async def _parse_extraction_results(result):
    # ← No span parameters needed!
    is_valid, error = await validate_extraction(data=data)

async def validate_extraction(data):
    # ← No span parameters needed!
    _submit_validation_evaluation(
        is_valid=is_valid,
        ...
    )

def _submit_validation_evaluation(is_valid, ...):
    # ← No span parameters needed!
    
    # Use official SDK method to get current span
    span_context = LLMObs.export_span(span=None)
    
    if not span_context:
        logger.warning("No active span context")
        return
    
    LLMObs.submit_evaluation(span=span_context, ...)
```

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Code Complexity** | High - manual threading | Low - automatic detection |
| **Function Signatures** | Extra span params everywhere | Clean, focused params |
| **Error Handling** | Check for None IDs | Check for None span_context |
| **Maintainability** | Difficult - many params | Easy - fewer params |
| **Robustness** | Manual context construction | SDK handles format |
| **Best Practices** | Custom approach | Official Datadog pattern |

## How `LLMObs.export_span()` Works

```python
# When called with span=None, it exports the current active span
span_context = LLMObs.export_span(span=None)

# Returns a dictionary like:
# {
#     "span_id": "14484272564170044706",
#     "trace_id": "140031489178122457..."
# }

# Or None if no active span
if not span_context:
    # No active span - can't submit evaluation
    return
```

The SDK automatically:
1. Detects the current active span in the trace context
2. Extracts the span_id and trace_id
3. Returns them in the correct format for `submit_evaluation()`

## Code Changes Summary

### Service Layer Changes

**`vote_extraction_service.py`**

1. `_submit_validation_evaluation()`:
   - ✅ Removed `span_id` and `trace_id` parameters
   - ✅ Added `span_context = LLMObs.export_span(span=None)`
   - ✅ Changed check from `if not span_id or not trace_id` to `if not span_context`
   - ✅ Use `span_context` directly (no manual dict construction)

2. `validate_extraction()`:
   - ✅ Removed `span_id` and `trace_id` parameters
   - ✅ Updated docstring to mention `export_span()`

3. All calls to `_submit_validation_evaluation()`:
   - ✅ Removed `span_id=...` and `trace_id=...` arguments

### Endpoint Layer Changes

**`vote_extraction.py`**

1. `_parse_extraction_results()`:
   - ✅ Removed `span_id` and `trace_id` parameters
   - ✅ Updated docstring

2. `extract_votes()` endpoint:
   - ✅ Removed early span context capture
   - ✅ Moved span context capture AFTER validation
   - ✅ Only captures for feedback submission

3. Call to `validate_extraction()`:
   - ✅ Removed `span_id=...` and `trace_id=...` arguments

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ HTTP Request: POST /api/v1/vote-extraction/extract     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ extract_from_images() @workflow                         │
│ ✅ Active span context created                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ _parse_extraction_results()                             │
│ - Parse ElectionFormData                                │
│ - Call validate_extraction(data)                        │
│   ← No span parameters needed!                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ validate_extraction(data)                               │
│ - Run validation checks                                 │
│ - Call _submit_validation_evaluation()                  │
│   ← No span parameters needed!                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ _submit_validation_evaluation()                         │
│ - span_context = LLMObs.export_span(span=None)         │
│   ✅ Automatic span detection!                          │
│ - LLMObs.submit_evaluation(span=span_context, ...)     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Custom Evaluations in Datadog LLMObs                    │
│ ✅ Properly linked to workflow span                     │
│ ✅ Automatic context detection                          │
└─────────────────────────────────────────────────────────┘
```

## When to Use `export_span()`

### Use `export_span(span=None)` when:
✅ Submitting evaluations from within the same trace context  
✅ You want automatic span detection  
✅ Following official Datadog SDK patterns  
✅ Simplifying code by removing manual span passing  

### Don't use `export_span()` when:
❌ Submitting evaluations asynchronously (e.g., from a background worker)  
❌ The evaluation context is different from the current span  
❌ You need to submit evaluations for historical spans  

For async/background evaluations, you still need to manually capture and pass the span context at the time of the LLM operation.

## Impact on Existing Functionality

### ✅ No Breaking Changes

- Evaluations still work the same way
- Same span linkage and trace context
- Same Datadog queries
- Same UI display

### ✅ Improved Code Quality

- Cleaner function signatures
- Fewer parameters to manage
- Less error-prone
- Easier to understand and maintain
- Follows official best practices

### ✅ Better Developer Experience

- Less boilerplate code
- Automatic span detection
- Standard SDK patterns
- Clear, concise code

## Testing

### Manual Testing

1. **Make an extraction request** via Streamlit
2. **Check backend logs**:
   ```bash
   docker-compose logs fastapi-backend --tail 50 | grep "validation evaluation"
   ```
   Expected: "✅ Submitted validation evaluation" messages

3. **Query Datadog**:
   ```
   service:vote-extractor @evaluations.validation_passed:pass
   service:vote-extractor @evaluations.validation_passed:fail
   ```
   Expected: Evaluations properly linked to extraction spans

4. **Check Datadog UI**:
   - Go to LLM Observability → Evaluations
   - Filter by `ml_app:vote-extractor`
   - Verify evaluations are linked to workflow spans
   - Verify `assessment` and `reasoning` fields populated

### Expected Behavior

- ✅ Evaluations submitted successfully
- ✅ Proper span linkage maintained
- ✅ Same trace IDs in Datadog UI
- ✅ No errors or warnings in logs

## Related Documentation

- [Datadog External Evaluations SDK](https://docs.datadoghq.com/llm_observability/evaluations/external_evaluations#submitting-external-evaluations-with-the-sdk)
- [Validation Custom Evaluations](VALIDATION_CUSTOM_EVALUATIONS.md)
- [Evaluation Metric Types Guide](../../guides/llmobs/03_EVALUATION_METRIC_TYPES.md)
- [Vote Extraction LLMObs Spans](VOTE_EXTRACTION_LLMOBS_SPANS.md)

## Key Takeaways

1. **Use the official SDK pattern**: `LLMObs.export_span(span=None)`
2. **Automatic is better**: Let the SDK detect the current span
3. **Simpler is better**: Fewer parameters = easier maintenance
4. **Follow best practices**: Official Datadog examples are authoritative
5. **Clean code wins**: Removes 20+ lines of parameter passing

## Migration Checklist

When migrating other code to use `export_span()`:

- [ ] Remove `span_id` and `trace_id` parameters from functions
- [ ] Add `span_context = LLMObs.export_span(span=None)` at evaluation point
- [ ] Change checks from `if not span_id or not trace_id` to `if not span_context`
- [ ] Remove manual span context dict construction
- [ ] Update all function calls to remove span parameters
- [ ] Update docstrings to mention `export_span()`
- [ ] Test to verify evaluations still link correctly

---

**This refactoring makes our code cleaner, more maintainable, and follows Datadog's official SDK patterns!** 🎯

