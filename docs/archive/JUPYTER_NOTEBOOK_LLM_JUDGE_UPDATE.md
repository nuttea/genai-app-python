# ✅ Jupyter Notebook Updated with LLM-as-Judge Evaluator

**Successfully integrated LLM-as-Judge evaluator into the Jupyter notebook for vote extraction experiments.**

---

## 📝 Summary of Changes

### 1. New Cell 23: `llm_judge_evaluator` Function
- **Function**: `llm_judge_evaluator(input_data, output_data, expected_output) -> float`
- **Model**: `gemini-3-pro-preview` via Vertex AI
- **Returns**: Quality score from 0.0 (worst) to 1.0 (perfect)
- **Features**:
  - Detailed reasoning for the score
  - Lists specific errors found
  - Error severity classification
  - Evaluates 4 dimensions: form info, voter stats, ballot stats, vote results

### 2. Updated Cell 27: Summary Evaluators
- **Added**: `avg_llm_judge_score()` summary evaluator
- **Function**: Calculates average LLM judge quality score across all records
- **Aggregates**: Individual LLM judge scores into dataset-level metric

### 3. Updated Cell 29: Baseline Experiment
- **Added**: `llm_judge_evaluator` to the `evaluators` list
- **Added**: `avg_llm_judge_score` to the `summary_evaluators` list
- **Updated**: Experiment description to mention LLM-as-Judge
- **Result**: Baseline experiments now include AI-powered quality assessment

### 4. Updated Cell 49: `run_model_experiments` Wrapper Function
- **Default evaluators**: Now include `llm_judge_evaluator` by default
- **Default summary evaluators**: Now include `avg_llm_judge_score` by default
- **Comparison table**: Added "Avg LLM Judge Score" column to results DataFrame
- **Result**: All experiments run through the wrapper automatically use LLM judge

---

## 🚀 How to Use

### Option 1: Run Individual Experiment (Cells 29-31)

```python
# Cell 29: Create experiment (LLM judge included automatically)
experiment = LLMObs.experiment(
    name="vote-extraction-baseline",
    task=vote_extraction_task,
    dataset=experiment_dataset,
    evaluators=[
        exact_form_match,
        ballot_accuracy_score,
        vote_results_quality,
        has_no_errors,
        llm_judge_evaluator  # ⭐ NEW
    ],
    summary_evaluators=[
        overall_accuracy,
        success_rate,
        avg_ballot_accuracy,
        avg_llm_judge_score  # ⭐ NEW
    ]
)

# Cell 31: Run experiment
results = experiment.run(
    sample_size=10,
    jobs=4,
    raise_errors=True
)
```

### Option 2: Use Wrapper Function (Cell 50)

```python
# Run multiple experiments with LLM judge automatically included
results = run_model_experiments(
    model_configs=[
        {"model": "gemini-2.5-flash", "temperature": 0.0},
        {"model": "gemini-2.5-flash-lite", "temperature": 0.0},
        {"model": "gemini-3-pro-preview", "temperature": 0.0}
    ],
    sample_size=10,
    jobs=2,
    raise_errors=True
)

# LLM judge runs automatically!
# Comparison table shows "Avg LLM Judge Score" column
```

---

## 📊 Expected Output

### Per-Record Evaluations

```
Record 1: บางบำหรุ1
   exact_form_match: True
   ballot_accuracy_score: 0.85
   vote_results_quality: excellent
   has_no_errors: True
   llm_judge_evaluator: 0.92 ⭐ NEW!
```

### Summary Metrics

```
Summary Metrics:
   overall_accuracy: 0.85 (85%)
   success_rate: 0.95 (95%)
   avg_ballot_accuracy: 0.82 (82%)
   avg_llm_judge_score: 0.88 (88%) ⭐ NEW!
```

### Comparison Table

```
╔══════════════════════════════╦═══════════╦═════════════╦══════════════════════╗
║ Experiment                   ║ Model     ║ Overall Acc ║ Avg LLM Judge Score  ║
╠══════════════════════════════╬═══════════╬═════════════╬══════════════════════╣
║ vote-extraction-flash-t0     ║ 2.5-flash ║ 0.85        ║ 0.88 ⭐               ║
║ vote-extraction-flash-lite   ║ 2.5-lite  ║ 0.82        ║ 0.84 ⭐               ║
║ vote-extraction-pro-t0       ║ 3-pro     ║ 0.92        ║ 0.95 ⭐               ║
╚══════════════════════════════╩═══════════╩═════════════╩══════════════════════╝
```

---

## ⚙️ Configuration

### Required Environment Variables

Already configured in your `docker-compose.yml`:

```bash
GOOGLE_CLOUD_PROJECT=datadog-sandbox       # ✅ Required for Vertex AI
VERTEX_AI_LOCATION=global                  # ✅ Defaults to "global"
DD_API_KEY=your-datadog-api-key           # ✅ Required for Datadog LLMObs
```

