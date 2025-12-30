# LLMObs Next Steps: Evaluations, Datasets & Experiments

Comprehensive guide for implementing advanced LLM Observability features in your GenAI application.

## Overview

This guide covers three key areas:
1. **Evaluations** - Custom evaluators, user feedback, quality annotations
2. **Datasets** - Managing test data and golden datasets
3. **Experiments** - Running A/B tests with Ragas and evaluation frameworks

---

## 1. Evaluations

### 1.1 Custom Evaluations

Custom evaluations allow you to measure and track LLM output quality using your own metrics.

#### Score-Based Evaluations

```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm

def calculate_quality_score(response: str, expected: str) -> float:
    """Custom quality scoring logic"""
    # Example: simple similarity score
    # In production, use more sophisticated metrics
    score = len(set(response.split()) & set(expected.split())) / len(set(expected.split()))
    return round(score * 10, 2)  # Scale to 0-10

@llm(model_name="gemini-2.5-flash", name="extract_votes", model_provider="vertexai")
def extract_vote_data(image_data):
    # Your LLM call
    result = vertex_ai_client.generate_content(...)

    # Export span context for evaluation
    span_context = LLMObs.export_span()

    # Submit custom evaluation
    LLMObs.submit_evaluation_for(
        span=span_context,
        ml_app="vote-extractor",
        label="extraction_quality",
        metric_type="score",
        value=calculate_quality_score(result, expected_data),
        tags={
            "evaluation_provider": "custom",
            "form_type": "constituency",
            "version": "v1.0"
        }
    )

    return result
```

#### Categorical Evaluations

```python
def classify_output_quality(response: dict) -> str:
    """Classify output into quality categories"""
    if not response.get("vote_results"):
        return "failed"
    elif len(response["vote_results"]) < 5:
        return "incomplete"
    elif all(r.get("vote_count") is not None for r in response["vote_results"]):
        return "excellent"
    else:
        return "good"

@llm(model_name="gemini-2.5-flash", name="extract_votes", model_provider="vertexai")
def extract_vote_data(image_data):
    result = vertex_ai_client.generate_content(...)
    span_context = LLMObs.export_span()

    LLMObs.submit_evaluation_for(
        span=span_context,
        ml_app="vote-extractor",
        label="output_classification",
        metric_type="categorical",
        value=classify_output_quality(result),
        tags={
            "evaluation_type": "automated",
            "classifier_version": "v2.0"
        }
    )

    return result
```

### 1.2 User Feedback Integration

Capture user feedback (thumbs up/down, comments) and associate with traces.

#### Backend API Endpoint for Feedback

```python
# app/api/v1/endpoints/feedback.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ddtrace.llmobs import LLMObs

router = APIRouter()

class FeedbackRequest(BaseModel):
    span_id: str
    trace_id: str
    feedback_type: str  # "thumbs_up", "thumbs_down"
    comment: str | None = None
    quality_score: int | None = None  # 1-5 stars
    tags: dict | None = None

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for a specific LLM interaction"""
    try:
        # Reconstruct span context
        span_context = {
            "span_id": feedback.span_id,
            "trace_id": feedback.trace_id
        }

        # Submit feedback as evaluation
        LLMObs.submit_evaluation_for(
            span=span_context,
            ml_app="vote-extractor",
            label="user_feedback",
            metric_type="categorical",
            value=feedback.feedback_type,
            tags={
                "user_comment": feedback.comment or "",
                "quality_score": feedback.quality_score or 0,
                "feedback_source": "user_interface",
                **(feedback.tags or {})
            }
        )

        # Optionally submit numeric score separately
        if feedback.quality_score:
            LLMObs.submit_evaluation_for(
                span=span_context,
                ml_app="vote-extractor",
                label="user_quality_rating",
                metric_type="score",
                value=feedback.quality_score,
                tags={"feedback_type": feedback.feedback_type}
            )

        return {"status": "success", "message": "Feedback recorded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Frontend Integration (Streamlit)

```python
# frontend/streamlit/pages/1_🗳️_Vote_Extractor.py
import streamlit as st
import requests

def display_extraction_results_with_feedback(result, span_id, trace_id):
    """Display results with feedback collection"""
    st.json(result)

    # Feedback section
    st.markdown("---")
    st.subheader("📝 How was this extraction?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👍 Good"):
            submit_feedback(span_id, trace_id, "thumbs_up")
            st.success("Thanks for your feedback!")

    with col2:
        if st.button("👎 Poor"):
            submit_feedback(span_id, trace_id, "thumbs_down")
            st.success("Thanks for your feedback!")

    # Detailed feedback
    with st.expander("Provide detailed feedback"):
        quality_score = st.slider("Quality (1-5 stars)", 1, 5, 3)
        comment = st.text_area("Comments (optional)")

        if st.button("Submit Detailed Feedback"):
            submit_feedback(
                span_id, trace_id,
                "thumbs_up" if quality_score >= 3 else "thumbs_down",
                comment=comment,
                quality_score=quality_score
            )
            st.success("Detailed feedback submitted!")

