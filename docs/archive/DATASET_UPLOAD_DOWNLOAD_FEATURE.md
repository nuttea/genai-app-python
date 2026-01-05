# ✅ Dataset Upload & Download Feature

**Feature**: Import/Export datasets from/to local machine  
**Status**: ✅ Implemented  
**Date**: January 4, 2026

---

## 🎯 Overview

Added two new features to the **Dataset Manager** "Load Existing Dataset" section:

1. **📤 Upload Dataset**: Import dataset JSON files from your local machine
2. **📥 Download Dataset**: Export the currently loaded dataset (all fields) to your local machine

These features enable easy dataset sharing, backup, and migration between environments.

---

## ✨ Features Added

### 1. Upload Dataset from Local Machine

**Location**: `📁 Load Existing Dataset` → Top section

**Features**:
- Drag-and-drop or browse to upload JSON files
- Validates dataset structure (checks for `metadata` and `records` fields)
- Loads dataset directly into the app
- **Optional**: Save uploaded dataset to server storage for reuse
- Shows dataset summary after upload (name, records, pages)

**Use Cases**:
- Import datasets created on another machine
- Restore datasets from backups
- Share datasets between team members
- Migrate datasets from development to production

### 2. Download Dataset to Local Machine

**Location**: `📁 Load Existing Dataset` → "Current Dataset" section

**Features**:
- One-click download button
- Exports **ALL fields** (metadata, records, input, ground truth, custom fields)
- Auto-generates filename with timestamp: `{name}_{timestamp}.json`
- Pretty-printed JSON (2-space indent, UTF-8 encoded)
- Shows export details (filename, fields included)

**Use Cases**:
- Backup datasets to local machine
- Share datasets with team members
- Version control for datasets
- Offline dataset editing

---

## 🚀 How to Use

### Upload a Dataset

1. Open Dataset Manager in Streamlit
2. Select **"📁 Load Existing Dataset"** from the sidebar
3. Go to **"📤 Upload Dataset from Local Machine"** section
4. Click **"Browse files"** or drag-and-drop a JSON file
5. The dataset will be loaded automatically
6. **Optional**: Enter a name and click **"💾 Save to Server"** to persist it

**Expected Output**:
```
✅ Uploaded dataset: vote-extraction-bangbamru-1-10
📊 Records: 10 | Pages: 60
```

### Download a Dataset

1. Load any dataset (from server or upload)
2. Scroll to **"💾 Export Dataset"** section
3. Click **"📥 Download Dataset (JSON)"**
4. The file will be downloaded to your browser's download folder

**Downloaded File**:
- **Filename**: `vote-extraction-bangbamru-1-10_20260104_151530.json`
- **Contains**: All dataset fields including metadata, records, input, ground truth

---

## 📂 File Structure

### Uploaded/Downloaded Dataset Format

```json
{
  "metadata": {
    "name": "vote-extraction-bangbamru-1-10",
    "version": "v1",
    "description": "Auto-generated from LLM extraction on 2026-01-04 02:20:54",
    "created_at": "2026-01-04T02:20:54",
    "num_records": 10,
    "total_pages": 60
  },
  "records": [
    {
      "id": "บางบำหรุ1",
      "input": {
        "form_set_name": "บางบำหรุ1",
        "image_paths": [
          "/app/assets/ss5-18-images/บางบำหรุ1_P01.jpg",
          "/app/assets/ss5-18-images/บางบำหรุ1_P02.jpg",
          ...
        ],
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
          "polling_station_number": "4"
        },
        "voter_statistics": {
          "eligible_voters": 806,
          "voters_present": 460
        },
        "ballot_statistics": {
          "ballots_allocated": 620,
          "ballots_used": 439,
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
          },
          ...
        ]
      },
      "pages_processed": 6,
      "extraction_status": "success"
    },
    ...
  ]
}
```

**All fields are preserved** in upload/download operations.

---

## 💡 Usage Examples

### Example 1: Share Dataset with Team Member

**Sender**:
1. Load dataset in Dataset Manager
2. Click **"📥 Download Dataset (JSON)"**
3. Send the `.json` file via email/Slack/etc.

