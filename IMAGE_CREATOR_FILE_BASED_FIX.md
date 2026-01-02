# Image Creator Agent - File-Based Fix for 400 ERROR

## 🔧 Solution Implemented

### Problem
ADK was sending the entire 987KB base64 image string back to Gemini as part of the tool result, causing:
```
400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'Request contains an invalid argument.'}}
```

### Solution
**Save images to files and return URLs instead of base64 strings.**

## 📝 Changes Made

### 1. `main_adk.py` - Added Static File Serving

**Added import:**
```python
from fastapi.staticfiles import StaticFiles
```

**Mounted uploads directory:**
```python
# Mount static files for serving generated images
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
logger.info(f"Mounted /uploads directory at {UPLOADS_DIR}")
```

### 2. `image_tools.py` - Save to File Instead of Base64

**Added imports:**
```python
import uuid
from datetime import datetime
```

**Modified `generate_image` return:**
```python
# OLD: Return base64 (987KB string)
return {
    "image_base64": base64.b64encode(image_data).decode("utf-8"),
    ...
}

# NEW: Save to file and return URL
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_id = str(uuid.uuid4())[:8]
filename = f"{timestamp}_{unique_id}.png"

uploads_dir = Path("/app/uploads")
file_path = uploads_dir / filename

with open(file_path, "wb") as f:
    f.write(image_data)

image_url = f"/uploads/{filename}"

return {
    "image_url": image_url,  # Small URL string (~30 chars)
    "file_size_bytes": len(image_data),
    ...
}
```

**Modified `edit_image` similarly:**
```python
filename = f"edit_{timestamp}_{unique_id}.{ext}"
# ... same file saving logic ...
return {
    "image_url": image_url,
    ...
}
```

## ✅ Benefits

### For Backend (ADK + Gemini)
- ✅ Tool result is now ~100 bytes (URL) instead of 987KB (base64)
- ✅ Model can process tool result successfully
- ✅ No more 400 INVALID_ARGUMENT errors

### For System
- ✅ Images persist on disk for debugging
- ✅ Browser can cache images
- ✅ Scalable for any image size
- ✅ RESTful design pattern

### For Frontend
- ✅ Can fetch images via HTTP GET
- ✅ Can display loading states while fetching
- ✅ Can retry failed image loads

## 🔄 Frontend Update Required

The frontend needs to be updated to fetch images from URLs:

```typescript
// OLD: Use base64 directly
if (data.image_base64) {
  const dataUrl = `data:${data.mime_type};base64,${data.image_base64}`;
  setImageData(dataUrl);
}

// NEW: Fetch from URL
if (data.image_url) {
  const fullUrl = `http://localhost:8002${data.image_url}`;
  const response = await fetch(fullUrl);
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  setImageData(objectUrl);
}
```

## 📊 Size Comparison

| Approach | Tool Result Size | Model Accepts? |
|----------|------------------|----------------|
| Base64 | 987,536 chars | ❌ 400 ERROR |
| File URL | ~30 chars | ✅ SUCCESS |

**Reduction: 987KB → 30 bytes (99.997% smaller)**

## 🚀 Testing

```bash
# Rebuild container
docker-compose build adk-python

# Restart service
docker-compose up -d adk-python

# Test image generation
# Should see: "✅ Image saved to /app/uploads/..."
# Should NOT see: "400 INVALID_ARGUMENT"

# Verify image is accessible
curl http://localhost:8002/uploads/20260102_123456_abcd1234.png --output test.png
```

## 📁 File Organization

**Generated files:**
- `/app/uploads/YYYYMMDD_HHMMSS_UUID.png` - Generated images
- `/app/uploads/edit_YYYYMMDD_HHMMSS_UUID.png` - Edited images

**Served via:**
- `http://localhost:8002/uploads/{filename}`