def submit_feedback(span_id, trace_id, feedback_type, comment=None, quality_score=None):
    """Submit feedback to backend API"""
    api_url = f"{st.session_state.get('api_base_url')}/api/v1/feedback"

    payload = {
        "span_id": span_id,
        "trace_id": trace_id,
        "feedback_type": feedback_type,
        "comment": comment,
        "quality_score": quality_score,
        "tags": {
            "user_session": st.session_state.get("session_id"),
            "page": "vote_extractor"
        }
    }

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers={"X-API-Key": st.secrets.get("API_KEY")}
        )
        response.raise_for_status()
    except Exception as e:
        st.error(f"Failed to submit feedback: {e}")
```

### 1.3 Annotating Spans for Golden Datasets

Mark high-quality results as potential golden dataset entries.

```python
from ddtrace.llmobs import LLMObs

def extract_with_annotation(image_data, expected_result=None):
    """Extract data and annotate for dataset creation"""

    with LLMObs.annotation_context(
        tags={
            "dataset_candidate": "true",  # Mark as potential golden dataset entry
            "form_type": "constituency",
            "validation_status": "pending"
        }
    ):
        result = vertex_ai_client.generate_content(...)

        # If ground truth available, evaluate accuracy
        if expected_result:
            accuracy = calculate_accuracy(result, expected_result)
            span_context = LLMObs.export_span()

            # Mark high-quality results for golden dataset
            if accuracy > 0.95:
                LLMObs.submit_evaluation_for(
                    span=span_context,
                    ml_app="vote-extractor",
                    label="golden_dataset_candidate",
                    metric_type="categorical",
                    value="approved",
                    tags={
                        "accuracy": accuracy,
                        "manual_review": "recommended",
                        "dataset_category": "high_quality"
                    }
                )

        return result
```

---

## 2. Dataset Management

While Datadog LLMObs doesn't have a built-in dataset management UI, you can implement your own system using tags and evaluations.

### 2.1 Dataset Structure

```python
# app/models/datasets.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DatasetEntry(BaseModel):
    """Single entry in a golden dataset"""
    id: str
    input_data: dict  # Image bytes, metadata, etc.
    expected_output: dict  # Ground truth
    span_id: Optional[str] = None  # Link to actual LLM trace
    trace_id: Optional[str] = None
    tags: dict = {}
    created_at: datetime
    validated: bool = False

class Dataset(BaseModel):
    """Collection of test/golden data"""
    name: str
    description: str
    version: str
    entries: List[DatasetEntry]
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime
```

### 2.2 Dataset Management API

```python
# app/api/v1/endpoints/datasets.py
from fastapi import APIRouter, HTTPException
from typing import List
import json

router = APIRouter()

# Simple file-based storage (replace with database in production)
DATASET_STORAGE_PATH = "data/datasets"

@router.get("/datasets")
async def list_datasets() -> List[dict]:
    """List all available datasets"""
    datasets = []
    for file in Path(DATASET_STORAGE_PATH).glob("*.json"):
        with open(file) as f:
            datasets.append(json.load(f))
    return datasets

@router.post("/datasets")
async def create_dataset(dataset: Dataset):
    """Create a new dataset"""
    file_path = Path(DATASET_STORAGE_PATH) / f"{dataset.name}_{dataset.version}.json"

    if file_path.exists():
        raise HTTPException(status_code=400, detail="Dataset already exists")

    with open(file_path, "w") as f:
        json.dump(dataset.dict(), f, indent=2, default=str)

    return {"status": "created", "name": dataset.name}

@router.get("/datasets/{name}/{version}")
async def get_dataset(name: str, version: str):
    """Get a specific dataset"""
    file_path = Path(DATASET_STORAGE_PATH) / f"{name}_{version}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")

    with open(file_path) as f:
        return json.load(f)

@router.post("/datasets/{name}/{version}/entries")
async def add_entry_to_dataset(name: str, version: str, entry: DatasetEntry):
    """Add an entry to a dataset"""
    file_path = Path(DATASET_STORAGE_PATH) / f"{name}_{version}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")

    with open(file_path, "r+") as f:
        dataset = json.load(f)
        dataset["entries"].append(entry.dict(default=str))
        dataset["updated_at"] = datetime.utcnow().isoformat()
        f.seek(0)
        json.dump(dataset, f, indent=2, default=str)
        f.truncate()

    return {"status": "added", "entry_id": entry.id}

