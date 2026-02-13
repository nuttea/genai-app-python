# Thai Election Form Extractor - Jupyter Notebooks

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nuttea/genai-app-python/blob/main/notebooks/gemini-ss5_18_bigquery_drive.ipynb)

Extract structured data from Thai election form PDFs (Form S.S. 5/18) using **Gemini with Structured Output**, **BigQuery**, and **Google Drive**.

## 🚀 Recommended Notebook

**[gemini-ss5_18_bigquery_drive.ipynb](gemini-ss5_18_bigquery_drive.ipynb)** - Production-ready notebook with:

- 🔍 **BigQuery Integration** - Query 105k+ PDF files
- 📁 **Google Drive Direct Access** - No downloads needed
- 🤖 **Gemini Structured Output** - Enhanced schema with NumberTextPair
- ✅ **7-Point Validation System** - Quality scoring (0-100%)
- 🔄 **Batch Processing** - Process multiple files efficiently
- 📊 **Comprehensive Evaluation** - Automatic quality assessment

## Quick Start

### Prerequisites

1. **Google Cloud Project** with:
   - Gemini API enabled
   - BigQuery API enabled
   - Access to `sourceinth.vote69_ect.raw_files` table

2. **Gemini API Key** (required)

### Environment Setup

#### Option 1: Using .env File (Recommended)

Create a `.env` file in the notebooks directory:

```bash
# notebooks/.env
GEMINI_API_KEY=your-api-key-here
GOOGLE_CLOUD_PROJECT=your-project-id
```

#### Option 2: Using Environment Variables

```bash
export GEMINI_API_KEY="your-api-key-here"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

#### Option 3: Google Colab Input (Recommended for Colab)

Add this cell at the beginning of your Colab notebook:

```python
import os
from getpass import getpass

# Set Gemini API Key (hidden input)
if 'GEMINI_API_KEY' not in os.environ:
    os.environ['GEMINI_API_KEY'] = getpass('Enter your Gemini API Key: ')

# Set Google Cloud Project ID
if 'GOOGLE_CLOUD_PROJECT' not in os.environ:
    os.environ['GOOGLE_CLOUD_PROJECT'] = input('Enter your Google Cloud Project ID: ')

print("✅ Environment variables set!")
```

**Alternative:** Use Colab Secrets
1. Click the 🔑 key icon in the left sidebar
2. Add secrets: `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`

### Installation

#### Local Jupyter

```bash
# 1. Navigate to notebooks directory
cd notebooks

# 2. Install dependencies
pip install -r requirements-pdf-extractor.txt

# 3. Start Jupyter
jupyter notebook gemini-ss5_18_bigquery_drive.ipynb
```

#### Google Colab

1. **Click** the "Open in Colab" badge above [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nuttea/genai-app-python/blob/main/notebooks/gemini-ss5_18_bigquery_drive.ipynb)

2. **Add configuration cell** at the top:
   ```python
   import os
   from getpass import getpass

   # Set your credentials
   os.environ['GEMINI_API_KEY'] = getpass('Gemini API Key: ')
   os.environ['GOOGLE_CLOUD_PROJECT'] = input('Project ID: ')
   ```

3. **Run the configuration cell** - Enter your API key and project ID

4. **Run all cells** - Process starts automatically!

### Google Colab Quick Setup

When running in Colab, add this cell **before Cell 2 (Configuration)**:

```python
# ═══════════════════════════════════════════════════════════
# 🔑 COLAB CONFIGURATION - Run this cell first!
# ═══════════════════════════════════════════════════════════

import os
from getpass import getpass

# 1. Set Gemini API Key (get from: https://aistudio.google.com/app/apikey)
if 'GEMINI_API_KEY' not in os.environ:
    os.environ['GEMINI_API_KEY'] = getpass('🔑 Enter your Gemini API Key: ')

