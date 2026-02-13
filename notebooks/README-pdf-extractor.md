# Thai Election Form PDF Extractor - Jupyter Notebook

Extract structured data from Thai election form PDFs (Form S.S. 5/18) using **Gemini with Structured Output**.

## Features

- 📄 **Direct PDF input** - Converts PDF pages to images automatically
- 🤖 **Gemini Structured Output** - Uses response_schema for guaranteed JSON structure
- 📊 **Pydantic Validation** - Type-safe data models with automatic validation
- ✅ **Business Logic Validation** - Checks ballot statistics and vote counts
- 🎨 **Rich Display** - Pretty printing with pandas DataFrames
- 🔄 **Batch Processing** - Process multiple PDFs efficiently

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-pdf-extractor.txt
```

**Note:** `pdf2image` requires `poppler-utils`:

- **macOS**: `brew install poppler`
- **Ubuntu/Debian**: `sudo apt-get install poppler-utils`
- **Windows**: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)

### 2. Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export VERTEX_AI_LOCATION="us-central1"  # or your preferred region
```

Or create a `.env` file:

```env
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
```

### 3. Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

### 4. Run the Notebook

```bash
jupyter notebook gemini-ss5_18_pdf_extractor.ipynb
```

## Notebook Structure

The notebook is organized into the following sections:

1. **Setup and Dependencies** - Import required libraries
2. **Configuration** - Set project ID, location, model name
3. **Define Pydantic Schema** - Type-safe data models
4. **Convert Pydantic to Gemini Schema** - Schema for structured output
5. **Initialize Gemini Client** - Set up Vertex AI client
6. **PDF Processing Functions** - Convert PDF to images
7. **Extraction Function** - Main extraction logic with Gemini
8. **Validation Functions** - Business logic validation
9. **Display Functions** - Pretty print results
10. **Run Extraction** - Process your PDF
11. **Save Results** - Export to JSON
12. **Validate with Pydantic** - Type validation
13. **Try Different PDF Files** - Quick examples
14. **Batch Processing** - Process multiple PDFs

## Supported Models

The notebook uses experimental Gemini models with structured output:

- `gemini-3-pro-preview` - Latest preview model
- `gemini-2.5-pro` - Current stable model
- `gemini-2.5-flash` - Fast model

## Usage Example

```python
# Process a single PDF
PDF_FILE = "assets/ss5-18/ss5-18-pdf/บางบำหรุ1.pdf"

# Convert PDF to images
image_bytes_list = pdf_to_images(PDF_FILE, dpi=200)

# Extract data with Gemini
result = extract_vote_data(
    image_bytes_list=image_bytes_list,
    model="gemini-exp-1206",
    temperature=0.0,
    max_tokens=8192,
)

# Display results
display_results(result)

# Save to JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## Batch Processing

```python
# Process multiple PDFs
pdf_files = [
    "assets/ss5-18/ss5-18-pdf/บางบำหรุ1.pdf",
    "assets/ss5-18/ss5-18-pdf/บางพลัด1.pdf",
    "assets/ss5-18/ss5-18-pdf/บางอ้อ1.pdf",
]

batch_results = process_pdf_batch(pdf_files)
```

## Schema Structure

The notebook extracts data according to this structure:

```json
[
  {
    "form_info": {
      "form_type": "Constituency | PartyList",
      "date": "14 May 2566",
      "province": "กรุงเทพมหานคร",
      "district": "บางบำหรุ",
      "sub_district": "...",
      "constituency_number": "1",
      "polling_station_number": "1"
    },
    "ballot_statistics": {
      "ballots_allocated": 500,
      "ballots_used": 450,
      "good_ballots": 440,
      "bad_ballots": 8,
      "no_vote_ballots": 2,
      "ballots_remaining": 50
    },
    "vote_results": [
      {
        "number": 1,
        "candidate_name": "นายสมชาย ใจดี",
        "party_name": "พรรคก้าวไกล",
        "vote_count": 120,
        "vote_count_text": "หนึ่งร้อยยี่สิบ"
      }
    ]
  }
]
```

## Validation

The notebook includes two types of validation:

### 1. Business Logic Validation

- Checks that `ballots_used = good_ballots + bad_ballots + no_vote_ballots`
- Ensures vote counts are non-negative
- Validates that vote results exist

### 2. Pydantic Model Validation

- Type checking (str, int, Optional fields)
- Required fields validation
- Automatic data coercion

## Troubleshooting

### PDF Conversion Issues

If you get errors about `poppler` not being installed:

```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils

# Windows
# Download from: https://github.com/oschwartz10612/poppler-windows/releases/
```

### Authentication Errors

Make sure you're authenticated with Google Cloud:

```bash
gcloud auth application-default login
```

### Model Not Found

If `gemini-exp-1206` is not available, try:

- `gemini-2.0-flash-exp`
- `gemini-1.5-pro-002`
- `gemini-1.5-flash-002`

### Memory Issues

For large PDFs or batch processing:

- Reduce DPI: `pdf_to_images(pdf_path, dpi=150)` (default is 200)
- Process fewer PDFs at once
- Use a machine with more RAM

## Comparison with Backend Service

This notebook provides similar functionality to the FastAPI backend service but in an interactive notebook format:

| Feature | Backend Service | Jupyter Notebook |
|---------|----------------|------------------|
| Input | Image files (JPG/PNG) | PDF files |
| Conversion | Not needed | PDF → Images |
| Model | Configurable via API | Configurable in code |
| Validation | Datadog LLMObs | Local validation |
| Output | JSON API response | JSON file + display |
| Deployment | Docker/Cloud Run | Local/Jupyter |
| Use Case | Production API | Research/Testing |

## Next Steps

1. **Experiment with different models** - Compare accuracy and speed
2. **Tune parameters** - Optimize temperature, top_p, top_k
3. **Add custom validation rules** - Extend business logic
4. **Export to different formats** - CSV, Excel, Database
5. **Integrate with backend** - Use as a testing/development tool

## Related Files

- **Backend Service**: `services/fastapi-backend/app/services/vote_extraction_service.py`
- **Frontend**: `frontend/streamlit/pages/1_🗳️_Vote_Extractor.py`
- **Pydantic Models**: `services/fastapi-backend/app/models/vote_extraction.py`

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the notebook comments and docstrings
3. Compare with the backend service implementation
4. Check Google GenAI SDK documentation: https://ai.google.dev/gemini-api/docs

## License

This notebook is part of the genai-app-python project.
