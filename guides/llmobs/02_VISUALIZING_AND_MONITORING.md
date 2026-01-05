# Part 02: Visualizing and Monitoring Our LLM Application

This guide shows how to use Datadog's visualization tools to monitor, debug, and optimize our Thai election vote extraction application.

## Overview

After instrumenting our application with LLMObs spans (Part 01), we can now:
- **Visualize** execution flow and timing
- **Debug** errors and performance issues
- **Monitor** LLM costs and quality
- **Optimize** based on real usage patterns

---

## Accessing LLM Observability in Datadog

### Navigate to LLMObs
1. Go to **APM → LLM Observability** in Datadog
2. Select your service: `vote-extractor`
3. Filter by environment: `DD_ENV=prod` or `DD_ENV=dev`

### Key Views
- **Traces**: Individual extraction requests
- **Analytics**: Aggregated metrics and trends
- **Experiments**: Model comparison results (covered separately)
- **Monitors**: Alerts for performance/errors

---

## Trace Visualization: Two Views

Datadog provides two complementary ways to visualize traces:

### 1. Span List View
Shows operations in **chronological order** with detailed metadata.

**Best for:**
- ✅ Reviewing step-by-step execution
- ✅ Inspecting input/output data
- ✅ Reading annotations and logs
- ✅ Following data transformations

**Example: Vote Extraction Trace**
```
extract_from_images (workflow)                              2.3s
├── _build_prompt_and_metadata (task)                     45ms
│   Input: { form_set_name: "บางบำหรุ5", num_images: 6 }
│   Output: { prompt_parts: [...], metadata: {...} }
│
├── _call_gemini_api (llm - auto-instrumented)           2.1s
│   Model: gemini-2.5-flash
│   Temperature: 0.0
│   Tokens: 16,384 (prompt: 12,000, completion: 4,384)
│   Cost: $0.05
│
├── _capture_workflow_span_context (task)                 5ms
│   Tags: { thinking_enabled: true, schema_version: "2024-01" }
│
└── Parse and validate response                          150ms
    Output: [ { form_type: "Constituency", ... }, { form_type: "PartyList", ... } ]
```

**Key Information Per Span:**
- **Duration**: How long it took
- **Input/Output**: Actual data processed
- **Metadata**: Custom annotations
- **Status**: Success, error, or timeout
- **Span Kind**: Visual icon (workflow, task, llm, etc.)

---

### 2. Flame Graph View
Shows operations as **horizontal bars** with color-coded hierarchy.

**Best for:**
- ✅ Identifying bottlenecks at a glance
- ✅ Spotting parallel operations
- ✅ Comparing relative time spent
- ✅ Understanding call relationships

**Example: Vote Extraction Flame Graph**
```
████████████████████████████████████████████████ extract_from_images (2.3s)
█ _build_prompt_and_metadata (45ms)
████████████████████████████████████ _call_gemini_api (2.1s) ← Bottleneck!
█ _capture_workflow_span_context (5ms)
██ Parse response (150ms)
```

**Color Coding:**
- 🟦 **Blue**: Workflow spans
- 🟩 **Green**: Task spans
- 🟨 **Yellow**: LLM spans
- 🟧 **Orange**: Tool/retrieval spans
- 🟥 **Red**: Error spans

**Width = Duration**: The wider the bar, the more time spent.

---

## Real-World Debugging Scenarios

### Scenario 1: Slow Extraction Performance

**Problem**: User reports that extracting บางบำหรุ5 takes >5 seconds.

**Investigation in Datadog:**

1. **Search for the trace:**
   ```
   service:vote-extractor @form_set_name:บางบำหรุ5 @duration:>5000
   ```

2. **Open Flame Graph:**
   ```
   ████████████████████████████████████████████████ extract_from_images (5.8s)
   █ _build_prompt_and_metadata (45ms)
   ███████████████████████████████████████ _call_gemini_api (5.5s) ← 95% of time!
   █ _capture_workflow_span_context (5ms)
   ██ Parse response (250ms)
   ```