**Receiver**:
1. Open Dataset Manager
2. Go to **"📁 Load Existing Dataset"**
3. Upload the received `.json` file
4. Click **"💾 Save to Server"** (optional, to persist)

### Example 2: Backup Before Editing

1. Load your dataset
2. Click **"📥 Download Dataset (JSON)"** to create a backup
3. Make changes to the dataset
4. If something goes wrong, upload the backup file to restore

### Example 3: Version Control

1. Download dataset: `my-dataset_v1_20260104.json`
2. Make improvements and download again: `my-dataset_v2_20260104.json`
3. Compare versions locally using diff tools
4. Upload the best version

### Example 4: Offline Editing

1. Download dataset to local machine
2. Edit the JSON file with your favorite text editor
3. Upload the modified dataset
4. Verify changes in Dataset Manager

---

## 🔧 Technical Details

### Upload Implementation

**File**: `frontend/streamlit/pages/2_📊_Dataset_Manager.py`

**Key Features**:
- Uses `st.file_uploader()` with `type=["json"]`
- Parses uploaded file with `json.loads()`
- Validates required fields (`metadata`, `records`)
- Optional server-side save with timestamp
- Error handling for invalid JSON and missing fields

**Code Location**: Lines ~755-795

### Download Implementation

**Key Features**:
- Uses `st.download_button()` with `mime="application/json"`
- Converts dataset to JSON with `json.dumps(indent=2, ensure_ascii=False)`
- Auto-generates filename with timestamp
- UTF-8 encoding for Thai characters
- Preserves all dataset fields (no filtering)

**Code Location**: Lines ~845-865

---

## 🎨 UI Design

### Upload Section

```
📤 Upload Dataset from Local Machine
┌─────────────────────────────────────────┐
│ [Browse files] or drag and drop         │
│ json files accepted                      │
└─────────────────────────────────────────┘

[After upload]
Save as (optional): imported-dataset     [💾 Save to Server]
✅ Uploaded dataset: vote-extraction-bangbamru-1-10
📊 Records: 10 | Pages: 60
```

### Download Section

```
💾 Export Dataset
Download the complete dataset (all fields) to your local machine

┌──────────────────────────────────────────────────────┐
│           📥 Download Dataset (JSON)                  │
└──────────────────────────────────────────────────────┘

💡 Export includes: All metadata, records, input data, 
   ground truth annotations, and custom fields.

   File: vote-extraction-bangbamru-1-10_20260104_151530.json
```

---

## 🧪 Testing Checklist

### Upload Tests

- [x] Upload valid dataset JSON → ✅ Loads successfully
- [x] Upload invalid JSON → ❌ Shows error message
- [x] Upload JSON without `metadata` field → ❌ Shows validation error
- [x] Upload JSON without `records` field → ❌ Shows validation error
- [x] Upload and save to server → ✅ File saved with timestamp
- [x] Upload dataset with Thai characters → ✅ UTF-8 preserved

### Download Tests

- [x] Download dataset → ✅ File downloaded to browser
- [x] Downloaded file is valid JSON → ✅ Can be parsed
- [x] Downloaded file preserves all fields → ✅ All fields present
- [x] Downloaded file has correct filename → ✅ `{name}_{timestamp}.json`
- [x] Downloaded file has Thai characters → ✅ UTF-8 encoded correctly
- [x] Upload downloaded file → ✅ Round-trip successful

---

## 📊 File Locations

| File | Change |
|------|--------|
| `frontend/streamlit/pages/2_📊_Dataset_Manager.py` | ✅ Added upload section (lines ~755-795)<br>✅ Added download section (lines ~845-865) |
| `DATASET_UPLOAD_DOWNLOAD_FEATURE.md` | ✅ Feature documentation (this file) |

---

## 🔗 Related Features

### Existing Features
- **Create/Edit Dataset**: Manually create datasets with ground truth annotations
- **Load from Server**: Load datasets from server storage
- **Push to Datadog**: Export datasets to Datadog LLM Observability

### Workflow Integration