@router.post("/datasets/{name}/{version}/from-trace")
async def add_trace_to_dataset(name: str, version: str, span_id: str, trace_id: str):
    """Add a trace result to dataset as golden data"""
    # Fetch trace from Datadog (use Datadog API)
    # Extract input/output from trace
    # Add to dataset

    # This would require Datadog API integration
    # For now, return placeholder
    return {
        "status": "added",
        "message": "Trace added to dataset",
        "span_id": span_id,
        "trace_id": trace_id
    }
```

### 2.3 Frontend Dataset Manager (Streamlit Page)

```python
# frontend/streamlit/pages/3_📊_Dataset_Manager.py
import streamlit as st
import requests
import pandas as pd

st.title("📊 Dataset Manager")

# Initialize Datadog RUM
from utils.datadog_rum import initialize_rum
initialize_rum()

API_BASE_URL = st.session_state.get("api_base_url", "http://localhost:8000")

# List datasets
st.header("Available Datasets")
response = requests.get(f"{API_BASE_URL}/api/v1/datasets")
if response.ok:
    datasets = response.json()
    if datasets:
        df = pd.DataFrame([
            {
                "Name": d["name"],
                "Version": d["version"],
                "Entries": len(d["entries"]),
                "Created": d["created_at"],
                "Updated": d["updated_at"]
            }
            for d in datasets
        ])
        st.dataframe(df)
    else:
        st.info("No datasets found")
else:
    st.error("Failed to load datasets")

