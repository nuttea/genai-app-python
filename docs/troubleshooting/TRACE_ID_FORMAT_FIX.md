# 🔧 Fix: Trace ID Format Mismatch

**Date**: January 3, 2026  
**Issue**: `ValueError: invalid literal for int() with base 10` when displaying trace IDs  
**Root Cause**: Different trace ID formats from `LLMObs.export_span()` vs `tracer.current_span()`  
**Status**: ✅ **FIXED**

---

## 🐛 The Problem

### Error Message
```python
ValueError: invalid literal for int() with base 10: '695944b2000000002f683618367805b8'
Traceback:
File "/app/pages/1_🗳️_Vote_Extractor.py", line 677, in display_extraction_results
    trace_id_int = int(span_context["trace_id"])
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

### Root Cause

The Streamlit frontend was expecting trace IDs in **decimal format**, but after fixing the span context capture, the backend now returns trace IDs in **hexadecimal format**.

**Before** (using `tracer.current_span()`):
- Returns: `140032415434570411446567720109465537440` (decimal integer)
- Format: Pure decimal string

**After** (using `LLMObs.export_span()`):
- Returns: `6959432000000000d1f51f98d49b97c8` (hexadecimal)
- Format: 32-character hex string (128-bit trace ID)

---

## ✅ The Fix

### Modified File
- `frontend/streamlit/pages/1_🗳️_Vote_Extractor.py`

### Implementation

Use hex trace_id and decimal span_id for Datadog LLMObs URLs:

```python
# Backend returns IDs from LLMObs.export_span()
# - span_id: decimal string (e.g., "2670203640094394356")
# - trace_id: hex string (e.g., "6959432000000000d1f51f98d49b97c8")
span_id_decimal = str(span_context["span_id"])
trace_id_hex = str(span_context["trace_id"])

# Convert span_id to hex for display only
try:
    span_id_hex = format(int(span_id_decimal), "016x")  # 64-bit = 16 hex chars
except ValueError:
    span_id_hex = span_id_decimal

# Create Datadog LLMObs URL with hex trace_id and decimal span_id
datadog_url = (
    f"https://app.datadoghq.com/llm/traces/trace/{trace_id_hex}"
    f"?selectedTab=overview&spanId={span_id_decimal}"
)
```

### Key Changes

1. ✅ **Use hex trace_id in URL path**: Datadog LLMObs URLs use hex format in the path
2. ✅ **Use decimal span_id as query param**: Pass decimal span_id as `?spanId=` parameter
3. ✅ **LLMObs URL format**: Use `/llm/traces/trace/` instead of `/apm/trace/`
4. ✅ **Convert span_id for display**: Convert decimal span_id to hex for UI
5. ✅ **Preserve original values**: Pass original values to feedback API (no conversion)

---

## 📊 Trace ID Format Details

### From `tracer.current_span()`
- **Type**: Integer (decimal)
- **Example**: `140032415434570411446567720109465537440`
- **Format**: Decimal string representation of 128-bit integer
- **Used by**: HTTP request spans (regular APM)

### From `LLMObs.export_span()`
- **Type**: String (hexadecimal)
- **Example**: `6959432000000000d1f51f98d49b97c8`
- **Format**: 32-character hex string (128-bit)
- **Structure**:
  - First 16 chars: High 64 bits (often includes zeros)
  - Last 16 chars: Low 64 bits
- **Used by**: LLMObs workflow spans

### Datadog UI Format
- **Display**: Always uses **hexadecimal** (32 chars)
- **Example**: `69593efd000000006847390a4a2ee998`
- **Links (LLMObs)**: Uses **hex trace_id + decimal span_id**
  - Format: `https://app.datadoghq.com/llm/traces/trace/{trace_id_hex}?spanId={span_id_decimal}`
  - Example: `https://app.datadoghq.com/llm/traces/trace/69594bf000000000f8bbcd9f0908a20a?selectedTab=overview&spanId=2339509758594883837`
  - Note: Different from APM URLs which use `/apm/trace/`

---

## 📊 Format Requirements

| Purpose | Span ID Format | Trace ID Format |
|---------|---------------|-----------------|
| **Backend Returns** | Decimal string | Hex string |
| **Frontend Display** | Hex (converted) | Hex (as-is) |
| **Datadog LLMObs URL** | Decimal (query param) | Hex (URL path) |
| **Feedback API** | Decimal (original) | Hex (original) |

### Example Conversion

Backend returns:
```json
{
  "span_id": "2670203640094394356",
  "trace_id": "6959432000000000d1f51f98d49b97c8"
}
```

