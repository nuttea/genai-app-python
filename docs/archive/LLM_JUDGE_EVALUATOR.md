# 🤖 LLM-as-Judge Evaluator - Gemini 3 Pro Preview

**Advanced quality assessment using LLM to evaluate extraction outputs**

---

## 📖 Overview

Added a powerful **LLM-as-Judge evaluator** that uses `gemini-3-pro-preview` to provide detailed, holistic quality assessment of vote extraction outputs. This evaluator complements rule-based evaluators by providing nuanced evaluation with detailed reasoning.

---

## 🎯 Why LLM-as-Judge?

### Traditional Evaluators (Rule-Based)
- ✅ Fast and deterministic
- ✅ Easy to debug
- ❌ Limited to specific field comparisons
- ❌ Miss contextual errors
- ❌ No holistic assessment

### LLM-as-Judge (AI-Powered)
- ✅ Holistic quality assessment
- ✅ Detects contextual errors
- ✅ Provides detailed reasoning
- ✅ Identifies subtle issues
- ✅ Human-like evaluation
- ⚠️ Slower (API call per evaluation)
- ⚠️ Requires API key

---

## 🔧 Implementation

### Function Signature

```python
def llm_judge_evaluator(
    input_data: Dict, 
    output_data: Dict, 
    expected_output: Dict
) -> float:
    """
    LLM-as-Judge evaluator using gemini-3-pro-preview.
    
    Args:
        input_data: Original input (form_set_name, image_paths)
        output_data: Model extraction output
        expected_output: Ground truth data
    
    Returns:
        float: Quality score between 0.0 and 1.0
    """
```

### Evaluation Process

1. **Build Comprehensive Prompt** - Includes:
   - Context (form set name, task description)
   - Model output (extracted data)
   - Ground truth (expected output)
   - Evaluation criteria (4 dimensions)
   - Scoring rubric (0.0 to 1.0)

2. **Call Gemini 3 Pro Preview**
   - Model: `gemini-3-pro-preview` (most capable)
   - Temperature: `0.0` (deterministic)
   - Response format: JSON
   - Max tokens: `4096` (detailed reasoning)

3. **Parse Structured Response**
   ```json
   {
     "score": 0.85,
     "reasoning": "The extraction is very accurate...",
     "errors": [
       {
         "field": "vote_results[5].vote_count",
         "expected": "232",
         "actual": "223",
         "severity": "major"
       }
     ],
     "summary": "Very good quality with minor vote count discrepancies"
   }
   ```

