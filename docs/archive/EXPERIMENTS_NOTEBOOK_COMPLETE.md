# Experiments Section Added to Jupyter Notebook ✅

**Date**: January 4, 2026  
**Status**: ✅ **COMPLETE** - Comprehensive Experiments section added to the dataset preparation notebook

---

## Executive Summary

Successfully added a complete **Experiments** section (Step 4) to the Jupyter notebook `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`. The notebook now provides end-to-end workflow from dataset creation to systematic LLM evaluation using Datadog LLMObs Experiments.

---

## What Was Added

### New Section: Step 4 - Run Experiments (8 cells)

#### 4.1 Load Dataset from Datadog
- **Cell Type**: Markdown + Code
- **Purpose**: Pull dataset from Datadog using `LLMObs.pull_dataset()`
- **Features**:
  - Initialize LLMObs with API keys
  - Load dataset by name and project
  - Preview record structure
  - Error handling with helpful messages

#### 4.2 Define Task Function
- **Cell Type**: Markdown + Code
- **Purpose**: Define the core workflow to evaluate
- **Implementation**: `vote_extraction_task()` decorated with `@workflow`
- **Features**:
  - Calls FastAPI backend for extraction
  - Handles multi-page forms
  - Returns structured output
  - Error handling

#### 4.3 Define Evaluator Functions
- **Cell Type**: Markdown + Code
- **Purpose**: Create evaluators to measure performance
- **Evaluators Implemented**:
  1. `exact_form_match()` - **Boolean**: Check if form info matches exactly
  2. `ballot_accuracy_score()` - **Score**: Calculate ballot statistics accuracy (0.0-1.0)
  3. `vote_results_quality()` - **Categorical**: Assess quality (excellent/good/fair/poor)
  4. `has_no_errors()` - **Boolean**: Check if extraction completed without errors

#### 4.4 Define Summary Evaluators (Optional)
- **Cell Type**: Markdown + Code
- **Purpose**: Aggregate metrics across all records
- **Summary Evaluators Implemented**:
  1. `overall_accuracy()` - Percentage of exact form matches
  2. `success_rate()` - Percentage processed without errors
  3. `avg_ballot_accuracy()` - Average ballot accuracy score

#### 4.5 Create Experiment
- **Cell Type**: Markdown + Code
- **Purpose**: Initialize experiment with all components
- **Features**:
  - Links task, dataset, evaluators, and summary evaluators
  - Configures model settings (gemini-2.5-flash, temperature=0.0)
  - Generates Datadog URL for viewing

#### 4.6 Run Experiment
- **Cell Type**: Markdown + Code
- **Purpose**: Execute experiment with various options
- **Options Demonstrated**:
  - Default: Run on all records
  - Sample: Test on subset (`sample_size=3`)
  - Parallel: Faster execution (`jobs=4`)
  - Debug: Stop on errors (`raise_errors=True`)

#### 4.7 View and Analyze Results
- **Cell Type**: Markdown + Code
- **Purpose**: Display and analyze experiment results
- **Features**:
  - Summary metrics (overall accuracy, success rate, etc.)
  - Per-record details (first 5 records)
  - Error reporting
  - Link to Datadog for full results

#### Tips & Next Steps
- **Cell Type**: Markdown
- **Purpose**: Guidance for experiment optimization and iteration
- **Content**:
  - Experiment optimization tips
  - How to compare multiple configurations
  - Using Pandas for advanced analysis
  - Workflow checklist
  - Links to documentation

---

## Key Features

### 1. End-to-End Workflow
The notebook now covers the complete lifecycle:
```
Dataset Creation → Push to Datadog → Run Experiments → Analyze Results
```

### 2. Production-Ready Code
- All functions include type hints
- Comprehensive error handling
- Detailed logging and progress feedback
- Follows Datadog SDK best practices

### 3. Educational Content
- Clear explanations for each step
- Multiple examples of evaluator types
- Tips for optimization
- Links to official documentation

