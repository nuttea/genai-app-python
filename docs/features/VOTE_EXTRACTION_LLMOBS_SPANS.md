# Vote Extraction - Datadog LLMObs Span Annotations

**Status**: ✅ Implemented  
**Date**: January 3, 2025

## Overview

This document describes the comprehensive Datadog LLM Observability (LLMObs) span annotations implemented for the Vote Extraction service. The implementation follows Datadog's best practices for instrumenting LLM applications with proper span kinds, input/output tracking, metadata, metrics, and tags.

## Span Architecture

The Vote Extraction service uses two primary span types:

### 1. Workflow Span - `extract_from_images`
**Type**: `@workflow`  
**Purpose**: Orchestrates the complete vote extraction process from Thai election form images.

### 2. Task Span - `validate_extraction`
**Type**: `@task`  
**Purpose**: Validates extracted data for consistency and correctness.

## Detailed Span Annotations

### Workflow Span: `extract_from_images`

This span represents the main extraction workflow that processes multiple election form images using Gemini's multimodal capabilities.

#### Input Data Captured

```python
{
    "images_count": 3,                          # Number of images processed
    "filenames": [                              # Original filenames for reference
        "form_page1.jpg",
        "form_page2.jpg",
        "form_page3.jpg"
    ],
    "prompt_template": "You are an expert...", # Truncated prompt (200 chars)
    "schema_version": "1.0.0",                  # Schema version for tracking
    "schema_hash": "a7f3b2e1"                   # Hash of schema structure
}
```

#### Output Data Captured

```python
{
    "forms_extracted": 2,                       # Number of forms extracted
    "result_type": "list",                      # Type of result (list/dict)
    "result_keys": [                            # Keys in extracted data
        "form_info",
        "voter_statistics",
        "ballot_statistics",
        "vote_results"
    ]
}
```

#### Metadata Captured

```python
{
    "model": "gemini-2.5-flash",               # LLM model used
    "provider": "vertex_ai",                   # LLM provider
    "temperature": 0.0,                        # Temperature setting
    "max_tokens": 16384,                       # Max output tokens
    "top_p": 0.95,                             # Top-p sampling
    "top_k": 40,                               # Top-k sampling
    "response_mime_type": "application/json",   # Response format
    "prompt_id": "thai-election-form-extraction", # Prompt identifier
    "prompt_version": "v1.0.0-schemaa7f3b2e1", # Full prompt version
    "schema_version": "1.0.0"                  # Data schema version
}
```

#### Metrics Captured

```python
{
    "input_tokens": 874,                       # Approx input tokens (258 per image + 100 for text)
    "output_tokens": 1024,                     # Approx output tokens (~4 chars per token)
    "total_tokens": 1898,                      # Total tokens used
    "pages_processed": 3,                      # Number of pages processed
    "forms_extracted": 2,                      # Forms successfully extracted
    "response_length": 4096                    # Character count of response
}
```

#### Tags Captured

```python
{
    "feature": "vote-extraction",               # Feature identifier
    "document_type": "thai-election-form",      # Document type
    "form_standard": "Form S.S. 5/18",          # Thai election form standard
    "language": "thai",                         # Document language
    "model": "gemini-2.5-flash",                # Model used
    "provider": "vertex_ai",                    # Provider used
    "schema_version": "1.0.0",                  # Schema version
    "multimodal": "true",                       # Multimodal input flag
    "extraction_success": "true"                # Success flag
}
```

#### Error Annotations

The workflow span captures detailed error context when extraction fails:

##### Parse Error (Invalid JSON Response)

```python
LLMObs.annotate(
    output_data={
        "error": "Invalid JSON response",
        "error_details": "Expecting value: line 1 column 1 (char 0)"
    },
    tags={
        "extraction_success": "false",
        "error_type": "ParseError"
    }
)
```

##### Unexpected Error

```python
LLMObs.annotate(
    output_data={
        "error": "Unexpected error",
        "error_details": "Connection timeout"
    },
    tags={
        "extraction_success": "false",
        "error_type": "TimeoutError"
    }
)
```

### Task Span: `validate_extraction`

This span performs standalone validation of extracted election form data.

#### Input Data Captured (Success Case)

```python
{
    "form_info": {
        "form_type": "Constituency",           # Constituency or PartyList
        "province": "กรุงเทพมหานคร"            # Province name (Thai)
    },
    "vote_results_count": 45,                  # Number of vote result entries
    "has_ballot_statistics": true             # Whether ballot stats present
}
```