### Optional: Disable LLM Judge for Specific Experiment

If you want to run an experiment WITHOUT the LLM judge:

```python
experiment = LLMObs.experiment(
    evaluators=[
        exact_form_match,
        ballot_accuracy_score,
        vote_results_quality,
        has_no_errors,
        # llm_judge_evaluator  # Comment out to disable
    ],
    summary_evaluators=[
        overall_accuracy,
        success_rate,
        avg_ballot_accuracy,
        # avg_llm_judge_score  # Comment out to disable
    ]
)
```

---

## 💡 Benefits

### 1. Holistic Quality Assessment
- Goes beyond simple rule-based metrics
- Evaluates overall extraction quality
- Identifies subtle issues that rules might miss

### 2. Detailed Error Analysis
- Lists specific errors found (field-by-field)
- Classifies error severity (minor/major/critical)
- Explains reasoning for the quality score

### 3. Model Comparison
- Compare models on overall quality (not just accuracy)
- Understand trade-offs (speed vs quality)
- Choose best model for production use

### 4. Production Monitoring
- Track quality trends over time
- Detect quality degradation early
- Investigate failures with detailed reasoning

---

## ⚠️ Considerations

### Cost
- **Per evaluation**: ~$0.01 USD
- **For 10 records**: ~$0.10 USD
- **For 100 records**: ~$1.00 USD

### Time
- **Per evaluation**: ~3-5 seconds
- **Parallelization**: Runs in parallel with other evaluators
- **Impact**: Slightly increases total experiment time

### Reliability
- **Requires**: GCP/Vertex AI access with `GOOGLE_CLOUD_PROJECT` set
- **Fallback**: Returns 0.0 score on error (other evaluators continue)
- **Logging**: Warnings logged if GCP not configured

---

## 📖 Related Documentation

- **[LLM_JUDGE_EVALUATOR.md](./LLM_JUDGE_EVALUATOR.md)** - Complete guide to LLM-as-Judge
- **[LLM_JUDGE_VERTEX_AI_UPDATE.md](./LLM_JUDGE_VERTEX_AI_UPDATE.md)** - Vertex AI integration details
- **[RUN_EXPERIMENTS_IMPLEMENTATION.md](./RUN_EXPERIMENTS_IMPLEMENTATION.md)** - Experiments API guide
- **[docs/INDEX.md](./docs/INDEX.md)** - Documentation index

---

## ✅ Next Steps

### 1. Test in Jupyter Notebook

```bash
# Open the notebook
jupyter lab notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb

# Or if using JupyterLab in Docker:
docker-compose up -d jupyter
# Navigate to: http://localhost:8888
```

### 2. Run Baseline Experiment (Cells 29-31)

- Run Cell 29 to create experiment
- Run Cell 31 to execute
- Check results for `llm_judge_evaluator` scores
- View `avg_llm_judge_score` in summary metrics

### 3. Run Multiple Experiments (Cell 50)

- Use `run_model_experiments()` wrapper
- LLM judge included automatically
- Compare models in the results table

### 4. Monitor in Datadog

- View experiments in Datadog LLMObs UI
- Check LLM judge scores per record
- Analyze quality trends over time

---

## 🎯 Technical Details

### LLM Judge Evaluation Prompt

The evaluator uses a structured prompt that asks `gemini-3-pro-preview` to:

1. **Compare** extracted output vs ground truth
2. **Evaluate** quality on 4 dimensions:
   - Form Information (date, location, polling station)
   - Voter Statistics (eligible voters, voters present)
   - Ballot Statistics (allocated, used, good, bad, no-vote)
   - Vote Results (candidate numbers, names, vote counts)
3. **Provide**:
   - `score`: float 0.0-1.0
   - `reasoning`: explanation of the score
   - `errors`: list of specific errors with severity

### Response Format

```json
{
  "score": 0.92,
  "reasoning": "Excellent extraction with high accuracy across all fields. Minor discrepancy in one vote count.",
  "errors": [
    {
      "field": "vote_results[5].vote_count",
      "expected": "232",
      "actual": "223",
      "severity": "minor"
    }
  ]
}
```

### Error Handling

- **Missing GCP Project**: Returns 0.0, logs warning
- **Vertex AI API Error**: Returns 0.0, logs error with stack trace
- **JSON Parse Error**: Returns 0.0, logs error with raw response
- **All cases**: Other evaluators continue normally

---

## 🎉 Conclusion

Your Jupyter notebook now includes:

✅ **LLM-as-Judge evaluator** using Vertex AI  
✅ **Average LLM judge score** summary metric  
✅ **Automatic integration** in all experiments  
✅ **Comparison table** with quality scores  
✅ **Same authentication** as main extraction service  

**Just run your experiments - LLM judge evaluates automatically!** 🚀

---

**File**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`  
**Updated**: 2026-01-04  
**Changes**: Added LLM-as-Judge evaluator (Cells 23, 27, 29, 49)

