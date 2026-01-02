# Non-Streaming Image Generation API - Solution

## ✅ Problem Solved

**Original Issue**: ADK's SSE streaming doesn't send tool results (image URLs) to the frontend, only the agent's text response.

**Solution**: Created a custom non-streaming endpoint that returns image URLs directly in JSON response.

---

## 📐 Architecture

### Backend: `/api/v1/images/generate` (Non-Streaming)

**File**: `services/adk-python/main_adk.py`

**Flow**:
1. Receive HTTP POST request with prompt, image_type, aspect_ratio
2. Create new ADK session (using Datadog RUM session ID from frontend)
3. Run `image_creator` agent synchronously (collect all events)
4. Tool generates image → saves to `/app/uploads/YYYYMMDD_HHMMSS_UUID.png`
5. Find the latest generated image file
6. Return JSON with `image_url`, `mime_type`, `text_response`

**Endpoint**:
```
POST http://localhost:8002/api/v1/images/generate
```

**Request**:
```json
{
  "prompt": "datadog and kiro bff",
  "image_type": "comic",
  "aspect_ratio": "1:1",
  "user_id": "user_nextjs",
  "session_id": "rum_abc123xyz"  // From Datadog RUM
}
```

**Response**:
```json
{
  "status": "success",
  "image_url": "/uploads/20260102_140000_abcd1234.png",
  "mime_type": "image/png",
  "text_response": "Image generated successfully",
  "session_id": "rum_abc123xyz",
  "prompt": "datadog and kiro bff",
  "image_type": "comic",
  "aspect_ratio": "1:1",
  "file_size_bytes": 678395
}
```

---

## 🎯 Key Changes

### 1. Backend - Non-Streaming Endpoint

**File**: `services/adk-python/main_adk.py`

```python
@app.post("/api/v1/images/generate")
async def generate_image_sync(request: dict):
    """
    Non-streaming endpoint for image generation.
    Returns image URL directly in JSON response.
    """
    from google.adk.runners import Runner
    from google.adk.sessions import DatabaseSessionService
    
    # Extract parameters
    prompt = request.get("prompt", "Generate an image")
    image_type = request.get("image_type", "illustration")
    aspect_ratio = request.get("aspect_ratio", "1:1")
    session_id = request.get("session_id") or f"img_gen_{int(time.time() * 1000)}"
    
    # Create runner with database session service
    session_service = DatabaseSessionService(SESSION_SERVICE_URI)
    runner = Runner(
        app_name="image_creator",
        agent=image_creator_root_agent,
        session_service=session_service,
    )
    
    # Create session
    new_session = Session(
        session_id=session_id,
        user_id=user_id,
        app_name="image_creator",
        history=[],
    )
    await session_service.create_session(new_session)
    
    # Run agent and collect results
    async for event in runner.run_async(...):
        # Process events
        pass
    
    # Find latest generated image
    image_files = glob.glob(os.path.join(uploads_path, "*.png"))
    latest_image = max(image_files, key=os.path.getmtime)
    image_url = f"/uploads/{os.path.basename(latest_image)}"
    
    return {
        "status": "success",
        "image_url": image_url,
        "mime_type": "image/png",
        ...
    }
```

### 2. Backend - Static File Serving

```python
# Mount uploads directory
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
```

### 3. Backend - Tool Returns URL (Not Base64)

**File**: `services/adk-python/image_creator/tools/image_tools.py`

```python
def generate_image(...) -> dict:
    # ... generate image_data (bytes) ...
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{timestamp}_{unique_id}.png"
    
    uploads_dir = Path("/app/uploads")
    file_path = uploads_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(image_data)
    
    image_url = f"/uploads/{filename}"
    
    # Return URL instead of base64
    return {
        "status": "success",
        "image_url": image_url,  # 30 bytes vs 987KB base64!
        "mime_type": "image/png",
        ...
    }
```

### 4. Frontend - Non-Streaming API Call

**File**: `frontend/nextjs/lib/api/imageCreator.ts`