### 4. Vote Extraction Specific
- Evaluators tailored for election form extraction
- Validates form info, ballot statistics, vote results
- Handles multi-page forms
- Integrates with FastAPI backend

---

## Code Examples

### Loading Dataset
```python
from ddtrace.llmobs import LLMObs

LLMObs.enable(
    ml_app="vote-extractor",
    api_key=DD_API_KEY,
    site=DD_SITE,
    agentless_enabled=True,
)

experiment_dataset = LLMObs.pull_dataset(
    dataset_name="vote-extraction-bangbamru-1-10",
    project_name="vote-extraction-project",
)
```

### Defining Task
```python
@workflow
def vote_extraction_task(input_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extract vote data from election form images."""
    # Call FastAPI backend
    response = client.post(
        f"{API_BASE_URL}/api/v1/vote-extraction/extract",
        files=files
    )
    return result
```

### Creating Evaluators
```python
# Boolean evaluator
def exact_form_match(input_data, output_data, expected_output) -> bool:
    return output_data.get("district") == expected_output.get("district")

# Score evaluator (0.0 to 1.0)
def ballot_accuracy_score(input_data, output_data, expected_output) -> float:
    matches = count_matching_fields(output_data, expected_output)
    return matches / total_fields

# Categorical evaluator
def vote_results_quality(input_data, output_data, expected_output) -> str:
    accuracy = calculate_accuracy(output_data, expected_output)
    return "excellent" if accuracy >= 0.95 else "good" if accuracy >= 0.80 else "fair"
```

### Running Experiment
```python
experiment = LLMObs.experiment(
    name="vote-extraction-baseline",
    task=vote_extraction_task,
    dataset=experiment_dataset,
    evaluators=[exact_form_match, ballot_accuracy_score, vote_results_quality],
    summary_evaluators=[overall_accuracy, success_rate],
    description="Baseline evaluation of vote extraction accuracy",
    config={"model": "gemini-2.5-flash", "temperature": 0.0},
)

results = experiment.run()

# View in Datadog
print(f"View results: {experiment.url}")
```

---

## Evaluator Design

### 1. Boolean Evaluators
- **Purpose**: Binary pass/fail checks
- **Return**: `True` or `False`
- **Examples**:
  - `exact_form_match`: District and polling station match
  - `has_no_errors`: Extraction completed successfully

### 2. Score Evaluators
- **Purpose**: Numeric performance measurement
- **Return**: `float` (typically 0.0 to 1.0)
- **Examples**:
  - `ballot_accuracy_score`: Percentage of correct ballot counts
  - Can be used for precision, recall, F1-score

### 3. Categorical Evaluators
- **Purpose**: Labeled quality assessment
- **Return**: `string` (category label)
- **Examples**:
  - `vote_results_quality`: "excellent", "good", "fair", "poor"
  - Useful for human-interpretable ratings

### 4. Summary Evaluators
- **Purpose**: Aggregate metrics across all records
- **Input**: Lists of all inputs, outputs, expected outputs, and evaluator results
- **Return**: `float`, `bool`, or `string`
- **Examples**:
  - `overall_accuracy`: Percentage of records with exact matches
  - `success_rate`: Percentage without errors
  - `avg_ballot_accuracy`: Average score across all records

---

## Integration with Existing Workflow

### Before (Steps 1-3)
1. **Discover Images**: Find available election form images
2. **Work with Local Dataset Files**: Create/manage JSON datasets
3. **Push Dataset to Datadog**: Upload datasets using SDK

### After (Step 4 - NEW!)
4. **Run Experiments**: Systematically evaluate LLM performance
   - Load dataset from Datadog
   - Define task and evaluators
   - Run experiments with different configurations
   - Analyze results
   - Compare performance metrics

### Complete Workflow
```
Images → Local Dataset → Datadog Dataset → Experiments → Analysis → Production
```

---

## Usage Instructions

