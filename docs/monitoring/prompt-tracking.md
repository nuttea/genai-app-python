# Datadog LLM Observability - Prompt Tracking

Complete guide for using Datadog Prompt Tracking to monitor and optimize your LLM prompts.

## Overview

Datadog's [Prompt Tracking](https://docs.datadoghq.com/llm_observability/monitoring/prompt_tracking) enables you to:

✅ **Track all prompts** used by your application  
✅ **Compare versions** by performance, cost, and quality  
✅ **Monitor changes** with automatic versioning  
✅ **Reproduce issues** using Playground  
✅ **Optimize costs** by tracking token usage per prompt  

## Implementation

### Vote Extraction Service

We've implemented prompt tracking in the vote extraction service with the following metadata:

**Prompt ID**: `thai-election-form-extraction`

**Version Format**: `v{schema_version}-schema{hash}`
- Schema version: `1.0.0` (manual)
- Schema hash: Automatic (detects schema changes)
- Example: `v1.0.0-schema3a7f9b2c`

**Template**: The instruction prompt for Gemini

**Variables**:
- `num_pages` - Number of pages in document
- `model` - Gemini model used
- `schema_version` - Schema version
- `schema_hash` - Hash of schema structure
- `form_type` - Document type
- `temperature` - Model temperature
- `response_format` - JSON format

**Tags**:
- `feature: vote-extraction`
- `document_type: thai-election-form`
- `schema_version: 1.0.0`
- `model: gemini-2.5-flash`
- `language: thai`

### Code Example

```python
from ddtrace.llmobs import LLMObs

# Prompt metadata
prompt_metadata = {
    "id": "thai-election-form-extraction",
    "version": f"v{schema_version}-schema{schema_hash}",
    "template": prompt_text.strip(),
    "variables": {
        "num_pages": len(image_files),
        "model": "gemini-2.5-flash",
        "schema_version": schema_version,
        "schema_hash": schema_hash,
    },
    "tags": {
        "feature": "vote-extraction",
        "document_type": "thai-election-form",
    },
}

# Attach prompt metadata to LLM span
with LLMObs.annotation_context(prompt=prompt_metadata):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content_parts,
        config=config,
    )
```

## View Prompt Analytics in Datadog

### Access Prompt Tracking

