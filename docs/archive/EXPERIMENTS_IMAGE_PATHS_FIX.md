# 🖼️ Experiments Image Paths - Container Fix

**Fixed: Image paths in datasets now work in both host and container environments**

---

## 🔍 Problem Identified

### Issue 1: Assets Not Mounted in FastAPI Backend

The FastAPI backend container **did not have the assets directory mounted**, causing experiments to fail when trying to read images.

**❌ Before** (`docker-compose.yml`):
```yaml
fastapi-backend:
  volumes:
    - ${HOME}/.config/gcloud:/root/.config/gcloud:ro
    - ./services/fastapi-backend/app:/app/app:ro
    # ❌ No assets mount!
```

### Issue 2: Absolute Host Paths in Dataset

The dataset contained absolute host paths that don't work in containers:

```json
{
  "input_data": {
    "image_paths": [
      "/Users/nuttee.jirattivongvibul/Projects/genai-app-python/assets/ss5-18-images/บางบำหรุ9_page1.jpg",
      "/Users/nuttee.jirattivongvibul/Projects/genai-app-python/assets/ss5-18-images/บางบำหรุ9_page2.jpg"
    ]
  }
}
```

**Problems:**
- ❌ Absolute path specific to host machine
- ❌ Won't work in Docker container (different filesystem)
- ❌ Even with mount, path inside container is different (`/app/assets/...`)

---

## ✅ Solutions Implemented

### Fix 1: Mount Assets in FastAPI Backend

**✅ After** (`docker-compose.yml`):
```yaml
fastapi-backend:
  volumes:
    - ${HOME}/.config/gcloud:/root/.config/gcloud:ro
    - ./services/fastapi-backend/app:/app/app:ro
    # ✅ NEW: Mount assets for experiments
    - ./assets:/app/assets:ro
    # ✅ NEW: Mount datasets for experiments
    - ./datasets:/app/datasets:ro
```

**Benefits:**
- ✅ FastAPI backend can now read images
- ✅ Read-only mount (safe)
- ✅ Consistent with streamlit-frontend setup

### Fix 2: Path Normalization Function

Added `_normalize_image_path()` in `experiments_service.py` to automatically translate paths:

**✅ Implementation**:
```python
def _normalize_image_path(path: str) -> str:
    """
    Normalize image path to work in both host and container environments.
    
    Converts absolute host paths to container paths if needed.
    
    Examples:
        Host: /Users/nuttee/Projects/genai-app-python/assets/... 
        → Container: /app/assets/...
        
        Already relative: assets/ss5-18-images/file.jpg 
        → Stays: assets/ss5-18-images/file.jpg (or /app/assets/... if in container)
    """
    import re
    
    # Pattern: /path/to/genai-app-python/(assets|datasets)/...
    match = re.search(r'genai-app-python[/\\](assets|datasets)[/\\](.+)$', path)
    if match:
        category = match.group(1)  # 'assets' or 'datasets'
        relative_path = match.group(2)  # rest of the path
        container_path = f"/app/{category}/{relative_path}"
        
        # Check if container path exists (we're in container)
        if os.path.exists(container_path):
            return container_path
        
        # Otherwise, try original path (we're on host)
        if os.path.exists(path):
            return path
        
        # Last resort: try relative path
        relative = f"{category}/{relative_path}"
        if os.path.exists(relative):
            return relative
    
    # Not matching pattern - use as is if it exists
    if os.path.exists(path):
        return path
    
    # Try as relative path from /app (container)
    if path.startswith('assets/') or path.startswith('datasets/'):
        container_path = f"/app/{path}"
        if os.path.exists(container_path):
            return container_path
    
    # Return original path (will fail later with clear error)
    return path
```

**Features:**
- ✅ Detects `genai-app-python/assets/` or `genai-app-python/datasets/` pattern
- ✅ Converts to `/app/assets/...` or `/app/datasets/...` in container
- ✅ Falls back to original path on host
- ✅ Works with both absolute and relative paths
- ✅ Supports Windows and Unix path separators

### Fix 3: Enhanced Error Handling

```python
# Read images from paths (normalize for container/host compatibility)
files = []
for path in image_paths:
    # Normalize path to work in both container and host
    normalized_path = _normalize_image_path(path)
    
    if os.path.exists(normalized_path):
        with open(normalized_path, "rb") as f:
            files.append(("images", (os.path.basename(path), f.read(), "image/jpeg")))
    else:
        logger.warning(f"Image not found: {path} (normalized: {normalized_path})")

if not files:
    raise FileNotFoundError(f"No images found for form {form_set_name}. Paths: {image_paths}")
```

**Benefits:**
- ✅ Clear warning for missing images
- ✅ Shows both original and normalized paths for debugging
- ✅ Fails fast with descriptive error if no images found

---

## 📊 Path Translation Examples

### Example 1: Host Absolute Path → Container Path

**Input (in dataset)**:
```
/Users/nuttee.jirattivongvibul/Projects/genai-app-python/assets/ss5-18-images/บางบำหรุ9_page1.jpg
```

**On Host** (development):
```
→ Path exists as-is
→ Returns: /Users/nuttee.jirattivongvibul/Projects/genai-app-python/assets/ss5-18-images/บางบำหรุ9_page1.jpg
```

**In Container** (Docker):
```
→ Detects pattern: genai-app-python/assets/...
→ Extracts: ss5-18-images/บางบำหรุ9_page1.jpg
→ Returns: /app/assets/ss5-18-images/บางบำหรุ9_page1.jpg
```

### Example 2: Relative Path