3. **Click on `_call_gemini_api` span:**
   ```
   Model: gemini-2.5-flash
   Temperature: 0.0
   Max Tokens: 16,384
   Actual Tokens Used: 15,800 (near limit!)
   Thinking Budget: -1 (unlimited)
   Finish Reason: STOP
   ```

4. **Root Cause:**
   - Model is spending extra time on complex reasoning (thinking mode enabled)
   - Token usage is near the max_tokens limit
   - Images might have complex layouts

5. **Solution:**
   ```python
   # Adjust for this specific form set
   if form_set_name == "บางบำหรุ5":
       config = LLMConfig(
           model="gemini-2.5-flash",
           temperature=0.0,
           max_tokens=20000,  # Increase limit
           thinking_budget=1000,  # Cap thinking time
       )
   ```

6. **Verify Fix:**
   - Re-run extraction
   - Check new trace: `2.3s` ✅ (60% improvement!)

---

### Scenario 2: LLM Judge Returns 0.0 Score

**Problem**: Experiment shows LLM judge giving 0.0 scores for some forms.

**Investigation in Datadog:**

1. **Search for failing evaluations:**
   ```
   service:vote-extractor operation_name:llm_judge.evaluate @final_score:0.0
   ```

2. **Open Span List View:**
   ```
   llm_judge.evaluate                                       3.2s (ERROR)
   ├── llm_judge.initialize_client                        120ms
   ├── llm_judge.build_prompt                              10ms
   ├── llm_judge.api_call (attempt 1)                      1.0s
   │   finish_reason: N/A
   │   response_valid: false
   │   response_text: None
   ├── llm_judge.api_call (attempt 2)                      1.0s
   │   finish_reason: N/A
   │   response_valid: false
   │   response_text: None
   ├── llm_judge.api_call (attempt 3)                      1.0s
   │   finish_reason: N/A
   │   response_valid: false
   │   response_text: None
   └── llm_judge.parse_response                             5ms
       → Returned 0.0 (no valid response after 3 retries)
   ```

3. **Click on `llm_judge.api_call` (attempt 1):**
   ```
   Response Debug:
   - has_text: False
   - text_length: 0
   - finish_reason: N/A
   - candidates_count: 0
   - response_type: GenerateContentResponse
   
   Error: Empty response from API
   ```

4. **Check Logs:**
   ```
   2026-01-05 10:30:45 WARNING Empty response for บางบำหรุ5
   2026-01-05 10:30:46 WARNING Retrying in 1.0s... (attempt 1/3)
   2026-01-05 10:30:48 WARNING Retrying in 2.0s... (attempt 2/3)
   2026-01-05 10:30:51 ERROR Empty response after 3 attempts
   ```

5. **Root Cause:**
   - API returning empty responses (possibly rate limiting or timeout)
   - Retry logic is working but not solving the issue
   - May need different approach (different model, shorter prompt)

6. **Solution:**
   ```python
   # Add more debugging and fallback
   try:
       response = client.models.generate_content(...)
       
       if not response or not response.text:
           logger.warning(
               f"Empty response, trying with shorter prompt",
               extra={"form": form_set_name}
           )
           # Try with simplified prompt
           response = client.models.generate_content(
               model="gemini-2.5-flash",  # Faster model
               contents=short_prompt,
               config=simplified_config,
           )
   except Exception as e:
       # Fallback to rule-based evaluation
       return rule_based_evaluation(output_data, expected_output)
   ```

---

### Scenario 3: High Token Costs

**Problem**: Monthly LLM costs are increasing unexpectedly.

**Investigation in Datadog Analytics:**

1. **Token Usage Over Time:**
   ```
   service:vote-extractor operation_name:_call_gemini_api
   | stats sum(@tokens_used) by @model
   ```

   **Results:**
   ```
   gemini-2.5-flash:      1,250,000 tokens ($50)
   gemini-3-pro-preview:    850,000 tokens ($340) ← Expensive!
   ```

