# Image Creator Agent

Standalone multimodal agent for image generation and editing using **Gemini 3 Pro Image**.

## Overview

The Image Creator Agent is a dedicated agent separate from the Content Creator Agent, designed specifically for multimodal image operations.

**Based on**: [Google Cloud Vertex AI Image Generation Documentation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)

## Why a Separate Agent?

### Problems with Sub-Agent Architecture:
- ❌ Token accumulation in conversation history (>1M limit)
- ❌ Mixed models (gemini-2.5-flash + gemini-3-pro-image-preview)
- ❌ Context pollution from unrelated conversations
- ❌ Complex debugging

### Benefits of Standalone Agent:
- ✅ Dedicated session management (no token buildup)
- ✅ Direct use of Gemini 3 Pro Image model
- ✅ Clean separation of concerns
- ✅ Independent scaling
- ✅ Better multimodal support (text + images in/out)
- ✅ Multi-turn conversational editing

## Architecture

```
services/adk-python/
├── content_creator_agent/     # Text content (blogs, videos, social)
│   └── agent.py
└── image_creator_agent/       # 🆕 Images (generate & edit)
    ├── __init__.py
    ├── agent.py               # Main agent with gemini-3-pro-image-preview
    ├── config.py              # Configuration
    └── tools/
        ├── __init__.py
        └── image_tools.py     # Image generation/editing tools
```

## Features

### 1. Image Generation
Generate images from text descriptions:
- **Diagrams**: Technical architecture, flowcharts, system diagrams
- **Comics**: Comic-style illustrations with characters
- **Slides**: Presentation-style visuals
- **Infographics**: Data visualizations
- **Illustrations**: General artwork
- **Photos**: Photorealistic images

### 2. Image Editing
Multi-turn conversational editing:
- Style changes ("make it more colorful")
- Object modifications
- Background changes
- Artistic transformations

### 3. Image Analysis
Analyze and describe images:
- Content description
- Object identification
- Text extraction (OCR)
- Detailed analysis

## API Endpoints

ADK automatically creates these endpoints:

```
POST   /apps/image_creator/users/{user_id}/sessions
GET    /apps/image_creator/users/{user_id}/sessions
POST   /apps/image_creator/users/{user_id}/sessions/{session_id}/query
DELETE /apps/image_creator/users/{user_id}/sessions/{session_id}
```

## Configuration

**Model**: `gemini-3-pro-image-preview`  
**Location**: `global` (required for image models)  
**Response Modalities**: `["TEXT", "IMAGE"]`

**Aspect Ratios Supported**:
- Square: `1:1` (default)
- Landscape: `16:9`, `3:2`, `4:3`, `21:9`
- Portrait: `9:16`, `2:3`, `3:4`
- Other: `4:5`, `5:4`

## Tools

### 1. `generate_image`
Generate a new image from text.

**Parameters**:
- `prompt` (str): Text description
- `image_type` (str): diagram, comic, slide, infographic, illustration, photo
- `aspect_ratio` (str): 1:1, 16:9, 9:16, etc.
- `reference_image_uri` (str, optional): GCS URI or local path for style reference

**Returns**:
```python
{
    "status": "success",
    "text_response": "Image description...",
    "image_base64": "iVBORw0KGgoAAAANS...",  # Base64 encoded
    "mime_type": "image/png",
    "prompt_used": "Enhanced prompt...",
    "aspect_ratio": "1:1",
    "image_type": "diagram"
}
```

### 2. `edit_image`
Edit an existing image conversationally.

**Parameters**:
- `edit_prompt` (str): Description of changes
- `original_image_base64` (str): Base64-encoded original image
- `aspect_ratio` (str): Desired aspect ratio

**Returns**: Same format as `generate_image`

### 3. `analyze_image`
Analyze and describe an image.

**Parameters**:
- `image_base64` (str): Base64-encoded image
- `analysis_prompt` (str): What to analyze

**Returns**:
```python
{
    "status": "success",
    "analysis": "Detailed description...",
    "prompt": "Analysis prompt used"
}
```

## Frontend Integration

### Handling `inline_data`

Images are returned in the response as `inline_data` with base64 encoding:

```javascript
// Example response from ADK
{
  "text": "I've generated a diagram showing...",
  "artifacts": [{
    "image_base64": "iVBORw0KGgoAAAANS...",
    "mime_type": "image/png"
  }]
}
```

### Display Images

```typescript
// Convert base64 to data URL
const imageUrl = `data:${response.mime_type};base64,${response.image_base64}`;

// Display in img tag
<img src={imageUrl} alt="Generated image" />

// Or use markdown
![Generated image](data:image/png;base64,${response.image_base64})
```

### Multi-Turn Editing

```typescript
// 1. Generate initial image
const initialResponse = await generateImage({
  prompt: "Create a diagram of APM"
});

// 2. Edit the image conversationally
const editedResponse = await editImage({
  edit_prompt: "Make it more colorful",
  original_image_base64: initialResponse.image_base64
});

// 3. Continue editing
const finalResponse = await editImage({
  edit_prompt: "Add a title",
  original_image_base64: editedResponse.image_base64
});
```

## Usage Examples

### Example 1: Generate a Diagram

**Prompt**: "Generate a diagram showing how Datadog APM traces work"

**Response**:
- Text: "I've created a technical diagram showing..."
- Image: Base64-encoded PNG diagram

### Example 2: Create a Comic

**Prompt**: "Create a comic-style image of a happy developer working with Datadog"

**Response**:
- Text: "Here's a comic illustration showing..."
- Image: Base64-encoded PNG comic

### Example 3: Multi-Turn Editing

**Turn 1**: "Generate a slide about Datadog benefits"
- Response: Initial slide image

**Turn 2**: "Make the background purple"
- Response: Edited slide with purple background

**Turn 3**: "Add a Datadog logo"
- Response: Final slide with logo

## Safety Filters

Gemini 3 Pro Image has comprehensive safety filters to prevent:
- Child content
- Violence
- Hate speech
- Sexual content
- Prohibited content
- Dangerous content
- PII (Personal Identifiable Information)

If content is blocked, the response includes:
```python
{
    "status": "error",
    "error": "Content blocked by safety filters...",
    "safety_blocked": True
}
```

## Testing

### 1. Test via ADK Web Interface
```
http://localhost:8002/apps/image_creator/web
```

### 2. Test via API
```bash
curl -X POST http://localhost:8002/apps/image_creator/users/test_user/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate a diagram showing how APM works"
  }'
```

### 3. Test via Frontend
```typescript
const response = await fetch(
  "http://localhost:8002/apps/image_creator/users/user_nextjs/sessions",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: "Create a comic image of a happy developer"
    })
  }
);
```

## Performance

- **Generation Time**: 5-15 seconds (depends on complexity)
- **Image Size**: ~50-200KB (base64 encoded)
- **Max Request Size**: 50MB (for multi-turn editing)
- **Token Limit**: 1,048,576 tokens (1M) per request

## Troubleshooting

### Issue: Model Not Found (404)
**Solution**: Ensure `location="global"` in config.py

### Issue: No Image Generated
**Possible causes**:
1. Safety filters blocked the prompt
2. Model timeout
3. Invalid parameters

**Check**: Response `finish_reason` and `safety_blocked` flag

### Issue: Base64 Decoding Error
**Solution**: Ensure image data is properly encoded/decoded

### Issue: Token Limit Exceeded
**Solution**: Start a new session (this agent uses fresh sessions)

## Related Documentation

- [Google Cloud Image Generation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)
- [Gemini Thought Signatures](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/thought-signatures)
- [Gemini 3 Image Notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/getting-started/intro_gemini_3_image_gen.ipynb)

## Deployment

The image creator agent is automatically deployed with the ADK Python service:

```bash
# Local development
docker-compose up -d adk-python

# Cloud Run
gcloud run deploy genai-adk-python --source .
```

## Next Steps

1. **Frontend Integration**: Add Image Creator tab to Next.js frontend
2. **Image Gallery**: Store and display generated images
3. **Batch Generation**: Generate multiple images at once
4. **Style Presets**: Pre-configured styles (Datadog brand, technical, comic, etc.)
5. **Image History**: Track and reuse previous generations

---

**Status**: ✅ Implemented and ready for testing  
**Version**: 1.0.0  
**Last Updated**: 2026-01-02

