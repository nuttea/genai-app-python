# 📤📥 Dataset Upload & Download - Quick Guide

**Status**: ✅ Ready to use  
**Location**: Dataset Manager → "📁 Load Existing Dataset"

---

## 🚀 Quick Start

### Upload a Dataset

1. Open **Dataset Manager** in Streamlit
2. Select **"📁 Load Existing Dataset"** from sidebar
3. Find **"📤 Upload Dataset from Local Machine"** section
4. Drop your `.json` file or click "Browse files"
5. ✅ Dataset loads automatically!
6. *Optional*: Click **"💾 Save to Server"** to keep it

### Download a Dataset

1. Load any dataset in **"📁 Load Existing Dataset"**
2. Scroll to **"💾 Export Dataset"** section
3. Click **"📥 Download Dataset (JSON)"**
4. ✅ File downloads to your computer!

---

## 💡 Common Use Cases

### Backup a Dataset
```
1. Load dataset
2. Click "Download Dataset (JSON)"
3. File saved: my-dataset_20260104_151530.json ✅
```

### Share with Team Member
```
Sender:  Download → Send file via email/Slack
Receiver: Upload → (Optional) Save to Server
```

### Edit Offline
```
1. Download dataset
2. Edit JSON file locally
3. Upload modified dataset
4. Verify changes in app
```

### Migrate Between Servers
```
Old Server: Download all datasets
New Server: Upload datasets one by one
```

---

## 📋 Features

| Feature | Description |
|---------|-------------|
| **Upload** | Import JSON from local machine |
| **Download** | Export all fields to local machine |
| **Validation** | Checks dataset structure on upload |
| **Auto-save** | Option to save uploaded datasets |
| **UTF-8** | Thai characters fully supported |
| **Timestamp** | Auto-generated filenames |

---

## ✅ What's Included in Downloads?

**Everything!** The download includes:
- ✅ Metadata (name, version, description)
- ✅ All records
- ✅ Input data (form names, image paths, pages)
- ✅ Ground truth annotations
- ✅ Custom fields and notes
- ✅ Extraction status and metadata

**Example filename**: `vote-extraction-bangbamru-1-10_20260104_151530.json`

---

## 🔧 File Format

Upload/download files must follow this structure:

```json
{
  "metadata": {
    "name": "my-dataset",
    "version": "v1",
    "description": "...",
    "created_at": "2026-01-04T02:20:54",
    "num_records": 10,
    "total_pages": 60
  },
  "records": [
    {
      "id": "record-1",
      "input": {
        "form_set_name": "...",
        "image_paths": [...],
        "num_pages": 6
      },
      "ground_truth": {
        "form_info": {...},
        "ballot_statistics": {...},
        "vote_results": [...]
      }
    }
  ]
}
```

---

## ⚠️ Important Notes

- **Valid JSON**: Upload files must be valid JSON format
- **Required Fields**: Must have `metadata` and `records` sections
- **Encoding**: UTF-8 encoding for Thai characters
- **File Size**: No hard limit, but large files may be slow
- **Browser Download**: Files download to your browser's default folder

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid JSON file" | Validate JSON syntax with [JSONLint](https://jsonlint.com/) |
| "Invalid dataset format" | Ensure `metadata` and `records` fields exist |
| Download doesn't start | Check browser download settings |
| Thai characters broken | Ensure UTF-8 encoding |
| Upload shows no records | Check `records` array has items |

---

## 📚 Full Documentation

For complete details, see: [DATASET_UPLOAD_DOWNLOAD_FEATURE.md](DATASET_UPLOAD_DOWNLOAD_FEATURE.md)

---

**Need Help?** Check the full documentation or ask in the project chat!