4. **Log Detailed Results** - See [Logging](#-logging-output) section

5. **Return Score** - Float between 0.0 and 1.0

---

## 📊 Evaluation Dimensions

The LLM judge evaluates across 4 key dimensions:

### 1. Form Information (Header Data)
- Date, location, polling station
- Province, district, sub-district
- Constituency and unit numbers

### 2. Voter Statistics
- Eligible voters count
- Voters present count

### 3. Ballot Statistics
- Ballots allocated, used, remaining
- Good ballots, bad ballots, no-vote ballots

### 4. Vote Results
- Candidate numbers and names
- Vote counts (numeric)
- Vote counts (text in Thai)
- Party names

---

## 📏 Scoring Rubric

| Score | Category | Description |
|-------|----------|-------------|
| **1.0** | Perfect | All data 100% correct |
| **0.8-0.9** | Very Good | Minor errors, mostly correct |
| **0.6-0.7** | Good | Some errors, generally accurate |
| **0.4-0.5** | Fair | Many errors, partially correct |
| **0.0-0.3** | Poor | Mostly incorrect |

---

## 📝 Logging Output

### Comprehensive Evaluation Log

```json
{
  "timestamp": "2026-01-04 12:50:00,123",
  "level": "INFO",
  "logger": "app.services.experiments_service",
  "message": "LLM Judge Evaluation - บางบำหรุ9",
  "llm_judge": {
    "form_set_name": "บางบำหรุ9",
    "score": 0.85,
    "summary": "Very good quality with minor vote count discrepancies",
    "reasoning": "The extraction shows high accuracy across all dimensions. Form information is perfect, voter statistics match exactly, ballot statistics are accurate. However, there are 2 vote count errors out of 16 candidates (87.5% accuracy). The errors are in candidates 5 and 12 where the vote counts are off by small margins.",
    "error_count": 2,
    "errors": [
      {
        "field": "vote_results[5].vote_count",
        "expected": "232",
        "actual": "223",
        "severity": "major"
      },
      {
        "field": "vote_results[12].vote_count",
        "expected": "5",
        "actual": "4",
        "severity": "minor"
      }
    ],
    "judge_model": "gemini-3-pro-preview"
  }
}
```

### Individual Error Logs

```json
{
  "timestamp": "2026-01-04 12:50:00,124",
  "level": "WARNING",
  "logger": "app.services.experiments_service",
  "message": "LLM Judge Error - บางบำหรุ9: vote_results[5].vote_count",
  "llm_judge_error": {
    "form_set_name": "บางบำหรุ9",
    "field": "vote_results[5].vote_count",
    "expected": "232",
    "actual": "223",
    "severity": "major"
  }
}
```

### Quality Level Summary

```
# Excellent (score >= 0.8)
INFO: LLM Judge: บางบำหรุ9 - Excellent quality (score=0.85): Very good quality with minor vote count discrepancies

# Good (0.6 <= score < 0.8)
INFO: LLM Judge: บางบำหรุ10 - Good quality (score=0.70): Good extraction with some ballot statistics errors

# Fair (0.4 <= score < 0.6)
WARNING: LLM Judge: บางบำหรุ11 - Fair quality (score=0.55): Fair extraction with multiple errors in vote results

# Poor (score < 0.4)
ERROR: LLM Judge: บางบำหรุ12 - Poor quality (score=0.30): Poor extraction with significant errors across all sections
```

---

## 🔗 Integration with Experiments

### Added to Evaluator List

```python
# In experiments_service.py
evaluators = [
    exact_form_match,           # Rule-based: Exact form info match
    ballot_accuracy_score,      # Rule-based: Ballot statistics accuracy
    vote_results_quality,       # Rule-based: Vote counts accuracy
    has_no_errors,              # Rule-based: No errors in output
    llm_judge_evaluator,        # 🆕 LLM-as-Judge: Holistic quality
]
```

### Updated Overall Accuracy

```python
def overall_accuracy(...):
    """Weighted average including LLM judge."""
    score = (
        result.get("exact_form_match", 0) * 0.15       # 15%
        + result.get("ballot_accuracy_score", 0) * 0.25  # 25%
        + result.get("vote_results_quality", 0) * 0.30   # 30%
        + result.get("llm_judge_evaluator", 0.5) * 0.30  # 30% (NEW!)
    )
```

**Rationale:**
- LLM judge gets **30% weight** (highest)
- Provides holistic assessment beyond individual metrics
- Complements rule-based evaluators

### New Summary Evaluator

```python
def avg_llm_judge_score(...):
    """Average LLM judge quality score across all records."""
    return sum(r.get("llm_judge_evaluator", 0.5) for r in evaluators_results) / len(evaluators_results)
```

---

## 🚀 Usage

### Prerequisites

1. **GCP Configuration** (already configured in your project)
   - Uses **Vertex AI** with Application Default Credentials
   - Same authentication as main extraction service
   - Requires `GOOGLE_CLOUD_PROJECT` environment variable (already set)
   - Uses `VERTEX_AI_LOCATION` (default: `us-central1`)

2. **No Additional API Keys Required!**
   - ✅ Uses same GCP auth as rest of the application
   - ✅ No need for separate `GEMINI_API_KEY`
   - ✅ Works automatically if extraction service works

### Run Experiments (Automatic)

The LLM judge evaluator runs **automatically** in all experiments!

**Via Streamlit UI:**
```
1. Go to: http://localhost:8501
2. Navigate to: 🧪 Run Experiments
3. Configure experiment
4. Click "Run Experiments"
5. LLM judge will evaluate each record automatically! ✅
```

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [
      {"model": "gemini-2.5-flash", "temperature": 0.0}
    ],
    "sample_size": 2
  }'
```

**Note:** LLM judge uses Vertex AI automatically - no additional setup required!

### Check Logs

**View LLM Judge Evaluations:**
```bash
# All LLM judge logs
docker logs genai-fastapi-backend | grep "LLM Judge"

# Specific form
docker logs genai-fastapi-backend | grep "LLM Judge: บางบำหรุ9"

# Errors only
docker logs genai-fastapi-backend | grep "LLM Judge Error"

# JSON formatted
docker logs genai-fastapi-backend --tail 100 | jq 'select(.llm_judge != null)'
```

---

## 📊 Example Output in Datadog

### Experiment Results

In Datadog LLMObs experiments, you'll see:

**Per-Record Metrics:**
- `exact_form_match`: 1.0 (perfect)
- `ballot_accuracy_score`: 1.0 (perfect)
- `vote_results_quality`: 0.875 (14/16 correct)
- `has_no_errors`: true
- **`llm_judge_evaluator`: 0.85** ⭐ (very good)

**Summary Metrics:**
- `overall_accuracy`: 0.88 (weighted average)
- `success_rate`: 1.0 (no errors)
- `avg_ballot_accuracy`: 1.0
- **`avg_llm_judge_score`: 0.82** ⭐ (average quality)

---

## ⚠️ Error Handling

### Missing GCP Project

```python
if not project_id:
    logger.warning("LLM Judge: GOOGLE_CLOUD_PROJECT not set, skipping evaluation")
    return 0.0  # Cannot evaluate
```

**Result:** Evaluation continues with score 0.0 (if GCP not configured)

### JSON Parse Error

```python
except json.JSONDecodeError as e:
    logger.error(f"LLM Judge: Failed to parse JSON response: {e}")
    return 0.0  # Score 0 on parse error
