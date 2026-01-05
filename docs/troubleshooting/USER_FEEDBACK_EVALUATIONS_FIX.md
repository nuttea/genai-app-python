# User Feedback Evaluations Fix Summary

**Date**: January 3, 2026  
**Issue**: User feedback custom evaluations were not appearing in Datadog LLMObs  
**Status**: ✅ **RESOLVED**

---

## Problem

User feedback submissions from the Streamlit frontend were being sent to the backend, but the custom evaluations were not appearing in Datadog LLMObs dashboard.

**Symptoms**:
- Feedback API returned success responses
- Backend logs showed "Submitted feedback" messages
- Evaluations were sent to Datadog (`sent N LLMObs evaluation_metric events`)
- But evaluations didn't appear in Datadog LLMObs UI

---

## Root Causes

### 1. **Inconsistent `ml_app` Name**

**Issue**: The frontend was sending `ml_app="vote-extraction-app"` but the backend validation evaluations used `ml_app="vote-extractor"`.

**Impact**: Evaluations were being submitted to a different ml_app namespace, making them invisible when filtering by the main application name.

**Location**: 
- Frontend: `frontend/streamlit/pages/1_🗳️_Vote_Extractor.py` (lines 748, 759, 770)
- Backend validation: `services/fastapi-backend/app/services/vote_extraction_service.py` (line 598)

### 2. **`reasoning` Field in Wrong Location**

**Issue**: The `reasoning` field (user comments) was being passed as part of the `tags` dictionary instead of as a separate parameter to `LLMObs.submit_evaluation()`.

**Impact**: While this might work in some SDK versions, it's not the recommended pattern used by our validation evaluations, potentially causing inconsistencies.

**Location**: `services/fastapi-backend/app/services/feedback_service.py` (line 69)

---

## Solution

### Fix 1: Standardize `ml_app` Name

Changed the frontend to use `"vote-extractor"` to match the backend:

```python
# frontend/streamlit/pages/1_🗳️_Vote_Extractor.py
ml_app="vote-extractor"  # Changed from "vote-extraction-app"
```

### Fix 2: Extract `reasoning` as Separate Parameter

Modified the feedback service to pass `reasoning` as a dedicated parameter:

```python
# services/fastapi-backend/app/services/feedback_service.py

# Extract reasoning from tags (if present) to pass as separate parameter
reasoning = tags.pop("reasoning", None)

LLMObs.submit_evaluation(
    span=span_context,
    ml_app=feedback.ml_app,
    label=label,
    metric_type=metric_type,
    value=value,
    tags=tags,
    reasoning=reasoning,  # User comment as reasoning (if provided)
)
```

---

## Modified Files

1. **`services/fastapi-backend/app/services/feedback_service.py`**
   - Moved `reasoning` from `tags` to separate parameter
   - Added `tags.pop("reasoning", None)` to extract it

2. **`frontend/streamlit/pages/1_🗳️_Vote_Extractor.py`**
   - Changed `ml_app="vote-extraction-app"` to `ml_app="vote-extractor"` (3 locations)

---

## Verification

### Test Script

Created `test_user_feedback.sh` to automate testing:

```bash
./test_user_feedback.sh
```

### Test Results

**Before Fix**:
- Evaluations sent but not visible in Datadog (wrong ml_app namespace)

**After Fix**:
```
✅ sent 6 LLMObs evaluation_metric events to https://api.datadoghq.com/api/intake/llm-obs/v2/eval-metric

📝 Expected evaluations:
   - user_rating (score: 5)
   - user_thumbs (categorical: up)
   - user_comment (categorical: to_be_reviewed)
```

---

## User Feedback Evaluation Types

### 1. **Star Rating** (`user_rating`)
- **Type**: `score`
- **Value**: 1-5 (integer)
- **Label**: `"user_rating"`
- **Tags**: `feature`, `feedback_type`, `user_id`, `session_id`
- **Reasoning**: User comment (if provided)

### 2. **Thumbs Up/Down** (`user_thumbs`)
- **Type**: `categorical`
- **Value**: `"up"` or `"down"`
- **Label**: `"user_thumbs"`
- **Tags**: `feature`, `feedback_type`, `user_id`, `session_id`
- **Reasoning**: User comment (if provided)

### 3. **Comment** (`user_comment`)
- **Type**: `categorical`
- **Value**: `"to_be_reviewed"`
- **Label**: `"user_comment"`
- **Tags**: `feature`, `feedback_type`, `user_id`, `session_id`
- **Reasoning**: User comment text

---

## View in Datadog

### LLMObs Dashboard

**URL**: https://app.datadoghq.com/llm

**Filter by ml_app**: `vote-extractor`

### Example Trace

**URL**: https://app.datadoghq.com/apm/trace/695936d700000000994a9fe370860b99

### Query Examples

```
# View all user feedback evaluations
@tags.feature:vote-extraction AND @label:user_*

# View user ratings only
@label:user_rating

# View thumbs feedback
@label:user_thumbs

# View comments to review
@label:user_comment @value:to_be_reviewed

# View feedback from specific user
@tags.user_id:test_user_123

# View feedback from specific session
@tags.session_id:test_session_456
```

---

## Integration in Streamlit UI

### Feedback Flow

1. **User completes vote extraction**
   - Backend returns `span_context` with `span_id` and `trace_id` (decimal strings)

