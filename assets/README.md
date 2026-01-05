# Assets Directory

This directory contains sample images and test data used for developing and testing the GenAI Vote Extraction application.

---

## 📄 Vote Documents (Thai Election Forms)

### Source

**Official Source**: Bangkok Metropolitan Administration (BMA) - Bang Phlat District Office

**URL**: https://webportal.bangkok.go.th/bangphlat/page/sub/26952/%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%87%E0%B8%B2%E0%B8%99%E0%B8%9C%E0%B8%A5%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%99%E0%B8%B1%E0%B8%9A%E0%B8%84%E0%B8%B0%E0%B9%81%E0%B8%99%E0%B8%99%E0%B8%AA%E0%B8%A1%E0%B8%B2%E0%B8%8A%E0%B8%B4%E0%B8%81%E0%B8%AA%E0%B8%A0%E0%B8%B2%E0%B8%9C%E0%B8%B9%E0%B9%89%E0%B9%81%E0%B8%97%E0%B8%99%E0%B8%A3%E0%B8%B2%E0%B8%A9%E0%B8%8E%E0%B8%A3

**Page Title**: รายงานผลการนับคะแนนสมาชิกสภาผู้แทนราษฎร  
**English Translation**: Report of Vote Counting Results for Members of the House of Representatives

**Election**: Thai General Election 2023 (May 14, 2023)

### Document Type

These are official **Form S.S. 5/18** (แบบ ส.ส. 5/18) documents used by the Election Commission of Thailand (ECT) for reporting vote counting results at polling stations.

Each document set contains:
- **Page 1**: Header information (district, date, polling station)
- **Pages 2-5**: Constituency vote results (candidates with names)
- **Page 6**: Party List vote results (party names only)

### Directory Structure

```
assets/
├── README.md (this file)
└── ss5-18-images/
    ├── บางบำหรุ1_page1.jpg
    ├── บางบำหรุ1_page2.jpg
    ├── บางบำหรุ1_page3.jpg
    ├── บางบำหรุ1_page4.jpg
    ├── บางบำหรุ1_page5.jpg
    ├── บางบำหรุ1_page6.jpg
    ├── บางบำหรุ2_page1.jpg
    ├── ... (more polling stations)
    ├── บางพลัด1_page1.jpg
    ├── ... (more polling stations)
    └── บางยี่ขัน1_page1.jpg
        ... (more polling stations)
```

### Naming Convention

**Format**: `{SubDistrict}{PollingStationNumber}_page{PageNumber}.jpg`

**Examples**:
- `บางบำหรุ1_page1.jpg` - Bang Bamru, Station 1, Page 1
- `บางพลัด10_page3.jpg` - Bang Phlat, Station 10, Page 3
- `บางยี่ขัน15_page6.jpg` - Bang Yi Khan, Station 15, Page 6

### Sub-Districts Included

The images cover three sub-districts (แขวง) in Bang Phlat district:

1. **บางบำหรุ (Bang Bamru)** - Stations 1-24
2. **บางพลัด (Bang Phlat)** - Stations 1-32
3. **บางยี่ขัน (Bang Yi Khan)** - Stations 1-20+

---

## 🎯 Usage in Testing

### Integration Tests

These images are used to test the Vote Extraction API with real-world data:

```bash
# Test with a single polling station (6 pages)
cd /path/to/genai-app-python
source .env

curl -X POST http://localhost:8000/api/v1/vote-extraction/extract \
  -H "X-API-Key: $API_KEY" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page1.jpg" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page2.jpg" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page3.jpg" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page4.jpg" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page5.jpg" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page6.jpg"
```

### Jupyter Notebooks

The images are also used in Jupyter notebooks for exploring and visualizing extraction results:

- `notebooks/google-vertex-genai.ipynb` - Gemini API testing and evaluation

### Expected Output

Each set of 6 pages should extract **2 forms**:

1. **Constituency Form** (Pages 1-5):
   - Form type: `"Constituency"`
   - Contains: Candidate names, party affiliations, vote counts
   - Ballot statistics: Total ballots, good/bad/no-vote ballots

2. **Party List Form** (Page 6):
   - Form type: `"PartyList"`
   - Contains: Party names (no candidates), vote counts
   - Ballot statistics: Total ballots, good/bad/no-vote ballots

---

## 📊 Data Characteristics

### Image Specifications

