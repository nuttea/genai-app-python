# Image Creator Agent - Testing Guide

## ✅ Deployment Status

**Status**: Successfully deployed and running!

```
✅ Content Creator Agent loaded: interactive_content_creator with 2 tools
✅ Image Creator Agent loaded: image_creator with 3 tools
```

## 🎯 What Changed

### Architectural Decision
Moved from **sub-agent** (within content_creator_agent) to **standalone agent** (image_creator_agent)

**Reason**: 
- ❌ Old: Token accumulation in conversation history (>1M limit)
- ✅ New: Independent sessions, no token buildup

### Implementation
Based on official Google Cloud documentation:
- [Vertex AI Image Generation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)
- [Thought Signatures](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/thought-signatures)
- [Gemini 3 Image Notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/getting-started/intro_gemini_3_image_gen.ipynb)

## 📋 Testing Options

### Option 1: ADK Web Interface (Easiest)

Navigate to: **http://localhost:8002/apps/image_creator/web**

Try these prompts:

1. **Simple Image**:
   ```
   Generate a simple comic image of a happy developer
   ```

2. **Technical Diagram**:
   ```
   Create a diagram showing how Datadog APM tracing works
   ```

3. **Slide**:
   ```
   Generate a presentation slide about the benefits of Datadog
   ```

4. **Multi-Turn Editing** (after generating an image):
   ```
   Make it more colorful
   ```
   Then:
   ```
   Add a purple background (Datadog purple: #632CA6)
   ```

### Option 2: curl API Test

```bash
# Test image generation
curl -X POST http://localhost:8002/apps/image_creator/users/test_user/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate a comic-style image of a happy developer working with Datadog"
  }' | jq
```

**Expected Response**:
```json
{
  "text": "I've created a comic-style image...",
  "artifacts": [{
    "image_base64": "iVBORw0KGgoAAAANS...",
    "mime_type": "image/png"
  }]
}
```

### Option 3: Frontend Integration (Next.js)

**API Endpoint**: `http://localhost:8002/apps/image_creator/users/user_nextjs/sessions`

**Request**:
```typescript
const response = await fetch(
  "http://localhost:8002/apps/image_creator/users/user_nextjs/sessions",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: "Create a diagram showing APM workflow"
    })
  }
);

const data = await response.json();
```

**Display Image**:
```typescript
// Convert base64 to data URL
const imageUrl = `data:${data.artifacts[0].mime_type};base64,${data.artifacts[0].image_base64}`;

// Render in React/Next.js
<img src={imageUrl} alt="Generated image" />

// Or in Markdown component
![Generated image](data:image/png;base64,${data.artifacts[0].image_base64})
```

## 🧪 Test Cases

### Test Case 1: Basic Image Generation
**Prompt**: "Generate a simple diagram"  
**Expected**: Image generated with text description  
**Success Criteria**: Response contains `image_base64` field

### Test Case 2: Specific Image Type
**Prompt**: "Create a comic-style illustration of a developer"  
**Expected**: Comic-style image  
**Success Criteria**: Image has cartoon/comic characteristics

### Test Case 3: Aspect Ratio
**Prompt**: "Generate a 16:9 slide about Datadog"  
**Expected**: Landscape image (16:9)  
**Success Criteria**: Image has correct aspect ratio

### Test Case 4: Multi-Turn Editing
1. "Generate a simple diagram"
2. "Make it more colorful"
3. "Add a title at the top"  
**Success Criteria**: Each turn refines the previous image

### Test Case 5: Safety Filters
**Prompt**: "Generate an image of violence" (intentionally blocked)  
**Expected**: Blocked by safety filters  
**Success Criteria**: Response contains `safety_blocked: true`

## 🔍 Verification

### Check Logs
```bash
# View agent startup logs
docker logs genai-adk-python --tail 50 | grep "Agent loaded"

# Expected output:
# ✅ Content Creator Agent loaded: interactive_content_creator with 2 tools
# ✅ Image Creator Agent loaded: image_creator with 3 tools
```

### Check Container
```bash
# Verify image_creator_agent directory exists
docker exec genai-adk-python ls -la /app/ | grep image_creator

# Expected:
# drwxr-xr-x ... image_creator_agent
```

### Test Agent Import
```bash
# Test Python import
docker exec genai-adk-python python3 -c "from image_creator_agent.agent import image_creator_agent; print(f'Agent: {image_creator_agent.name}, Tools: {len(image_creator_agent.tools)}')"

# Expected:
# Agent: image_creator, Tools: 3
```

## 📊 Performance Expectations

| Metric | Expected Value |
|--------|----------------|
| Image Generation Time | 5-15 seconds |
| Image Size (base64) | 50-200KB |
| Max Request Size | 50MB (multi-turn) |
| Token Limit | 1,048,576 (1M) per request |

## 🚨 Troubleshooting

### Issue: No image generated
**Check**:
1. Model accessible: `location="global"` ✅
2. Response contains `finish_reason`
3. Safety filters not blocking

### Issue: Model not found (404)
**Solution**: Verify `gemini-3-pro-image-preview` is available in `global` endpoint  
**Status**: ✅ Fixed (was `us-central1`)

### Issue: Token limit exceeded
**Solution**: Start a new session (independent from content creator)

### Issue: Image not displaying in frontend
**Check**:
1. Base64 data is valid
2. Data URL format: `data:image/png;base64,{data}`
3. MIME type matches (`image/png`)

## 📖 Documentation

- **Agent Docs**: `services/adk-python/IMAGE_CREATOR_AGENT.md`
- **API Docs**: Auto-generated at `/docs` (FastAPI)
- **Google Docs**: [Image Generation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)

## 🎨 Example Prompts

### Diagrams
```
- "Create a technical architecture diagram showing how APM works"
- "Generate a flowchart for user authentication"
- "Create a system diagram showing microservices architecture"
```

### Comics
```
- "Create a comic-style image of a happy developer"
- "Generate a funny comic about debugging"
- "Create a superhero developer fighting bugs"
```

### Slides
```
- "Generate a presentation slide about Datadog benefits"
- "Create a slide showing key metrics"
- "Generate a title slide for a tech talk"
```

### Infographics
```
- "Create an infographic about observability"
- "Generate a data visualization for APM metrics"
- "Create an infographic showing deployment pipeline stages"
```

## 🚀 Next Steps

1. **Test locally**: Use ADK web interface or curl
2. **Frontend integration**: Add Image Creator tab to Next.js app
3. **Multi-turn editing**: Test conversational refinement
4. **Style presets**: Add Datadog brand colors/styles
5. **Image gallery**: Store and display generated images

## 📝 Commits

- `edae6aa`: feat: Add standalone Image Creator Agent with Gemini 3 Pro Image
- `178bed3`: fix: Copy image_creator_agent to Docker container

---

**Status**: ✅ Ready for testing!  
**Last Updated**: 2026-01-02