# 2. Set Google Cloud Project ID
if 'GOOGLE_CLOUD_PROJECT' not in os.environ:
    os.environ['GOOGLE_CLOUD_PROJECT'] = input('📦 Enter your Google Cloud Project ID: ')

# Verify
print("\n✅ Configuration complete!")
print(f"   Project: {os.environ['GOOGLE_CLOUD_PROJECT']}")
print(f"   API Key: {'*' * 20}...{os.environ['GEMINI_API_KEY'][-8:]}")
```

Then run the rest of the notebook normally!

### Local Development Authentication

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project
gcloud config set project your-project-id
```

## 📚 Available Notebooks

| Notebook | Use Case | Features |
|----------|----------|----------|
| **[gemini-ss5_18_bigquery_drive.ipynb](gemini-ss5_18_bigquery_drive.ipynb)** ⭐ | Production | BigQuery, Drive URLs, Evaluation, Batch |
| [gemini-ss5_18_pdf_extractor.ipynb](gemini-ss5_18_pdf_extractor.ipynb) | Testing | Simple Drive URL method |

## 🎯 Features

### 1. Enhanced Data Schema

**NumberTextPair Structure:**
```python
{
  "vote_count": {
    "arabic": 120,
    "thai_text": "หนึ่งร้อยยี่สิบ"
  }
}
```

**New Fields:**
- `set_number` (ชุดที่) - Set/batch number
- `village_moo` (หมู่ที่) - Village number
- `total_votes_recorded` - Total from table footer
- `voter_statistics` - Eligible and present voters
- `officials` - Committee members who signed

### 2. Comprehensive Validation

**7 Validation Checks:**
1. ✅ Form info completeness
2. ✅ Ballot accounting (used = good + bad + no_vote)
3. ✅ Total votes (sum = recorded total)
4. ⚠️ Voter/ballot consistency
5. ✅ Vote results exist
6. ✅ Non-negative votes
7. ⚠️ Thai text quality

**Quality Score:** 0-100% based on passed/failed/warning checks

### 3. Batch Processing

```python
# Process multiple files with automatic evaluation
batch_results = batch_process_from_bigquery(
    limit=10,
    province="กรุงเทพมหานคร",
    min_size_kb=50.0,      # Exclude corrupted files
    max_size_mb=50.0,      # Limit file size
    model="gemini-exp-1206",
    run_evaluation=True    # Quality assessment
)
```

**Output:**
- Success rate, average quality score
- Per-file evaluations
- Summary table (CSV)
- Full results (JSON)

## 📋 Usage Example

### Basic Workflow

```python
# 1. Query BigQuery for PDF files
pdf_files = query_pdf_files(
    limit=10,
    province="กรุงเทพมหานคร",
    min_size_kb=50.0,
    max_size_mb=50.0
)

# 2. Select a file
test_file = pdf_files[0]
drive_uri = f"https://drive.google.com/uc?export=download&id={test_file['file_id']}"

# 3. Extract data
result = extract_from_drive_url(drive_uri, model="gemini-exp-1206")

# 4. Display results
display_results(result)

# 5. Run evaluation
eval_result = evaluate_extraction(result[0])
print_evaluation_summary(eval_result)
```

### BigQuery Queries

#### Find Small Files for Testing
```sql
SELECT file_id, path, size / 1024 / 1024 as size_mb
FROM `sourceinth.vote69_ect.raw_files`
WHERE mime_type = 'application/pdf'
  AND size >= 51200        -- Min 50 KB
  AND size <= 20971520     -- Max 20 MB
ORDER BY size ASC
LIMIT 10;
```

#### Count Files by Province
```sql
SELECT
    province_name,
    COUNT(*) as file_count,
    SUM(size) / 1024 / 1024 / 1024 as total_gb
FROM `sourceinth.vote69_ect.raw_files`
WHERE mime_type = 'application/pdf'
  AND size >= 51200
GROUP BY province_name
ORDER BY file_count DESC;
```