- **Format**: JPEG
- **Resolution**: Variable (typically 1000-2000 pixels width)
- **Color**: Grayscale or color scans
- **Quality**: Variable (some images may have scanning artifacts)

### Text Content

- **Language**: Thai
- **Numbers**: Arabic numerals (0-9)
- **Text Format**: Both handwritten and printed

### Challenges for OCR/LLM

1. **Handwriting Variations**: Different handwriting styles across polling stations
2. **Scanning Quality**: Some images have shadows, skew, or low contrast
3. **Complex Layout**: Multi-column tables with nested sections
4. **Thai Language**: Requires Unicode support and proper rendering
5. **Number Formats**: Vote counts in both numeric and text format (e.g., "23" and "ยี่สิบสาม")

---

## 🔒 Data Privacy & Usage

### Public Information

These documents are **publicly available** official election results published by government authorities for transparency and public verification purposes.

### Permitted Use

- ✅ Research and development
- ✅ Testing and evaluation of AI/ML models
- ✅ Educational purposes
- ✅ Non-commercial applications

### Attribution

When using these images, please attribute:
```
Source: Bangkok Metropolitan Administration - Bang Phlat District Office
Election: Thai General Election 2023
Form Type: Election Commission of Thailand Form S.S. 5/18
```

---

## 🚀 Quick Start for Developers

### 1. Test Single Polling Station

```bash
# Use the first station from Bang Bamru sub-district
./scripts/test_extraction.sh assets/ss5-18-images/บางบำหรุ1_page*.jpg
```

### 2. Batch Process Multiple Stations

```bash
# Process all stations in Bang Bamru
for station in {1..24}; do
  curl -X POST http://localhost:8000/api/v1/vote-extraction/extract \
    -H "X-API-Key: $API_KEY" \
    -F "files=@assets/ss5-18-images/บางบำหรุ${station}_page1.jpg" \
    -F "files=@assets/ss5-18-images/บางบำหรุ${station}_page2.jpg" \
    -F "files=@assets/ss5-18-images/บางบำหรุ${station}_page3.jpg" \
    -F "files=@assets/ss5-18-images/บางบำหรุ${station}_page4.jpg" \
    -F "files=@assets/ss5-18-images/บางบำหรุ${station}_page5.jpg" \
    -F "files=@assets/ss5-18-images/บางบำหรุ${station}_page6.jpg"
done
```

### 3. View in Streamlit

```bash
# Start the frontend
docker-compose up streamlit-frontend

# Open http://localhost:8501
# Navigate to "Vote Extractor" page
# Upload images from assets/ss5-18-images/
```

---

## 📚 Related Documentation

- **Vote Extraction Guide**: [`docs/features/VOTE_EXTRACTION.md`](../docs/features/VOTE_EXTRACTION.md)
- **Troubleshooting**: [`docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md`](../docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md)
- **LLM Configuration**: [`docs/features/LLM_CONFIGURATION.md`](../docs/features/LLM_CONFIGURATION.md)
- **API Documentation**: [`docs/api/VOTE_EXTRACTION_API.md`](../docs/api/VOTE_EXTRACTION_API.md)

---

## 🔗 External Resources

### Official Sources

- **Election Commission of Thailand**: https://www.ect.go.th/
- **Bangkok Metropolitan Administration**: https://www.bangkok.go.th/
- **Bang Phlat District Office**: https://webportal.bangkok.go.th/bangphlat/

### Election Information

- **2023 General Election Results**: https://www.ect.go.th/ewt_news.php?nid=9876
- **Form S.S. 5/18 Specification**: Available from ECT

---

## ⚠️ Notes

1. **File Size**: The `ss5-18-images` directory contains ~500 images (total ~2GB). Consider using Git LFS for version control.

2. **API Limits**: When testing with multiple images:
   - Maximum file size per image: 10MB
   - Maximum total upload: 30MB
   - Recommended: 6 pages per request (one polling station)

3. **Token Limits**: 
   - Default max tokens: 16,384
   - For 6-page documents: Usually sufficient
   - If extraction fails: Increase `max_tokens` to 32,768 or 65,536

4. **Processing Time**:
   - Average per station (6 pages): 50-70 seconds
   - Batch processing: Use async/parallel requests

---

**Last Updated**: January 3, 2026  
**Maintained By**: GenAI App Team

