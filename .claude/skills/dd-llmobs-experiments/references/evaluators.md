# Evaluator Patterns Reference

Reference: [01-basic-experiments.ipynb](https://github.com/DataDog/llm-observability/blob/main/experiments/notebooks/01-basic-experiments.ipynb)

## Return Types

| Type | Return | Aggregation in UI |
|---|---|---|
| Boolean | `True` / `False` | Ratio of True |
| Score | `float` | Average |
| Categorical | `str` | Mode (most frequent) |
| JSON | `dict` | N/A |

## Function-based Evaluators

Signature: `(input_data, output_data, expected_output) -> bool | float | str | EvaluatorResult`

The evaluator function name becomes the evaluator name in the Datadog UI.

```python
# Boolean: exact match
def exact_match(input_data, output_data, expected_output):
    return expected_output == output_data

# Boolean: contains answer
def contains_answer(input_data, output_data, expected_output):
    return expected_output in output_data

# Boolean: case-insensitive match
def case_insensitive_match(input_data, output_data, expected_output):
    return str(output_data).lower().strip() == str(expected_output).lower().strip()

# Score: Jaccard overlap
def overlap(input_data, output_data, expected_output):
    out_set = set(str(output_data))
    exp_set = set(str(expected_output))
    intersection = len(out_set & exp_set)
    union = len(out_set | exp_set)
    return intersection / union if union > 0 else 0.0

# Score: keyword coverage
def keyword_coverage(input_data, output_data, expected_output):
    keywords = expected_output if isinstance(expected_output, list) else [expected_output]
    output_lower = str(output_data).lower()
    matches = sum(1 for kw in keywords if kw.lower() in output_lower)
    return matches / len(keywords) if keywords else 0.0

# Categorical: classify output quality
def quality_tier(input_data, output_data, expected_output):
    score = len(set(str(output_data)) & set(str(expected_output))) / max(len(set(str(expected_output))), 1)
    if score >= 0.9:
        return "excellent"
    elif score >= 0.7:
        return "good"
    elif score >= 0.4:
        return "fair"
    return "poor"
```

## EvaluatorResult (Rich Results)

Use `EvaluatorResult` to capture reasoning, assessment, and tags alongside the score:

```python
from ddtrace.llmobs import EvaluatorResult

def contains_answer(input_data, output_data, expected_output):
    found = expected_output in output_data
    string_index = output_data.find(expected_output)
    reasoning = f"found at index {string_index}" if found else "not found"
    return EvaluatorResult(
        value=found,                               # bool, float, str, or dict
        reasoning=reasoning,                       # explanation (shown in UI)
        assessment="pass" if found else "fail",    # "pass" or "fail"
        tags={"task": "contains_answer"},           # optional tags dict
    )
```

`EvaluatorResult` fields:
- `value` (required): the score -- `bool`, `float`, `str`, or `dict`
- `reasoning` (optional): explanation string
- `assessment` (optional): `"pass"` or `"fail"`
- `metadata` (optional): additional metadata dict
- `tags` (optional): tags dict for filtering in the UI

## Evaluators with Structured Outputs

When the task returns a dict, access fields from `output_data` and `expected_output`:

```python
def exact_match(input_data, output_data, expected_output):
    return expected_output["labels"] == output_data["response"]

def false_confidence(input_data, output_data, expected_output):
    return output_data["certainty"] > 0.8 and expected_output["labels"] != output_data["response"]
```

## Class-based Evaluators

Subclass `BaseEvaluator` for reusable evaluators with configuration:

```python
from ddtrace.llmobs import BaseEvaluator, EvaluatorContext, EvaluatorResult

class SemanticSimilarityEvaluator(BaseEvaluator):
    def __init__(self, threshold: float = 0.8):
        super().__init__(name="semantic_similarity")
        self.threshold = threshold

    def evaluate(self, context: EvaluatorContext) -> EvaluatorResult:
        score = compute_similarity(context.output_data, context.expected_output)
        return EvaluatorResult(
            value=score,
            reasoning=f"Similarity: {score:.2f}, threshold: {self.threshold}",
            assessment="pass" if score >= self.threshold else "fail",
        )

evaluator = SemanticSimilarityEvaluator(threshold=0.85)
```

## Summary Evaluators

Run after all row-level evaluators complete. Receive aggregated results across the entire dataset.

### Function-based

Signature: `(inputs, outputs, expected_outputs, evaluators_results) -> bool | float | str | dict`

`evaluators_results` is a dict keyed by evaluator function name; each value is a list of results.

```python
def num_exact_matches(inputs, outputs, expected_outputs, evaluators_results):
    return evaluators_results["exact_match"].count(True)

def pass_rate(inputs, outputs, expected_outputs, evaluators_results):
    results = evaluators_results["exact_match"]
    return sum(1 for r in results if r) / len(results) if results else 0.0

def average_overlap(inputs, outputs, expected_outputs, evaluators_results):
    scores = evaluators_results["overlap"]
    return sum(scores) / len(scores) if scores else 0.0
```

### Class-based

```python
from ddtrace.llmobs import BaseSummaryEvaluator, SummaryEvaluatorContext

class AverageScoreEvaluator(BaseSummaryEvaluator):
    def __init__(self, target_evaluator: str):
        super().__init__(name="average_score")
        self.target_evaluator = target_evaluator

    def evaluate(self, context: SummaryEvaluatorContext):
        scores = context.evaluation_results.get(self.target_evaluator, [])
        return sum(scores) / len(scores) if scores else None
```

## LLM-as-a-Judge Pattern

Use another LLM to evaluate outputs:

```python
from ddtrace.llmobs import EvaluatorResult

def llm_judge(input_data, output_data, expected_output):
    prompt = f"""Rate this answer on a scale of 1-5.
Question: {input_data}
Expected: {expected_output}
Actual: {output_data}
Respond with JSON: {{"score": <1-5>, "reasoning": "<explanation>"}}"""

    response = call_llm(prompt)
    parsed = json.loads(response)

    return EvaluatorResult(
        value=parsed["score"] / 5.0,
        reasoning=parsed["reasoning"],
        assessment="pass" if parsed["score"] >= 4 else "fail",
        tags={"judge_model": "gemini-2.5-flash"},
    )
```

## Vote Extraction Evaluators (Project-Specific)

Example evaluators for Thai election vote extraction:

```python
import json

def json_valid(input_data, output_data, expected_output):
    try:
        if isinstance(output_data, str):
            json.loads(output_data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def field_accuracy(input_data, output_data, expected_output):
    if isinstance(output_data, str):
        output_data = json.loads(output_data)
    if isinstance(expected_output, str):
        expected_output = json.loads(expected_output)

    if not isinstance(output_data, dict) or not isinstance(expected_output, dict):
        return 0.0

    all_keys = set(expected_output.keys())
    if not all_keys:
        return 1.0
    matching = sum(1 for k in all_keys if output_data.get(k) == expected_output.get(k))
    return matching / len(all_keys)
```
