# Frontend Image URL Extraction Fix

## Problem

The backend successfully generates images and saves them to `/app/uploads/`, but the frontend doesn't receive the `image_url` in a structured format through SSE.

**What's happening:**
1. ✅ Backend generates image
2. ✅ Backend saves to `/app/uploads/YYYYMMDD_HHMMSS_UUID.png`
3. ✅ Backend returns `{"image_url": "/uploads/...", "status": "success"}`  
4. ❌ ADK processes this tool result internally but doesn't send it to frontend in SSE
5. ❌ Frontend never receives the structured `image_url`

## Solution

Extract image filenames from the agent's text response and construct URLs manually.

**The agent's thoughts contain filenames:**
```
"The intended filename is `20260102_124312_4a94326c.png`"
"I'm now implementing the correct file name, `20260102_124355_9b13f31`, within..."
```

##Implementation

Update `/libs/api/imageCreator.ts` to:
1. Monitor the full text response for filename patterns
2. Extract filenames matching `/uploads/YYYYMMDD_HHMMSS_UUID.ext`
3. Fetch images after streaming completes
4. Convert to base64 for display

### Pattern to Match

```regex
/uploads/\d{8}_\d{6}_[a-f0-9]{8}\.(?:png|jpg|jpeg|webp|gif)
```

Or simpler (from agent's text):
```regex
\d{8}_\d{6}_[a-f0-9]{8}\.png
```

Then prepend `/uploads/` to construct the full URL.

## Testing

```bash
# Verify images exist
ls -lh /app/uploads/

# Verify they're accessible
curl -I http://localhost:8002/uploads/20260102_130100_abcd1234.png
```