2. **Breakdown by Operation:**
   ```
   | stats avg(@tokens_used) by operation_name
   ```

   **Results:**
   ```
   extract_from_images:     15,000 tokens/call
   llm_judge.api_call:       8,000 tokens/call ← Using expensive model!
   ```

3. **Cost Analysis:**
   ```
   Daily Extractions:   100 forms × 15K tokens = 1.5M tokens
   Daily Evaluations:   100 evals × 8K tokens  = 0.8M tokens
   
   Monthly Cost:
   - Extractions: 45M tokens × $0.04/1M = $1.80
   - Evaluations: 24M tokens × $0.40/1M = $9.60 ← 84% of cost!
   ```

4. **Root Cause:**
   - LLM Judge using expensive `gemini-3-pro-preview`
   - Evaluating EVERY extraction (including duplicates)
   - Large prompts with full JSON dumps

5. **Optimizations:**
   ```python
   # 1. Use cheaper model for simple evaluations
   if evaluation_type == "simple":
       model = "gemini-2.5-flash"  # 10x cheaper
   else:
       model = "gemini-3-pro-preview"  # Only for complex cases
   
   # 2. Sample evaluations (not every extraction)
   if random.random() < 0.1:  # 10% sampling
       score = llm_judge_evaluator(...)
   
   # 3. Reduce prompt size
   # Instead of full JSON, send only diff
   diff = compute_diff(expected, actual)
   prompt = f"Evaluate differences: {diff}"  # Much shorter!
   ```

6. **Results After Optimization:**
   ```
   Monthly Cost: $1.80 + $0.96 = $2.76 (71% reduction!) ✅
   ```

---

## Monitoring Dashboards

### Create Custom Dashboard

**1. LLM Performance Dashboard**

**Widgets:**
- **Request Rate**: `count:vote-extractor.extract_from_images`
- **Avg Latency**: `avg:vote-extractor.extract_from_images.duration`
- **Error Rate**: `count:vote-extractor.extract_from_images{@error:true}`
- **Token Usage**: `sum:@tokens_used by @model`
- **Cost Estimate**: `sum:@tokens_used * cost_per_token`

**Query Examples:**
```
# Average extraction time by model
service:vote-extractor operation_name:extract_from_images
| stats avg(@duration) by @model

# P95 latency for extractions
service:vote-extractor operation_name:extract_from_images
| stats p95(@duration)

# Error rate over time
service:vote-extractor @error:true
| timeseries count() by operation_name
```

---

**2. LLM Judge Quality Dashboard**

**Widgets:**
- **Avg Score**: `avg:@final_score by @form_set_name`
- **Score Distribution**: Histogram of `@final_score`
- **Retry Rate**: `count:@attempt>1 / count:@attempt=1`
- **Empty Responses**: `count:@response_valid:false`

**Query Examples:**
```
# Forms with consistently low scores
service:vote-extractor operation_name:llm_judge.evaluate
| stats avg(@final_score) by @form_set_name
| where avg(@final_score) < 0.5

# Retry success rate
service:vote-extractor operation_name:llm_judge.api_call
| stats count() by @attempt, @response_valid

# Most common finish reasons
service:vote-extractor operation_name:llm_judge.api_call
| stats count() by @finish_reason
```

---

### Set Up Alerts

**1. High Latency Alert**
```yaml
Monitor Type: APM
Metric: avg:vote-extractor.extract_from_images.duration
Threshold: > 3000ms for 5 minutes
Alert: "@slack-alerts-channel High latency detected!"
```

**2. High Error Rate Alert**
```yaml
Monitor Type: APM
Metric: count:vote-extractor.extract_from_images{@error:true}
Threshold: > 5% for 10 minutes
Alert: "@pagerduty-oncall Extraction errors spiking!"
```

