# Inline Data Handling for Gemini Image Generation

## Overview

Proper `inline_data` handling with correct `mimeType` is **critical** for Gemini 3 Pro Image API to work correctly. This document explains how images are handled in both input (editing/analysis) and output (generation) scenarios.

**Reference**: [Google Cloud Vertex AI Image Generation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)

---

## 🔑 Key Concepts

### 1. **Input: Images TO the API**
When sending images to Gemini (for editing or analysis):
- ✅ **MUST** use `types.Part.from_bytes(data=bytes, mime_type=str)`
- ✅ **MUST** specify correct `mime_type` matching actual image format
- ❌ **DON'T** hardcode MIME type (detect from image bytes)

### 2. **Output: Images FROM the API**
When receiving images from Gemini (generated or edited):
- Images are returned in `inline_data` structure
- Format: `part.inline_data.data` (bytes) + `part.inline_data.mime_type` (string)
- ✅ **MUST** preserve the `mime_type` from the response
- ✅ **MUST** encode `data` as base64 for JSON transport

---

## 📥 Input Handling (Images TO API)

### Problem
User provides a base64-encoded image, but we don't know the format (PNG? JPEG? WebP?).

### Solution: MIME Type Detection

```python
def _detect_mime_type_from_bytes(image_bytes: bytes) -> str:
    """
    Detect MIME type from image magic bytes.
    
    Critical for proper inline_data handling.
    """
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    
    # JPEG: FF D8 FF
    elif image_bytes[:3] == b'\xff\xd8\xff':
        return "image/jpeg"
    
    # GIF: GIF87a or GIF89a
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"
    
    # WebP: RIFF....WEBP
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return "image/webp"
    
    else:
        return "image/png"  # Default
```

### Example: Edit Image

```python
# 1. Decode base64
image_bytes = base64.b64decode(original_image_base64)

# 2. Detect MIME type (CRITICAL!)
detected_mime_type = _detect_mime_type_from_bytes(image_bytes)

# 3. Create Part with correct MIME type
content_parts = [
    types.Part.from_bytes(
        data=image_bytes,
        mime_type=detected_mime_type,  # ✅ Use detected type
    ),
    types.Part.from_text(text="Make it more colorful"),
]
```

**Why This Matters**:
- ❌ Wrong MIME type → API error or incorrect processing
- ✅ Correct MIME type → API understands image format correctly

---

## 📤 Output Handling (Images FROM API)

### Response Structure

```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"text": "I've created an image..."},
        {
          "inline_data": {
            "mime_type": "image/png",
            "data": "iVBORw0KGgoAAAANS..."  // Raw bytes or base64
          }
        }
      ]
    }
  }]
}
```

### Extraction Process

```python
# Iterate through streaming response
for chunk in client.models.generate_content_stream(...):
    if hasattr(chunk, "candidates") and chunk.candidates:
        for candidate in chunk.candidates:
            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        # Extract both data and mime_type
                        image_data = part.inline_data.data  # bytes
                        image_mime_type = part.inline_data.mime_type  # str (e.g., "image/png")
```

### Convert for Frontend

```python
# Convert bytes to base64 string for JSON transport
if isinstance(image_data, bytes):
    image_base64 = base64.b64encode(image_data).decode("utf-8")

# Return with MIME type
return {
    "image_base64": image_base64,  # Base64 string
    "mime_type": image_mime_type,  # e.g., "image/png"
}
```

---

## 🎨 Frontend Integration

### Display Image

```typescript
// Method 1: Data URL
const imageUrl = `data:${response.mime_type};base64,${response.image_base64}`;

<img src={imageUrl} alt="Generated image" />
```

```typescript
// Method 2: Blob (for downloads)
const binaryString = atob(response.image_base64);
const bytes = new Uint8Array(binaryString.length);
for (let i = 0; i < binaryString.length; i++) {
  bytes[i] = binaryString.charCodeAt(i);
}
const blob = new Blob([bytes], { type: response.mime_type });
const url = URL.createObjectURL(blob);

<img src={url} alt="Generated image" />
```

### Download Image

```typescript
function downloadImage(base64: string, mimeType: string, filename: string) {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: mimeType });
  
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
}

// Usage
downloadImage(
  response.image_base64,
  response.mime_type,
  'generated-image.png'
);
```

---

## 🔍 MIME Type Reference

