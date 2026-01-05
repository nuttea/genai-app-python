# 🧪 Model Comparison Experiments

**Feature**: Multi-model comparison experiments for vote extraction  
**Status**: ✅ Complete  
**Date**: January 4, 2026

---

## 🎯 Overview

Added comprehensive model comparison experiments to the Jupyter notebook to determine the optimal Gemini model for production vote extraction tasks.

**Notebook**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`  
**Section**: 5. Model Comparison Experiments

---

## 🔬 Experiments Added

### Experiment 1: gemini-2.5-flash (T=0.0) - Baseline
- **Model**: `gemini-2.5-flash`
- **Temperature**: `0.0` (deterministic)
- **Purpose**: Baseline for comparison
- **Cost Tier**: Medium
- **Parameters**: `sample_size=10`, `jobs=2`, `raise_errors=True`

### Experiment 2: gemini-2.5-flash-lite (T=0.0) - Speed Test
- **Model**: `gemini-2.5-flash-lite`
- **Temperature**: `0.0` (deterministic)
- **Purpose**: Ultra-fast, cost-effective option
- **Cost Tier**: Low
- **Parameters**: `sample_size=10`, `jobs=2`, `raise_errors=True`

### Experiment 3: gemini-3-pro-preview (T=0.0) - Quality Test
- **Model**: `gemini-3-pro-preview`
- **Temperature**: `0.0` (deterministic)
- **Purpose**: Maximum quality, highest capability
- **Cost Tier**: High
- **Parameters**: `sample_size=10`, `jobs=2`, `raise_errors=True`

### Experiment 4: gemini-2.5-flash (T=0.1) - Tolerance Test
- **Model**: `gemini-2.5-flash`
- **Temperature**: `0.1` (slight variation)
- **Purpose**: Test impact of temperature on structured data
- **Cost Tier**: Medium
- **Parameters**: `sample_size=10`, `jobs=2`, `raise_errors=True`

---

## 📊 Evaluation Metrics

All experiments use the same evaluators for consistency:

### Per-Record Evaluators
1. **`exact_form_match`**: Boolean - All fields match ground truth exactly
2. **`ballot_accuracy_score`**: Float (0-100%) - Ballot statistics accuracy
3. **`vote_results_quality`**: Categorical - "excellent", "good", "fair", "poor"
4. **`has_no_errors`**: Boolean - No extraction errors

### Summary Evaluators
1. **`overall_accuracy`**: Mean of all accuracy scores
2. **`success_rate`**: Percentage of successful extractions (no errors)
3. **`avg_ballot_accuracy`**: Average ballot statistics accuracy

---

## 🎨 Comparison Features

### Automated Comparison Table

```
Experiment                         Cost Tier  Overall Accuracy  Success Rate  Avg Ballot Accuracy
gemini-2.5-flash (T=0.0)          Medium     XX.X%             XX.X%         XX.X%
gemini-2.5-flash-lite (T=0.0)     Low        XX.X%             XX.X%         XX.X%
gemini-3-pro-preview (T=0.0)      High       XX.X%             XX.X%         XX.X%
gemini-2.5-flash (T=0.1)          Medium     XX.X%             XX.X%         XX.X%
```

### Intelligent Recommendations

The notebook automatically identifies:
- 🏆 **Best Accuracy**: Model with highest overall accuracy
- 💰 **Best Value**: Flash-lite if accuracy ≥ 95% (fastest + cheapest)
- 🌡️ **Temperature Impact**: Comparison of T=0.0 vs T=0.1

---

## ⚙️ Optimized Parameters

### For Data Extraction Tasks

```python
# Recommended parameters for structured data extraction
experiment.run(
    sample_size=10,      # Full dataset (10 records)
    jobs=2,              # Parallel processing (balanced for API rate limits)
    raise_errors=True    # Fail fast for debugging
)
```

**Why These Parameters?**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `sample_size` | `10` | Full dataset evaluation for complete accuracy assessment |
| `jobs` | `2` | Parallel processing without hitting API rate limits |
| `raise_errors` | `True` | Immediate failure detection for faster debugging |

### Temperature Strategy

| Temperature | Use Case | Expected Behavior |
|-------------|----------|-------------------|
| `0.0` | **Structured data extraction** (RECOMMENDED) | Deterministic, consistent output |
| `0.1` | **Tolerance testing** | Slightly more varied, test robustness |
| `0.5-1.0` | **Creative tasks** (NOT for vote extraction) | More variation, less predictable |

**Recommendation**: Use `temperature=0.0` for all production vote extraction to ensure consistent, deterministic results.

---

## 🚀 Production Deployment Strategy

The notebook provides three deployment strategies based on requirements:

### 1️⃣ High Volume / Cost Sensitive
```yaml
Model: gemini-2.5-flash-lite
Temperature: 0.0
Use When: Processing thousands of forms, budget constraints
Trade-off: Slightly lower accuracy acceptable
```

### 2️⃣ Balanced (RECOMMENDED)
```yaml
Model: gemini-2.5-flash
Temperature: 0.0
Use When: Standard production workloads
Trade-off: None - optimal for most use cases
```

### 3️⃣ Maximum Quality
```yaml
Model: gemini-3-pro-preview
Temperature: 0.0
Use When: Critical data, legal/compliance requirements
Trade-off: Higher cost, slower processing
```

---

## 📋 Implementation Steps

### 1. Run All Experiments

```python
# Execute cells 34-40 in the notebook
# This will run all 4 experiments in sequence
```

### 2. Review Comparison

```python
# Execute cell 42 to see the comparison table
# Review recommendations based on your requirements
```

### 3. Update Backend Configuration

```python
# File: services/fastapi-backend/app/config.py
DEFAULT_MODEL = 'gemini-2.5-flash'  # Or chosen model
DEFAULT_TEMPERATURE = 0.0
```

### 4. Deploy to Production

```bash
git add -A
git commit -m 'chore: Update to optimal model from experiments'
git push origin main
# CI/CD automatically deploys
```

### 5. Monitor Performance

- Set up Datadog monitors for:
  - Overall accuracy threshold (< 95%)
  - Success rate threshold (< 90%)
  - Error rate spike (> 5%)
  - Latency increase (p95 > 10s)
  - Cost anomalies

---

## 🧪 How to Use the Notebook

### Quick Start

1. **Load the notebook**:
   ```bash
   jupyter notebook notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb
   ```

2. **Run setup cells** (Cells 1-27):
   - Install packages
   - Load environment variables
   - Load dataset from Datadog
   - Define task and evaluators
   - Create baseline experiment

3. **Run model comparison** (Cells 33-42):
   - Execute each experiment (5-10 minutes per model)
   - Review comparison table
   - See automatic recommendations

4. **Review production strategy** (Cell 44):
   - Choose deployment approach
   - Get implementation steps
   - Set up monitoring

### Customization Options

#### Test Different Temperature Values

```python
experiment_custom = LLMObs.experiment(
    name="vote-extraction-custom",
    task=vote_extraction_task,
    dataset=experiment_dataset,
    evaluators=[...],
    metadata={
        "model": "gemini-2.5-flash",
        "temperature": 0.2,  # Custom value
    }
)
```

#### Test Subset of Dataset

```python
# Quick iteration on 3 records
results = experiment.run(
    sample_size=3,
    jobs=2,
    raise_errors=True
)
```

#### Increase Parallelism

```python
# Faster execution (if API rate limits allow)
results = experiment.run(
    sample_size=10,
    jobs=4,  # More parallel jobs
    raise_errors=True
)
```

---

## 📊 Monitoring Checklist

### Pre-Deployment
- [ ] All experiments completed successfully
- [ ] Comparison table reviewed
- [ ] Model selected based on requirements
- [ ] Backend configuration updated
- [ ] Local testing passed

### Post-Deployment
- [ ] Datadog monitors configured
- [ ] Accuracy tracking dashboard created
- [ ] Cost tracking enabled
- [ ] Latency alerts set up
- [ ] Error rate monitoring active

### Ongoing
- [ ] Weekly accuracy review
- [ ] Monthly cost vs. performance analysis
- [ ] Quarterly experiment re-runs
- [ ] New model version testing

---

## 📈 Expected Results

### Typical Performance

| Model | Accuracy Range | Speed | Cost | Recommendation |
|-------|---------------|-------|------|----------------|
| gemini-2.5-flash-lite | 92-96% | ⚡⚡⚡ Fastest | 💰 Lowest | High volume |
| gemini-2.5-flash | 95-98% | ⚡⚡ Fast | 💰💰 Medium | **Default** |
| gemini-3-pro-preview | 97-99% | ⚡ Slower | 💰💰💰 High | Critical data |

**Note**: Actual results depend on your specific dataset and ground truth quality.

### Temperature Impact

| Temperature | Typical Variance | Use Case |
|-------------|-----------------|----------|
| `0.0` | 0-2% | **Production** (deterministic) |
| `0.1` | 1-3% | Testing robustness |
| `0.5+` | 5-10% | Not recommended for structured data |

---

## 🔗 Related Resources

### Notebook Sections
- **Section 1-3**: Setup and dataset preparation
- **Section 4**: Single experiment baseline
- **Section 5**: Model comparison experiments (NEW!)
  - 5.1: Flash (T=0.0)
  - 5.2: Flash-Lite (T=0.0)
  - 5.3: Pro Preview (T=0.0)
  - 5.4: Flash (T=0.1)
  - 5.5: Comparison table
  - 5.6: Production strategy

### Documentation
- **Complete Notebook**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`
- **Experiments Guide**: `EXPERIMENTS_NOTEBOOK_COMPLETE.md`
- **Dataset Guide**: `DATASET_WORKFLOW_COMPLETE_SUMMARY.md`
- **LLMObs Documentation**: `docs/monitoring/DATADOG_LLMOBS_COMPLETE.md`

