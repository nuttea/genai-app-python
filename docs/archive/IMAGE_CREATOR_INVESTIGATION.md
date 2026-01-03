# Image Creator Agent - 400 INVALID_ARGUMENT Investigation

## 🔍 Root Cause Analysis

### The Problem
After successfully generating an image (740KB PNG → 987KB base64), ADK throws:
```
400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'Request contains an invalid argument.'}}
```

### The Flow
1. ✅ User requests image generation
2. ✅ Model calls `generate_image` tool with function_call
3. ✅ Tool generates image successfully (987KB base64 string)
4. ❌ ADK tries to send tool result back to model → **400 ERROR**
5. ❌ Model fails to process the tool result

### Why It Fails
**ADK sends the entire tool result (including 987KB base64) back to Gemini for final response generation.**

Gemini 3 Pro Image rejects this because:
- Tool results are expected to be text summaries, not large binary data
- 987KB base64 string exceeds reasonable text input limits
- The model doesn't need the full image data to formulate a response

### Key Insight
```python
# Tool returns (in image_tools.py line 205-214):
return {
    "status": "success",
    "text_response": text_response or "Image generated successfully",
    "image_base64": image_base64,  # ❌ 987KB string sent to model
    "mime_type": image_mime_type,
    "prompt_used": enhanced_prompt,
    "aspect_ratio": aspect_ratio,
    "image_type": image_type,
    "safety_blocked": False,
}
```

ADK then formats this entire dict as the tool result and sends it back to Gemini, which rejects it.

## 🔧 Solution Options

### Option 1: Save to File + Return URL (RECOMMENDED)
**Pros:**
- Clean separation of data and metadata
- Model only receives filename/URL (small text)
- Frontend can fetch image via HTTP
- Scalable for large images

**Implementation:**
1. Save image to `/app/uploads/{timestamp}_{uuid}.png`
2. Add StaticFiles mount to serve `/uploads`
3. Return `{"image_url": "/uploads/...", "status": "success"}`
4. Frontend fetches image from URL

### Option 2: Truncate Tool Result
**Pros:**
- Minimal changes to tool code
- Model gets summary only

**Cons:**
- Still need to pass full base64 to frontend somehow
- Hacky solution

**Implementation:**
```python
return {
    "status": "success",
    "text_response": f"Generated {image_type} image ({len(image_base64)} bytes)",
    "image_base64": image_base64[:100] + "...[TRUNCATED]",  # For model
    "_full_image_base64": image_base64,  # For session state
}
```

### Option 3: Use Session State
**Pros:**
- Keep image in session, return just ID

**Cons:**
- More complex state management
- Session size limits

### Option 4: Streaming Binary Data
**Pros:**
- Efficient for large files

**Cons:**
- ADK may not support this well
- Complex to implement

## ✅ Recommended Solution: Option 1

### Implementation Plan

#### 1. Update `main_adk.py` - Add Static File Serving
```python
from fastapi.staticfiles import StaticFiles
import os

# After app creation
uploads_dir = Path(__file__).parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
```

#### 2. Update `image_tools.py` - Save to File
```python
import uuid
from datetime import datetime
from pathlib import Path

def generate_image(...) -> dict[str, any]:
    # ... existing code to generate image_data ...
    
    # Save image to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{timestamp}_{unique_id}.png"
    
    uploads_dir = Path("/app/uploads")
    file_path = uploads_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(image_data)  # image_data is bytes
    
    image_url = f"/uploads/{filename}"
    logger.info(f"✅ Image saved to {file_path}")
    
    # Return URL instead of base64
    return {
        "status": "success",
        "text_response": text_response or "Image generated successfully",
        "image_url": image_url,  # ✅ Small URL string
        "mime_type": image_mime_type,
        "prompt_used": enhanced_prompt,
        "aspect_ratio": aspect_ratio,
        "image_type": image_type,
        "safety_blocked": False,
    }
```

#### 3. Update Frontend - Fetch from URL
```typescript
// In imageCreator.ts
if (data.image_url) {
  const imageResponse = await fetch(`${ADK_BASE_URL}${data.image_url}`);
  const blob = await imageResponse.blob();
  const reader = new FileReader();
  reader.onloadend = () => {
    const base64 = reader.result as string;
    // Use base64 for display
  };
  reader.readAsDataURL(blob);
}
```

## 📊 Benefits of File-Based Approach

1. **Scalability**: Works for images of any size
2. **Performance**: Model doesn't process large binary data
3. **Caching**: Browser can cache images
4. **Standard**: RESTful approach for serving files
5. **Debugging**: Can inspect files on disk
6. **Reusability**: Images persist across sessions

## 🚀 Next Steps

1. Implement static file serving in `main_adk.py`
2. Update `generate_image` tool to save files
3. Update `edit_image` and `analyze_image` similarly
4. Update frontend to fetch from URLs
5. Add cleanup for old files (optional)
6. Test end-to-end