1. Go to [LLM Observability](https://app.datadoghq.com/llm/home)
2. Click **"Prompts"** in the left sidebar
3. View your prompts dashboard

### Key Metrics

**Prompt Call Count**:
- Timeseries of calls per prompt/version
- Compare versions side-by-side

**Performance**:
- Average latency per prompt version
- Token usage (input/output)
- Cost per call

**Recent Updates**:
- Latest prompt versions
- Change history
- Diff between versions

**Most Tokens Used**:
- Prompts ranked by token consumption
- Identify expensive prompts

**Highest Latency**:
- Prompts ranked by duration
- Optimize slow prompts

### Prompt Detail View

Click any prompt to see:

**Version Activity**:
- All versions and their usage
- Performance comparison
- Token usage trends

**Diff View**:
- Compare two versions
- See what changed
- Understand impact

**Trace Explorer**:
- Filter by prompt version
- See all requests using this prompt
- Debug issues

**Playground**:
- Pre-populated with template and variables
- Test prompt variations
- Quick experimentation

## Schema Version Tracking

### Automatic Hash Detection

The schema hash automatically updates when you modify `ELECTION_FORM_SCHEMA`:

```python
schema_hash = str(hash(json.dumps(ELECTION_FORM_SCHEMA, sort_keys=True)))[:8]
```

**Benefits**:
- ✅ Detects schema changes automatically
- ✅ Links schema to prompt version
- ✅ Track performance by schema version
- ✅ A/B test schema variations

### Manual Version Updates

When making significant changes, increment the schema version:

```python
# In vote_extraction_service.py
schema_version = "1.1.0"  # Changed from 1.0.0
```

**When to increment**:
- Major schema changes (breaking)
- Adding/removing required fields
- Changing field types
- Updating validation rules

### Version Naming Convention

Format: `v{major}.{minor}.{patch}-schema{hash}`

**Examples**:
- `v1.0.0-schema3a7f9b2c` - Initial version
- `v1.1.0-schemab4e8c1d9` - Minor update (new optional field)
- `v2.0.0-schema7f2a3c4e` - Major update (breaking change)

## Using Prompt Tracking

### Compare Prompt Versions

In Datadog Prompts view:

1. Select a prompt (`thai-election-form-extraction`)
2. View all versions
3. Compare metrics:
   - Call count
   - Average latency
   - Token usage
   - Error rate

### Filter Traces by Prompt

In Trace Explorer:

```
@llm.prompt.id:thai-election-form-extraction
@llm.prompt.version:v1.0.0-schema3a7f9b2c
```

Find all requests using a specific prompt version.

### Reproduce Issues

1. Find a trace with an issue
2. Click the LLM span
3. Click "Open in Playground"
4. Playground pre-populates with:
   - Exact prompt template
   - Exact variables used
   - Same model settings
5. Test variations to fix the issue

### Monitor Prompt Performance

Create monitors for:

**High latency**:
```
avg(last_5m):avg:llm.request.duration{llm.prompt.id:thai-election-form-extraction} > 30s
```

**High token usage** (cost alert):
```
sum(last_1h):sum:llm.token.count{llm.prompt.id:thai-election-form-extraction} > 1000000
```

**Error rate**:
```
sum(last_5m):sum:llm.request.errors{llm.prompt.id:thai-election-form-extraction}.as_count() > 5
```

## Best Practices

### 1. Use Descriptive IDs

✅ Good:
```python
"id": "thai-election-form-extraction"
"id": "customer-support-greeting"
"id": "document-summarization"
```

❌ Bad:
```python
"id": "prompt1"
"id": "template"
"id": "test"
```

### 2. Include Schema in Version

✅ Good:
```python
"version": f"v{schema_version}-schema{schema_hash}"
```

This links prompt changes to schema changes.

### 3. Use Static Templates with Variables

✅ Good:
```python
"template": "Translate to {{lang}}: {{text}}",
"variables": {"lang": "fr", "text": user_input}
```

❌ Bad:
```python
"template": f"Translate to {lang}: {user_input}"  # Hard to track
```

### 4. Add Meaningful Tags

```python
"tags": {
    "feature": "vote-extraction",
    "document_type": "thai-election-form",
    "team": "data-extraction",
    "priority": "high",
}
```

### 5. Version Prompts Semantically

- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features
- **Patch** (1.0.0 → 1.0.1): Bug fixes

## Prompt Optimization Workflow

### 1. Identify Issues

In Datadog Prompts view:
- Find prompts with high latency
- Find prompts with high token usage
- Find prompts with high error rate

### 2. Analyze Traces

- Filter traces by prompt version
- Review successful vs failed requests
- Identify patterns

### 3. Test Variations

- Use Playground to test changes
- Try different:
  - Instruction wording
  - Example format
  - Temperature settings
  - Schema structure

### 4. Deploy New Version

```python
# Increment version
schema_version = "1.1.0"

# Deploy and monitor
# Compare v1.0.0 vs v1.1.0 in Datadog
```

### 5. A/B Test

Deploy both versions:
```python
import random

version = "1.0.0" if random.random() < 0.5 else "1.1.0"
prompt_metadata["version"] = f"v{version}-schema{hash}"
```

Compare results in Datadog.

## Troubleshooting

### Prompts Not Appearing in Datadog

**Check**:
1. ✅ LLMObs enabled: `DD_LLMOBS_ENABLED=1`
2. ✅ ML app set: `DD_LLMOBS_ML_APP=your-app`
3. ✅ ddtrace installed: `pip list | grep ddtrace`
4. ✅ Generating traffic to prompts

**Debug**:
```python
# Check if LLMObs is enabled
from ddtrace.llmobs import LLMObs
print(LLMObs._instance is not None)
```

### Prompt Metadata Not Attached

**Check**:
1. ✅ `LLMObs.annotation_context()` wraps the provider call
2. ✅ Context manager is directly before API call
3. ✅ Metadata format is correct

**Correct placement**:
```python
# ✅ Good - immediate before call
with LLMObs.annotation_context(prompt=metadata):
    response = client.generate()

# ❌ Bad - too far from call
with LLMObs.annotation_context(prompt=metadata):
    data = process_data()
    response = client.generate()  # Too far!
```

### Version Not Updating

**Check**:
1. ✅ Schema version incremented
2. ✅ Service redeployed
3. ✅ Cache cleared (if any)

**Force new version**:
```python
schema_version = "1.1.0"  # Increment
# Rebuild and redeploy
```

## Advanced: Schema Evolution Tracking

### Track Schema Changes

Every schema change automatically gets a new hash:

```python
# Original schema
ELECTION_FORM_SCHEMA = {
    "properties": {
        "form_info": {...},
        "ballot_statistics": {...},
        "vote_results": {...},
    }
}
# Hash: 3a7f9b2c

# After adding new field
ELECTION_FORM_SCHEMA = {
    "properties": {
        "form_info": {...},
        "ballot_statistics": {...},
        "vote_results": {...},
        "additional_notes": {...},  # NEW FIELD
    }
}
# Hash: b4e8c1d9  # Automatically different!
```

### Monitor Schema Impact

In Datadog, compare:
- `v1.0.0-schema3a7f9b2c` (before)
- `v1.0.0-schemab4e8c1d9` (after)

Metrics to check:
- Success rate
- Latency
- Token usage
- Error types

### Schema Validation in Logs

```python
logger.info(
    "Successfully extracted vote data",
    extra={
        "schema_version": schema_version,
        "schema_hash": schema_hash,
        "prompt_version": prompt_metadata["version"],
    }
)
```

## Example Queries

### Find All Calls to a Prompt

```
@llm.prompt.id:thai-election-form-extraction
```

### Compare Versions

```
@llm.prompt.id:thai-election-form-extraction
@llm.prompt.version:(v1.0.0* OR v1.1.0*)
```

### High Cost Prompts

```
@llm.prompt.id:thai-election-form-extraction
@llm.total_tokens:>10000
```

### Errors with Specific Prompt

```
@llm.prompt.id:thai-election-form-extraction
status:error
```

## Resources

- [Datadog Prompt Tracking Documentation](https://docs.datadoghq.com/llm_observability/monitoring/prompt_tracking)
- [LLM Observability Python SDK](https://docs.datadoghq.com/llm_observability/instrumentation/sdk/?tab=python)
- [LLM Observability Best Practices](https://docs.datadoghq.com/llm_observability/)

---

**Quick Start**: Prompt tracking is already implemented! Just enable LLMObs and view prompts at:
https://app.datadoghq.com/llm/prompts

