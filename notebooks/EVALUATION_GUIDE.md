# Comprehensive Evaluation System - Guide

## ✅ Implementation Complete!

**Notebook:** [gemini-ss5_18_bigquery_drive.ipynb](gemini-ss5_18_bigquery_drive.ipynb)

All priorities implemented with comprehensive evaluation system integrated into batch processing.

## 🎯 What Was Added

### 1. Enhanced Data Models

#### NumberTextPair
```python
class NumberTextPair(BaseModel):
    arabic: int          # Required: 120
    thai_text: str      # Optional: "หนึ่งร้อยยี่สิบ"
```

#### Updated Models
- ✅ FormInfo: Added `set_number`, `village_moo`
- ✅ VoterStatistics: Uses NumberTextPair
- ✅ BallotStatistics: Uses NumberTextPair
- ✅ VoteResult: Uses NumberTextPair for vote_count
- ✅ Official: New model for committee members
- ✅ ElectionFormData: Added `total_votes_recorded`, `officials`

### 2. Evaluation System

#### ValidationCheck Dataclass
```python
@dataclass
class ValidationCheck:
    check_name: str
    status: "pass" | "fail" | "warning" | "skip"
    message: str
    expected: Optional[int]
    actual: Optional[int]
```

#### EvaluationResult Dataclass
```python
@dataclass
class EvaluationResult:
    report_index: int
    is_valid: bool
    quality_score: float  # 0.0 to 1.0
    checks_passed: int
    checks_failed: int
    checks_warning: int
    checks_skipped: int
    total_checks: int
    validation_checks: list[ValidationCheck]
    errors: list[str]
    warnings: list[str]
```

### 3. Seven Validation Checks

| # | Check Name | Type | Description |
|---|------------|------|-------------|
| 1 | form_info_complete | Critical | Required fields present |
| 2 | ballot_accounting | Critical | ballots_used = good + bad + no_vote |
| 3 | total_votes | Critical | sum(votes) = total_recorded |
| 4 | voter_ballot_consistency | Warning | present_voters ≈ ballots_used |
| 5 | vote_results_exist | Critical | Vote results not empty |
| 6 | non_negative_votes | Critical | All votes >= 0 |
| 7 | thai_text_quality | Quality | Thai text coverage % |

### 4. Quality Score Calculation

```python
quality_score = (checks_passed + 0.5 * checks_warning) / (checks_passed + checks_failed + checks_warning)
```

**Example:**
- 5 passed, 0 failed, 2 warnings → Quality: 85.7%
- 7 passed, 0 failed, 0 warnings → Quality: 100%
- 3 passed, 2 failed, 1 warning → Quality: 58.3%

## 📊 Evaluation Output Example

### Compact Summary (During Batch Processing)
```
Processing 1/3: เขตเลือกตั้งที่ 3/อำเภอโพธิ์ประทับช้าง/...
================================================================================
🤖 Extracting with gemini-exp-1206...
✅ Extraction complete! Extracted 1 report(s)

📊 Running evaluation...
   ✅ Report 1: Quality=85.7%, Passed=6/7
```

### Detailed Summary
```
================================================================================
EVALUATION SUMMARY - Report #1
================================================================================

📊 Overall Status: ✅ VALID
📈 Quality Score: 85.7%

📋 Check Results:
   ✅ Passed: 6/7
   ❌ Failed: 0/7
   ⚠️  Warnings: 1/7
   ⏭️  Skipped: 0/7

🔍 Detailed Checks:
   ✅ form_info_complete: All required form info fields present
   ✅ ballot_accounting: Ballot accounting correct: 450 = 450
      Expected: 450, Actual: 450
   ✅ total_votes: Total votes match: 440 = 440
      Expected: 440, Actual: 440
   ⚠️  voter_ballot_consistency: Discrepancy: present_voters=455, ballots_used=450 (diff=5)
      Expected: 450, Actual: 455
   ✅ vote_results_exist: Vote results present: 25 entries
   ✅ non_negative_votes: All vote counts are non-negative
   ✅ thai_text_quality: Thai text extraction: 92.3% coverage

⚠️  WARNINGS (1):
   - Voter/ballot discrepancy: 5
```