# Create new dataset
st.header("Create New Dataset")
with st.form("create_dataset"):
    name = st.text_input("Dataset Name", "vote_extraction_test")
    version = st.text_input("Version", "v1.0")
    description = st.text_area("Description")

    if st.form_submit_button("Create Dataset"):
        payload = {
            "name": name,
            "version": version,
            "description": description,
            "entries": [],
            "metadata": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = requests.post(
            f"{API_BASE_URL}/api/v1/datasets",
            json=payload
        )

        if response.ok:
            st.success(f"Dataset '{name}' created!")
            st.rerun()
        else:
            st.error(f"Failed to create dataset: {response.text}")

# View and manage dataset entries
st.header("Manage Dataset Entries")
selected_dataset = st.selectbox(
    "Select Dataset",
    options=[f"{d['name']}_{d['version']}" for d in datasets] if response.ok and datasets else []
)

if selected_dataset:
    name, version = selected_dataset.split("_")
    response = requests.get(f"{API_BASE_URL}/api/v1/datasets/{name}/{version}")

    if response.ok:
        dataset = response.json()
        st.subheader(f"Dataset: {dataset['name']} ({dataset['version']})")
        st.write(dataset['description'])
        st.metric("Total Entries", len(dataset['entries']))

        if dataset['entries']:
            for entry in dataset['entries']:
                with st.expander(f"Entry {entry['id']}"):
                    st.json(entry)
```

---

## 3. Experiments with Ragas

Datadog LLMObs natively supports Ragas for RAG evaluation.

### 3.1 Ragas Setup

```bash
pip install ragas==0.1.21 ddtrace>=3.0.0
```

### 3.2 Enable Ragas Evaluators

```python
import os

# Enable Ragas evaluators
os.environ["DD_LLMOBS_EVALUATORS"] = "ragas_faithfulness,ragas_answer_relevancy,ragas_context_precision"
os.environ["DD_API_KEY"] = "your_dd_api_key"
os.environ["DD_SITE"] = "datadoghq.com"
os.environ["DD_LLMOBS_ENABLED"] = "1"
os.environ["DD_LLMOBS_ML_APP"] = "vote-extractor"
```

### 3.3 Instrument with RAG Context

```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm

@llm(model_name="gemini-2.5-flash", name="extract_with_context", model_provider="vertexai")
def extract_with_rag_context(image_data, reference_docs):
    """Extract votes with RAG context for Ragas evaluation"""

    # Prepare prompt with context
    prompt = f"""
    Reference documentation:
    {reference_docs}

    Extract vote data from the following image...
    """

    # Use annotation_context to provide RAG context for Ragas
    with LLMObs.annotation_context(
        prompt={
            "template": "Extract vote data with reference: {{reference}}",
            "variables": {"reference": reference_docs}
        },
        tags={
            "experiment": "rag_evaluation",
            "rag_enabled": "true"
        }
    ):
        result = vertex_ai_client.generate_content(
            contents=[image_data, prompt]
        )

    return result
```

### 3.4 Running Experiments

```python
# experiments/ragas_evaluation.py
from ddtrace import tracer
from ddtrace.llmobs import LLMObs
import json

def run_ragas_experiment(dataset_name: str, version: str):
    """Run Ragas evaluation on a dataset"""

    # Load dataset
    with open(f"data/datasets/{dataset_name}_{version}.json") as f:
        dataset = json.load(f)

    results = []

    for entry in dataset["entries"]:
        # Extract with RAG context
        result = extract_with_rag_context(
            entry["input_data"],
            entry.get("reference_docs", "")
        )

        # Ragas will automatically evaluate:
        # - Faithfulness (is answer faithful to context?)
        # - Answer Relevancy (is answer relevant to question?)
        # - Context Precision (is context relevant?)

        results.append({
            "entry_id": entry["id"],
            "result": result,
            "expected": entry["expected_output"]
        })

    return results

if __name__ == "__main__":
    # Run experiment
    results = run_ragas_experiment("vote_extraction_test", "v1.0")

    # Results will be visible in Datadog LLMObs UI
    # under Custom Evaluations
    print(f"Experiment complete. Check Datadog for Ragas evaluation scores.")
```

### 3.5 A/B Testing Different Prompts

```python
# experiments/prompt_comparison.py
def run_prompt_ab_test():
    """Compare two different prompt strategies"""

    prompts = {
        "prompt_a": """Extract all vote data from the image in JSON format...""",
        "prompt_b": """Analyze the election form and extract:
        1. Form information
        2. Vote results
        3. Ballot statistics..."""
    }

    for prompt_name, prompt_template in prompts.items():
        with LLMObs.annotation_context(
            tags={
                "experiment": "prompt_comparison",
                "prompt_version": prompt_name
            }
        ):
            result = extract_vote_data_with_prompt(image_data, prompt_template)

            # Results will be tagged with prompt_version
            # allowing comparison in Datadog
```

---

## 4. Implementation Roadmap

### Phase 1: Basic Evaluations (Week 1-2)
- [ ] Implement custom score evaluators
- [ ] Add categorical quality classifiers
- [ ] Create feedback API endpoint
- [ ] Add basic feedback UI in Streamlit

### Phase 2: User Feedback Integration (Week 3-4)
- [ ] Export span context to frontend
- [ ] Implement thumbs up/down UI
- [ ] Add comment system
- [ ] Submit feedback to Datadog via API

### Phase 3: Dataset Management (Week 5-6)
- [ ] Design dataset schema
- [ ] Implement dataset CRUD API
- [ ] Create dataset manager UI
- [ ] Add trace-to-dataset functionality

### Phase 4: Ragas Integration (Week 7-8)
- [ ] Set up Ragas evaluators
- [ ] Instrument with RAG context
- [ ] Run baseline experiments
- [ ] Compare with/without RAG

### Phase 5: Advanced Experiments (Week 9-10)
- [ ] Implement A/B testing framework
- [ ] Compare multiple prompts
- [ ] Test different models
- [ ] Create experiment dashboard

---

## 5. Monitoring & Visualization

### View Evaluations in Datadog

1. Go to **LLM Observability** → **Traces**
2. Filter by `ml_app:vote-extractor`
3. Select a trace
4. View **Custom Evaluations** section
5. See your custom metrics and Ragas scores

### Create Dashboards

Create custom dashboards to monitor:
- Average quality scores over time
- User feedback distribution
- Ragas evaluation trends
- Experiment comparisons

### Set Up Alerts

Alert on:
- Quality score drops below threshold
- High rate of negative feedback
- Ragas faithfulness score < 0.7
- Evaluation failures

---

## 6. References

- [Datadog LLM Observability Evaluations](https://docs.datadoghq.com/llm_observability/evaluations/)
- [Submit Custom Evaluations](https://docs.datadoghq.com/llm_observability/evaluations/submit_evaluations/)
- [Ragas Integration](https://docs.datadoghq.com/llm_observability/evaluations/ragas_evaluations/)
- [Ragas Quickstart](https://docs.datadoghq.com/llm_observability/guide/ragas_quickstart/)
- [LLMObs Python SDK](https://docs.datadoghq.com/llm_observability/setup/sdk/python/)

---

## Next Steps

1. **Start with Phase 1**: Implement basic evaluations
2. **Iterate**: Add features incrementally
3. **Monitor**: Use Datadog to track improvements
4. **Experiment**: Run A/B tests to optimize
5. **Scale**: Expand to more use cases

**Ready to enhance your LLM observability!** 🚀
