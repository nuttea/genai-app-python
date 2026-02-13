# Test File Information

## Selected PDF File for Testing

From BigQuery table: `sourceinth.vote69_ect.raw_files`

### File Details

```
Province: กระบี่
Path: เขตเลือกตั้งที่ 1/ล่วงหน้านอกเขตและนอกราชอาณาจักรฯ/นอกเขต.pdf
File ID: 1SWv__IY3oqrc4u64OyEV4D9M9K5Awqr6
Size: 13.13 MB
Modified: 2026-02-10T06:58:38.000Z
```

### Google Drive URI

```
https://drive.google.com/uc?export=download&id=1SWv__IY3oqrc4u64OyEV4D9M9K5Awqr6
```

## Usage in Notebook

### Method 1: Direct URI (Recommended)

```python
# Use Google Drive URI directly - no download needed!
drive_uri = "https://drive.google.com/uc?export=download&id=1SWv__IY3oqrc4u64OyEV4D9M9K5Awqr6"

# Create file part from URI
file_part = types.Part.from_uri(
    file_uri=drive_uri,
    mime_type="application/pdf"
)

# Extract data
result = extract_from_drive_url(drive_uri, model="gemini-exp-1206")
```

### Method 2: Query from BigQuery

```python
# Query BigQuery for files
query = """
SELECT file_id, path, province_name, size
FROM `sourceinth.vote69_ect.raw_files`
WHERE mime_type = 'application/pdf'
  AND size <= 20000000  -- Max 20MB
LIMIT 10
"""

files = bq_client.query(query).result()

# Use first file
test_file = list(files)[0]
drive_uri = f"https://drive.google.com/uc?export=download&id={test_file.file_id}"
```

## BigQuery Query Examples

### Get Small PDF Files (< 20 MB)

```sql
SELECT
    file_id,
    path,
    province_name,
    size / 1024 / 1024 as size_mb
FROM `sourceinth.vote69_ect.raw_files`
WHERE mime_type = 'application/pdf'
  AND size < 20000000
ORDER BY size ASC
LIMIT 10;
```

### Get Files by Province

```sql
SELECT
    file_id,
    path,
    size / 1024 / 1024 as size_mb
FROM `sourceinth.vote69_ect.raw_files`
WHERE mime_type = 'application/pdf'
  AND province_name = 'กระบี่'
ORDER BY size ASC
LIMIT 5;
```

### Count Files by Province

```sql
SELECT
    province_name,
    COUNT(*) as file_count,
    SUM(size) / 1024 / 1024 / 1024 as total_size_gb
FROM `sourceinth.vote69_ect.raw_files`
WHERE mime_type = 'application/pdf'
GROUP BY province_name
ORDER BY file_count DESC;
```

## Available Notebooks

1. **gemini-ss5_18_pdf_extractor.ipynb** (Original)
   - Local PDF file input
   - Converts PDF to images
   - Good for: Testing with local files

2. **gemini-ss5_18_bigquery_drive.ipynb** (NEW - Recommended!)
   - BigQuery integration
   - Google Drive URL direct access
   - No download/conversion needed
   - Good for: Production workflows

## Quick Start

### Using the BigQuery + Drive Notebook

```bash
# 1. Navigate to notebooks directory
cd notebooks

# 2. Open the notebook
jupyter notebook gemini-ss5_18_bigquery_drive.ipynb

# 3. Run cells in order:
#    - Cell 1-5: Setup and configuration
#    - Cell 6: Query BigQuery for files
#    - Cell 7: Select test file
#    - Cell 8-9: Extract data
#    - Cell 10: Display results
```

## Advantages of Google Drive URL Method

✅ **No Local Downloads** - Files stay in Google Drive
✅ **No PDF Conversion** - Gemini handles PDF directly
✅ **Faster Processing** - No download/upload overhead
✅ **Scalable** - Easy to process thousands of files
✅ **Cost Effective** - No egress charges
✅ **BigQuery Integration** - Query metadata easily

## Reference

- **Gemini File Input Methods**: https://ai.google.dev/gemini-api/docs/file-input-methods
- **BigQuery Table**: `sourceinth.vote69_ect.raw_files`
- **Total PDF Files**: 105,450 files
- **Provinces Covered**: Multiple provinces across Thailand

## Troubleshooting

### If file access fails:

1. **Check file permissions** - Make sure the Google Drive file is accessible
2. **Verify file ID** - Ensure the file_id from BigQuery is correct
3. **Check file size** - Very large files (>100 MB) may timeout
4. **Try smaller files first** - Start with files < 20 MB

### If BigQuery query fails:

```bash
# Re-authenticate
gcloud auth application-default login

# Set project
gcloud config set project sourceinth
```

## Next Steps

1. ✅ Test with single file (13.13 MB)
2. ✅ Validate extraction results
3. 🔄 Test with multiple files (batch processing)
4. 📊 Analyze extraction accuracy
5. 🚀 Scale to full dataset