## 🔧 Configuration

### Required Environment Variables

```bash
# Required
GEMINI_API_KEY=your-gemini-api-key-here
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional
VERTEX_AI_LOCATION=us-central1  # Not used currently, but can switch to Vertex AI
```

### .env File Template

```bash
# Gemini API Configuration
GEMINI_API_KEY=AIzaSy...your-key-here

# Google Cloud Project
GOOGLE_CLOUD_PROJECT=your-project-id

# BigQuery Dataset (already set in notebook)
# BQ_TABLE=sourceinth.vote69_ect.raw_files
```

## 📊 Supported Models

The notebooks support Gemini models via API:

- **`gemini-3-pro-preview`** - Latest experimental
- **`gemini-3-flash-preview`** - Fast experimental
- **`gemini-2.5-pro`** - Stable production
- **`gemini-2.5-flash`** - Fast production

**Note:** Currently configured to use Gemini API (not Vertex AI). Set `GEMINI_API_KEY` in your environment.

## 📈 What Gets Extracted

### Form Information
- Form type (Constituency/PartyList)
- Province, District, Sub-district
- Polling station number
- Set number, Village number
- Date

### Voter Statistics
- Eligible voters (with Thai text)
- Present voters (with Thai text)

### Ballot Statistics
- Allocated, Used, Remaining
- Good, Bad, No-vote ballots
- Each with Arabic number + Thai text

### Vote Results
- Candidate/Party number
- Candidate name (for Constituency)
- Party name
- Vote count (Arabic + Thai text)

### Additional Data
- Total votes recorded (for validation)
- Committee members/officials

## 🎯 Quality Metrics

After extraction, you get:

- **Quality Score**: 0-100% based on validation checks
- **Validation Status**: Pass/Fail for each check
- **Errors**: Critical issues that must be fixed
- **Warnings**: Non-critical issues

**Example Output:**
```
📊 Overall Status: ✅ VALID
📈 Quality Score: 92.9%

📋 Check Results:
   ✅ Passed: 6/7
   ⚠️  Warnings: 1/7
```

## 🔍 Validation Rules

1. **Ballot Accounting**: `ballots_used = good + bad + no_vote`
2. **Total Votes**: `sum(vote_counts) = total_recorded`
3. **Voter Consistency**: `present_voters ≈ ballots_used` (±5 tolerance)
4. **Thai Text Quality**: Checks if Thai text is extracted (>80% coverage)

## 🚀 Production Workflow

### Step 1: Test Single File (5 minutes)
```python
# Test with one small file
pdf_files = query_pdf_files(limit=1, max_size_mb=5.0)
result = extract_from_drive_url(...)
```

### Step 2: Small Batch (30 minutes)
```python
# Process 10 files
batch_results = batch_process_from_bigquery(limit=10)
```

### Step 3: Province Batch (hours)
```python
# Process all files for one province
batch_results = batch_process_from_bigquery(
    province="กรุงเทพมหานคร",
    limit=1000
)
```

### Step 4: Full Dataset (days)
```python
# Process all 105k files
# Run in batches of 100-500 files
# Save checkpoints regularly
```

## 📦 Output Files

After batch processing:

1. **batch_results_{N}files.json** - Full extraction + evaluation results
2. **batch_summary_{N}files.csv** - Quick summary table
3. **extracted_data_{file_id}.json** - Individual files (optional)

## 🔗 Integration

### With FastAPI Backend

The schema matches the backend service:
- Same Pydantic models
- Same validation logic
- Can share extracted data

### With Streamlit Frontend

Display extracted data in the Vote Extractor UI.

### With BigQuery

Save results back to BigQuery for analysis:
```python
# Flatten and save to BigQuery
bq_table.insert_rows(flattened_results)
```

## 💡 Tips

### For Best Results

