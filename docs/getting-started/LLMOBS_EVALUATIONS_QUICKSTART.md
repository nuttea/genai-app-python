# LLMObs Evaluations Quick Start

Quick reference for implementing evaluations, user feedback, and experiments in Datadog LLMObs.

## 🎯 Quick Commands

### Enable Ragas Evaluators
```bash
export DD_LLMOBS_EVALUATORS="ragas_faithfulness,ragas_answer_relevancy,ragas_context_precision"
export DD_LLMOBS_ENABLED=1
export DD_LLMOBS_ML_APP="vote-extractor"
```

### Install Dependencies
```bash
pip install ragas==0.1.21 ddtrace>=3.0.0
```

## 📊 Code Snippets

### 1. Submit Score Evaluation
```python
from ddtrace.llmobs import LLMObs

span_context = LLMObs.export_span()
LLMObs.submit_evaluation_for(
    span=span_context,
    ml_app="vote-extractor",
    label="quality_score",
    metric_type="score",
    value=8.5,
    tags={"evaluator": "custom"}
)
```

### 2. Submit Categorical Evaluation
```python
LLMObs.submit_evaluation_for(
    span=span_context,
    ml_app="vote-extractor",
    label="output_quality",
    metric_type="categorical",
    value="excellent",
    tags={"auto_evaluated": "true"}
)
```

### 3. User Feedback (Thumbs Up/Down)
```python
# Backend API
@router.post("/feedback")
async def submit_feedback(span_id: str, trace_id: str, feedback: str):
    LLMObs.submit_evaluation_for(
        span={"span_id": span_id, "trace_id": trace_id},
        ml_app="vote-extractor",
        label="user_feedback",
        metric_type="categorical",
        value=feedback,  # "thumbs_up" or "thumbs_down"
        tags={"source": "user_interface"}
    )
```

### 4. Annotate for Golden Dataset
```python
with LLMObs.annotation_context(
    tags={
        "golden_dataset": "true",
        "quality": "high",
        "validated": "pending"
    }
):
    result = llm_call()
```

### 5. RAG Context for Ragas
```python
with LLMObs.annotation_context(
    prompt={
        "template": "Answer using context: {{context}}",
        "variables": {"context": reference_docs}
    },
    tags={"rag_enabled": "true"}
):
    result = llm_call()
```

## 🔬 Experiment Examples

### A/B Test Different Prompts
```python
for prompt_version in ["v1", "v2"]:
    with LLMObs.annotation_context(
        tags={
            "experiment": "prompt_test",
            "version": prompt_version
        }
    ):
        result = extract_with_prompt(prompts[prompt_version])
```

### Compare Models
```python
models = ["gemini-pro", "gemini-2.5-flash"]
for model in models:
    with LLMObs.annotation_context(tags={"model": model}):
        result = extract_with_model(model)
```

## 📈 View Results in Datadog

1. Go to **LLM Observability** → **Traces**
2. Filter: `ml_app:vote-extractor`
3. View **Custom Evaluations** tab
4. See scores, categories, and Ragas metrics

## 🎯 Evaluation Types

| Type | Use Case | Example Value |
|------|----------|---------------|
| **score** | Numeric ratings | 8.5, 0.95, 7 |
| **categorical** | Classifications | "excellent", "good", "poor" |
| **Ragas** | RAG evaluation | Auto-calculated scores |

## 🏷️ Common Labels

- `quality_score` - Overall quality (0-10)
- `user_feedback` - Thumbs up/down
- `output_classification` - Category
- `extraction_accuracy` - Accuracy score
- `user_quality_rating` - Star rating (1-5)

## 📚 Full Documentation

See `docs/monitoring/LLMOBS_NEXT_STEPS.md` for:
- Complete implementation examples
- Dataset management
- Advanced experiments
- Phase-by-phase roadmap

## 🚀 Quick Start

1. **Add evaluation to your code** (5 min)
2. **Test with sample data** (10 min)
3. **View in Datadog UI** (5 min)
4. **Iterate and improve** (ongoing)

---

**Total setup time: ~20 minutes to first evaluation!** ⚡