```typescript
generateImage: async (request: ImageGenerationRequest) => {
  // Get Datadog RUM session ID
  let rumSessionId: string | undefined;
  if (typeof window !== 'undefined' && (window as any).DD_RUM) {
    const session = (window as any).DD_RUM.getInternalContext();
    if (session?.session_id) {
      rumSessionId = `rum_${session.session_id}`;
    }
  }
  
  // Call non-streaming endpoint
  const response = await fetch(`${API_BASE_URL}/api/v1/images/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: request.prompt,
      image_type: request.imageType || 'illustration',
      aspect_ratio: request.aspectRatio || '1:1',
      session_id: rumSessionId,
    }),
  });
  
  const data = await response.json();
  
  if (data.status === 'success' && data.image_url) {
    // Fetch the image from URL
    const imageResponse = await fetch(`${API_BASE_URL}${data.image_url}`);
    const blob = await imageResponse.blob();
    
    // Convert to base64 for display
    const base64 = await new Promise<string>((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1]);
      };
      reader.readAsDataURL(blob);
    });
    
    return {
      text: data.text_response,
      images: [{
        mime_type: data.mime_type,
        data: base64,
      }],
      status: 'success',
    };
  }
}
```

### 5. Frontend - Datadog RUM Session Management

**File**: `frontend/nextjs/app/image-creator/page.tsx`

```typescript
export default function ImageCreatorPage() {
  const [sessionId] = useState(() => {
    const rumSessionId = datadogRum.getInternalContext()?.session_id;
    return rumSessionId ? `img_dd_${rumSessionId}` : `img_${Date.now()}`;
  });

  // Stop RUM session on page unload/refresh (kiosk session pattern)
  useEffect(() => {
    const handleBeforeUnload = () => {
      try {
        datadogRum.stopSession();
        console.log('📊 Stopped Datadog RUM session on page unload');
      } catch (e) {
        console.warn('Could not stop RUM session:', e);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      handleBeforeUnload(); // Also stop on component unmount
    };
  }, []);
  
  // ... rest of component
}
```

---

## 🎯 Benefits

### 1. Simple & Direct
- No SSE parsing complexity
- Direct JSON response
- Standard HTTP request/response

### 2. Tool Result Size Reduction
- **Before**: 987,536 bytes (base64 string sent to model) → 400 ERROR
- **After**: ~30 bytes (URL string sent to model) → ✅ SUCCESS
- **Reduction**: 99.997%

### 3. Scalability
- Images stored on disk
- Browser can cache images
- Works for any image size
- RESTful pattern

### 4. Datadog RUM Integration
- Uses RUM session ID for correlation
- Stops session on page refresh (kiosk pattern)
- Fresh session on every page load
- Prevents session accumulation

---

## 📊 Comparison: Streaming vs Non-Streaming

| Aspect | SSE Streaming | Non-Streaming (Implemented) |
|--------|---------------|----------------------------|
| **Complexity** | High (SSE parsing) | Low (simple fetch) |
| **Real-time Updates** | Yes (text streaming) | No (wait for completion) |
| **Image Delivery** | ❌ Tool results not sent | ✅ Direct URL in JSON |
| **Error Handling** | Complex (partial streams) | Simple (HTTP status) |
| **Debugging** | Difficult | Easy |
| **Browser Compat** | EventSource required | Universal (fetch) |
| **Backend Load** | Higher (keep connection open) | Lower (one-shot) |
| **Use Case** | Long conversations | Single image generation |

---

## 🚀 Testing

### 1. Start Services

```bash
docker-compose up -d adk-python
docker-compose logs -f adk-python
```

### 2. Test Backend Directly

```bash
curl -X POST http://localhost:8002/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A diagram showing Datadog APM",
    "image_type": "diagram",
    "aspect_ratio": "16:9",
    "session_id": "test_123"
  }' | jq .
```

**Expected Output**:
```json
{
  "status": "success",
  "image_url": "/uploads/20260102_140500_abc12345.png",
  "mime_type": "image/png",
  "text_response": "Generated diagram...",
  "session_id": "test_123"
}
```

### 3. Verify Image

```bash
curl -I http://localhost:8002/uploads/20260102_140500_abc12345.png
```

**Expected**:
```
HTTP/1.1 200 OK
content-type: image/png
content-length: 678395
```

### 4. Test Frontend

1. Navigate to: http://localhost:3000/image-creator
2. Enter prompt: "datadog and kiro bff"
3. Select type: "Comic"
4. Click "Generate Image"
5. **Expected**: Image appears after ~20 seconds

### 5. Check RUM Session

Open browser console:
```javascript
DD_RUM.getInternalContext()
// Should see: { session_id: "abc-123-xyz", ... }
```

Refresh page:
```javascript
DD_RUM.getInternalContext()
// Should see: { session_id: "def-456-uvw", ... } // NEW session
```

---

## 📝 Key Files Changed

1. **`services/adk-python/main_adk.py`**
   - Added `/api/v1/images/generate` endpoint
   - Added static file serving for `/uploads`
   - Integrated ADK Runner with DatabaseSessionService

2. **`services/adk-python/image_creator/tools/image_tools.py`**
   - Modified `generate_image` to save files and return URLs
   - Modified `edit_image` similarly

3. **`frontend/nextjs/lib/api/imageCreator.ts`**
   - Changed `generateImage` to use non-streaming endpoint
   - Added Datadog RUM session ID extraction
   - Added image fetching from URL

4. **`frontend/nextjs/app/image-creator/page.tsx`**
   - Added `useEffect` for `stopSession()` on unload
   - Uses RUM session ID for session management

---

## 🔐 Security Considerations

1. **File Storage**: Images stored in `/app/uploads/` with timestamped unique names
2. **Static Files**: Served via FastAPI StaticFiles (no directory traversal)
3. **Session Isolation**: Each session gets unique ID from RUM
4. **Cleanup**: Consider adding cron job to delete old images

---

## 🎓 References

- **Datadog RUM Kiosk Sessions**: https://docs.datadoghq.com/real_user_monitoring/guide/monitor-kiosk-sessions-using-rum/?tab=npm
- **Google ADK Runners**: https://github.com/google/adk-python
- **FastAPI StaticFiles**: https://fastapi.tiangolo.com/tutorial/static-files/

---

## ✅ Success Criteria

- [x] Backend generates images successfully
- [x] Images saved to `/app/uploads/`
- [x] Images accessible via HTTP GET
- [x] Non-streaming endpoint returns image URL
- [x] Frontend fetches and displays images
- [x] No 400 INVALID_ARGUMENT errors
- [x] Datadog RUM session ID integration
- [x] Session stops on page refresh

**Status: ✅ COMPLETE**