### Batch Summary
```
================================================================================
BATCH PROCESSING SUMMARY
================================================================================

📊 Processing Statistics:
   Total Files: 3
   ✅ Successful: 3
   ❌ Failed: 0
   Success Rate: 100.0%

📈 Quality Metrics:
   Total Reports Extracted: 3
   Average Quality Score: 88.5%
   Valid Reports: 3/3
   Invalid Reports: 0/3
```

### Summary Table
```
| File            | Province | Size (KB) | Success | Reports | Quality | Valid |
|-----------------|----------|-----------|---------|---------|---------|-------|
| สส5ทับ18 น_09.pdf | พิจิตร   | 50.0      | ✅      | 1       | 85.7%   | 1     |
| สส5ทับ18 น_10.pdf | พิจิตร   | 50.1      | ✅      | 1       | 91.2%   | 1     |
| สส5ทับ18 น_18.pdf | พิจิตร   | 50.1      | ✅      | 1       | 88.9%   | 1     |
```

## 🔧 Usage Examples

### Single File Evaluation
```python
# Extract data
result = extract_from_drive_url(drive_uri, model="gemini-exp-1206")

# Evaluate
eval_result = evaluate_extraction(result[0], report_index=0)

# Print summary
print_evaluation_summary(eval_result)

# Access results
print(f"Valid: {eval_result.is_valid}")
print(f"Quality: {eval_result.quality_score:.1%}")
print(f"Errors: {eval_result.errors}")
```

### Batch Processing with Evaluation
```python
# Process multiple files with automatic evaluation
batch_results = batch_process_from_bigquery(
    limit=10,
    province="พิจิตร",
    min_size_kb=50.0,
    max_size_mb=5.0,
    model="gemini-exp-1206",
    run_evaluation=True  # ← Enable evaluation
)

# Results include:
# - file_info
# - success (bool)
# - data (extracted reports)
# - evaluations (list of EvaluationResult)
# - reports_count
```

### Access Evaluation Results
```python
# Get evaluations from batch results
for batch_result in batch_results:
    if batch_result['success']:
        file_name = batch_result['file_info']['path']
        evaluations = batch_result['evaluations']

        for eval_dict in evaluations:
            print(f"{file_name}: Quality={eval_dict['quality_score']:.1%}")

            if not eval_dict['is_valid']:
                print(f"  Errors: {eval_dict['errors']}")
```

## 📈 Quality Metrics Explained

### Quality Score Components

1. **Passed Checks** - Full credit (1.0 per check)
2. **Warnings** - Half credit (0.5 per check)
3. **Failed Checks** - No credit (0.0 per check)
4. **Skipped Checks** - Not counted

**Formula:**
```python
score = (passed + 0.5 * warnings) / (passed + failed + warnings)
```

### Interpreting Quality Scores

| Score Range | Quality Level | Action |
|-------------|--------------|--------|
| 90-100% | Excellent ⭐⭐⭐ | Ready for production |
| 75-89% | Good ⭐⭐ | Review warnings |
| 60-74% | Fair ⭐ | Check errors, may need retry |
| <60% | Poor ❌ | Likely extraction failed |

## 🔍 Validation Check Details

### Check 1: form_info_complete
**Required fields:** form_type, province, district, polling_station_number
**Result:** Pass/Fail
**Impact:** Critical - can't identify the report without this

### Check 2: ballot_accounting
**Rule:** ballots_used.arabic = good + bad + no_vote
**Result:** Pass/Fail
**Impact:** Critical - data integrity issue if fails

### Check 3: total_votes
**Rule:** sum(vote_results[].vote_count.arabic) = total_votes_recorded.arabic
**Result:** Pass/Fail
**Impact:** Critical - missing vote entries if fails

### Check 4: voter_ballot_consistency
**Rule:** |present_voters.arabic - ballots_used.arabic| <= 5
**Result:** Pass/Warning
**Impact:** Medium - unusual but sometimes legitimate

