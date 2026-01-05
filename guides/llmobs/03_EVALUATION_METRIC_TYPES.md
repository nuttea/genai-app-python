# Guide: Evaluation Metric Types in Datadog LLM Observability

**Version**: 1.1  
**Last Updated**: January 4, 2026  
**Audience**: Backend developers, ML engineers, data scientists

**What's New in v1.1**:
- ✨ Added **Example 4: Real-World Vote Extraction (Production)** - Comprehensive production implementation
- 📊 Demonstrates all three metric types in a real application
- 🔗 Shows proper Datadog LLMObs URL format and span context management
- 💬 Includes user feedback system integration
- ✅ Production-ready code with validation and error handling

---

## Table of Contents

1. [Overview](#overview)
2. [Understanding Metric Types](#understanding-metric-types)
3. [Score Metric Type](#score-metric-type)
4. [Categorical Metric Type](#categorical-metric-type)
5. [Common Evaluation Labels](#common-evaluation-labels)
6. [Choosing the Right Metric Type](#choosing-the-right-metric-type)
7. [Implementation Examples](#implementation-examples)
   - Example 1: User Feedback System
   - Example 2: Automated Quality Checks
   - Example 3: A/B Test Tracking
   - **Example 4: Real-World Vote Extraction (Production)** ⭐ **NEW**
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

Datadog LLMObs supports **three metric types** for evaluations:

| Metric Type | Data Type | Use Case | Example Values |
|-------------|-----------|----------|----------------|
| **`score`** | Numeric (float/int) | Quantitative measurements, ratings, continuous metrics | `0.95`, `4`, `3.5`, `0.0` |
| **`categorical`** | String (label) | Qualitative classifications, discrete states | `"pass"`, `"fail"`, `"relevant"`, `"toxic"`, `"positive"` |
| **`boolean`** | Boolean (true/false) | Binary true/false evaluations | `true`, `false` |

**Source**: [Datadog LLM Observability API Documentation](https://docs.datadoghq.com/llm_observability/instrumentation/api/?tab=model#evalmetric)

### Quick Decision Tree

```
What type of evaluation result do you have?
│
├─ NUMBER (rating, score, measurement) → Use `score`
│   └─ Examples: 4.5, 0.87, 125, 99.9
│
├─ BOOLEAN (true/false only) → Use `boolean`
│   └─ Examples: true, false
│
└─ CATEGORY (labels, classifications) → Use `categorical`
    └─ Examples: "pass", "fail", "relevant", "positive", "high"
```

**💡 Tip**: 
- Use `boolean` for simple true/false checks (e.g., "Is answer factual?")
- Use `categorical` for multi-option classifications (e.g., "pass"/"fail"/"partial")
- Use `score` for numeric ratings and measurements

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

## Boolean Metric Type

### Definition

The **`boolean`** metric type is used for **simple true/false evaluations** where the result is a binary boolean value. Boolean evaluations are ideal for:

- **Factuality checks**: Is the answer grounded in facts? (true/false)
- **Relevance checks**: Is the response on-topic? (true/false)
- **Presence checks**: Does the output contain PII? (true/false)
- **Binary flags**: Any yes/no question with no middle ground

### Characteristics

| Property | Details |
|----------|---------|
| **Field Name** | `boolean_value` (API), `value` (Python SDK) |
| **Data Type** | `boolean` |
| **Values** | `true` or `false` only |
| **Aggregations** | Count of true/false, percentage true |
| **Alerts** | Count-based (e.g., `false > 10` occurrences) |

### When to Use Boolean

✅ **Use `boolean` when:**
- You have exactly 2 possible outcomes: true or false
- The evaluation is a simple yes/no question
- You don't need descriptive labels
- You want to calculate "% true" or "% false"

❌ **Don't use `boolean` when:**
- You need more than 2 values (use `categorical` instead)
- You want descriptive labels like "pass"/"fail" (use `categorical`)
- You need to track "uncertain" or "unknown" states (use `categorical`)

### Python SDK Example (Boolean)

```python
from ddtrace.llmobs import LLMObs

def check_factuality(response: str, sources: list) -> bool:
    """Check if response is grounded in provided sources."""
    # Your factuality checking logic here
    return True  # or False

# Submit boolean evaluation
LLMObs.submit_evaluation(
    span_context={"span_id": "abc123", "trace_id": "xyz789"},
    ml_app="content-creator-app",
    label="factuality_check",
    metric_type="boolean",  # Boolean type
    value=check_factuality(response, sources),  # true or false
    tags={
        "checker": "source_comparison",
        "version": "v1.0"
    }
)
```

### API Example (Boolean)

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
          "metric_type": "boolean",
          "label": "factuality_check",
          "boolean_value": true,
          "tags": {
            "checker": "source_comparison",
            "version": "v1.0"
          }
        }
      ]
    }
  }
}
```

### Boolean Use Cases

| Use Case | Label | Description |
|----------|-------|-------------|
| **Factuality** | `is_factual` | Is the response grounded in facts? |
| **Relevance** | `is_relevant` | Is the response on-topic? |
| **PII Detection** | `contains_pii` | Does output contain personal info? |
| **Topic Match** | `topic_relevancy` | Does response match expected topic? |
| **Completeness** | `is_complete` | Is the answer complete? |
| **Coherence** | `is_coherent` | Is the response logically coherent? |

---

## Categorical Metric Type

### Definition

The **`categorical`** metric type is used for **discrete, non-numeric classifications** where the result is one of a predefined set of labels or categories (more than 2 options). Categorical values represent:

- **Multi-value classifications**: Pass/Fail/Partial, Good/Neutral/Bad
- **Multi-class labels**: High/Medium/Low, Positive/Neutral/Negative
- **Status indicators**: Safe/Unsafe/Warning, Relevant/Irrelevant/Unknown
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

#### 1. **Binary Classification (Categorical)**

Best for: Multi-option pass/fail checks, detection tasks with labels

```python
# Example: Toxicity detection with categories
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="toxicity_check",
    metric_type="categorical",
    value="safe"  # or "unsafe", "unknown"
)
```

**Standard categorical values** (use when you need labels, not just true/false): 
- Pass/Fail: `"pass"`, `"fail"`, `"partial"`
- Detection: `"detected"`, `"not_detected"`, `"uncertain"`
- Safety: `"safe"`, `"unsafe"`, `"warning"`
- Quality: `"good"`, `"acceptable"`, `"poor"`

**Use `categorical`** when:
- You have more than 2 possible values
- You need descriptive labels instead of true/false
- You want to track distribution across multiple categories

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
┌──────────────────────────────────────────────────────────────┐
│ Question                      │ Answer → Metric Type        │
├──────────────────────────────────────────────────────────────┤
│ Is the result a number?       │ YES → score                 │
│                               │ NO → continue below         │
├──────────────────────────────────────────────────────────────┤
│ Is it exactly true/false?     │ YES → boolean               │
│                               │ NO → continue below         │
├──────────────────────────────────────────────────────────────┤
│ Multiple categories/labels?   │ YES → categorical           │
│                               │ NO → boolean                │
├──────────────────────────────────────────────────────────────┤
│ Need to calculate % true?     │ YES → boolean               │
│ Need to track distribution?   │ YES → categorical           │
│ Need to calculate averages?   │ YES → score                 │
└──────────────────────────────────────────────────────────────┘
```

### Use Score When:

✅ You need to calculate **averages**, **trends**, or **percentiles**  
✅ You want **threshold-based alerts** (e.g., `score < 0.8`)  
✅ The metric represents a **continuous measurement** (latency, cost)  
✅ You're tracking **user ratings** (1-5 stars)  
✅ You need **statistical analysis** (correlation, regression)  

**Examples**: User ratings, accuracy scores, latency, cost, confidence levels

### Use Boolean When:

✅ You have **exactly 2 outcomes**: true or false  
✅ It's a **simple yes/no question**  
✅ You want to calculate **% true** or **% false**  
✅ You need **binary flags** without descriptive labels  
✅ You're doing **presence/absence checks**

**Examples**: Factuality checks, relevance checks, PII detection, topic match, completeness flags

### Use Categorical When:

✅ You have **3+ discrete categories** (pass/fail/partial)  
✅ You want to track **distribution across classes**  
✅ The metric represents a **qualitative state** with labels  
✅ You need **count-based alerts** (e.g., `> 10 "fail" instances`)  
✅ You're doing **multi-class classification**

**Examples**: Quality levels (good/neutral/bad), safety states (safe/unsafe/warning), sentiment (positive/neutral/negative)

### Can You Use Multiple Types?

**Yes!** You can submit multiple evaluations for the same span with different metric types:

```python
# Submit all three metric types for comprehensive evaluation
# 1. Boolean: Simple true/false check
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="is_safe",
    metric_type="boolean",
    value=True  # Is it safe?
)

# 2. Score: Numeric toxicity score
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="toxicity_score",
    metric_type="score",
    value=0.05  # 0-1 scale, lower is better
)

# 3. Categorical: Classification with labels
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="my-chatbot",
    label="safety_level",
    metric_type="categorical",
    value="safe"  # safe, warning, or unsafe
)
```

This approach gives you:
- **Boolean**: Quick true/false overview (% safe)
- **Score**: Trend analysis over time (improving/degrading)
- **Categorical**: Distribution across safety levels

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

### Example 4: Real-World Vote Extraction (Production)

**Scenario**: Thai election vote extraction with automated validation and user feedback.

This example demonstrates a complete implementation combining:
- ✅ Automated validation evaluations
- ✅ User feedback collection
- ✅ Proper span context management
- ✅ All three metric types in production

#### Part 1: Automated Validation as Custom Evaluations

```python
from ddtrace.llmobs import LLMObs
from typing import Optional

def submit_validation_evaluation(
    is_valid: bool,
    check_type: str,
    error_msg: Optional[str],
    validation_checks: list,
    form_index: int,
) -> None:
    """
    Submit validation result as Datadog LLMObs Custom Evaluation.
    Uses LLMObs.export_span() to automatically get the active span context.
    """
    # Get active span context from workflow
    span_context = LLMObs.export_span(span=None)
    if not span_context:
        logger.warning("No active span context found")
        return
    
    tags = {
        "feature": "vote-extraction",
        "validation_check": check_type,
        "form_index": str(form_index),
    }
    
    # 1. Submit overall validation result (categorical: pass/fail)
    LLMObs.submit_evaluation(
        span=span_context,
        ml_app="vote-extractor",
        label=f"validation_passed_form_{form_index}",  # Unique per form
        metric_type="categorical",
        value="pass" if is_valid else "fail",
        tags=tags,
        assessment="pass" if is_valid else "fail",
        reasoning=error_msg if error_msg else "All validation checks passed",
    )
    
    # 2. Submit validation check type (categorical)
    LLMObs.submit_evaluation(
        span=span_context,
        ml_app="vote-extractor",
        label=f"validation_check_type_form_{form_index}",
        metric_type="categorical",
        value=check_type,  # e.g., "ballot_statistics", "vote_results"
        tags=tags,
        assessment="pass" if is_valid else "fail",
        reasoning=f"Validated {check_type} successfully" if is_valid else error_msg,
    )
    
    # 3. Submit validation score (numeric: checks passed / total checks)
    checks_passed = len([c for c in validation_checks if c.get("passed", False)])
    total_checks = len(validation_checks)
    validation_score = checks_passed / total_checks if total_checks > 0 else 1.0
    
    LLMObs.submit_evaluation(
        span=span_context,
        ml_app="vote-extractor",
        label=f"validation_score_form_{form_index}",
        metric_type="score",
        value=validation_score,
        tags=tags,
        assessment="pass" if is_valid else "fail",
        reasoning=f"Passed {checks_passed}/{total_checks} validation checks",
    )
    
    logger.info(
        f"✅ Submitted validation evaluation: {check_type} "
        f"(passed={is_valid}, score={validation_score:.2f})"
    )

# Example usage in workflow
@workflow
async def extract_from_images(image_files: list) -> dict:
    """Extract vote data with validation."""
    # ... extraction logic ...
    
    # Validate within workflow to ensure active span context
    for idx, extracted_form in enumerate(extracted_forms):
        is_valid, error_msg = await validate_extraction(extracted_form, idx)
        
        # Submit evaluation happens inside this function
        submit_validation_evaluation(
            is_valid=is_valid,
            check_type="ballot_statistics" if error_msg else "complete",
            error_msg=error_msg,
            validation_checks=validation_results,
            form_index=idx,
        )
    
    # Capture workflow span context before returning
    workflow_span_context = LLMObs.export_span(span=None)
    
    return {
        "extraction_results": extracted_forms,
        "span_context": {
            "span_id": str(workflow_span_context.get("span_id")),
            "trace_id": str(workflow_span_context.get("trace_id")),
        }
    }
```

#### Part 2: User Feedback System

```python
from pydantic import BaseModel, Field

class FeedbackRequest(BaseModel):
    """User feedback model."""
    span_id: str = Field(..., description="Workflow span ID (decimal string)")
    trace_id: str = Field(..., description="Workflow trace ID (hex string)")
    ml_app: str = Field(..., description="Application name")
    feature: str = Field(..., description="Feature name")
    
    # Feedback types
    feedback_type: str = Field(..., description="thumbs, rating, or comment")
    thumbs: Optional[str] = Field(None, description="up or down")
    rating: Optional[int] = Field(None, ge=1, le=5, description="1-5 stars")
    comment: Optional[str] = Field(None, description="User comment")
    
    # Context
    user_id: Optional[str] = Field(None)
    session_id: Optional[str] = Field(None)

def submit_user_feedback(feedback: FeedbackRequest) -> dict:
    """Submit user feedback as Datadog LLMObs evaluations."""
    span_context = {
        "span_id": feedback.span_id,  # Use original decimal string
        "trace_id": feedback.trace_id,  # Use original hex string
    }
    
    tags = {
        "feature": feedback.feature,
        "feedback_type": feedback.feedback_type,
        "user_id": feedback.user_id or "anonymous",
        "session_id": feedback.session_id or "unknown",
    }
    
    # 1. Submit thumbs feedback (categorical: up/down)
    if feedback.thumbs:
        LLMObs.submit_evaluation(
            span=span_context,
            ml_app=feedback.ml_app,
            label="user_thumbs",
            metric_type="categorical",
            value=feedback.thumbs,  # "up" or "down"
            tags=tags,
        )
        logger.info(f"✅ Submitted thumbs: {feedback.thumbs}")
    
    # 2. Submit rating (score: 1-5)
    if feedback.rating:
        LLMObs.submit_evaluation(
            span=span_context,
            ml_app=feedback.ml_app,
            label="user_rating",
            metric_type="score",
            value=feedback.rating,
            tags=tags,
        )
        logger.info(f"✅ Submitted rating: {feedback.rating}")
    
    # 3. Submit comment (categorical with reasoning field)
    if feedback.comment:
        LLMObs.submit_evaluation(
            span=span_context,
            ml_app=feedback.ml_app,
            label="user_feedback",
            metric_type="categorical",
            value="to_be_reviewed",  # Indicates comment needs review
            tags=tags,
            reasoning=feedback.comment,  # User's actual comment
        )
        logger.info(f"✅ Submitted comment: {feedback.comment[:50]}...")
    
    return {"success": True, "message": "Feedback submitted successfully"}

# FastAPI endpoint example
@router.post("/feedback/submit")
async def submit_feedback_endpoint(feedback: FeedbackRequest):
    """API endpoint for user feedback submission."""
    result = submit_user_feedback(feedback)
    return result
```

#### Part 3: Frontend Integration (Streamlit)

```python
import streamlit as st
from datadog_rum import datadogRum

# After extraction, display trace context
if extraction_result and extraction_result.get("span_context"):
    span_context = extraction_result["span_context"]
    
    # Display IDs for transparency
    with st.expander("🔍 Trace Context (for Datadog LLMObs)"):
        # Backend returns:
        # - span_id: decimal string (e.g., "5009943010419557822")
        # - trace_id: hex string (e.g., "69594bf000000000f8bbcd9f0908a20a")
        
        span_id_decimal = span_context["span_id"]
        trace_id_hex = span_context["trace_id"]
        
        # Convert span_id to hex for display
        span_id_hex = format(int(span_id_decimal), "016x")
        
        st.text_input("Span ID (Hex)", value=span_id_hex, disabled=True)
        st.text_input("Span ID (Decimal)", value=span_id_decimal, disabled=True)
        st.text_input("Trace ID (Hex)", value=trace_id_hex, disabled=True)
        
        # Create Datadog LLMObs trace link
        datadog_url = (
            f"https://app.datadoghq.com/llm/traces/trace/{trace_id_hex}"
            f"?selectedTab=overview&spanId={span_id_decimal}"
        )
        st.markdown(f"🔗 **[View in Datadog LLMObs]({datadog_url})**")
    
    # User feedback section
    st.markdown("### 💬 Rate this extraction")
    
    # Thumbs feedback
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Helpful", key="thumbs_up"):
            submit_feedback_api(
                span_id=span_id_decimal,  # Use original values
                trace_id=trace_id_hex,
                feedback_type="thumbs",
                thumbs="up",
            )
            st.success("Thanks for your feedback!")
    
    with col2:
        if st.button("👎 Not Helpful", key="thumbs_down"):
            submit_feedback_api(
                span_id=span_id_decimal,
                trace_id=trace_id_hex,
                feedback_type="thumbs",
                thumbs="down",
            )
            st.success("Thanks for your feedback!")
    
    # Star rating
    rating = st.slider("⭐ Rate 1-5 stars", 1, 5, 3)
    comment = st.text_area("💭 Optional comment")
    
    if st.button("Submit Rating"):
        submit_feedback_api(
            span_id=span_id_decimal,
            trace_id=trace_id_hex,
            feedback_type="rating",
            rating=rating,
            comment=comment if comment else None,
            session_id=datadogRum.getInternalContext().get("session_id"),
        )
        st.success("✅ Rating submitted!")
```

#### Key Takeaways from Production Example

1. **Span Context Management**:
   - Use `LLMObs.export_span(span=None)` to auto-detect active span
   - Capture workflow span context *before* returning from workflow
   - Pass original values (decimal span_id, hex trace_id) to feedback API

2. **Unique Labels per Form**:
   - Use `label=f"validation_passed_form_{form_index}"` for multi-form validation
   - Prevents Datadog from rejecting duplicate evaluations

3. **All Three Metric Types**:
   - **Score**: `validation_score` (0-1), `user_rating` (1-5)
   - **Categorical**: `validation_passed` (pass/fail), `user_thumbs` (up/down), `user_feedback` (to_be_reviewed)
   - **Boolean**: (not used in this example, but could be used for simple yes/no checks)

4. **Reasoning Field**:
   - Used for validation error messages
   - Used for user comments (qualitative feedback)
   - Searchable and filterable in Datadog

5. **Proper URL Format**:
   - LLMObs URL: `/llm/traces/trace/{trace_id_hex}?spanId={span_id_decimal}`
   - Not the same as APM URL (`/apm/trace/`)

6. **Real-Time Feedback Loop**:
   - Users can rate extractions immediately
   - Feedback linked to specific LLM operations
   - Enables tracking model quality over time

#### Datadog Queries for Production Monitoring

```
# View all validation failures
@label:validation_passed @value:fail

# User ratings distribution
@label:user_rating @ml_app:vote-extractor

# Comments needing review
@label:user_feedback @value:to_be_reviewed

# Low validation scores
@label:validation_score @value:<0.5

# Negative feedback correlation
(@label:user_thumbs @value:down) OR (@label:user_rating @value:<=2)
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

### 4a. **Use the `reasoning` Field for Explanations**

The `reasoning` tag is the **Datadog-recommended field** for providing explanations or justifications for evaluation values. Use it for:

- User feedback comments
- Automated evaluation explanations
- Failure reasons
- Quality assessment justifications

✅ **Good**: Using reasoning for user comments
```python
# User provides rating with comment
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="vote-extraction-app",
    label="user_rating",
    metric_type="score",
    value=4,  # 4 out of 5 stars
    tags={
        "reasoning": "Extraction was accurate but missed one candidate name",
        "feedback_source": "user_ui",
        "user_id": "user_123"
    }
)
```

✅ **Good**: Using reasoning for automated checks
```python
# Automated quality check with explanation
LLMObs.submit_evaluation(
    span_context=span_context,
    ml_app="content-creator-app",
    label="toxicity_check",
    metric_type="categorical",
    value="unsafe",
    tags={
        "reasoning": "Detected profanity in paragraph 3",
        "detector_version": "v2.0",
        "confidence": "high"
    }
)
```

**Why use `reasoning`?**
- ✅ Follows Datadog best practices
- ✅ Structured and queryable in Datadog UI
- ✅ Searchable with `@tags.reasoning:*`
- ✅ Provides context for evaluation decisions

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

| Aspect | Score | Boolean | Categorical |
|--------|-------|---------|-------------|
| **Data Type** | Numeric (float/int) | Boolean (true/false) | String (label) |
| **Use For** | Measurements, ratings, continuous metrics | Simple true/false checks | Classifications, multi-option labels |
| **Aggregations** | avg, min, max, sum, percentiles | count true/false, % true | count, distribution by category |
| **Alerts** | Threshold-based (`< value`) | Count-based (`false > N`) | Count-based (`"fail" > N`) |
| **Examples** | 4.5, 0.87, 125, 99.9 | true, false | "pass", "fail", "relevant", "safe" |
| **Visualization** | Line charts, gauges, heatmaps | Boolean bars, percentage gauges | Pie charts, bar charts, top lists |

### Key Takeaways

1. ✅ Use **`score`** for numeric, measurable quantities
2. ✅ Use **`boolean`** for simple true/false evaluations
3. ✅ Use **`categorical`** for multi-option classifications or labels
4. ✅ Standardize your labels and value ranges
5. ✅ Add context with tags (including `reasoning` for explanations)
6. ✅ Submit multiple evaluations per span for comprehensive analysis
7. ✅ Choose scales appropriate for your use case
8. ✅ Document your evaluation standards for team consistency

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

