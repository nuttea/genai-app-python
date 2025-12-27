# 🗳️ Vote Extractor User Guide

Complete guide for using the Thai Election Form Vote Extractor feature.

## Overview

The Vote Extractor is a tool that automatically extracts structured data from Thai election documents (Form S.S. 5/18) using AI-powered document understanding.

## Features

✅ **Multi-page Document Support** - Process complete election reports with multiple pages  
✅ **Structured Data Extraction** - Get JSON-formatted data ready for analysis  
✅ **Automatic Consolidation** - Merge data from all pages into a single report  
✅ **Data Validation** - Automatic validation of ballot counts  
✅ **Multiple Export Formats** - Download as CSV or JSON  
✅ **Real-time Processing** - See results as they're extracted  

## What Gets Extracted

### 1. Form Information
- Date of election
- Province name
- District name (Amphoe/Khet)
- Constituency number
- Polling station number
- Form type (Constituency or PartyList)

### 2. Ballot Statistics
- Total ballots used
- Valid ballots count
- Void/Spoiled ballots count
- No-vote ballots count

### 3. Vote Results
Complete table of all candidates/parties with:
- Candidate/Party number
- Candidate/Party name
- Vote count (numeric)
- Vote count (Thai text)

## Quick Start

### 1. Access the Application

**Local Development:**
```bash
# Start the services
make docker-up

# Or run individually
make run-fastapi      # Terminal 1
make run-streamlit    # Terminal 2
```

**Access URLs:**
- Streamlit Frontend: http://localhost:8501
- FastAPI Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 2. Navigate to Vote Extractor

1. Open http://localhost:8501 in your browser
2. Look for "🗳️ Vote Extractor" in the sidebar menu
3. Click to open the vote extraction page

### 3. Upload Election Form Images

1. Click "Browse files" button
2. Select one or more image files:
   - Supported formats: JPG, JPEG, PNG
   - Multiple pages: Yes (recommended for complete reports)
   - File size: No strict limit, but larger files take longer

3. Preview uploaded images to verify they're correct

### 4. Extract Data

1. Click "🚀 Extract Vote Data" button
2. Wait for processing (typically 10-30 seconds per page)
3. View results in organized tabs

### 5. Review and Export Results

The results are displayed in four tabs:

**📋 Summary Tab:**
- Form information (Province, District, Date, etc.)
- Key metrics displayed as cards

**📊 Vote Results Tab:**
- Complete table of all candidates/parties
- Total votes counted
- Download as CSV button

**📦 Ballot Statistics Tab:**
- Ballot counts (Used, Valid, Void, No Vote)
- Automatic validation check
- Visual indicators for data quality

**🔍 Raw JSON Tab:**
- Complete extracted data in JSON format
- Download as JSON button

## Best Practices

### Image Quality

✅ **Good:**
- Clear, high-resolution scans or photos
- Properly oriented (upright text)
- Good lighting with minimal shadows
- All text clearly readable

❌ **Avoid:**
- Blurry or low-resolution images
- Rotated or skewed documents
- Heavy shadows or glare
- Cropped text or tables

### Multi-page Documents

✅ **Recommended:**
- Upload all pages of the same report together
- Name files sequentially (e.g., page1.jpg, page2.jpg)
- Keep pages in order

❌ **Avoid:**
- Mixing pages from different reports
- Uploading pages in wrong order
- Missing pages from a report

### File Organization

```
election-forms/
├── district-bangphlat/
│   ├── station-001-page1.jpg
│   ├── station-001-page2.jpg
│   ├── station-002-page1.jpg
│   └── station-002-page2.jpg
└── district-pathumwan/
    └── ...
```

## Validation and Quality Checks

### Automatic Validation

The system automatically validates:

1. **Ballot Count Consistency:**
   - Total Ballots Used = Valid + Void + No Vote
   - Shows ✅ if correct, ❌ if mismatch

2. **Data Completeness:**
   - Required fields present
   - Vote results not empty

3. **Data Types:**
   - Numbers are numeric
   - Text fields are text

### Manual Verification

Always verify:
- ✓ Province and district names match the document
- ✓ Polling station number is correct
- ✓ Vote counts match the document
- ✓ All candidates/parties are listed
- ✓ Total votes make sense

## Troubleshooting

### Extraction Failed

**Problem:** "Failed to extract vote data" error

**Solutions:**
1. Check image quality (clarity, orientation)
2. Verify images are Thai election forms (Form S.S. 5/18)
3. Try re-uploading with better quality images
4. Check backend logs for detailed errors

### Incomplete Data

**Problem:** Some fields are missing or incorrect

**Solutions:**
1. Ensure all pages of the report are uploaded
2. Check if text in images is readable
3. Try re-scanning with higher resolution
4. Verify the form type (Constituency vs PartyList)

### Validation Warnings

**Problem:** "Ballot count mismatch" warning

**Solutions:**
1. Manually verify the numbers on the document
2. Check if all pages were uploaded
3. Look for partial or incomplete ballot statistics
4. Document may have errors (report to election officials)

### Slow Processing

**Problem:** Taking too long to process

