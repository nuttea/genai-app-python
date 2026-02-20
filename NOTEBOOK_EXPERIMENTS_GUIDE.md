# LLMObs Experiments Guide - gemini-ss5_18_bigquery_drive.ipynb

## 🎉 What's New

The notebook has been updated to support **Datadog LLMObs Experiments** with:
- ✅ Dataset pulling from LLMObs
- ✅ Multiple model configurations with thinking modes
- ✅ Focused evaluators for ballot/voter statistics
- ✅ Automated experiment execution with @workflow

## 📚 New Components

### 1. **Dataset Integration**
```python
# Pulls dataset from Datadog LLMObs
dataset = LLMObs.pull_dataset(
    dataset_name="ss5_18_nuttee",
    project_name=LLMOBS_PROJECT_NAME,
)
```

### 2. **Experiment Configuration**
```python
@dataclass
class ExperimentConfig:
    model: str
    temperature: float = 0.0
    max_tokens: int = 8192
    thinking_mode: Optional[Literal["LOW", "HIGH"]] = None
```

**Predefined configurations:**
- `gemini-3-flash-preview` (thinking: LOW)
- `gemini-3-flash-preview` (thinking: HIGH)
- `gemini-3-pro-preview` (thinking: LOW)
- `gemini-3-pro-preview` (thinking: HIGH)
- `gemini-2.5-flash` (no thinking mode)

### 3. **Updated extract_from_drive_url()**
```python
@task
def extract_from_drive_url(
    file_info: dict,
    config: Optional[ExperimentConfig] = None,
) -> list[dict]:
    """
    Now accepts ExperimentConfig for model/temperature/thinking_mode.
    Automatically tracked by ddtrace LLMObs.
    """
```

### 4. **Evaluator Functions**

Three focused evaluators that measure extraction accuracy:

#### `evaluate_ballot_statistics()`
Checks:
- ballots_allocated, ballots_used
- good_ballots, bad_ballots, no_vote_ballots
- ballots_remaining
- Validation: used = good + bad + no_vote

#### `evaluate_voter_statistics()`
Checks:
- eligible_voters
- present_voters

#### `evaluate_total_votes()`
Checks:
- Sum of all vote counts
- Matches total_votes_recorded
- Matches expected value

**Score calculation:**
- `score`: 0.0 to 1.0 (percentage of correct fields)
- `label`: "pass" or "fail"
- `details`: Extracted vs expected values

### 5. **Experiment Execution**

```python
@workflow
def run_experiment(config: ExperimentConfig, dataset_item: Dict) -> Dict:
    """
    Runs extraction with config and evaluates results.
    Automatically logs to Datadog LLMObs.
    """

def run_all_experiments(dataset, configs: List[ExperimentConfig], max_items: int = None):
    """
    Runs all configs across all dataset items.
    Returns results with evaluation scores.
    """
```

## 🚀 How to Use

### Step 1: Run Setup Cells
Execute cells in order until you reach the dataset pull:
```python
dataset = LLMObs.pull_dataset(
    dataset_name="ss5_18_nuttee",
    project_name=LLMOBS_PROJECT_NAME,
)
# Output: ✅ Dataset loaded: X items
```

### Step 2: Review Experiment Configs
The predefined `EXPERIMENT_CONFIGS` list contains 5 configurations ready to test.

### Step 3: Run Experiments
```python
# Run on first 5 dataset items
results = run_all_experiments(
    dataset, 
    EXPERIMENT_CONFIGS, 
    max_items=5
)

# Run on all dataset items
results = run_all_experiments(
    dataset, 
    EXPERIMENT_CONFIGS
)
```

### Step 4: View Results
Each experiment logs to Datadog LLMObs with:
- Model configuration (model, temperature, thinking_mode)
- Evaluation scores for each metric
- Pass/fail labels
- Detailed comparison of extracted vs expected values

### Step 5: Analyze in Datadog
Visit your Datadog LLMObs dashboard to:
- Compare model performance across configs
- Identify which thinking mode works best
- Track evaluation metrics over time
- Debug failed extractions

## 📊 What Gets Evaluated

### ✅ Evaluated (Focus Areas)
- **Ballot Statistics**: All ballot counts and validation
- **Voter Statistics**: Eligible and present voters
- **Total Votes**: Sum validation and accuracy

### ❌ NOT Evaluated (Excluded)
- Officials/committee members names
- Location data (Province, District, Sub-district, etc.)
- Polling station numbers, Village numbers
- Candidate names, Party names

**Reason**: Focus on numerical accuracy and data integrity. Names and locations are less critical for testing model extraction capabilities.

## 🔍 Evaluator Scoring

Each evaluator returns:
```python
{
    "score": 0.85,  # 0.0 to 1.0
    "label": "pass",  # "pass" or "fail"
    "details": {
        "correct_fields": 6,
        "total_fields": 7,
        "extracted": {...},
        "expected": {...},
        # ... metric-specific details
    }
}
```

**Pass criteria:**
- `ballot_statistics`: ≥ 85% fields correct
- `voter_statistics`: 100% fields correct
- `total_votes`: 100% correct (both checks must pass)

## 💡 Tips

1. **Start small**: Use `max_items=5` to test quickly
2. **Monitor Datadog**: Watch experiments in real-time via LLMObs dashboard
3. **Compare thinking modes**: See if HIGH vs LOW makes a difference
4. **Check token usage**: LLMObs tracks token costs per experiment
5. **Debug failures**: Use `details` in evaluation results to see what went wrong

## 🐛 Troubleshooting

### Dataset not found
```python
# Check dataset name and project
dataset = LLMObs.pull_dataset(
    dataset_name="ss5_18_nuttee",  # Verify this matches your dataset
    project_name=LLMOBS_PROJECT_NAME,  # Check project name
)
```

### Thinking mode error
```python
# Only gemini-3-* models support thinking_mode
config = ExperimentConfig(
    model="gemini-3-flash-preview",  # ✅ Supports thinking_mode
    thinking_mode="LOW"
)

config = ExperimentConfig(
    model="gemini-2.5-flash",  # ❌ Does NOT support thinking_mode
    thinking_mode=None  # Must be None for gemini-2.5
)
```

### Extract function not found
Make sure you've executed all cells including:
- Imports
- Pydantic schemas
- LLMObs enable
- ExperimentConfig definition
- extract_from_drive_url function

## 🎯 Expected Output

```
🚀 Running experiments:
   Configurations: 5
   Dataset items: 5
   Total experiments: 25

================================================================================
Config 1/5: gemini-3-flash-preview (thinking: LOW)
================================================================================

  [1/5] Processing: เขตเลือกตั้งที่ 3/อำเภอโพธิ์ประทับช้าง/...
     Evaluations:
       ✅ ballot_statistics: 100.00% (pass)
       ✅ voter_statistics: 100.00% (pass)
       ✅ total_votes: 100.00% (pass)

  [2/5] Processing: ...

================================================================================
✅ Experiments completed: 25 successful
================================================================================
```

## 📈 Next Steps

1. **Analyze results** in Datadog LLMObs dashboard
2. **Compare configurations** to find optimal settings
3. **Expand dataset** with more test cases
4. **Refine evaluators** based on insights
5. **Deploy best config** to production

---

**Need help?** Check the Datadog LLMObs documentation or the notebook comments for more details.
