# Dataset Preparation Notebooks

This directory contains Jupyter notebooks for creating and managing datasets for Datadog LLM Experiments.

## 📓 Available Notebooks

### 1. `01_prepare_vote_extraction_dataset.ipynb`

**Purpose**: Prepare Thai election form dataset for vote extraction experiments.

**What it does**:
- Loads test images from `assets/ss5-18-images/`
- Creates dataset records with ground truth
- Validates dataset quality
- Saves dataset locally as JSON
- Pushes dataset to Datadog via API

**Prerequisites**:
```bash
pip install jupyter requests pillow python-dotenv
```

**How to run**:
```bash
cd notebooks/datasets
jupyter notebook 01_prepare_vote_extraction_dataset.ipynb
```

**Environment variables** (set in `.env`):
- `DD_API_KEY`: Your Datadog API key
- `DD_APP_KEY`: Your Datadog Application key
- `DD_SITE`: Your Datadog site (default: `datadoghq.com`)

---

## 🎯 Quick Start

1. **Install dependencies**:
   ```bash
   pip install jupyter requests pillow python-dotenv
   ```

2. **Set up environment**:
   ```bash
   # Copy .env.example to .env and add your keys
   cp ../../.env.example ../../.env
   # Edit .env and add DD_API_KEY and DD_APP_KEY
   ```

3. **Launch Jupyter**:
   ```bash
   jupyter notebook
   ```

4. **Open and run** `01_prepare_vote_extraction_dataset.ipynb`

---

## 📁 Output Files

Datasets are saved to: `../../datasets/vote-extraction/`

**File naming**:
- Timestamped: `vote-extraction-thai-elections-v1_20260104_123456.json`
- Latest symlink: `vote-extraction-thai-elections-v1_latest.json`

**Format**:
```json
{
  "metadata": {
    "name": "vote-extraction-thai-elections-v1",
    "version": "v1",
    "created_at": "2026-01-04T12:34:56",
    "num_records": 1
  },
  "records": [
    {
      "id": "form-001",
      "input": {
        "image_paths": ["assets/ss5-18-images/page1.jpg", ...],
        "form_type": "ss5_18",
        "province": "Bangkok"
      },
      "expected_output": {
        "ballot_statistics": {
          "total_votes": 520,
          "valid_ballots": 495,
          "invalid_ballots": 25
        },
        "vote_results": [...]
      }
    }
  ]
}
```

---

## 🔗 Related Documentation

- **[Guide 04: Experiments and Datasets](../../guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md)** - Complete guide
- **[Assets README](../../assets/README.md)** - Image source information
- **[Datadog Experiments Docs](https://docs.datadoghq.com/llm_observability/experiments/)** - Official documentation

---

## 💡 Tips

### Adding Ground Truth

1. **Manual Review**: Carefully verify each form by eye
2. **Double-Check Math**: Ensure `valid + invalid = total`
3. **Document Issues**: Note any unclear or damaged forms
4. **Version Control**: Commit JSON files to Git

### Dataset Quality

**Good practices**:
- ✅ Include typical cases (60%)
- ✅ Add edge cases (30%)
- ✅ Include error cases (10%)
- ✅ Verify all data manually
- ✅ Regular quality audits

### Datadog Integration

**Before pushing to Datadog**:
1. Validate all records locally
2. Test with a small dataset first (1-2 records)
3. Verify in Datadog UI before adding more
4. Document dataset ID and project ID

---

## 🚨 Troubleshooting

### Issue: Import errors

**Solution**:
```bash
pip install --upgrade jupyter requests pillow python-dotenv
```

### Issue: API authentication fails

**Solution**:
- Check that `DD_API_KEY` and `DD_APP_KEY` are set in `.env`
- Verify keys are valid in Datadog UI (Organization Settings → API Keys)
- Ensure you have proper permissions

### Issue: Images not found

**Solution**:
- Verify images exist in `assets/ss5-18-images/`
- Check file paths in ground truth data
- Ensure you're running notebook from `notebooks/datasets/` directory

---

**Last Updated**: January 4, 2026  
**Maintained By**: GenAI App Team