### Check 5: vote_results_exist
**Rule:** vote_results array is not empty
**Result:** Pass/Fail
**Impact:** Critical - no data if fails

### Check 6: non_negative_votes
**Rule:** All vote_count.arabic >= 0
**Result:** Pass/Fail
**Impact:** Critical - data corruption if fails

### Check 7: thai_text_quality
**Rule:** % of fields with thai_text populated
**Thresholds:**
- >= 80%: Pass
- 50-79%: Warning
- < 50%: Fail
**Impact:** Medium - affects cross-validation capability

## 📦 Output Files

### 1. Batch Results JSON
**File:** `batch_results_{N}files.json`

**Structure:**
```json
{
  "metadata": {
    "model": "gemini-exp-1206",
    "total_files": 3,
    "successful": 3,
    "failed": 0,
    "total_reports": 3,
    "quality_metrics": {
      "average_quality_score": 0.885,
      "valid_reports": 3,
      "invalid_reports": 0,
      "total_checks_run": 21,
      "total_passed": 18,
      "total_failed": 0,
      "total_warnings": 3
    }
  },
  "results": [...]
}
```

### 2. Summary CSV
**File:** `batch_summary_{N}files.csv`

**Columns:**
- File, Province, Size (KB), Success, Reports, Quality, Valid

**Use for:**
- Quick overview of batch processing
- Import into spreadsheets for analysis
- Generate reports

### 3. Individual Extractions
**File:** `extracted_data_{file_id}.json`

**Structure:**
```json
{
  "source_file": {...},
  "extracted_data": [...],
  "model": "gemini-exp-1206"
}
```

## 🚀 Production Workflow

### Step 1: Query Files
```python
pdf_files = query_pdf_files(
    limit=100,
    province="กรุงเทพมหานคร",
    min_size_kb=50.0,
    max_size_mb=50.0
)
```

### Step 2: Batch Process with Evaluation
```python
batch_results = batch_process_from_bigquery(
    limit=100,
    province="กรุงเทพมหานคร",
    min_size_kb=50.0,
    max_size_mb=50.0,
    model="gemini-exp-1206",
    run_evaluation=True  # ← Get quality metrics
)
```

### Step 3: Analyze Results
```python
# Overall metrics
successful = sum(1 for r in batch_results if r['success'])
all_evals = [e for r in batch_results if r.get('success') for e in r.get('evaluations', [])]
avg_quality = sum(e['quality_score'] for e in all_evals) / len(all_evals)

print(f"Success Rate: {successful/len(batch_results)*100:.1f}%")
print(f"Average Quality: {avg_quality:.1%}")
```

### Step 4: Filter High-Quality Results
```python
# Get only high-quality extractions (>90% quality score)
high_quality = [
    r for r in batch_results
    if r.get('success')
    and all(e['quality_score'] > 0.9 for e in r.get('evaluations', []))
]

print(f"High quality results: {len(high_quality)}/{len(batch_results)}")
```

### Step 5: Save to BigQuery
```python
# Flatten results for BigQuery
bq_rows = []
for result in batch_results:
    if result['success']:
        for report in result['data']:
            # Flatten NumberTextPair to separate columns
            row = {
                'file_id': result['file_info']['file_id'],
                'province': report['form_info']['province'],
                'district': report['form_info']['district'],
                'ballots_used': report['ballot_statistics']['ballots_used']['arabic'],
                # ... etc
            }
            bq_rows.append(row)

# Insert into BigQuery
# table.insert_rows(bq_rows)
```

## 📊 Evaluation Metrics Dashboard

### Per-File Metrics
- Success rate
- Reports extracted per file
- Average quality score
- Common errors

### Per-Report Metrics
- Quality score (0-100%)
- Checks passed/failed/warning
- Specific validation errors
- Thai text coverage

### Aggregate Metrics
- Overall success rate
- Average quality score
- Total reports extracted
- Most common errors
- Processing time per file

## 🎓 Best Practices