**3. LLM Judge Failures Alert**
```yaml
Monitor Type: APM
Metric: count:llm_judge.evaluate{@final_score:0.0}
Threshold: > 10 in 1 hour
Alert: "@team-ml LLM judge failing, check API status"
```

**4. High Cost Alert**
```yaml
Monitor Type: Custom
Metric: sum:@tokens_used by @model
Threshold: > 10M tokens/day
Alert: "@team-lead Daily token usage exceeds budget!"
```

---

## Advanced Trace Analysis

### Using Trace Search

**Find problematic patterns:**

```
# Long-running extractions
service:vote-extractor @duration:>5000

# Extractions with thinking enabled
service:vote-extractor @thinking_enabled:true

# High token usage
service:vote-extractor @tokens_used:>20000

# Specific form sets
service:vote-extractor @form_set_name:บางบำหรุ*

# Errors by type
service:vote-extractor @error.type:TimeoutError

# LLM judge with specific finish reasons
service:vote-extractor @finish_reason:SAFETY

# Successful evaluations with low scores
service:vote-extractor @final_score:[0.0 TO 0.5] -@error:true
```

### Correlate with APM Traces

**Link LLM operations to HTTP requests:**

1. **Find slow API requests:**
   ```
   service:fastapi-backend resource_name:POST_/api/v1/vote-extraction/extract @duration:>5000
   ```

2. **Click on trace → See full breakdown:**
   ```
   POST /api/v1/vote-extraction/extract               5.8s
   ├── Authentication                                 15ms
   ├── Rate limiting check                            5ms
   ├── extract_from_images (LLMObs workflow)         5.5s ← Our instrumented workflow!
   │   ├── _build_prompt_and_metadata                45ms
   │   ├── _call_gemini_api                          5.2s
   │   └── _capture_workflow_span_context            5ms
   ├── Response serialization                        200ms
   └── Datadog trace submission                      80ms
   ```

**Benefits:**
- 🔗 See LLM operations in context of full request
- 📊 Understand where time is spent end-to-end
- 🐛 Trace errors from HTTP → FastAPI → LLMObs → Gemini
- 📈 Optimize based on complete picture

---

### Correlate with RUM (Real User Monitoring)

**If you have Datadog RUM on your Streamlit frontend:**

1. **User clicks "Extract" button in Streamlit**
   - RUM captures user action
   - Session ID: `abc123`

2. **Frontend makes API call**
   - Request ID: `req-456`
   - Linked to RUM session

3. **Backend processes extraction**
   - APM trace ID: `trace-789`
   - Linked to request ID

4. **LLMObs workflow executes**
   - Workflow span ID: `span-101112`
   - Part of APM trace

**Query Across All Layers:**
```
# Find user sessions with slow extractions
@session.id:abc123 @duration:>5000

# Link RUM → APM → LLMObs
session_id:abc123 → request_id:req-456 → trace_id:trace-789 → span_id:span-101112
```

**Benefits:**
- 🔗 Connect user experience to backend performance
- 📊 See real user impact of LLM latency
- 🐛 Debug issues end-to-end (user click → LLM response)
- 📈 Optimize based on actual user behavior

---

## Best Practices for Visualization

### 1. Use Both Views Strategically
- **Flame Graph**: Quick overview, identify bottlenecks
- **Span List**: Detailed debugging, inspect data

### 2. Add Meaningful Annotations
```python
LLMObs.annotate(
    metadata={
        "form_type": "constituency",  # For filtering
        "extraction_version": "v2.1",  # Track changes
        "user_id": user.id,  # Correlate with users
    },
    tags={
        "experiment": "baseline",  # A/B testing
        "priority": "high",  # SLA tracking
    }
)
```

### 3. Set Up Saved Views
Create saved searches for common queries:
- "Slow Extractions (>3s)"
- "LLM Judge Failures"
- "High Token Usage (>20K)"
- "Production Errors"