### Prerequisites
1. Dataset created and pushed to Datadog (Steps 1-3)
2. FastAPI backend running (`docker-compose up -d`)
3. Datadog API keys configured in `.env`
4. `ddtrace>=3.18.0` installed

### Running the Notebook
```bash
# 1. Start Jupyter
cd notebooks/datasets
jupyter notebook 01_prepare_vote_extraction_dataset.ipynb

# 2. Run cells in order:
- Cell 0-12: Setup and dataset creation (existing)
- Cell 13: Introduction to Experiments (NEW)
- Cell 14-15: Load dataset from Datadog (NEW)
- Cell 16-17: Define task function (NEW)
- Cell 18-19: Define evaluators (NEW)
- Cell 20-21: Define summary evaluators (NEW)
- Cell 22-23: Create experiment (NEW)
- Cell 24-25: Run experiment (NEW)
- Cell 26-27: View results (NEW)
- Cell 28: Tips & next steps (NEW)
```

### Quick Start (Experiments Only)
If you already have a dataset in Datadog:
```python
# Skip to Step 4
# 1. Run cells 2, 4 (setup and config)
# 2. Jump to cell 14 (Load dataset)
# 3. Continue through experiment cells (14-27)
```

---

## Experiment Optimization

### 1. Fast Iteration
```python
# Test on small sample first
results = experiment.run(sample_size=3)
```

### 2. Parallel Processing
```python
# Speed up execution on large datasets
results = experiment.run(jobs=4)
```

### 3. Debug Mode
```python
# Stop on first error for debugging
results = experiment.run(raise_errors=True)
```

### 4. Comparing Configurations
```python
# Run multiple experiments
configs = [
    {"model": "gemini-2.5-flash", "temperature": 0.0},
    {"model": "gemini-2.5-flash", "temperature": 0.2},
    {"model": "gemini-2.5-pro", "temperature": 0.0},
]

for i, config in enumerate(configs):
    exp = LLMObs.experiment(
        name=f"vote-extraction-v{i+1}",
        task=task,
        dataset=dataset,
        evaluators=evaluators,
        config=config
    )
    results = exp.run()
    print(f"Config {i+1}: {exp.url}")
```

---

## Expected Output

### After Running Experiment
```
✅ Experiment created: vote-extraction-baseline
   Dataset: vote-extraction-bangbamru-1-10
   Records: 10
   Evaluators: 4
   Summary Evaluators: 3

📊 View in Datadog: https://app.datadoghq.com/llm/experiments/...

🚀 Running experiment on all records...
⏱️  This may take several minutes depending on dataset size...
Processing: บางบำหรุ 1 (6 pages)
Processing: บางบำหรุ 2 (6 pages)
...

✅ Experiment completed!
   Total records processed: 10

📊 Experiment Results Summary
================================================================================

🎯 Summary Metrics:
   overall_accuracy: 85.00%
   success_rate: 100.00%
   avg_ballot_accuracy: 92.50%

📄 Per-Record Results:
--------------------------------------------------------------------------------

1. Record 0:
   Form: บางบำหรุ 1
   exact_form_match: True
   ballot_accuracy_score: 95.00%
   vote_results_quality: excellent
   has_no_errors: True

2. Record 1:
   Form: บางบำหรุ 2
   exact_form_match: True
   ballot_accuracy_score: 90.00%
   vote_results_quality: good
   has_no_errors: True

...

🔗 View full results in Datadog:
   https://app.datadoghq.com/llm/experiments/...
```

---

## Files Modified

### 1. `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
- ✅ Added Step 4: Run Experiments (16 new cells)
- ✅ Added 8 markdown cells for documentation
- ✅ Added 8 code cells for implementation
- ✅ Total cells: 13 (existing) + 16 (new) = 29 cells