### External Resources
- [Datadog LLMObs Experiments](https://docs.datadoghq.com/llm_observability/experiments/)
- [Gemini Model Documentation](https://ai.google.dev/gemini-api/docs/models)
- [Temperature Parameter Guide](https://ai.google.dev/gemini-api/docs/text-generation#configure_model_parameters)

---

## ✨ Key Features

### Automated Experiment Management
- ✅ 4 experiments with different models and temperatures
- ✅ Consistent evaluation metrics across all experiments
- ✅ Automatic comparison table generation
- ✅ Intelligent recommendations based on results

### Production-Ready
- ✅ Optimized parameters for data extraction (`T=0.0`, `jobs=2`)
- ✅ Deployment strategy with 3 options
- ✅ Implementation steps included
- ✅ Monitoring checklist provided

### Comprehensive Analysis
- ✅ Cost vs. performance comparison
- ✅ Temperature impact analysis
- ✅ Speed vs. accuracy trade-offs
- ✅ Direct links to Datadog for detailed results

---

## 🎯 Next Steps

1. **Run the experiments**: Execute cells 34-40 in the notebook
2. **Review results**: Check the comparison table (cell 42)
3. **Choose model**: Based on your requirements (cost/speed/accuracy)
4. **Deploy**: Update backend config and push to main
5. **Monitor**: Set up Datadog monitors and dashboards
6. **Iterate**: Re-run experiments quarterly or when new models release

---

**Ready to run!** 🚀 Open the notebook and execute the model comparison experiments to find your optimal configuration.

**Recommendation**: Start with all 4 experiments to get a complete baseline, then iterate based on specific needs.