1. **Start small** - Test with 1-3 files first
2. **Check quality** - Aim for >80% quality score
3. **Monitor errors** - Review failed extractions
4. **Adjust filters** - Use min_size_kb=50 to exclude corrupted files
5. **Save regularly** - Save batch results every 10-50 files

### Performance

- **Small files** (<5 MB): ~10-20 seconds per file
- **Medium files** (5-20 MB): ~30-60 seconds per file
- **Large files** (>20 MB): ~1-3 minutes per file

### Cost Optimization

- Filter by file size (min_size_kb=50, max_size_mb=20)
- Process smaller files first (test accuracy)
- Use batches of 100-500 files
- Monitor API usage

## 🆘 Troubleshooting

### Error: "GEMINI_API_KEY not found"

```bash
# Check if env var is set
echo $GEMINI_API_KEY

# If not, set it
export GEMINI_API_KEY="your-key-here"

# Or create .env file
echo 'GEMINI_API_KEY=your-key-here' > .env
```

### Error: "BigQuery authentication failed"

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Verify project
gcloud config get-value project
```

### Error: "Model not found"

```python
# Try different model
MODEL_NAME = "gemini-1.5-flash-002"  # Stable fallback
```

### Error: "File access denied"

Check if the Google Drive files are accessible:
- Files must be shared with your Google account
- Or files must be in a shared drive you have access to

## 📚 Documentation

- **[SCHEMA_COMPARISON.md](SCHEMA_COMPARISON.md)** - Schema analysis
- **[SCHEMA_UPDATES.md](SCHEMA_UPDATES.md)** - Migration guide
- **[EVALUATION_GUIDE.md](EVALUATION_GUIDE.md)** - Validation system guide
- **[TEST_FILE_INFO.md](TEST_FILE_INFO.md)** - Sample test files

## 🎓 Learning Resources

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Gemini File Input Methods](https://ai.google.dev/gemini-api/docs/file-input-methods)
- [BigQuery Python Client](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🔗 Related Files

### Backend Service
- `services/fastapi-backend/app/services/vote_extraction_service.py`
- `services/fastapi-backend/app/models/vote_extraction.py`

### Frontend
- `frontend/streamlit/pages/1_🗳️_Vote_Extractor.py`

## 📊 Dataset Information

**BigQuery Table:** `sourceinth.vote69_ect.raw_files`

- **Total PDF files:** 105,450
- **Provinces:** All provinces in Thailand
- **File size range:** 50 KB - 264 MB
- **Format:** Thai election forms (S.S. 5/18)

## 🎉 What Makes This Better

| Feature | Local PDF Processing | **This Notebook** |
|---------|---------------------|-------------------|
| Input | Download PDFs locally | ☁️ Google Drive URLs |
| Conversion | pdf2image + poppler | ❌ Not needed |
| Storage | Local disk | ☁️ Cloud only |
| BigQuery | ❌ Manual queries | ✅ Integrated |
| Validation | Basic (2 checks) | ✅ Advanced (7 checks) |
| Quality Score | ❌ No metrics | ✅ 0-100% scoring |
| Batch Processing | Manual loop | ✅ Automated with eval |
| Thai Text | Single format | ✅ Dual format validation |
| Speed | Slower | ⚡ Faster |
| Scale | Difficult | ✅ 105k+ files ready |

## 🎬 Example Session

```python
# Set up
%env GEMINI_API_KEY=your-key-here

# Query files
pdf_files = query_pdf_files(limit=5, province="พิจิตร", min_size_kb=50.0)

# Process with evaluation
batch_results = batch_process_from_bigquery(
    limit=5,
    province="พิจิตร",
    run_evaluation=True
)

# Results:
# ✅ Successful: 5/5
# 📈 Average Quality: 88.5%
# 💾 Saved: batch_results_5files.json
```

## 📄 License

This notebook is part of the genai-app-python project.

---

**Ready to extract from 105,450 Thai election forms!** 🗳️🇹🇭