#### Output Data Captured (Success Case)

```python
{
    "is_valid": true,                          # Overall validation result
    "validation_checks": [                     # List of all checks performed
        {"check": "ballot_statistics", "passed": true},
        {"check": "vote_counts", "passed": true}
    ],
    "checks_passed": 2,                        # Number of checks passed
    "total_checks": 2                          # Total number of checks
}
```

#### Input Data Captured (Failure Case - Ballot Mismatch)

```python
{
    "ballots_used": 1000,                      # Reported ballots used
    "good_ballots": 950,                       # Good ballots
    "bad_ballots": 30,                         # Bad ballots
    "no_vote_ballots": 15                      # No vote ballots (sum = 995)
}
```

#### Output Data Captured (Failure Case)

```python
{
    "is_valid": false,
    "error": "Ballot mismatch: ballots_used (1000) != sum of good+bad+no_vote (995)",
    "validation_checks": [
        {
            "check": "ballot_statistics",
            "passed": false,
            "error": "Ballot mismatch: ballots_used (1000) != sum of good+bad+no_vote (995)"
        }
    ]
}
```

#### Metrics Captured

```python
{
    "vote_results_count": 45,                  # Number of vote results
    "checks_passed": 2,                        # Number of checks passed
    "total_checks": 2                          # Total checks performed
}
```

#### Tags Captured

```python
{
    "validation_result": "passed",             # "passed" or "failed"
    "feature": "vote-extraction",              # Feature identifier
    "form_type": "Constituency",               # Form type validated
    "check_type": "ballot_statistics"          # Specific check type (on failures)
}
```

## Code Implementation

### Decorator Usage

```python
from ddtrace.llmobs.decorators import task, workflow
from ddtrace.llmobs import LLMObs

@workflow
async def extract_from_images(
    self,
    image_files: list[bytes],
    image_filenames: list[str],
    llm_config: Optional["LLMConfig"] = None,
) -> dict[str, Any] | None:
    """Extract vote data from multiple document pages using Gemini."""
    # ... extraction logic ...
    
    # Annotate with success context
    LLMObs.annotate(
        input_data={...},
        output_data={...},
        metadata={...},
        metrics={...},
        tags={...}
    )
    
    return result

@task
async def validate_extraction(
    self,
    data: ElectionFormData,
) -> tuple[bool, str | None]:
    """Validate extracted vote data for consistency."""
    # ... validation logic ...
    
    # Annotate with validation results
    LLMObs.annotate(
        input_data={...},
        output_data={...},
        metrics={...},
        tags={...}
    )
    
    return is_valid, error_message
```

### No-Op Decorators for Environments Without ddtrace

```python
try:
    from ddtrace.llmobs import LLMObs
    from ddtrace.llmobs.decorators import task, workflow
    DDTRACE_AVAILABLE = True
except ImportError:
    DDTRACE_AVAILABLE = False
    
    # Define no-op decorators if ddtrace is not available
    def workflow(func):
        """No-op workflow decorator when ddtrace is not available."""
        return func

    def task(func):
        """No-op task decorator when ddtrace is not available."""
        return func
```

## Benefits of Span Annotations

### 1. Complete Observability
- **Full trace visibility**: See the entire extraction workflow from image processing to validation
- **Input/output tracking**: Know exactly what went in and what came out for every operation
- **Error context**: Detailed error information for debugging failures

### 2. Performance Insights
- **Token usage**: Track approximate token consumption for cost analysis
- **Processing metrics**: Monitor pages processed, forms extracted, response sizes
- **Validation metrics**: Track validation check success rates

### 3. Debugging Capabilities
- **Prompt tracking**: Know which prompt version was used for each extraction
- **Schema versioning**: Track which schema version was active
- **Validation failures**: Identify specific validation checks that failed with context

### 4. Business Intelligence
- **Form type distribution**: See breakdown of Constituency vs PartyList forms
- **Document languages**: Track which languages are being processed
- **Success rates**: Monitor extraction and validation success rates by tags

## Usage Patterns

### Filtering Traces by Feature

```
feature:vote-extraction
```

### Finding Failed Extractions

```
feature:vote-extraction extraction_success:false
```

### Tracking Specific Document Types

```
document_type:thai-election-form form_standard:"Form S.S. 5/18"
```

### Monitoring Validation Failures

```
validation_result:failed check_type:ballot_statistics
```

### Finding Multimodal Operations

```
multimodal:true
```

## Metrics Analysis