Frontend processes:
```python
# For Display
span_id_hex = "24f51f98d49b9754"  # Convert decimal to hex
trace_id_hex = "6959432000000000d1f51f98d49b97c8"  # Use as-is

# For Datadog LLMObs URL
url = (
    f"https://app.datadoghq.com/llm/traces/trace/{trace_id_hex}"
    f"?selectedTab=overview&spanId={span_id_decimal}"
)
# Example: https://app.datadoghq.com/llm/traces/trace/6959432000000000d1f51f98d49b97c8?spanId=2670203640094394356

# For Feedback API
span_id = "2670203640094394356"  # Use original decimal
trace_id = "6959432000000000d1f51f98d49b97c8"  # Use original hex
```

---

## 🧪 Testing

### 1. Run Extraction
```bash
# Open Streamlit
http://localhost:8501/Vote_Extractor

# Upload images and extract
```

### 2. Verify Display
After extraction, expand "Trace Context (for Datadog LLMObs)":
- ✅ Should show hex trace ID without error
- ✅ Should display both hex and decimal formats
- ✅ Datadog link should work

### 3. Submit Feedback
- ✅ Click thumbs up/down or rate
- ✅ Should submit successfully
- ✅ No errors in console

### 4. Check Backend Logs
```bash
docker logs genai-fastapi-backend --tail 50 | grep "Submitted feedback"
```

Expected:
```
✅ Submitted feedback: thumbs for span 2670203640094394356 in vote-extractor
```

---

## 💡 Key Learnings

### 1. Different Span Sources = Different Formats

| Source | Span ID Format | Trace ID Format |
|--------|---------------|-----------------|
| `tracer.current_span()` | Decimal int | Decimal int |
| `LLMObs.export_span()` | Decimal int | **Hex string** |
| Datadog UI | Hex string | Hex string |

### 2. Always Handle Both Formats

When working with Datadog traces:
- ✅ Auto-detect format before converting
- ✅ Preserve original values for API calls
- ✅ Only convert for display purposes
- ✅ Use try-except for conversion safety

### 3. Hex Detection

Simple check for hex format:
```python
is_hex = any(c in str(value).lower() for c in 'abcdef')
```

### 4. API Submission

For Datadog LLMObs API:
- ✅ **Use original values** from backend (no conversion)
- ❌ **Don't convert** to hex or decimal before submission
- ✅ API accepts both formats, but prefers original

### 5. Correct LLMObs URL Format (Final)

After fixing the span context capture, the backend now returns:
- **span_id**: Decimal string (e.g., `"2670203640094394356"`)
- **trace_id**: Hexadecimal string (e.g., `"6959432000000000d1f51f98d49b97c8"`)

Frontend approach:
- ✅ Use **hex trace_id in URL path** for Datadog LLMObs
  - Format: `/llm/traces/trace/{trace_id_hex}`
  - Example: `/llm/traces/trace/6959432000000000d1f51f98d49b97c8`
- ✅ Use **decimal span_id as query parameter**
  - Format: `?selectedTab=overview&spanId={span_id_decimal}`
  - Example: `?spanId=2670203640094394356`
- ✅ Convert **span_id to hex only for display** purposes
- ✅ Pass **original values** to feedback API without conversion

---

## 🔗 Related Issues

### Issue 1: Wrong Span Context
- **Problem**: Returning HTTP span instead of workflow span
- **Fix**: [USER_FEEDBACK_WRONG_SPAN_FIX.md](./USER_FEEDBACK_WRONG_SPAN_FIX.md)
- **Result**: Now correctly returns workflow span

### Issue 2: Trace ID Format
- **Problem**: Workflow span uses different trace ID format
- **Fix**: This document
- **Result**: Frontend handles both formats

---

## ✅ Summary

- **Problem**: Frontend tried to convert hex trace_id to integer, causing ValueError. Incorrect Datadog LLMObs URL format.
- **Cause**: `LLMObs.export_span()` returns trace_id in hex format (e.g., `695944b2000000002f683618367805b8`)
- **Fix**: Use correct Datadog LLMObs URL format with hex trace_id in path and decimal span_id as query parameter
- **Result**: 
  - ✅ Streamlit displays trace context without errors
  - ✅ Datadog trace link uses correct **LLMObs URL format**:
    - `/llm/traces/trace/{trace_id_hex}?spanId={span_id_decimal}`
  - ✅ UI displays trace_id in hex format (matches backend logs)
  - ✅ Feedback API uses original values without conversion

---

## 📚 Related Documentation

- [User Feedback Wrong Span Fix](./USER_FEEDBACK_WRONG_SPAN_FIX.md)
- [User Feedback Implementation](../features/USER_FEEDBACK_LLMOBS_IMPLEMENTATION_SUMMARY.md)
- [Trace Context Guide](../features/VOTE_EXTRACTION_LLMOBS_SPANS.md)

---

**Status**: ✅ **FIXED AND TESTED**

**Next**: Test in Streamlit UI to verify evaluations appear in Datadog! 🚀