### 4. Use Trace Sampling Intelligently
```python
# Sample traces based on importance
if is_production and not is_error:
    sample_rate = 0.1  # 10% sampling
else:
    sample_rate = 1.0  # Always trace errors and dev
```

---

## Key Metrics to Track

### Performance Metrics
| Metric | Goal | Alert Threshold |
|--------|------|-----------------|
| P50 Latency | < 2s | > 3s |
| P95 Latency | < 5s | > 10s |
| P99 Latency | < 10s | > 20s |
| Error Rate | < 1% | > 5% |

### Quality Metrics
| Metric | Goal | Alert Threshold |
|--------|------|-----------------|
| LLM Judge Avg Score | > 0.8 | < 0.6 |
| Empty Response Rate | < 1% | > 5% |
| Retry Success Rate | > 80% | < 50% |
| Validation Pass Rate | > 95% | < 90% |

### Cost Metrics
| Metric | Goal | Alert Threshold |
|--------|------|-----------------|
| Daily Token Usage | < 5M | > 10M |
| Cost per Extraction | < $0.05 | > $0.10 |
| Avg Tokens per Call | < 15K | > 25K |
| Monthly Cost | < $100 | > $200 |

---

## Troubleshooting Common Issues

### Issue: Traces Not Appearing
**Check:**
1. ✅ `DD_API_KEY` and `DD_APP_KEY` set
2. ✅ `LLMObs.enable()` called at startup
3. ✅ Service name matches: `vote-extractor`
4. ✅ Network connectivity to Datadog

### Issue: Missing Span Data
**Check:**
1. ✅ Decorators applied: `@workflow`, `@task`, etc.
2. ✅ `LLMObs.annotate()` called within span
3. ✅ Data serializable to JSON
4. ✅ Not hitting annotation size limits

### Issue: High Cardinality Tags
**Avoid:**
```python
# ❌ BAD: user_id has thousands of unique values
span.set_tag("user_id", user.id)

# ❌ BAD: timestamp creates infinite cardinality
span.set_tag("timestamp", datetime.now().isoformat())
```

**Instead:**
```python
# ✅ GOOD: Low cardinality categories
span.set_tag("user_tier", "premium")  # Only 3-4 values

# ✅ GOOD: Bucketed values
span.set_tag("hour_of_day", datetime.now().hour)  # Only 24 values
```

---

## Next Steps

Now that you understand instrumentation and visualization, explore:

- **[Experiments & Evaluations](../../docs/features/LLMOBS_EVALUATIONS.md)** - Compare models systematically
- **[Prompt Version Tracking](./sources/99_ADDITIONAL_TOPICS.md)** - Track prompt changes
- **[Agent Monitoring](./sources/99_ADDITIONAL_TOPICS.md)** - Monitor AI agent behavior
- **[Cost Optimization](../../docs/reference/COST_OPTIMIZATION.md)** - Reduce LLM costs

---

## Summary

### ✅ Visualization Tools
- **Span List**: Chronological, detailed view
- **Flame Graph**: Visual hierarchy, bottleneck identification
- **Dashboards**: Custom metrics and trends
- **Alerts**: Proactive monitoring

### ✅ Debugging Workflow
1. **Search** for problematic traces
2. **Visualize** with flame graphs
3. **Inspect** span details
4. **Correlate** with logs and APM
5. **Optimize** based on findings

### ✅ Monitoring Best Practices
- Track performance, quality, and cost metrics
- Set up alerts for critical thresholds
- Use both LLMObs and APM views
- Correlate with RUM for full picture

---

## Related Resources

- **Part 01**: [Instrumenting Our Application](./01_INSTRUMENTING_VOTE_EXTRACTION.md)
- **Source Material**: [Datadog LLMObs Docs](./sources/)
- **Implementation**: `services/fastapi-backend/app/services/`
- **Dashboards**: [Datadog LLMObs](https://app.datadoghq.com/llm/)

---

**Last Updated**: January 5, 2026

