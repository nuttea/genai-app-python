# Dataset Manager - Quick Start

## 🚀 Running the Dataset Manager

### Local Development

```bash
# From project root
streamlit run frontend/streamlit/pages/2_📊_Dataset_Manager.py
```

**Requirements**:
- Images in `assets/ss5-18-images/`
- `.env` file with Datadog API keys (optional for local storage only)

---

### Docker / Production

#### Option 1: Docker Compose (Recommended)

The Dataset Manager is already included in the Streamlit service.

**First, create the datasets directory**:
```bash
mkdir -p datasets/vote-extraction
```

**Then start the service**:
```bash
docker-compose up streamlit-frontend
```

**Important**: Make sure volumes are mounted correctly in `docker-compose.yml`:

```yaml
services:
  streamlit-frontend:
    volumes:
      - ./frontend/streamlit:/app:ro     # Code (read-only)
      - ./assets:/app/assets:ro          # Images (read-only)
      - ./datasets:/app/datasets          # Datasets (read-write) ← REQUIRED
```

#### Option 2: Standalone Docker

```bash
docker run -p 8501:8501 \
  -v $(pwd)/assets:/app/assets:ro \
  -v $(pwd)/datasets:/app/datasets \
  -v $(pwd)/.env:/app/.env:ro \
  your-streamlit-image
```

---

## 📂 Directory Structure

```
project-root/
├── assets/
│   └── ss5-18-images/          # ← Place your images here
│       ├── form1_page1.jpg
│       ├── form1_page2.jpg
│       └── ...
│
├── datasets/
│   └── vote-extraction/        # ← Datasets saved here
│       ├── vote-extraction-dataset_<timestamp>.json
│       └── vote-extraction-dataset_latest.json
│
└── frontend/streamlit/
    └── pages/
        └── 2_📊_Dataset_Manager.py
```

---

## 🔧 Troubleshooting

### Issue: "Permission denied: '/datasets'"

**Cause**: The app can't create the datasets directory.

**Solutions**:

1. **Local Development**:
   ```bash
   # Create the directory manually
   mkdir -p datasets/vote-extraction
   chmod 755 datasets
   ```

2. **Docker**:
   ```bash
   # Ensure the volume is mounted
   docker-compose down
   mkdir -p datasets/vote-extraction
   docker-compose up
   ```

3. **Check `docker-compose.yml`**:
   ```yaml
   volumes:
     - ./datasets:/app/datasets  # ← This line must exist
   ```

---

### Issue: "No images found"

**Cause**: Images directory doesn't exist or is empty.

**Solutions**:

1. **Check directory exists**:
   ```bash
   ls -la assets/ss5-18-images/
   ```

2. **Add images**:
   ```bash
   # Copy your images
   cp /path/to/images/*.jpg assets/ss5-18-images/
   ```

3. **Docker volume**:
   ```yaml
   volumes:
     - ./assets:/app/assets:ro  # ← This line must exist
   ```

---

### Issue: "Cannot push to Datadog"

**Cause**: API keys not configured.

**Solutions**:

1. **Check `.env` file**:
   ```bash
   cat .env | grep DD_
   ```

2. **Required variables**:
   ```bash
   DD_API_KEY=your_api_key_here
   DD_APP_KEY=your_app_key_here
   DD_SITE=datadoghq.com  # Optional
   ```

3. **Restart Streamlit**:
   ```bash
   # Ctrl+C to stop
   streamlit run frontend/streamlit/pages/2_📊_Dataset_Manager.py
   ```

---

## ✅ Verification Checklist

Before using the Dataset Manager:

- [ ] Images exist in `assets/ss5-18-images/`
- [ ] Images are `.jpg` or `.png` format
- [ ] `datasets/` directory exists and is writable
- [ ] `.env` file has `DD_API_KEY` and `DD_APP_KEY` (if pushing to Datadog)
- [ ] Streamlit can access both directories

### Quick Check Command

```bash
# Verify everything is set up
tree -L 2 assets/ datasets/
cat .env | grep DD_ | wc -l  # Should output 2 or 3
```

---

## 🎯 Usage Flow

1. **Launch App**:
   ```bash
   streamlit run frontend/streamlit/pages/2_📊_Dataset_Manager.py
   ```

2. **Navigate to App**:
   - Open browser: `http://localhost:8501`
   - Or in Docker: `http://localhost:8501`

3. **Create Dataset**:
   - Click "📝 Create/Edit Dataset"
   - Select a form set
   - Fill in ground truth
   - Click "💾 Save Ground Truth"

4. **Push to Datadog** (Optional):
   - Click "📤 Push to Datadog"
   - Click "🚀 Push to Datadog" button
   - View in Datadog UI

---

## 📚 Related Documentation

- [Complete Workflow Guide](../../DATASET_WORKFLOW_COMPLETE.md)
- [Quick Start Guide](../../notebooks/datasets/QUICKSTART.md)
- [Experiments Guide](../../guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md)

---

## 💡 Tips

### Tip 1: Automatic Saving

The app auto-saves to JSON every time you click "Save Ground Truth". No manual export needed!

### Tip 2: Version Control

All datasets are timestamped:
```
vote-extraction-dataset_20260104_123456.json
vote-extraction-dataset_20260104_134500.json
vote-extraction-dataset_latest.json  ← Symlink to newest
```

### Tip 3: Team Collaboration

1. Save dataset to JSON
2. Commit to Git: `git add datasets/ && git commit -m "Add dataset v1"`
3. Team members pull and continue adding ground truth
4. Merge datasets by loading and adding more forms

### Tip 4: Docker Permissions

If you encounter permission issues in Docker:

```bash
# Set ownership to your user
sudo chown -R $USER:$USER datasets/

# Or run with correct user
docker-compose run --user $(id -u):$(id -g) streamlit-frontend
```

---

**Last Updated**: January 4, 2026  
**Need Help?** Check the troubleshooting section above or open an issue

