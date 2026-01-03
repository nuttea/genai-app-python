# Guide: Evaluation Metric Types in Datadog LLM Observability

**Version**: 1.0  
**Last Updated**: January 2026  
**Audience**: Backend developers, ML engineers, data scientists

---

## Table of Contents

1. [Overview](#overview)
2. [Understanding Metric Types](#understanding-metric-types)
3. [Score Metric Type](#score-metric-type)
4. [Categorical Metric Type](#categorical-metric-type)
5. [Common Evaluation Labels](#common-evaluation-labels)
6. [Choosing the Right Metric Type](#choosing-the-right-metric-type)
7. [Implementation Examples](#implementation-examples)
8. [Best Practices](#best-practices)
9. [Visualization and Monitoring](#visualization-and-monitoring)
10. [Common Patterns and Anti-Patterns](#common-patterns-and-anti-patterns)

---

## Overview

Datadog LLM Observability (LLMObs) allows you to attach **custom evaluations** to your LLM spans, enabling you to track quality, safety, and performance metrics for your AI applications. Understanding the different **metric types** is crucial for properly monitoring and improving your LLM systems.

### What are Evaluation Metrics?

Evaluation metrics in LLMObs are structured data points that assess various aspects of your LLM's behavior:

- **Quality Metrics**: Accuracy, relevance, coherence
- **Safety Metrics**: Toxicity, bias, PII detection
- **Performance Metrics**: Latency, token count, cost
- **User Metrics**: Satisfaction ratings, feedback, engagement

### Why Use Custom Evaluations?

Custom evaluations allow you to:

✅ Track model quality over time  
✅ Detect degradation or drift  
✅ Compare different models or prompts  
✅ Correlate user feedback with model behavior  
✅ Set up automated alerts for quality issues  
✅ Build comprehensive evaluation dashboards

---

## Understanding Metric Types

Datadog LLMObs supports **two primary metric types** for evaluations:

| Metric Type | Data Type | Use Case | Example Values |
|-------------|-----------|----------|----------------|
| **`score`** | Numeric (float/int) | Quantitative measurements, ratings, continuous metrics | `0.95`, `4`, `3.5`, `0.0` |
| **`categorical`** | String (label) | Qualitative classifications, discrete states | `"pass"`, `"fail"`, `"relevant"`, `"toxic"` |

### Quick Decision Tree

```
Is your evaluation result a number?
│
├─ YES → Use `score`
│   └─ Examples: ratings (1-5), probabilities (0-1), latency (ms)
│
└─ NO → Use `categorical`
    └─ Examples: pass/fail, detected/not_detected, classes
```

---

## Score Metric Type

### Definition

The **`score`** metric type is used for **numeric evaluations** where the result is a measurable quantity. Scores can represent:

- **Ratings**: User satisfaction (1-5 stars)
- **Probabilities**: Confidence scores (0.0-1.0)
- **Measurements**: Latency in milliseconds, token count
- **Percentages**: Accuracy (0-100%), similarity (0-100%)
- **Arbitrary scales**: Quality scores, custom metrics

### Characteristics

| Property | Details |
|----------|---------|
| **Field Name** | `score_value` (API), `value` (Python SDK) |
| **Data Type** | `float` or `int` |
| **Range** | No enforced limits (define your own) |
| **Aggregations** | Average, min, max, percentiles, sum |
| **Alerts** | Threshold-based (e.g., `< 0.8`, `> 100ms`) |

### Common Score Scales

#### 1. **Probability Scale (0.0 - 1.0)**

Best for: Confidence scores, relevance scores, accuracy percentages

```python
# Example: Relevance score
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="relevance_score",
    metric_type="score",
    value=0.87  # 87% relevant
)
```

**Interpretation**:
- `0.0`: Completely irrelevant/incorrect
- `0.5`: Neutral/uncertain
- `1.0`: Highly relevant/correct

#### 2. **Star Rating Scale (1 - 5)**

Best for: User feedback, satisfaction ratings

```python
# Example: User satisfaction
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="user_satisfaction",
    metric_type="score",
    value=4,  # 4 out of 5 stars
    tags={"feedback_source": "user_rating"}
)
```

**Interpretation**:
- `1`: Very dissatisfied
- `2`: Dissatisfied
- `3`: Neutral
- `4`: Satisfied
- `5`: Very satisfied

#### 3. **Percentage Scale (0 - 100)**

Best for: Accuracy, precision, recall metrics

```python
# Example: Answer accuracy
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="answer_accuracy",
    metric_type="score",
    value=92.5  # 92.5% accurate
)
```

#### 4. **Custom Scales**

Define your own scales based on your domain:

```python
# Example: Quality score (0-10)
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="content_quality",
    metric_type="score",
    value=8.3,  # 8.3 out of 10
    tags={"scale": "0-10"}
)
```

### Score Metric Use Cases

| Use Case | Label | Scale | Description |
|----------|-------|-------|-------------|
| **User Feedback** | `user_rating` | 1-5 | Star ratings from users |
| **Relevance** | `relevance_score` | 0-1 | How relevant is the response |
| **Accuracy** | `accuracy_score` | 0-1 or 0-100 | Correctness of extracted data |
| **Latency** | `response_latency` | milliseconds | Time to generate response |
| **Cost** | `request_cost` | dollars | Cost per request |
| **Confidence** | `model_confidence` | 0-1 | Model's confidence in output |
| **Similarity** | `similarity_score` | 0-1 | Semantic similarity to reference |
| **Coherence** | `coherence_score` | 0-1 | Logical flow of response |

### Python SDK Example (Score)

```python
from ddtrace.llmobs import LLMObs

def evaluate_response_quality(response: str, expected: str) -> float:
    """Calculate quality score (simplified example)."""
    # Your evaluation logic here
    return 0.85  # 85% quality

# Submit score evaluation
LLMObs.submit_evaluation(
    span_context={"span_id": "abc123", "trace_id": "xyz789"},
    ml_app="vote-extraction-app",
    label="extraction_accuracy",
    metric_type="score",
    value=evaluate_response_quality(response, expected),
    tags={
        "evaluator": "custom_metric",
        "version": "v1.0"
    }
)
```

### API Example (Score)

```json
POST /api/v2/llm_observability/evaluations
{
  "data": {
    "type": "evaluation_metric",
    "attributes": {
      "metrics": [
        {
          "span_id": "abc123",
          "trace_id": "xyz789",
          "ml_app": "vote-extraction-app",
          "timestamp_ms": 1704067200000,
          "metric_type": "score",
          "label": "extraction_accuracy",
          "score_value": 0.85,
          "tags": {
            "evaluator": "custom_metric",
            "version": "v1.0"
          }
        }
      ]
    }
  }
}
```

---

## Categorical Metric Type

### Definition

The **`categorical`** metric type is used for **discrete, non-numeric classifications** where the result is one of a predefined set of labels or categories. Categorical values represent:

- **Binary classifications**: Pass/Fail, Yes/No, Detected/Not Detected
- **Multi-class labels**: Good/Neutral/Bad, High/Medium/Low
- **Status indicators**: Safe/Unsafe, Relevant/Irrelevant
- **Custom categories**: Domain-specific classifications

### Characteristics

| Property | Details |
|----------|---------|
| **Field Name** | `categorical_value` (API), `value` (Python SDK) |
| **Data Type** | `string` |
| **Values** | Any string (recommend standardized set) |
| **Aggregations** | Count, distribution, percentages by category |
| **Alerts** | Count-based (e.g., `"fail" > 10` occurrences) |

### Common Categorical Patterns

#### 1. **Binary Classification**

Best for: Pass/fail checks, detection tasks

```python
# Example: Toxicity detection
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="toxicity_check",
    metric_type="categorical",
    value="safe"  # or "unsafe"
)
```

**Standard values**: `"pass"`, `"fail"`, `"yes"`, `"no"`, `"detected"`, `"not_detected"`, `"safe"`, `"unsafe"`

#### 2. **Tri-State Classification**

Best for: Sentiment, quality levels

```python
# Example: Response quality
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="response_quality",
    metric_type="categorical",
    value="good"  # "good", "neutral", or "bad"
)
```

**Standard values**: `"good"`, `"neutral"`, `"bad"`, `"high"`, `"medium"`, `"low"`, `"positive"`, `"neutral"`, `"negative"`

#### 3. **Multi-Class Classification**

Best for: Named entity recognition, intent classification

```python
# Example: User intent
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="user_intent",
    metric_type="categorical",
    value="question"  # question, command, statement, etc.
)
```

#### 4. **Status Indicators**

Best for: Workflow states, result types

```python
# Example: Extraction result
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="vote-extraction-app",
    label="extraction_status",
    metric_type="categorical",
    value="success"  # success, partial, failed
)
```

### Categorical Metric Use Cases

| Use Case | Label | Categories | Description |
|----------|-------|------------|-------------|
| **Toxicity** | `toxicity_check` | `safe`, `unsafe` | Content safety detection |
| **Bias** | `bias_detection` | `detected`, `not_detected` | Bias presence check |
| **Hallucination** | `hallucination_check` | `grounded`, `hallucinated` | Factuality verification |
| **Relevance** | `relevance_check` | `relevant`, `irrelevant` | Response relevance |
| **PII Detection** | `pii_check` | `present`, `absent` | Personal info detection |
| **Sentiment** | `sentiment` | `positive`, `neutral`, `negative` | Response sentiment |
| **Intent** | `user_intent` | `question`, `command`, `statement` | User request type |
| **Completeness** | `response_completeness` | `complete`, `partial`, `incomplete` | Answer completeness |

### Python SDK Example (Categorical)

```python
from ddtrace.llmobs import LLMObs

def check_toxicity(text: str) -> str:
    """Check if text contains toxic content (simplified)."""
    # Your toxicity detection logic here
    return "safe"  # or "unsafe"

# Submit categorical evaluation
LLMObs.submit_evaluation(
    span_context={"span_id": "abc123", "trace_id": "xyz789"},
    ml_app="content-creator-app",
    label="toxicity_check",
    metric_type="categorical",
    value=check_toxicity(response_text),
    tags={
        "detector": "custom_toxicity_model",
        "version": "v2.0"
    }
)
```

### API Example (Categorical)

```json
POST /api/v2/llm_observability/evaluations
{
  "data": {
    "type": "evaluation_metric",
    "attributes": {
      "metrics": [
        {
          "span_id": "abc123",
          "trace_id": "xyz789",
          "ml_app": "content-creator-app",
          "timestamp_ms": 1704067200000,
          "metric_type": "categorical",
          "label": "toxicity_check",
          "categorical_value": "safe",
          "tags": {
            "detector": "custom_toxicity_model",
            "version": "v2.0"
          }
        }
      ]
    }
  }
}
```

---

## Common Evaluation Labels

Here's a comprehensive list of commonly used evaluation labels in LLM applications:

### Quality Metrics

| Label | Metric Type | Scale/Categories | Description |
|-------|-------------|------------------|-------------|
| `accuracy` | score | 0-1 or 0-100 | Correctness of the response |
| `relevance` | score | 0-1 | How relevant is the response to the query |
| `coherence` | score | 0-1 | Logical flow and clarity |
| `completeness` | score | 0-1 | How complete is the answer |
| `conciseness` | score | 0-1 | How concise is the response (not verbose) |

### Safety Metrics

| Label | Metric Type | Scale/Categories | Description |
|-------|-------------|------------------|-------------|
| `toxicity` | categorical | `safe`, `unsafe` | Offensive or harmful content |
| `bias` | categorical | `detected`, `not_detected` | Unfair or prejudiced content |
| `pii_detection` | categorical | `present`, `absent` | Personal identifiable information |
| `profanity` | categorical | `clean`, `profane` | Profanity presence |

### Factuality Metrics

| Label | Metric Type | Scale/Categories | Description |
|-------|-------------|------------------|-------------|
| `hallucination` | categorical | `grounded`, `hallucinated` | Made-up vs factual information |
| `factuality` | score | 0-1 | How factually correct is the response |
| `citation_accuracy` | score | 0-1 | Accuracy of cited sources |

### User Experience Metrics

| Label | Metric Type | Scale/Categories | Description |
|-------|-------------|------------------|-------------|
| `user_rating` | score | 1-5 | User satisfaction rating |
| `user_thumbs` | categorical | `up`, `down` | Binary user feedback |
| `helpfulness` | score | 0-1 | How helpful is the response |
| `sentiment` | categorical | `positive`, `neutral`, `negative` | User sentiment |

### Performance Metrics

| Label | Metric Type | Scale/Categories | Description |
|-------|-------------|------------------|-------------|
| `latency` | score | milliseconds | Response time |
| `token_count` | score | integer | Number of tokens used |
| `cost` | score | dollars | Cost per request |
| `throughput` | score | requests/sec | Processing rate |

### Task-Specific Metrics

| Label | Metric Type | Scale/Categories | Description |
|-------|-------------|------------------|-------------|
| `extraction_accuracy` | score | 0-1 | Data extraction correctness |
| `translation_quality` | score | 0-1 | Translation accuracy |
| `summarization_quality` | score | 0-1 | Summary quality |
| `code_correctness` | categorical | `correct`, `incorrect`, `partial` | Code generation quality |

---

## Choosing the Right Metric Type

### Decision Matrix

```
┌─────────────────────────────────────────────────────────┐
│ Question                    │ Answer → Metric Type      │
├─────────────────────────────────────────────────────────┤
│ Is the result a number?     │ YES → score               │
│                             │ NO → categorical          │
├─────────────────────────────────────────────────────────┤
│ Can you rank/order results? │ YES → score               │
│                             │ NO → categorical          │
├─────────────────────────────────────────────────────────┤
│ Do you need averages?       │ YES → score               │
│                             │ NO → categorical          │
├─────────────────────────────────────────────────────────┤
│ Are there fixed classes?    │ YES → categorical         │
│                             │ NO → score                │
└─────────────────────────────────────────────────────────┘
```

### Use Score When:

✅ You need to calculate **averages**, **trends**, or **percentiles**  
✅ You want **threshold-based alerts** (e.g., `score < 0.8`)  
✅ The metric represents a **continuous measurement** (latency, cost)  
✅ You're tracking **user ratings** (1-5 stars)  
✅ You need **statistical analysis** (correlation, regression)  

**Examples**: User ratings, accuracy scores, latency, cost, confidence levels

### Use Categorical When:

✅ You have **discrete, predefined categories** (pass/fail)  
✅ You want to track **distribution across classes**  
✅ The metric represents a **qualitative state** (safe/unsafe)  
✅ You need **count-based alerts** (e.g., `> 10 "fail" instances`)  
✅ You're doing **classification** tasks

**Examples**: Toxicity detection, bias flags, hallucination checks, status indicators

### Can You Use Both?

**Yes!** You can submit multiple evaluations for the same span with different metric types:

```python
# Submit both score and categorical for the same aspect
# 1. Numeric toxicity score
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="toxicity_score",
    metric_type="score",
    value=0.05  # Low toxicity (0-1 scale)
)

# 2. Categorical toxicity classification
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="toxicity_check",
    metric_type="categorical",
    value="safe"  # Classification result
)
```

This approach gives you:
- **Numeric analysis**: Track toxicity trends over time
- **Classification view**: See distribution of safe vs unsafe content

---

## Implementation Examples

### Example 1: User Feedback System

**Scenario**: Collect user ratings and comments for vote extraction results.

```python
from ddtrace.llmobs import LLMObs
from typing import Optional

def submit_user_feedback(
    span_id: str,
    trace_id: str,
    rating: int,  # 1-5
    comment: Optional[str] = None
):
    """Submit user feedback as evaluation."""
    span_context = {"span_id": span_id, "trace_id": trace_id}
    
    # Submit rating as score
    LLMObs.submit_evaluation(
        span_context=span_context,
        ml_app="vote-extraction-app",
        label="user_rating",
        metric_type="score",
        value=rating,
        tags={
            "feedback_type": "user_rating",
            "has_comment": str(comment is not None).lower()
        }
    )
    
    # If comment provided, submit as categorical
    if comment:
        LLMObs.submit_evaluation(
            span_context=span_context,
            ml_app="vote-extraction-app",
            label="user_feedback",
            metric_type="categorical",
            value="comment_provided",
            tags={
                "comment": comment[:500],  # Truncate for tags
                "feedback_type": "user_comment"
            }
        )
```

### Example 2: Automated Quality Checks

**Scenario**: Run automated quality checks on generated content.

```python
from ddtrace.llmobs import LLMObs
import re

def evaluate_content_quality(content: str, span_context: dict):
    """Run multiple quality evaluations."""
    
    # 1. Check for PII (categorical)
    pii_detected = check_for_pii(content)  # Your PII detection logic
    LLMObs.submit_evaluation(
        span_context=span_context,
        ml_app="content-creator-app",
        label="pii_check",
        metric_type="categorical",
        value="present" if pii_detected else "absent"
    )
    
    # 2. Toxicity score (score)
    toxicity_score = calculate_toxicity(content)  # Returns 0-1
    LLMObs.submit_evaluation(
        span_context=span_context,
        ml_app="content-creator-app",
        label="toxicity_score",
        metric_type="score",
        value=toxicity_score
    )
    
    # 3. Completeness (score)
    completeness = calculate_completeness(content)  # Returns 0-1
    LLMObs.submit_evaluation(
        span_context=span_context,
        ml_app="content-creator-app",
        label="completeness",
        metric_type="score",
        value=completeness
    )
    
    # 4. Overall quality classification (categorical)
    if toxicity_score < 0.3 and completeness > 0.7:
        quality = "good"
    elif toxicity_score < 0.6 and completeness > 0.5:
        quality = "acceptable"
    else:
        quality = "poor"
    
    LLMObs.submit_evaluation(
        span_context=span_context,
        ml_app="content-creator-app",
        label="overall_quality",
        metric_type="categorical",
        value=quality
    )

def check_for_pii(content: str) -> bool:
    """Simplified PII detection."""
    patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
        r'\b[\w.-]+@[\w.-]+\.\w+\b'  # Email
    ]
    return any(re.search(pattern, content) for pattern in patterns)

def calculate_toxicity(content: str) -> float:
    """Simplified toxicity scoring."""
    # Your actual toxicity model here
    return 0.05  # Low toxicity

def calculate_completeness(content: str) -> float:
    """Calculate content completeness."""
    # Your logic here
    word_count = len(content.split())
    return min(word_count / 100, 1.0)  # Assume 100 words = complete
```

### Example 3: A/B Test Tracking

**Scenario**: Track performance of different model versions.

```python
def evaluate_extraction_with_version(
    extracted_data: dict,
    ground_truth: dict,
    span_context: dict,
    model_version: str
):
    """Evaluate extraction and tag with model version."""
    
    # Calculate accuracy
    accuracy = calculate_accuracy(extracted_data, ground_truth)
    
    # Submit evaluation with version tag
    LLMObs.submit_evaluation(
        span_context=span_context,
        ml_app="vote-extraction-app",
        label="extraction_accuracy",
        metric_type="score",
        value=accuracy,
        tags={
            "model_version": model_version,
            "experiment": "model_comparison",
            "ground_truth_available": "true"
        }
    )
    
    # Classify result (categorical)
    if accuracy >= 0.95:
        result = "excellent"
    elif accuracy >= 0.80:
        result = "good"
    elif accuracy >= 0.60:
        result = "acceptable"
    else:
        result = "poor"
    
    LLMObs.submit_evaluation(
        span_context=span_context,
        ml_app="vote-extraction-app",
        label="accuracy_classification",
        metric_type="categorical",
        value=result,
        tags={
            "model_version": model_version,
            "experiment": "model_comparison"
        }
    )

def calculate_accuracy(extracted: dict, truth: dict) -> float:
    """Calculate extraction accuracy."""
    # Your accuracy calculation logic
    total_fields = len(truth)
    correct_fields = sum(1 for k, v in truth.items() if extracted.get(k) == v)
    return correct_fields / total_fields if total_fields > 0 else 0.0
```

---

## Best Practices

### 1. **Standardize Your Labels**

❌ **Bad**: Inconsistent labels
```python
LLMObs.submit_evaluation(..., label="user_rating", value=4)
LLMObs.submit_evaluation(..., label="UserRating", value=5)
LLMObs.submit_evaluation(..., label="rating", value=3)
```

✅ **Good**: Consistent, descriptive labels
```python
# Define constants
LABEL_USER_RATING = "user_rating"
LABEL_EXTRACTION_ACCURACY = "extraction_accuracy"

LLMObs.submit_evaluation(..., label=LABEL_USER_RATING, value=4)
LLMObs.submit_evaluation(..., label=LABEL_USER_RATING, value=5)
```

### 2. **Define Clear Value Ranges**

❌ **Bad**: Unclear scale
```python
# What does 8 mean? Out of 10? 100?
LLMObs.submit_evaluation(..., label="quality", metric_type="score", value=8)
```

✅ **Good**: Document and tag scale
```python
# Clear scale with tags
LLMObs.submit_evaluation(
    ...,
    label="quality_score",
    metric_type="score",
    value=0.8,  # 0-1 scale
    tags={"scale": "0-1", "description": "quality_percentage"}
)
```

### 3. **Use Consistent Categories**

❌ **Bad**: Varying categories
```python
LLMObs.submit_evaluation(..., label="safety", value="Safe")
LLMObs.submit_evaluation(..., label="safety", value="safe")
LLMObs.submit_evaluation(..., label="safety", value="SAFE")
LLMObs.submit_evaluation(..., label="safety", value="ok")
```

✅ **Good**: Standardized categories
```python
# Define category constants
SAFETY_SAFE = "safe"
SAFETY_UNSAFE = "unsafe"

LLMObs.submit_evaluation(..., label="safety_check", value=SAFETY_SAFE)
LLMObs.submit_evaluation(..., label="safety_check", value=SAFETY_UNSAFE)
```

### 4. **Add Context with Tags**

✅ **Good**: Rich context
```python
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="vote-extraction-app",
    label="extraction_accuracy",
    metric_type="score",
    value=0.92,
    tags={
        "model_version": "v2.1.0",
        "document_type": "ballot_form",
        "complexity": "high",
        "pages_processed": "6",
        "evaluation_method": "ground_truth_comparison"
    }
)
```

### 5. **Choose Appropriate Scales**

| Scenario | Recommended Scale |
|----------|-------------------|
| User ratings | 1-5 (integer) |
| Probabilities/percentages | 0-1 (float) |
| Latency | Milliseconds (integer) |
| Cost | Dollars (float, 2 decimals) |
| Custom quality metrics | 0-1 (float) for normalization |

### 6. **Normalize Scores for Comparison**

✅ **Good**: Normalize to 0-1
```python
def normalize_rating(rating: int, min_val: int = 1, max_val: int = 5) -> float:
    """Normalize rating to 0-1 scale."""
    return (rating - min_val) / (max_val - min_val)

# Submit normalized score
normalized_rating = normalize_rating(rating=4, min_val=1, max_val=5)
LLMObs.submit_evaluation(
    ...,
    label="user_satisfaction_normalized",
    metric_type="score",
    value=normalized_rating,  # 0.75
    tags={"original_rating": "4", "scale": "1-5"}
)
```

### 7. **Batch Related Evaluations**

✅ **Good**: Submit related evaluations together
```python
def evaluate_response_comprehensive(response: str, span_context: dict):
    """Run all evaluations for a response."""
    evaluations = [
        ("toxicity_score", "score", calculate_toxicity(response)),
        ("relevance_score", "score", calculate_relevance(response)),
        ("safety_check", "categorical", check_safety(response)),
        ("completeness", "score", calculate_completeness(response))
    ]
    
    for label, metric_type, value in evaluations:
        LLMObs.submit_evaluation(
            span_context=span_context,
            ml_app="my-chatbot",
            label=label,
            metric_type=metric_type,
            value=value
        )
```

---

## Visualization and Monitoring

### Score Metrics - Visualization Options

#### 1. **Timeseries Charts**

Track score trends over time:

```
Datadog Query:
avg:llmobs.evaluation.user_rating{ml_app:vote-extraction-app} by {ml_app}
```

**Use for**: Identifying quality degradation, tracking improvements

#### 2. **Heatmaps**

Visualize score distribution:

```
Datadog Query:
avg:llmobs.evaluation.extraction_accuracy{*} by {model_version,document_type}
```

**Use for**: Comparing performance across dimensions

#### 3. **Gauges**

Show current average score:

```
Datadog Query:
avg:llmobs.evaluation.user_rating{ml_app:vote-extraction-app}
```

**Use for**: At-a-glance quality indicators

### Categorical Metrics - Visualization Options

#### 1. **Pie Charts**

Show category distribution:

```
Datadog Query:
count:llmobs.evaluation.safety_check{*} by {value}
```

**Use for**: Understanding proportion of each category

#### 2. **Stacked Bar Charts**

Compare categories over time:

```
Datadog Query:
count:llmobs.evaluation.overall_quality{*} by {value}
```

**Use for**: Tracking category shifts over time

#### 3. **Top Lists**

Show most common categories:

```
Datadog Query:
count:llmobs.evaluation.user_intent{*} by {value}.as_count()
```

**Use for**: Identifying dominant patterns

### Alert Examples

#### Score Alerts

```yaml
# Alert when average user rating drops
Monitor: avg(last_4h):avg:llmobs.evaluation.user_rating{ml_app:vote-extraction-app} < 3
Message: |
  User satisfaction has dropped below 3.0 stars
  Current: {{value}}
  Investigate recent changes
```

```yaml
# Alert when extraction accuracy is low
Monitor: avg(last_1h):avg:llmobs.evaluation.extraction_accuracy{*} < 0.80
Message: |
  Extraction accuracy below 80%
  Current: {{value}}
  Check model performance
```

#### Categorical Alerts

```yaml
# Alert on safety issues
Monitor: count(last_15m):count:llmobs.evaluation.safety_check{value:unsafe} > 10
Message: |
  More than 10 unsafe content detections in 15 minutes
  Immediate review required
```

```yaml
# Alert on high failure rate
Monitor: count(last_1h):count:llmobs.evaluation.hallucination_check{value:hallucinated} > 50
Message: |
  High hallucination rate detected
  Count: {{value}}
  Review model prompts
```

---

## Common Patterns and Anti-Patterns

### ✅ Good Patterns

#### Pattern 1: Hierarchical Metrics

Submit both granular and aggregated metrics:

```python
# Granular: Individual field accuracy
LLMObs.submit_evaluation(..., label="candidate_name_accuracy", value=1.0)
LLMObs.submit_evaluation(..., label="vote_count_accuracy", value=0.95)

# Aggregated: Overall accuracy
LLMObs.submit_evaluation(..., label="overall_accuracy", value=0.975)
```

#### Pattern 2: Complementary Metrics

Use both score and categorical for comprehensive view:

```python
# Score: Numeric latency
LLMObs.submit_evaluation(..., label="response_latency", value=1250)  # ms

# Categorical: Latency tier
latency_tier = "fast" if latency < 500 else "medium" if latency < 2000 else "slow"
LLMObs.submit_evaluation(..., label="latency_tier", value=latency_tier)
```

#### Pattern 3: Versioned Evaluations

Track metrics across versions:

```python
LLMObs.submit_evaluation(
    ...,
    label="extraction_accuracy",
    value=accuracy,
    tags={
        "model_version": "v2.5.0",
        "evaluator_version": "v1.0.0",
        "experiment": "prompt_optimization"
    }
)
```

### ❌ Anti-Patterns

#### Anti-Pattern 1: Mixing Scales

❌ **Bad**: Inconsistent scales for same metric
```python
# Sometimes 0-1, sometimes 0-100
LLMObs.submit_evaluation(..., label="accuracy", value=0.85)
LLMObs.submit_evaluation(..., label="accuracy", value=85)
```

#### Anti-Pattern 2: Too Many Categories

❌ **Bad**: Too many categories (hard to analyze)
```python
# 20+ different status values
LLMObs.submit_evaluation(..., label="status", value="processing_step_12_substep_a")
```

✅ **Better**: Hierarchical tags
```python
LLMObs.submit_evaluation(
    ...,
    label="status",
    value="processing",
    tags={"step": "12", "substep": "a"}
)
```

#### Anti-Pattern 3: Using Categorical for Numbers

❌ **Bad**: Categorical for numeric data
```python
# Lost ability to calculate averages
LLMObs.submit_evaluation(..., label="latency", metric_type="categorical", value="1250ms")
```

✅ **Better**: Score for numeric data
```python
LLMObs.submit_evaluation(..., label="latency", metric_type="score", value=1250)
```

#### Anti-Pattern 4: No Standardization

❌ **Bad**: No standards across team
```python
# Team member 1
LLMObs.submit_evaluation(..., label="user_feedback", value="positive")

# Team member 2
LLMObs.submit_evaluation(..., label="feedback", value="good")

# Team member 3
LLMObs.submit_evaluation(..., label="rating", value=5)
```

✅ **Better**: Shared constants and documentation
```python
# shared_constants.py
EVALUATION_LABELS = {
    "USER_RATING": "user_rating",  # Score: 1-5
    "USER_SENTIMENT": "user_sentiment"  # Categorical: positive/neutral/negative
}

# Usage
LLMObs.submit_evaluation(..., label=EVALUATION_LABELS["USER_RATING"], value=5)
```

---

## Summary

### Quick Reference Table

| Aspect | Score | Categorical |
|--------|-------|-------------|
| **Data Type** | Numeric (float/int) | String (label) |
| **Use For** | Measurements, ratings, continuous metrics | Classifications, states, discrete labels |
| **Aggregations** | avg, min, max, sum, percentiles | count, distribution |
| **Alerts** | Threshold-based (`< value`) | Count-based (`> N occurrences`) |
| **Examples** | 4.5, 0.87, 125, 99.9 | "pass", "fail", "relevant", "safe" |
| **Visualization** | Line charts, gauges, heatmaps | Pie charts, bar charts, top lists |

### Key Takeaways

1. ✅ Use **`score`** for numeric, measurable quantities
2. ✅ Use **`categorical`** for discrete classifications or labels
3. ✅ Standardize your labels and value ranges
4. ✅ Add context with tags
5. ✅ Submit multiple evaluations per span for comprehensive analysis
6. ✅ Choose scales appropriate for your use case
7. ✅ Document your evaluation standards for team consistency

---

## Related Documentation

- **[01_INSTRUMENTING_SPANS.md](./01_INSTRUMENTING_SPANS.md)** - How to create and annotate LLMObs spans
- **[02_VISUALIZING_TRACES_AND_SPANS.md](./02_VISUALIZING_TRACES_AND_SPANS.md)** - Viewing traces in Datadog
- **[docs/features/USER_FEEDBACK_LLMOBS_PLAN.md](../../docs/features/USER_FEEDBACK_LLMOBS_PLAN.md)** - User feedback implementation plan
- **[docs/features/VOTE_EXTRACTION_LLMOBS_SPANS.md](../../docs/features/VOTE_EXTRACTION_LLMOBS_SPANS.md)** - Production implementation example

## External Resources

- [Datadog LLM Observability - Submit Evaluations](https://docs.datadoghq.com/llm_observability/evaluations/submit_evaluations/)
- [Datadog LLM Observability - Python SDK](https://docs.datadoghq.com/llm_observability/setup/sdk/python/)
- [Datadog LLM Observability - Terminology](https://docs.datadoghq.com/llm_observability/terms/)

---

**Version History**:
- v1.0 (January 2026): Initial guide creation

