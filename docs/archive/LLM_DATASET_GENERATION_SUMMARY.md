# LLM Dataset Generation - Summary

**Date**: January 4, 2026  
**Status**: ✅ **COMPLETE** - Dataset successfully generated and fixed

---

## 📊 Generated Dataset

### **File Information:**
- **Path**: `datasets/vote-extraction/vote-extraction-bangbamru-1-10_20260104_023007.json`
- **Size**: 310.6 KB
- **Records**: 10 form sets
- **Total Pages**: 60 images

### **Form Sets Included:**
1. บางบำหรุ1 (6 pages)
2. บางบำหรุ2 (6 pages)
3. บางบำหรุ3 (6 pages)
4. บางบำหรุ4 (6 pages)
5. บางบำหรุ5 (6 pages)
6. บางบำหรุ6 (6 pages)
7. บางบำหรุ7 (6 pages)
8. บางบำหรุ8 (6 pages)
9. บางบำหรุ9 (6 pages)
10. บางบำหรุ10 (6 pages)

### **Processing Stats:**
- ✅ **Success Rate**: 10/10 (100%)
- ⏱️ **Total Time**: ~9 minutes (~1 min per form)
- 🤖 **Method**: LLM extraction via FastAPI backend

---

## 🔧 Issue & Fix

### **Issue Encountered:**
```
KeyError: 'num_pages'
```

The generated dataset was missing the `num_pages` field in the `input` section of each record, which the Dataset Manager expects.

### **Root Cause:**
The script `generate_dataset_from_llm.py` was creating records with `pages_processed` at the top level but not including `num_pages` in the `input` dict.

### **Fix Applied:**
1. ✅ Updated the script to include `num_pages` in `input` section
2. ✅ Fixed the existing dataset file by adding missing `num_pages` field
3. ✅ Verified all 10 records are now compatible with Dataset Manager

---

## 📖 How to Use the Dataset

### **Step 1: Load in Dataset Manager**

1. Open Streamlit: http://localhost:8501/Dataset_Manager
2. Select **📁 Load Existing Dataset**
3. Choose: `vote-extraction-bangbamru-1-10_20260104_023007.json`
4. Click **📂 Load Dataset**

### **Step 2: Review Ground Truth**

The LLM has already extracted all data, but you should review for accuracy:

**✅ What's Included:**
- **Form Information**: Date, province, district, sub-district, constituency number, polling station
- **Voter Statistics**: Eligible voters, voters present
- **Ballot Statistics**: All 6 fields (allocated, used, good, bad, no vote, remaining)
- **Vote Results**: All candidates with:
  - Candidate number
  - Candidate name (for Constituency forms)
  - Party name
  - Vote count (numeric)
  - Vote count (Thai text)

**⚠️ What to Verify:**
- ✅ Ballot math: `good + bad + no_vote = used`
- ✅ Thai text transcription accuracy
- ✅ Candidate/party name spelling
- ✅ Vote count correctness

### **Step 3: Edit Ground Truth (if needed)**

If you find any errors:
1. Switch to **📝 Create/Edit Dataset** tab
2. Select the form set with errors
3. Correct the ground truth
4. Click **💾 Save Ground Truth**

### **Step 4: Push to Datadog**

Once you're satisfied with the dataset:
1. Switch to **📤 Push to Datadog** tab
2. Configure your Datadog credentials
3. Push the dataset for experiments

---

## 🚀 Script Usage

### **Location:**
```bash
scripts/datasets/generate_dataset_from_llm.py
```

### **How it Works:**
1. Discovers images in `assets/ss5-18-images/`
2. Groups images by form set name
3. Calls FastAPI backend `/api/v1/vote-extraction/extract` for each form set
4. Converts API response to ground truth format
5. Saves dataset to `datasets/vote-extraction/`

### **Customization:**

To generate datasets for different form sets, edit the `form_names` list in `main()`:

```python
form_names = [
    "บางบำหรุ1",
    "บางบำหรุ2",
    # ... add more form names
]
```

### **Run Command:**
```bash
python3 scripts/datasets/generate_dataset_from_llm.py
```

---

## 📋 Dataset Schema

Each record in the dataset follows this structure:

```json
{
  "id": "บางบำหรุ1",
  "input": {
    "form_set_name": "บางบำหรุ1",
    "image_paths": ["assets/ss5-18-images/บางบำหรุ1_page1.jpg", ...],
    "num_pages": 6
  },
  "ground_truth": {
    "form_info": {
      "form_type": "Constituency",
      "date": "14/05/2566",
      "province": "กรุงเทพมหานคร",
      "district": "บางกอกน้อย",
      "sub_district": "บางบำหรุ",
      "constituency_number": "7",
      "polling_station_number": "1"
    },
    "voter_statistics": {
      "eligible_voters": 806,
      "voters_present": 460
    },
    "ballot_statistics": {
      "ballots_allocated": 620,
      "ballots_used": 460,
      "good_ballots": 439,
      "bad_ballots": 4,
      "no_vote_ballots": 17,
      "ballots_remaining": 160
    },
    "vote_results": [
      {
        "number": 1,
        "candidate_name": "นายจักรพันธ์ พรหมิมา",
        "party_name": "ภูมิใจไทย",
        "vote_count": 8,
        "vote_count_text": "แปด"
      }
      // ... more candidates
    ],
    "notes": "Auto-generated from LLM extraction. Please review and correct."
  },
  "pages_processed": 6,
  "created_at": "2026-01-04T02:20:45.873000",
  "last_updated": "2026-01-04T02:20:45.873000",
  "extraction_metadata": {
    "api_response": { /* full API response */ },
    "needs_review": true
  }
}
```

---

## ✨ Key Features

### **Automated Extraction:**
- ✅ No manual data entry required
- ✅ Consistent schema across all records
- ✅ Full API response preserved for debugging

### **Quality Indicators:**
- ✅ `needs_review: true` flag on all records
- ✅ Notes field mentions auto-generation
- ✅ Preserves original API response for verification

### **Easy Review:**
- ✅ Load in Dataset Manager for visual review
- ✅ Edit directly in the UI
- ✅ Ballot math validation built-in

---

## 📊 Next Steps

### **Immediate:**
1. ✅ Load dataset in Dataset Manager
2. ✅ Review first 2-3 form sets thoroughly
3. ✅ Spot-check remaining form sets

### **After Review:**
1. ✅ Generate datasets for remaining 106 form sets
2. ✅ Push all datasets to Datadog
3. ✅ Run experiments to evaluate model performance

### **Future Improvements:**
- 🔄 Add parallel processing for faster generation
- 🔄 Add confidence scores from LLM
- 🔄 Add automatic validation against known patterns
- 🔄 Add support for incremental updates

---

## 📚 Related Documentation

- **Dataset Manager Guide**: `frontend/streamlit/DATASET_MANAGER_QUICKSTART.md`
- **Schema Update**: `DATASET_MANAGER_SCHEMA_UPDATE.md`
- **Experiments Guide**: `guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md`
- **Vote Extraction Service**: `services/fastapi-backend/app/services/vote_extraction_service.py`

---

**Status**: ✅ Ready for review in Dataset Manager  
**Quality**: High (LLM extraction, needs human verification)  
**Coverage**: 10/116 form sets (8.6%)