### Structure After Update
```
Cell 0: Title and Introduction
Cell 1-2: Setup and Imports
Cell 3-4: Configuration & API Keys
Cell 5-6: Step 1: Discover Images
Cell 7-8: Step 2: Work with Local Dataset Files
Cell 9-12: Step 3: Push Dataset to Datadog

--- NEW SECTION ---
Cell 13: Step 4: Introduction to Experiments
Cell 14-15: 4.1 Load Dataset from Datadog
Cell 16-17: 4.2 Define Task Function
Cell 18-19: 4.3 Define Evaluator Functions
Cell 20-21: 4.4 Define Summary Evaluators
Cell 22-23: 4.5 Create Experiment
Cell 24-25: 4.6 Run Experiment
Cell 26-27: 4.7 View and Analyze Results
Cell 28: Tips & Next Steps
```

---

## Related Documentation

### Guides
- [`guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md`](./guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md) - Comprehensive experiments guide
- [`guides/llmobs/03_EVALUATION_METRIC_TYPES.md`](./guides/llmobs/03_EVALUATION_METRIC_TYPES.md) - Evaluation metric types explained

### Implementation
- [`DATASET_DATADOG_SDK_SUCCESS.md`](./DATASET_DATADOG_SDK_SUCCESS.md) - Dataset push to Datadog using SDK
- [`DATASET_WORKFLOW_COMPLETE_SUMMARY.md`](./DATASET_WORKFLOW_COMPLETE_SUMMARY.md) - Complete dataset workflow

### Datadog Documentation
- [LLMObs Experiments](https://docs.datadoghq.com/llm_observability/experiments/)
- [Creating Datasets](https://docs.datadoghq.com/llm_observability/experiments/#creating-a-dataset)
- [Running Experiments](https://docs.datadoghq.com/llm_observability/experiments/#creating-an-experiment)

---

## Benefits

### 1. Systematic Testing
- Run LLM applications across entire datasets
- Measure performance consistently
- Track improvements over time

### 2. Compare Configurations
- Test different models side-by-side
- Evaluate temperature/parameter changes
- Identify optimal settings

### 3. Production Validation
- Validate before deployment
- Catch regressions early
- Build confidence in changes

### 4. Data-Driven Decisions
- Objective performance metrics
- Identify failure patterns
- Focus improvement efforts

---

## Next Steps

### 1. Run Your First Experiment ✅ Ready
1. Open the notebook
2. Ensure FastAPI backend is running
3. Run Step 4 cells in order
4. View results in Datadog

### 2. Iterate on Models
1. Run baseline experiment (gemini-2.5-flash)
2. Run comparison experiment (gemini-2.5-pro)
3. Compare results in Datadog UI
4. Select best performing model

### 3. Refine Evaluators
1. Add domain-specific evaluators
2. Implement advanced metrics (precision, recall, F1)
3. Create custom summary evaluators
4. Validate against business requirements

### 4. Automate Testing
1. Create CI/CD pipeline
2. Run experiments on every model change
3. Block deployments with low scores
4. Track performance over time

---

## Success Metrics

✅ **All Objectives Met**:
1. ✅ Added comprehensive Experiments section (Step 4)
2. ✅ Implemented dataset loading from Datadog
3. ✅ Created task function for vote extraction
4. ✅ Defined 4 evaluator functions (boolean, score, categorical)
5. ✅ Defined 3 summary evaluator functions
6. ✅ Implemented experiment creation and execution
7. ✅ Added results viewing and analysis
8. ✅ Included optimization tips and examples
9. ✅ Provided clear documentation and guidance
10. ✅ Maintained consistency with existing notebook style

---

## Conclusion

The Jupyter notebook now provides a **complete end-to-end workflow** for:
1. Creating datasets with ground truth
2. Pushing datasets to Datadog
3. Running systematic experiments
4. Analyzing and comparing results

Users can now:
- Establish performance baselines
- Compare different model configurations
- Validate improvements before production
- Make data-driven decisions about LLM deployments

This completes the Datadog LLMObs integration, enabling systematic testing and continuous improvement of the vote extraction application. 🎉

---

**Ready**: Open the notebook and run your first experiment!