### 1. Start Small
```python
# Test with 3-5 files first
batch_results = batch_process_from_bigquery(limit=3, max_size_mb=5.0)
```

### 2. Monitor Quality
```python
# Check average quality before scaling up
avg_quality = calculate_average_quality(batch_results)
if avg_quality < 0.8:
    print("⚠️  Quality too low, check extraction issues")
```

### 3. Handle Errors Gracefully
```python
# Separate successful from failed
successful = [r for r in batch_results if r['success']]
failed = [r for r in batch_results if not r['success']]

# Retry failed with different model
for fail in failed:
    retry_with_model("gemini-1.5-pro-002")
```

### 4. Save Intermediate Results
```python
# Save after every 10 files
if len(batch_results) % 10 == 0:
    save_batch_results(batch_results, f"checkpoint_{len(batch_results)}.json")
```

### 5. Track Progress
```python
# Use progress bar for large batches
from tqdm import tqdm

for file in tqdm(files):
    result = process_and_evaluate(file)
```

## 🔧 Customization Options

### Adjust Validation Thresholds
```python
# In evaluate_extraction function:
# - Voter/ballot discrepancy threshold (currently 5)
# - Thai text quality thresholds (currently 80%/50%)
# - Add custom business rules
```

### Add Custom Checks
```python
def evaluate_extraction(data: dict, report_index: int = 0):
    # ... existing checks ...

    # Custom check: Minimum vote count per candidate
    min_votes = 10
    low_vote_candidates = [
        v for v in vote_results
        if get_number_value(v.get("vote_count")) < min_votes
    ]

    if low_vote_candidates:
        checks.append(ValidationCheck(
            check_name="minimum_votes",
            status="warning",
            message=f"Found {len(low_vote_candidates)} candidates with <{min_votes} votes"
        ))
```

### Export to Different Formats
```python
# Export evaluations to CSV
eval_df = pd.DataFrame([e.to_dict() for e in evaluations])
eval_df.to_csv("evaluation_results.csv", index=False)

# Export to Excel with multiple sheets
with pd.ExcelWriter("batch_results.xlsx") as writer:
    summary_df.to_sheet(writer, sheet_name="Summary")
    details_df.to_sheet(writer, sheet_name="Details")
    evaluations_df.to_sheet(writer, sheet_name="Evaluations")
```

## 🎯 Integration with Production

### Backend Service Integration

The evaluation system can be integrated into the FastAPI backend:

```python
# In vote_extraction_service.py
async def extract_from_images(self, image_files, image_filenames):
    # ... existing extraction ...

    # Run evaluation
    from notebooks.evaluation import evaluate_extraction

    evaluations = []
    for report_data in result:
        eval_result = evaluate_extraction(report_data)
        evaluations.append(eval_result.to_dict())

    # Submit to Datadog LLMObs
    for eval_result in evaluations:
        LLMObs.submit_evaluation(
            span=span_context,
            ml_app="vote-extractor",
            label="extraction_quality",
            metric_type="score",
            value=eval_result.quality_score,
            tags={"form_type": report_data["form_info"]["form_type"]}
        )

    return result, evaluations
```

## 📊 Sample Output Files

After running batch processing, you'll get:

1. **batch_results_3files.json** - Full results with evaluations
2. **batch_summary_3files.csv** - Quick summary table
3. **extracted_data_{file_id}.json** - Individual extractions (if saved separately)

## 🎉 Success Criteria

A successful batch processing run should have:

- ✅ Success rate > 95%
- ✅ Average quality score > 80%
- ✅ Valid reports > 90%
- ✅ Thai text coverage > 70%
- ✅ No critical errors

## 🔗 Next Steps

1. **Test the evaluation** - Run on test file
2. **Batch process small set** - 5-10 files
3. **Analyze quality metrics** - Identify issues
4. **Tune prompts** - Improve Thai text extraction
5. **Scale to province** - Process all files for one province
6. **Full deployment** - Process all 105k files

The comprehensive evaluation system is now ready for production use! 🚀