### Average Token Usage per Extraction

Query: `avg:llmobs.span.metrics.total_tokens{feature:vote-extraction} by {model}`

### Forms Extracted Over Time

Query: `sum:llmobs.span.metrics.forms_extracted{feature:vote-extraction}`

### Validation Success Rate

Query: `(sum:llmobs.span.count{validation_result:passed} / sum:llmobs.span.count{feature:vote-extraction,span.kind:task}) * 100`

## Code Quality Improvements

### Refactoring for Maintainability

The implementation includes several helper methods to keep the main functions clean:

1. **`_process_images_to_content_parts`**: Handles image processing logic
2. **`_annotate_extraction_success`**: Centralizes successful extraction annotations
3. **`_annotate_validation_failure`**: Centralizes validation failure annotations
4. **`_validate_ballot_statistics`**: Separate ballot validation logic

### Linter Compliance

All Datadog Static Analysis (DDSA) linter errors were fixed:

- ✅ **DDSA-60211743**: Too many nesting levels (fixed by extracting helper methods)
- ✅ **DDSA-49089457**: Too many nested ifs (fixed with early returns and guard clauses)
- ✅ **DDSA-59679240**: Function exceeds 200 lines (fixed by extracting logic to helpers)

## Best Practices Followed

### 1. Semantic Span Kinds
- **Workflow** for orchestrating sequences
- **Task** for standalone validation logic
- Clear separation of concerns

### 2. Comprehensive Annotations
- Input data: What went into the operation
- Output data: What came out of the operation
- Metadata: Configuration and context
- Metrics: Quantitative measurements
- Tags: Categorical data for filtering

### 3. Error Handling
- Error annotations for all failure paths
- Detailed error context in output_data
- Error type tags for categorization

### 4. Cost Tracking
- Approximate token usage for multimodal operations
- Page/form counts for volume metrics
- Response size tracking

### 5. Version Tracking
- Schema version and hash in annotations
- Prompt ID and version for reproducibility
- Model and provider tracking

## Future Enhancements

### 1. Add Tool Spans
- Annotate database lookups with `@tool`
- Track external API calls

### 2. Add LLM Spans
- If using custom LLM implementations
- Track specific LLM calls separately

### 3. Enhanced Metrics
- Add cost estimates based on actual token pricing
- Track processing time per page
- Add quality scores for extracted data

### 4. Custom Evaluations
- Implement LLMObs evaluations for extraction quality
- Track accuracy metrics against ground truth
- Monitor model drift over time

## Related Documentation

- **[Datadog LLM Observability Terms](https://docs.datadoghq.com/llm_observability/terms/)** - Official span types documentation
- **[Datadog LLM Observability SDK - Python](https://docs.datadoghq.com/llm_observability/setup/sdk/python/)** - Python SDK reference
- **[guides/llmobs/sources/01_INSTRUMENTING_SPANS.md](../../guides/llmobs/sources/01_INSTRUMENTING_SPANS.md)** - Instrumentation guide
- **[services/fastapi-backend/app/services/vote_extraction_service.py](../../services/fastapi-backend/app/services/vote_extraction_service.py)** - Implementation

## Testing

To test the span annotations:

1. **Enable LLMObs** (if not already enabled):
   ```bash
   export DD_LLMOBS_ENABLED=1
   export DD_LLMOBS_ML_APP=vote-extraction-app
   export DD_API_KEY=your_api_key
   export DD_LLMOBS_AGENTLESS_ENABLED=1
   ```

2. **Run vote extraction**:
   ```bash
   # Submit a vote extraction request via API or frontend
   ```

3. **View spans in Datadog**:
   - Navigate to APM → LLM Observability
   - Filter by `feature:vote-extraction`
   - Inspect traces to see annotations

4. **Verify annotations**:
   - Check that input_data contains images_count, filenames, prompt_template
   - Check that output_data contains forms_extracted, result_type
   - Check that metadata contains model config
   - Check that metrics contains token counts
   - Check that tags are properly set

## Summary

The Vote Extraction service now has comprehensive Datadog LLMObs span annotations that provide:

✅ **Complete observability** of the extraction workflow  
✅ **Detailed input/output tracking** for debugging  
✅ **Token usage metrics** for cost analysis  
✅ **Validation insights** with granular check results  
✅ **Error tracking** with contextual annotations  
✅ **Clean, maintainable code** that passes all linter checks  

This implementation follows Datadog's best practices and serves as a reference for instrumenting other LLM-powered features in the application.

