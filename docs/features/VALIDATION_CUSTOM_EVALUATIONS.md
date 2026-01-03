# Validation as Custom Evaluations

## Overview

Vote extraction validation is now implemented as **Datadog LLMObs Custom Evaluations** instead of simple annotations. This provides better tracking, quantitative metrics, and structured analysis of validation quality in Datadog.

**Reference**: [Datadog External Evaluations Documentation](https://docs.datadoghq.com/llm_observability/evaluations/external_evaluations#submitting-external-evaluations-with-the-sdk)

### SDK Compatibility

**Important**: The Datadog LLMObs SDK supports **only TWO metric types**:
- `"score"` - Numeric values (0.0-1.0 recommended)
- `"categorical"` - String values (e.g., "pass", "fail", "excellent", "good")

❌ **Not supported**: `"boolean"` (even though the API might support it, the SDK does not)

### Additional Parameters

The SDK supports these optional parameters:
- `assessment` - String: `"pass"` or `"fail"` (provides standardized assessment field)
- `reasoning` - String: Explanation for the evaluation (supports analysis and debugging)
- `tags` - Dict: Additional context tags
- `timestamp_ms` - Integer: Unix timestamp in milliseconds (optional, defaults to current time)

## Architecture

### Before: Annotations Only
```python
# Old approach - just annotations
if validation_failed:
    LLMObs.annotate(
        output_data={"is_valid": False, "error": error_msg},
        tags={"validation_result": "failed"}
    )
```

❌ **Limitations**:
- No structured metrics
- Difficult to query validation patterns
- No aggregation or trends
- Mixed with other span metadata

### After: Custom Evaluations
```python
# New approach - custom evaluations
LLMObs.submit_evaluation(
    span={"span_id": span_id, "trace_id": trace_id},
    ml_app="vote-extractor",
    label="validation_passed",
    metric_type="boolean",
    value=is_valid,
    reasoning=error_msg or "All validation checks passed"
)
```

✅ **Benefits**:
- Structured evaluation metrics
- Easy to query and analyze
- Aggregation and trends available
- Separate from span metadata
- Standard evaluation patterns

## Evaluation Metrics

The validation submits **three custom evaluations** (two categorical, one score) for each validation check:

### 1. Categorical: Validation Passed/Failed
```python
LLMObs.submit_evaluation(
    label="validation_passed",
    metric_type="categorical",
    value="pass" or "fail",  # Overall pass/fail
    assessment="pass" or "fail",  # Optional assessment field
    reasoning="All validation checks passed" or error_msg
)
```

**Use Case**: Track overall validation success rate
**Query**: `@evaluations.validation_passed:pass|fail`

**Note**: The Datadog SDK only supports `"score"` and `"categorical"` metric types (not `"boolean"`). See [official documentation](https://docs.datadoghq.com/llm_observability/evaluations/external_evaluations#submitting-external-evaluations-with-the-sdk).

### 2. Categorical: Check Type
```python
LLMObs.submit_evaluation(
    label="validation_check_type",
    metric_type="categorical",
    value="ballot_statistics|vote_counts|vote_results|all_checks",
    assessment="pass" or "fail",  # Optional assessment field
    reasoning="Validated {check_type} successfully" or error_msg
)
```

**Use Case**: Identify which validation checks fail most often
**Query**: `@evaluations.validation_check_type:ballot_statistics`

### 3. Score: Validation Quality
```python
LLMObs.submit_evaluation(
    label="validation_score",
    metric_type="score",
    value=0.0 to 1.0,  # checks_passed / total_checks
    assessment="pass" or "fail",  # Optional assessment field
    reasoning=f"Passed {checks_passed}/{total_checks} validation checks"
)
```

**Use Case**: Measure validation quality over time
**Query**: `@evaluations.validation_score:<0.5` (partial failures)

## Validation Check Types

### 1. `ballot_statistics`
Validates that ballot counts are consistent:
```
ballots_used = good_ballots + bad_ballots + no_vote_ballots
```

**Fails when**:
- Missing required ballot counts (None values)
- Sum mismatch (ballots_used ≠ good + bad + no_vote)

**Evaluation**:
- `validation_passed`: `"fail"`
- `validation_check_type`: `"ballot_statistics"`
- `validation_score`: `< 1.0`

### 2. `vote_results`
Validates that vote results are present:
```
data.vote_results must not be empty
```

**Fails when**:
- No vote results extracted
- Empty vote_results list

**Evaluation**:
- `validation_passed`: `"fail"`
- `validation_check_type`: `"vote_results"`
- `validation_score`: `0.0`

### 3. `vote_counts`
Validates that all vote counts are non-negative:
```
all vote_count >= 0
```

**Fails when**:
- Any candidate/party has negative vote count

**Evaluation**:
- `validation_passed`: `"fail"`
- `validation_check_type`: `"vote_counts"`
- `validation_score`: `< 1.0`

### 4. `all_checks`
All validation checks passed:

**Success when**:
- All ballot statistics valid (or not present)
- Vote results present
- All vote counts non-negative

**Evaluation**:
- `validation_passed`: `"pass"`
- `validation_check_type`: `"all_checks"`
- `validation_score`: `1.0`

## Data Flow

```
1. User uploads election form images
   ↓
2. extract_from_images() workflow
   - Calls Gemini API
   - Extracts vote data
   - Returns result
   - ✅ Workflow span created
   ↓
3. Capture span context
   - span_id: "14484272564170044706"
   - trace_id: "140031489178122457..."
   ↓
4. _parse_extraction_results()
   - Parse ElectionFormData
   - Call validate_extraction(data, span_id, trace_id)
   ↓
5. validate_extraction()
   ├─ _validate_ballot_statistics()
   ├─ Validate vote results
   ├─ Validate vote counts
   └─ _submit_validation_evaluation()
       ├─ Submit boolean evaluation (passed/failed)
       ├─ Submit categorical evaluation (check type)
       └─ Submit score evaluation (quality)
   ↓
6. Custom Evaluations in Datadog LLMObs
   - Linked to extraction workflow span
   - Queryable and aggregatable
   - Visible in trace timeline
```

## Implementation Details

### Service Method Signature

```python
# services/fastapi-backend/app/services/vote_extraction_service.py

async def validate_extraction(
    self,
    data: ElectionFormData,
    span_id: str | None = None,
    trace_id: str | None = None,
) -> tuple[bool, str | None]:
    """
    Validate extracted vote data and submit Custom Evaluations.
    
    Args:
        data: Extracted election form data
        span_id: Span ID from extraction workflow
        trace_id: Trace ID from extraction workflow
    
    Returns:
        Tuple of (is_valid, error_message)
    """
```

### Endpoint Integration

```python
# services/fastapi-backend/app/api/v1/endpoints/vote_extraction.py

# 1. Extract vote data
result = await vote_extraction_service.extract_from_images(...)

# 2. Capture span context immediately after workflow
span_context = _get_span_context()
span_id = span_context.span_id if span_context else None
trace_id = span_context.trace_id if span_context else None

# 3. Parse and validate with span context
extracted_reports, warnings = await _parse_extraction_results(
    result=result,
    image_files_count=len(image_files),
    span_id=span_id,  # ← Pass to validation
    trace_id=trace_id,  # ← Pass to validation
)
```

### Evaluation Submission

```python
def _submit_validation_evaluation(
    self,
    span_id: str | None,
    trace_id: str | None,
    is_valid: bool,
    check_type: str,
    error_msg: str | None,
    validation_checks: list,
    data: ElectionFormData,
) -> None:
    """Submit validation result as Custom Evaluation."""
    
    if not span_id or not trace_id:
        logger.warning("Cannot submit evaluation: missing span context")
        return
    
    # Prepare span context
    span_context = {
        "span_id": span_id,
        "trace_id": trace_id,
    }
    
    # Submit 3 evaluations: boolean, categorical, score
    LLMObs.submit_evaluation(...)
```

## Datadog Queries

### Find Validation Failures
```
service:vote-extractor @evaluations.validation_passed:fail
```

### Find Specific Check Failures
```
service:vote-extractor @evaluations.validation_check_type:ballot_statistics @evaluations.validation_passed:fail
```

### Find Low-Quality Extractions
```
service:vote-extractor @evaluations.validation_score:<0.5
```

### Aggregate Validation Success Rate
```
service:vote-extractor
| stats count by @evaluations.validation_passed
```

### Analyze Check Type Distribution
```
service:vote-extractor @evaluations.validation_passed:fail
| stats count by @evaluations.validation_check_type
```

## Datadog Dashboards

### Recommended Widgets

#### 1. Validation Success Rate
```
Type: Timeseries
Query: service:vote-extractor @evaluations.validation_passed:*
Group by: @evaluations.validation_passed
```

#### 2. Failed Check Types
```
Type: Pie Chart
Query: service:vote-extractor @evaluations.validation_passed:fail
Group by: @evaluations.validation_check_type
```

#### 3. Validation Score Distribution
```
Type: Histogram
Query: service:vote-extractor @evaluations.validation_score:*
Metric: @evaluations.validation_score
```

#### 4. Validation Timeline
```
Type: Timeseries
Query: service:vote-extractor
Metrics: 
  - avg(@evaluations.validation_score)
  - count(@evaluations.validation_passed:pass)
  - count(@evaluations.validation_passed:fail)
```

## Monitoring & Alerts

### Alert: High Validation Failure Rate
```yaml
name: "Vote Extraction: High Validation Failure Rate"
query: |
  service:vote-extractor @evaluations.validation_passed:fail
threshold:
  warning: > 10 failures in 15 minutes
  critical: > 20 failures in 15 minutes
notification:
  - "@slack-team-ops"
  - "@pagerduty-on-call"
```

### Alert: Ballot Statistics Failures
```yaml
name: "Vote Extraction: Ballot Statistics Mismatch"
query: |
  service:vote-extractor 
  @evaluations.validation_check_type:ballot_statistics
  @evaluations.validation_passed:fail
threshold:
  warning: > 5 failures in 1 hour
notification:
  - "@slack-data-quality"
```

### Alert: Low Validation Score Trend
```yaml
name: "Vote Extraction: Declining Validation Quality"
query: |
  service:vote-extractor
  avg(@evaluations.validation_score)
threshold:
  warning: avg < 0.8 for 1 hour
  critical: avg < 0.6 for 30 minutes
notification:
  - "@slack-team-ops"
```

## Benefits

### 1. **Quantitative Metrics**
- Track validation success rate over time
- Identify trends in data quality
- Measure impact of model changes

### 2. **Structured Analysis**
- Query specific validation checks
- Aggregate failure patterns
- Correlate with other metrics

### 3. **Better Debugging**
- See validation results in trace timeline
- Link evaluations to specific extractions
- Understand failure context

### 4. **Proactive Monitoring**
- Set alerts on validation failures
- Track quality degradation
- Automated incident detection

### 5. **Product Insights**
- Understand which forms are problematic
- Identify common extraction issues
- Guide model improvements

## Migration from Annotations

### Before (Annotations)
```python
# Old code - just tags and metadata
LLMObs.annotate(
    output_data={"is_valid": False, "error": error_msg},
    tags={"validation_result": "failed"}
)
```

### After (Custom Evaluations)
```python
# New code - structured evaluations
_submit_validation_evaluation(
    span_id=span_id,
    trace_id=trace_id,
    is_valid=False,
    check_type="ballot_statistics",
    error_msg=error_msg,
    validation_checks=validation_checks,
    data=data,
)
```

### Changes Required

1. ✅ Add `span_id` and `trace_id` parameters to `validate_extraction`
2. ✅ Capture span context after workflow completes
3. ✅ Pass span context to validation methods
4. ✅ Replace `LLMObs.annotate` with `LLMObs.submit_evaluation`
5. ✅ Submit multiple evaluation types (boolean, categorical, score)
6. ✅ Remove old `_annotate_validation_failure` helper

## Testing

### 1. Manual Test
```bash
# Upload a test form via Streamlit
# Check Datadog LLMObs for evaluations
```

### 2. Check Logs
```bash
docker-compose logs fastapi-backend --tail 50 | grep "validation evaluation"
```

Expected output:
```
✅ Submitted validation evaluation: ballot_statistics (passed=false, score=0.67)
✅ Submitted validation evaluation: all_checks (passed=true, score=1.00)
```

### 3. Query Datadog
```
service:vote-extractor @evaluations.validation_passed:*
```

Expected: See evaluation events linked to extraction spans

## Related Documentation

- [Vote Extraction LLMObs Spans](./VOTE_EXTRACTION_LLMOBS_SPANS.md)
- [User Feedback Implementation](./USER_FEEDBACK_LLMOBS_IMPLEMENTATION_SUMMARY.md)
- [Evaluation Metric Types Guide](../../guides/llmobs/03_EVALUATION_METRIC_TYPES.md)
- [LLMObs Instrumentation Guide](../../guides/llmobs/sources/01_INSTRUMENTING_SPANS.md)

## Key Takeaways

✅ **Validation as Custom Evaluations**: Better than annotations for tracking quality  
✅ **Three Metric Types**: Boolean (pass/fail), Categorical (check type), Score (quality)  
✅ **Linked to Workflow**: Span context connects evaluations to extractions  
✅ **Queryable & Aggregatable**: Standard evaluation patterns in Datadog  
✅ **Proactive Monitoring**: Alerts on validation failures and quality trends  

This approach provides **comprehensive validation tracking** while maintaining the simplicity of the validation logic! 🎯