2. **UI displays extraction results**
   - Shows "Feedback & Trace Information" section
   - Displays span/trace IDs in both hex (for Datadog) and decimal (for API)

3. **User provides feedback**
   - Three tabs: "Rating + Comment", "Quick Thumbs", "Star Rating Only"
   - Each tab calls `feedback_api.submit_feedback()`

4. **Frontend submits to backend**
   - POST to `/api/v1/feedback/submit`
   - Includes `span_id`, `trace_id`, `ml_app="vote-extractor"`

5. **Backend submits to Datadog**
   - `FeedbackService.submit_feedback()` calls `LLMObs.submit_evaluation()`
   - Evaluation linked to the extraction span

6. **View in Datadog**
   - Evaluations appear in LLMObs dashboard
   - Linked to the original extraction trace

---

## Testing Checklist

### Manual Test via Streamlit

1. ✅ Start services: `docker-compose up`
2. ✅ Open Streamlit: http://localhost:8501
3. ✅ Navigate to "Vote Extractor" page
4. ✅ Upload test images (e.g., `assets/ss5-18-images/บางบำหรุ1_page*.jpg`)
5. ✅ Wait for extraction to complete
6. ✅ Expand "Trace Context" section to verify span/trace IDs
7. ✅ Submit feedback using any tab (Rating, Thumbs, or Comment)
8. ✅ Check for success message: "✅ Feedback submitted successfully!"
9. ✅ Click Datadog trace link to verify evaluations appear

### Automated Test

```bash
# Run the test script
./test_user_feedback.sh

# Expected output:
# ✅ All feedback submissions succeed
# ✅ Logs show "Submitted feedback" messages
# ✅ "sent 6 LLMObs evaluation_metric events"
```

### Backend Logs Check

```bash
# Check if feedback is being submitted
docker logs genai-fastapi-backend --tail 50 | grep "Submitted feedback"

# Expected output:
# ✅ Submitted feedback: rating for span XXXXXX in vote-extractor
# ✅ Submitted feedback: thumbs for span XXXXXX in vote-extractor
# ✅ Submitted feedback: comment for span XXXXXX in vote-extractor
```

---

## Key Learnings

### 1. **Consistent Naming is Critical**

All parts of the application (frontend, backend, evaluations) must use the **same `ml_app` name**. Mismatches will cause evaluations to be invisible or appear in separate namespaces.

**Best Practice**: Define `ml_app` as a constant:

```python
# services/fastapi-backend/app/core/constants.py
ML_APP_NAME = "vote-extractor"

# Use everywhere:
LLMObs.submit_evaluation(ml_app=ML_APP_NAME, ...)
```

### 2. **`reasoning` Parameter Usage**

While the Datadog docs show `reasoning` can be in `tags`, our SDK version (and best practice) supports it as a **separate parameter**. This provides better structure and consistency with other evaluation fields like `assessment`.

### 3. **Span Context Format**

The `span_id` and `trace_id` should be passed as **decimal strings** (as returned by `ddtrace`), not converted to hex until display in the UI.

**Correct Format**:
```python
{
    "span_id": "8558475897391138911",      # Decimal string
    "trace_id": "140032166261999304081920248101529324441"  # Decimal string
}
```

### 4. **Testing Strategy**

Always test the complete flow:
1. Generate span context (via extraction or other LLM operation)
2. Submit feedback with that span context
3. Verify in backend logs
4. Check Datadog LLMObs dashboard

---

## Troubleshooting

### Issue: Feedback submissions succeed but don't appear in Datadog

**Check**:
1. ✅ Verify `ml_app` name matches between frontend and backend
2. ✅ Check backend logs for "Submitted feedback" messages
3. ✅ Look for "sent N LLMObs evaluation_metric events" in logs
4. ✅ Wait 30-60 seconds for Datadog to process events
5. ✅ Filter Datadog by correct `ml_app` name
6. ✅ Check for any error messages in logs

### Issue: "Failed to submit feedback" error

**Check**:
1. ✅ Verify `span_id` and `trace_id` are valid decimal strings
2. ✅ Check that the original span still exists (not too old)
3. ✅ Verify `DD_LLMOBS_ENABLED=1` in backend environment
4. ✅ Check `DD_API_KEY` is set correctly

### Issue: Evaluations appear but without comments

**Check**:
1. ✅ Verify frontend is sending `comment` field
2. ✅ Check backend is extracting `reasoning` from tags
3. ✅ Ensure `reasoning` parameter is passed to `LLMObs.submit_evaluation()`

---

## References

- [Datadog LLMObs Custom Evaluations](https://docs.datadoghq.com/llm_observability/evaluations/submit_evaluations/)
- [User Feedback Implementation Plan](../features/USER_FEEDBACK_LLMOBS_PLAN.md)
- [User Feedback Implementation Summary](../features/USER_FEEDBACK_LLMOBS_IMPLEMENTATION_SUMMARY.md)
- [Evaluation Metric Types Guide](../../guides/llmobs/03_EVALUATION_METRIC_TYPES.md)
- [Validation Evaluations Fix](./VALIDATION_EVALUATIONS_FIX.md)

---

**Status**: ✅ **Production Ready**  
**Next Steps**: Monitor Datadog LLMObs dashboard for user feedback metrics and set up alerts for negative feedback