```

**Result:** Logged error with raw response, score 0.0 returned

### Vertex AI Error

```python
except Exception as e:
    logger.error(f"LLM Judge: Error evaluating: {e}", exc_info=True)
    return 0.0  # Score 0 on error
```

**Result:** Full stack trace logged, score 0.0 returned

---

## 🎯 Benefits

### For Development
- ✅ **Identify subtle issues** rule-based evaluators miss
- ✅ **Understand why** extractions fail
- ✅ **Prioritize fixes** based on error severity
- ✅ **Validate improvements** with holistic scores

### For Production Monitoring
- ✅ **Track overall quality** trends over time
- ✅ **Detect degradation** early
- ✅ **Alert on quality drops** (avg score < threshold)
- ✅ **Investigate failures** with detailed reasoning

### For Model Comparison
- ✅ **Compare models** beyond accuracy metrics
- ✅ **Assess trade-offs** (speed vs quality)
- ✅ **Choose best model** for production

---

## 💰 Cost Considerations

### Gemini 3 Pro Preview Pricing
- **Input**: ~$2.50 per 1M tokens
- **Output**: ~$10.00 per 1M tokens

### Typical Evaluation
- **Input**: ~2,000 tokens (dataset record + prompt)
- **Output**: ~500 tokens (evaluation + reasoning)
- **Cost per evaluation**: ~$0.01

### For 100 Records
- **Total cost**: ~$1.00
- **Time**: ~5-10 minutes (parallel execution)

**Recommendation:**
- ✅ Use for experiments (offline evaluation)
- ⚠️ Consider cost for large-scale production monitoring
- 💡 Can be disabled by not setting `GEMINI_API_KEY`

---

## 🔧 Configuration

### Enable/Disable

**Enable (default):**
```bash
# Already configured! Uses same GCP settings as main app
export GOOGLE_CLOUD_PROJECT="your-gcp-project"  # Already set
export VERTEX_AI_LOCATION="us-central1"        # Already set
```

**Disable:**
```bash
# Cannot disable without breaking main extraction service
# LLM judge uses same Vertex AI configuration
```

**If GCP not configured:**
- LLM judge returns 0.0 (no score)
- Warning logged: "GOOGLE_CLOUD_PROJECT not set, skipping evaluation"
- Other evaluators continue normally

### Adjust Weights

To change the importance of LLM judge in overall accuracy, edit `overall_accuracy()` in `experiments_service.py`:

```python
# Current (LLM judge = 30%)
score = (
    result.get("exact_form_match", 0) * 0.15
    + result.get("ballot_accuracy_score", 0) * 0.25
    + result.get("vote_results_quality", 0) * 0.30
    + result.get("llm_judge_evaluator", 0.5) * 0.30  # ← Change this
)

# Example: Increase to 40%
score = (
    result.get("exact_form_match", 0) * 0.10
    + result.get("ballot_accuracy_score", 0) * 0.25
    + result.get("vote_results_quality", 0) * 0.25
    + result.get("llm_judge_evaluator", 0.5) * 0.40  # Higher weight!
)
```

---

## 📚 Related Documentation

- **Experiments**: `RUN_EXPERIMENTS_IMPLEMENTATION.md`
- **Complete Fix**: `EXPERIMENTS_COMPLETE_FIX.md`
- **Tracing**: `DATADOG_TRACING_BEST_PRACTICES.md`
- **LLMObs**: `guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md`

---

## 🎓 Best Practices

### 1. Review Logs Regularly
```bash
# Check quality trends
docker logs genai-fastapi-backend | grep "LLM Judge.*score=" | tail -20

# Investigate low scores
docker logs genai-fastapi-backend | grep "Poor quality"
```

### 2. Use for Debugging
- When an experiment shows low accuracy, check LLM judge reasoning
- Identifies root causes faster than manual review

### 3. Compare with Rule-Based
- If LLM judge score differs significantly from rule-based metrics, investigate
- May indicate contextual issues

### 4. Monitor Costs
```bash
# Count evaluations
docker logs genai-fastapi-backend | grep "LLM Judge: Evaluating" | wc -l

# Estimate cost: count * $0.01
```

---

## ✅ Summary

**Added:**
- ✅ `llm_judge_evaluator()` - Gemini 3 Pro Preview quality assessment
- ✅ `avg_llm_judge_score()` - Summary metric for LLM judge scores
- ✅ Updated `overall_accuracy()` - Includes LLM judge (30% weight)
- ✅ Comprehensive structured logging
- ✅ Error-by-error detailed logging
- ✅ Graceful error handling

**Benefits:**
- 🎯 Holistic quality assessment
- 📝 Detailed reasoning in logs
- 🔍 Identifies subtle errors
- 📊 Complements rule-based evaluators
- 🚀 Automatic in all experiments

**Cost:**
- 💰 ~$0.01 per evaluation
- ⏱️ ~3-5 seconds per evaluation
- ⚠️ Optional (disabled if no API key)

---

**LLM-as-Judge evaluator ready!** Use it to gain deeper insights into extraction quality! 🤖✨