**Input (in dataset)**:
```
assets/ss5-18-images/บางบำหรุ9_page1.jpg
```

**On Host**:
```
→ Path exists as-is (from project root)
→ Returns: assets/ss5-18-images/บางบำหรุ9_page1.jpg
```

**In Container**:
```
→ Detects 'assets/' prefix
→ Tries: /app/assets/ss5-18-images/บางบำหรุ9_page1.jpg
→ Exists! Returns: /app/assets/ss5-18-images/บางบำหรุ9_page1.jpg
```

---

## 🧪 Testing

### Test on Host (Development)

```bash
# Start services
docker-compose up -d

# Run experiment via API
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [{"model": "gemini-2.5-flash", "temperature": 0.0}],
    "sample_size": 2
  }'
```

**Expected**: ✅ Images found and processed successfully

### Test in Container

```bash
# Exec into container
docker exec -it genai-fastapi-backend bash

# Check mounts
ls -la /app/assets/
ls -la /app/datasets/

# Test path normalization (Python)
python -c "
import os
from app.services.experiments_service import _normalize_image_path

path = '/Users/nuttee/Projects/genai-app-python/assets/ss5-18-images/test.jpg'
normalized = _normalize_image_path(path)
print(f'Original: {path}')
print(f'Normalized: {normalized}')
print(f'Exists: {os.path.exists(normalized)}')
"
```

**Expected**: 
```
Original: /Users/nuttee/Projects/genai-app-python/assets/ss5-18-images/test.jpg
Normalized: /app/assets/ss5-18-images/test.jpg
Exists: True
```

---

## 🔄 Applying the Fix

### Step 1: Update Docker Compose

```bash
# Restart backend with new volume mounts
docker-compose stop fastapi-backend
docker-compose start fastapi-backend

# Verify mounts
docker exec genai-fastapi-backend ls -la /app/assets/
docker exec genai-fastapi-backend ls -la /app/datasets/
```

### Step 2: Verify Experiments Work

**Via Streamlit UI**:
1. Go to http://localhost:8501
2. Navigate to 🧪 Run Experiments
3. Select dataset: `vote-extraction-bangbamru-1-10`
4. Configure experiment
5. Click "Run Experiments"
6. Should work! ✅

**Via API**:
```bash
curl -X POST http://localhost:8000/api/v1/experiments/run \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "vote-extraction-bangbamru-1-10",
    "model_configs": [{"model": "gemini-2.5-flash", "temperature": 0.0}],
    "sample_size": 2
  }'
```

---

## 📋 Best Practices

### For Future Datasets

**✅ Recommended**: Use relative paths in datasets
```json
{
  "input_data": {
    "image_paths": [
      "assets/ss5-18-images/บางบำหรุ9_page1.jpg",
      "assets/ss5-18-images/บางบำหรุ9_page2.jpg"
    ]
  }
}
```

**Why?**
- ✅ Works on any machine
- ✅ Works in containers
- ✅ No user-specific paths
- ✅ Portable and shareable

**⚠️ Acceptable**: Absolute paths (with normalization)
```json
{
  "input_data": {
    "image_paths": [
      "/Users/nuttee/Projects/genai-app-python/assets/ss5-18-images/บางบำหรุ9_page1.jpg"
    ]
  }
}
```

**Why?**
- ✅ Still works (thanks to path normalization)
- ⚠️ But less portable

**❌ Avoid**: Non-standard absolute paths
```json
{
  "input_data": {
    "image_paths": [
      "/var/data/my-images/file.jpg"  // Won't work!
    ]
  }
}
```

---

## 🔧 Updating Existing Datasets

If you have datasets with absolute paths, you can:

**Option 1: Keep as-is** (path normalization handles it automatically)

**Option 2: Convert to relative paths** (recommended for portability)

```python
import json
import re

# Load dataset
with open('datasets/vote-extraction/my-dataset.json', 'r') as f:
    dataset = json.load(f)

# Convert paths
for record in dataset['records']:
    new_paths = []
    for path in record['input']['image_paths']:
        # Extract relative part
        match = re.search(r'genai-app-python[/\\](assets|datasets)[/\\](.+)$', path)
        if match:
            relative = f"{match.group(1)}/{match.group(2)}"
            new_paths.append(relative)
        else:
            new_paths.append(path)
    
    record['input']['image_paths'] = new_paths

# Save updated dataset
with open('datasets/vote-extraction/my-dataset.json', 'w') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)
```

---

## 🎯 Summary

### What Changed

| Component | Before | After |
|-----------|--------|-------|
| **docker-compose.yml** | No assets mount | ✅ Assets + datasets mounted |
| **experiments_service.py** | Read paths as-is | ✅ Path normalization |
| **Error handling** | Generic errors | ✅ Detailed path errors |

### Impact

- ✅ Experiments now work in Docker containers
- ✅ Datasets with absolute paths work automatically
- ✅ Compatible with both host and container execution
- ✅ Clear error messages for debugging

### Files Modified

1. `docker-compose.yml` - Added volume mounts
2. `services/fastapi-backend/app/services/experiments_service.py` - Added path normalization
3. `EXPERIMENTS_IMAGE_PATHS_FIX.md` - This documentation

---

## 📚 Related Documentation

- **Run Experiments**: `RUN_EXPERIMENTS_IMPLEMENTATION.md`
- **Complete Fix**: `EXPERIMENTS_COMPLETE_FIX.md`
- **Dataset Workflow**: `DATASET_WORKFLOW_COMPLETE.md`

---

**Image paths are now fully container-compatible!** 🐳✨