| Format | MIME Type | Magic Bytes | File Extension |
|--------|-----------|-------------|----------------|
| PNG | `image/png` | `89 50 4E 47 0D 0A 1A 0A` | `.png` |
| JPEG | `image/jpeg` | `FF D8 FF` | `.jpg`, `.jpeg` |
| GIF | `image/gif` | `GIF87a` or `GIF89a` | `.gif` |
| WebP | `image/webp` | `RIFF....WEBP` | `.webp` |

---

## ✅ Best Practices

### Input (Sending Images)
1. ✅ **Always detect MIME type** from image bytes
2. ✅ **Never hardcode** MIME type as "image/png"
3. ✅ **Validate** image data before sending
4. ✅ **Log** detected MIME type for debugging

### Output (Receiving Images)
1. ✅ **Always extract** `mime_type` from `inline_data`
2. ✅ **Preserve** the exact MIME type in response
3. ✅ **Convert** bytes to base64 for JSON transport
4. ✅ **Include** MIME type in API response

### Frontend
1. ✅ **Use** `mime_type` from response (not hardcoded)
2. ✅ **Validate** base64 data before display
3. ✅ **Handle errors** gracefully (invalid data, wrong type)
4. ✅ **Support** all common formats (PNG, JPEG, WebP, GIF)

---

## 🚨 Common Issues

### Issue 1: Wrong MIME Type on Input
**Problem**: Hardcoded `mime_type="image/png"` but image is JPEG

**Symptom**: API error or incorrect processing

**Solution**: Detect MIME type from bytes
```python
detected_mime_type = _detect_mime_type_from_bytes(image_bytes)
```

### Issue 2: Lost MIME Type on Output
**Problem**: Not extracting `mime_type` from `inline_data`

**Symptom**: Frontend assumes PNG, fails for JPEG

**Solution**: Always extract and return both data and MIME type
```python
image_data = part.inline_data.data
image_mime_type = part.inline_data.mime_type
```

### Issue 3: Base64 Encoding Issues
**Problem**: Double encoding or wrong encoding

**Symptom**: Corrupt images in frontend

**Solution**: Check if data is already base64 or bytes
```python
if isinstance(image_data, bytes):
    image_base64 = base64.b64encode(image_data).decode("utf-8")
else:
    image_base64 = image_data  # Already base64
```

---

## 🧪 Testing

### Test Case 1: PNG Input
```python
# Create PNG test data
png_data = b'\x89PNG\r\n\x1a\n...'
assert _detect_mime_type_from_bytes(png_data) == "image/png"
```

### Test Case 2: JPEG Input
```python
# Create JPEG test data
jpeg_data = b'\xff\xd8\xff...'
assert _detect_mime_type_from_bytes(jpeg_data) == "image/jpeg"
```

### Test Case 3: Output Preservation
```python
# Generate image
result = generate_image(prompt="Test")

# Verify MIME type is included
assert "mime_type" in result
assert result["mime_type"] in ["image/png", "image/jpeg", "image/webp"]

# Verify base64 is valid
base64.b64decode(result["image_base64"])  # Should not raise
```

---

## 📖 References

- [Google Cloud Vertex AI Image Generation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)
- [Google GenAI Types](https://github.com/googleapis/python-genai/blob/main/google/genai/types.py)
- [File Signatures (Magic Bytes)](https://en.wikipedia.org/wiki/List_of_file_signatures)
- [Base64 Encoding](https://developer.mozilla.org/en-US/docs/Web/API/btoa)

---

## 🔄 Changes Made

### Before (❌ Incorrect)
```python
# Hardcoded MIME type
content_parts = [
    types.Part.from_bytes(
        data=image_bytes,
        mime_type=config.output_mime_type,  # ❌ Always "image/png"
    ),
]
```

### After (✅ Correct)
```python
# Detected MIME type
detected_mime_type = _detect_mime_type_from_bytes(image_bytes)
content_parts = [
    types.Part.from_bytes(
        data=image_bytes,
        mime_type=detected_mime_type,  # ✅ Actual image format
    ),
]
```

---

**Status**: ✅ Implemented  
**Files Updated**:
- `image_creator_agent/tools/image_tools.py`
  - Added `_detect_mime_type_from_bytes()` function
  - Updated `edit_image()` to use detected MIME type
  - Updated `analyze_image()` to use detected MIME type
  - Enhanced logging for inline_data extraction

**Last Updated**: 2026-01-02