```
┌─────────────────────────────────────────────────────────┐
│                   Dataset Lifecycle                     │
└─────────────────────────────────────────────────────────┘

1. Create/Edit     → Manual annotation in Dataset Manager
2. Save to Server  → Store in datasets/vote-extraction/
3. Download        → Backup to local machine (NEW!)
4. Share           → Send JSON file to team members
5. Upload          → Import on another machine (NEW!)
6. Push to Datadog → Use for LLM experiments
```

---

## 💡 Best Practices

### 1. **Regular Backups**

Download datasets after major changes:
```
my-dataset_20260104_morning.json    # Before editing
my-dataset_20260104_afternoon.json  # After editing
```

### 2. **Version Naming**

Use descriptive names when saving uploaded datasets:
```
vote-extraction-v1-baseline.json
vote-extraction-v2-corrected.json
vote-extraction-v3-expanded.json
```

### 3. **Share with Context**

When sharing datasets, include a README:
```
Dataset: vote-extraction-bangbamru-1-10
Purpose: Baseline testing for Thai election forms
Records: 10 forms (60 pages)
Created: 2026-01-04
Notes: Hand-verified ground truth from บางบำหรุ district
```

### 4. **Validate After Upload**

After uploading a dataset:
1. Check record count matches expected
2. Verify a few sample records
3. Test with an experiment to ensure compatibility

---

## 🚨 Error Handling

### Upload Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid JSON file" | Malformed JSON syntax | Use a JSON validator before uploading |
| "Invalid dataset format" | Missing `metadata` or `records` | Ensure file has correct structure |
| "Error loading file" | Unexpected exception | Check file encoding (should be UTF-8) |

### Download Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Download fails | Browser blocked download | Check browser download settings |
| File corrupted | Encoding issue | Ensure UTF-8 support in browser |
| No data in file | Dataset not loaded | Load a dataset first |

---

## 🎉 Benefits

### For Users
- ✅ **Easy Backup**: Download datasets to local machine with one click
- ✅ **Easy Sharing**: Send JSON files via email, Slack, or file sharing
- ✅ **Offline Editing**: Edit datasets locally with any text editor
- ✅ **Version Control**: Track changes with timestamped filenames

### For Teams
- ✅ **Collaboration**: Share datasets between team members
- ✅ **Portability**: Move datasets between dev/staging/production
- ✅ **Consistency**: Same dataset format across all environments
- ✅ **Reproducibility**: Archive datasets for future reference

### For Operations
- ✅ **Disaster Recovery**: Backup critical datasets
- ✅ **Migration**: Move datasets between servers
- ✅ **Auditing**: Track dataset changes over time
- ✅ **Compliance**: Export datasets for archival requirements

---

## 🔮 Future Enhancements

Potential improvements for future versions:

1. **Bulk Upload**: Upload multiple datasets at once
2. **Format Conversion**: Import/export CSV or Excel formats
3. **Compression**: Download as `.zip` for large datasets
4. **Cloud Storage**: Upload/download from Google Drive, Dropbox
5. **Auto-backup**: Scheduled backups to cloud storage
6. **Diff View**: Compare two dataset versions side-by-side
7. **Merge Datasets**: Combine multiple datasets into one

---

## 📚 Related Documentation

- **Dataset Manager Guide**: `DATASET_MANAGER_QUICKSTART.md`
- **Schema Documentation**: `DATASET_MANAGER_SCHEMA_UPDATE.md`
- **Datadog Integration**: `DATASET_DATADOG_SDK_SUCCESS.md`
- **Experiments Notebook**: `notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb`

---

## ✅ Summary

| Feature | Status | Description |
|---------|--------|-------------|
| Upload Dataset | ✅ Complete | Import JSON from local machine |
| Save Uploaded Dataset | ✅ Complete | Optionally save to server storage |
| Download Dataset | ✅ Complete | Export all fields to local machine |
| Validation | ✅ Complete | Check structure on upload |
| Error Handling | ✅ Complete | Clear messages for issues |
| UTF-8 Support | ✅ Complete | Thai characters preserved |

---

**Ready to use!** 🚀 

Upload and download datasets in the Dataset Manager's "📁 Load Existing Dataset" section.