**Reasons:**
- Large image file sizes
- Multiple pages
- Server load

**Solutions:**
1. Resize images to reasonable size (1-2 MB per page)
2. Process fewer pages at once
3. Use JPEG instead of PNG (smaller file size)
4. Wait patiently (typical: 10-30s per page)

### Connection Errors

**Problem:** "Connection refused" or timeout

**Solutions:**
1. Verify FastAPI backend is running:
   ```bash
   curl http://localhost:8000/health
   ```
2. Check `API_BASE_URL` in Streamlit configuration
3. Restart services:
   ```bash
   make docker-restart
   ```

## API Integration

### Direct API Usage

You can also use the API directly without the Streamlit frontend:

```bash
# Extract vote data
curl -X POST http://localhost:8000/api/v1/vote-extraction/extract \
  -F "files=@page1.jpg" \
  -F "files=@page2.jpg"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "form_info": {
      "province": "กรุงเทพมหานคร",
      "district": "บางพลัด",
      "polling_station_number": "25",
      "form_type": "Constituency"
    },
    "ballot_statistics": {
      "ballots_used": 500,
      "good_ballots": 480,
      "bad_ballots": 15,
      "no_vote_ballots": 5
    },
    "vote_results": [
      {
        "number": 1,
        "name": "สมชาย ใจดี",
        "vote_count": 250,
        "vote_count_text": "สองร้อยห้าสิบ"
      }
    ]
  },
  "pages_processed": 2
}
```

### Python Client Example

```python
import httpx

# Prepare files
files = [
    ("files", ("page1.jpg", open("page1.jpg", "rb"), "image/jpeg")),
    ("files", ("page2.jpg", open("page2.jpg", "rb"), "image/jpeg")),
]

# Call API
with httpx.Client(timeout=120.0) as client:
    response = client.post(
        "http://localhost:8000/api/v1/vote-extraction/extract",
        files=files
    )
    result = response.json()
    
    if result["success"]:
        print("Extraction successful!")
        print(f"Province: {result['data']['form_info']['province']}")
        print(f"Total votes: {len(result['data']['vote_results'])}")
    else:
        print(f"Extraction failed: {result['error']}")
```

## Data Format

### JSON Schema

```json
{
  "form_info": {
    "date": "string",
    "province": "string",
    "district": "string",
    "constituency_number": "string",
    "polling_station_number": "string",
    "form_type": "Constituency" | "PartyList"
  },
  "ballot_statistics": {
    "ballots_used": "integer",
    "good_ballots": "integer",
    "bad_ballots": "integer",
    "no_vote_ballots": "integer"
  },
  "vote_results": [
    {
      "number": "integer",
      "name": "string",
      "vote_count": "integer",
      "vote_count_text": "string"
    }
  ]
}
```

### CSV Export Format

```csv
number,name,vote_count,vote_count_text
1,สมชาย ใจดี,250,สองร้อยห้าสิบ
2,สมหญิง รักชาติ,230,สองร้อยสามสิบ
```

## Privacy and Security

### Data Handling

- ✅ Images are processed in memory (not permanently stored)
- ✅ Extracted data can be downloaded for your records
- ✅ No data is shared with third parties
- ✅ HTTPS recommended for production deployments

### Recommendations

1. **Don't upload sensitive personal documents** other than official election forms
2. **Verify extracted data** before using in official contexts
3. **Keep backups** of original documents
4. **Use secure networks** when uploading documents

## Support

### Getting Help

1. **Check the documentation:**
   - [Getting Started Guide](docs/GETTING_STARTED.md)
   - [API Documentation](http://localhost:8000/docs)

2. **Review logs:**
   ```bash
   make docker-logs-streamlit  # Frontend logs
   make docker-logs-fastapi    # Backend logs
   ```

3. **Report issues:**
   - Describe the problem
   - Include example images (if not sensitive)
   - Share error messages
   - Mention browser/OS version

## Advanced Usage

### Batch Processing

For processing many documents, consider using the API directly with a script:

```python
import os
import httpx
import json
from pathlib import Path

# Directory containing election form images
image_dir = Path("election-forms/")
output_dir = Path("extracted-data/")
output_dir.mkdir(exist_ok=True)

# Group images by report (assumes naming: reportX_pageY.jpg)
reports = {}
for img_file in image_dir.glob("*.jpg"):
    report_id = img_file.stem.split("_page")[0]
    if report_id not in reports:
        reports[report_id] = []
    reports[report_id].append(img_file)

# Process each report
with httpx.Client(timeout=120.0) as client:
    for report_id, pages in reports.items():
        print(f"Processing {report_id} ({len(pages)} pages)...")
        
        # Prepare files
        files = [
            ("files", (p.name, open(p, "rb"), "image/jpeg"))
            for p in sorted(pages)
        ]
        
        # Extract
        response = client.post(
            "http://localhost:8000/api/v1/vote-extraction/extract",
            files=files
        )
        
        # Save result
        result = response.json()
        output_file = output_dir / f"{report_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved to {output_file}")
```

---

**Questions or feedback?** Check the main [README.md](README.md) or [PROJECT_PLAN.md](PROJECT_PLAN.md)

