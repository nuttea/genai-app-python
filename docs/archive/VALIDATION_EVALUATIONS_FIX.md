# Validation Evaluations Fix Summary

**Date**: January 3, 2026  
**Issue**: Datadog LLMObs custom evaluations from `validate_extraction()` were not being submitted
**Status**: ✅ **RESOLVED**

---

## Problem

Validation evaluations were failing to submit with error:
```
LLMObsExportSpanError: No span provided and no active LLMObs-generated span found.
```

**Root Cause**: The `validate_extraction` method was being called **after** the `@workflow` span (`extract_from_images`) had already closed, so `LLMObs.export_span()` couldn't find an active span context.

---

## Solution

### 1. **Move Validation Inside the Workflow Span**

Created a new method `_validate_within_workflow()` that is called **inside** the `extract_from_images` workflow, **before** it returns. This ensures that validation runs while the workflow span is still active.

**File**: `services/fastapi-backend/app/services/vote_extraction_service.py`

```python
@workflow
async def extract_from_images(...) -> dict:
    # ... extraction logic ...
    
    # Validate BEFORE returning (while workflow span is active)
    await self._validate_within_workflow(result)
    
    return result
```

### 2. **Make Evaluation Labels Unique Per Form**

When multiple forms are extracted (e.g., Constituency + PartyList), both were trying to submit evaluations with the same labels (`validation_passed`, `validation_check_type`, `validation_score`) at nearly the same timestamp, causing Datadog to reject them as duplicates.

**Fix**: Added a `form_index` parameter to make labels unique:

```python
label=f"validation_passed_form_{form_index}"  # e.g., validation_passed_form_0, validation_passed_form_1
label=f"validation_check_type_form_{form_index}"
label=f"validation_score_form_{form_index}"
```

### 3. **Remove Duplicate Validation from Endpoint**

The endpoint (`_parse_extraction_results`) was also calling `validate_extraction`, creating duplicate attempts. This was removed since validation now happens inside the workflow.

---

## Changes Made

### Modified Files

1. **`services/fastapi-backend/app/services/vote_extraction_service.py`**
   - Added `_validate_within_workflow()` method
   - Modified `extract_from_images()` to call validation before returning
   - Updated `validate_extraction()` to accept `form_index` parameter
   - Updated `_submit_validation_evaluation()` to use unique labels per form
   - Added `form_index` tag to evaluation metadata

2. **`services/fastapi-backend/app/api/v1/endpoints/vote_extraction.py`**
   - Removed validation call from `_parse_extraction_results()`
   - Added comment explaining that validation now happens in the workflow

---

## Verification

### Test Results

**Test**: 6-page election form extraction (2 forms: Constituency + PartyList)

**Before Fix**:
```
❌ Failed to submit validation evaluation: No span provided and no active LLMObs-generated span found.
```

**After Fix**:
```
✅ sent 6 LLMObs evaluation_metric events to https://api.datadoghq.com/api/intake/llm-obs/v2/eval-metric
✅ sent 2 LLMObs span events to https://llmobs-intake.datadoghq.com/api/v2/llmobs
```

**Evaluations Submitted**:
- Form 0: `validation_passed_form_0`, `validation_check_type_form_0`, `validation_score_form_0`
- Form 1: `validation_passed_form_1`, `validation_check_type_form_1`, `validation_score_form_1`

---

## Datadog Integration

### Evaluation Metrics

Each form now submits 3 custom evaluations:

1. **`validation_passed_form_N`** (categorical):
   - **Value**: `"pass"` or `"fail"`
   - **Assessment**: `"pass"` or `"fail"`
   - **Reasoning**: Error message or "All validation checks passed"

2. **`validation_check_type_form_N`** (categorical):
   - **Value**: Check type (e.g., `"ballot_statistics"`, `"vote_results"`, `"vote_counts"`, `"all_checks"`)
   - **Assessment**: `"pass"` or `"fail"`
   - **Reasoning**: Detailed check description

3. **`validation_score_form_N`** (score):
   - **Value**: `checks_passed / total_checks` (0.0 to 1.0)
   - **Assessment**: `"pass"` or `"fail"`
   - **Reasoning**: "Passed X/Y validation checks"

### Tags

Each evaluation includes these tags for filtering and grouping:
- `feature`: `"vote-extraction"`
- `validation_check`: Check type
- `form_type`: `"Constituency"` or `"PartyList"`
- `form_index`: `"0"`, `"1"`, etc.
- `vote_results_count`: Number of vote results
- `has_ballot_statistics`: `"True"` or `"False"`

---

## View in Datadog

**Trace URL**: https://app.datadoghq.com/apm/trace/6959345500000000973864a506f61c5b

**LLMObs Dashboard**: https://app.datadoghq.com/llm

**Query Examples**:
```
# View all validation evaluations
@tags.feature:vote-extraction

# View evaluations by form type
@tags.form_type:Constituency

# View evaluations by form index
@tags.form_index:0

# View failed validations only
@label:validation_passed_form_* AND @value:fail
```

---

## Key Learnings

1. **Span Context Timing**: Custom evaluations must be submitted **while the span is still active**. Use `@workflow` span boundaries carefully.

2. **Unique Labels Required**: When submitting multiple evaluations with the same label to the same span at similar timestamps, Datadog may reject them as duplicates. Make labels unique using suffixes or indices.

3. **Use `LLMObs.export_span(span=None)`**: This method automatically detects the active LLMObs span context, eliminating the need to manually pass span IDs through function parameters.

4. **Validation Location**: Validation that submits evaluations should happen **inside** the workflow span, not in the API endpoint layer.

---

## References

- [Datadog LLMObs Custom Evaluations](https://docs.datadoghq.com/llm_observability/evaluations/external_evaluations#submitting-external-evaluations-with-the-sdk)
- [Datadog LLMObs SDK Reference](https://docs.datadoghq.com/llm_observability/instrumentation/sdk/?tab=python)
- [Evaluation Metric Types Guide](guides/llmobs/03_EVALUATION_METRIC_TYPES.md)

---

**Status**: ✅ **Production Ready**  
**Next Steps**: Monitor Datadog LLMObs dashboard for validation metrics and alerts

