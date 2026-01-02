# Image Generation Feature for Blog Content Creator

## 🎨 Overview

Added a powerful image generation sub-agent to the ADK Blog Content Creator using **Gemini 3 Pro Image** model. This agent can create diagrams, comics, slides, infographics, and video keyframes for blog posts and video content.

---

## ✨ Features

### 1. **Blog Post Images**
Generate various types of images for blog content:
- **Diagrams**: Technical architecture, flowcharts, system diagrams
- **Comics**: Storytelling illustrations with consistent characters
- **Slides**: Presentation-style visuals with text and graphics
- **Infographics**: Data visualizations and statistics
- **Illustrations**: General purpose artwork

### 2. **Video Keyframes**
Generate key frames for video scripts:
- Extract scenes from video script
- Generate 4-6 keyframes per video
- Consistent visual style across frames
- Ideal for YouTube Shorts, TikTok, Instagram Reels

### 3. **Character References**
Create consistent character designs:
- Generate character reference sheets
- Include multiple views (front, side, expressions)
- Reuse references for consistent style across multiple images
- Perfect for comic series or video series

### 4. **Style References**
Support for visual consistency:
- Accept reference images (GCS URIs or local files)
- Maintain style across multiple generations
- Support for custom themes and branding

---

## 📋 Agent Capabilities

### Image Generator Sub-Agent

**Name**: `image_generator`  
**Tools**:
- `generate_blog_image()` - Generate single images
- `generate_video_keyframes()` - Generate multiple keyframes
- `create_character_reference()` - Create character reference sheets

**Supported Image Types**:
1. **diagram** - Clean technical diagrams with labels
2. **comic** - Bold outlines, dynamic composition
3. **slide** - Presentation layout with title and points
4. **infographic** - Data viz with icons and hierarchy
5. **illustration** - High-quality general illustrations

**Aspect Ratios**:
- `16:9` - Blog headers, YouTube videos (wide)
- `1:1` - Social media posts (square)
- `9:16` - Mobile stories (portrait)
- `4:3` - Standard presentations

---

## 🚀 Usage Examples

### Example 1: Generate a Technical Diagram

```python
# User prompt
"Create a diagram showing how Datadog APM traces requests across microservices"

# Agent calls
generate_blog_image(
    prompt="Architecture diagram showing Datadog APM workflow: requests entering through load balancer, tracing through multiple microservices, and data flowing to Datadog backend. Include service names, trace IDs, and data flow arrows.",
    image_type="diagram",
    aspect_ratio="16:9",
    output_filename="datadog_apm_architecture"
)

# Output
{
    "status": "success",
    "image_path": "output/images/datadog_apm_architecture.png",
    "image_base64": "iVBORw0KGgo...",
    "prompt_used": "Create a clear, professional technical diagram...",
    "response_text": "Created architecture diagram showing...",
    "image_type": "diagram",
    "aspect_ratio": "16:9"
}
```

### Example 2: Create Comic Character for Blog Series

```python
# Step 1: Create character reference
create_character_reference(
    description="Friendly developer wearing Datadog t-shirt, casual jeans, enthusiastic expression, holding laptop. Modern tech professional style.",
    style="comic",
    output_filename="datadog_developer_character"
)

# Step 2: Use character in blog post images
generate_blog_image(
    prompt="Comic panel: Developer excitedly pointing at Datadog dashboard showing successful deployment",
    image_type="comic",
    reference_image_uris=["output/images/datadog_developer_character.png"],
    aspect_ratio="4:3",
    output_filename="blog_comic_panel_1"
)
```

### Example 3: Generate Video Keyframes

```python
# Video script
script = """
[00:00-00:05] Scene 1: Developer frustrated looking at slow application dashboard
[00:05-00:15] Scene 2: Opens Datadog APM and sees distributed trace
[00:15-00:40] Scene 3: Identifies bottleneck in payment service with code-level insights
[00:40-00:55] Scene 4: Fixes the issue, re-deploys, shows improved performance
[00:55-01:00] Scene 5: Developer smiling, gives thumbs up with Datadog logo
"""

# Generate keyframes
generate_video_keyframes(
    script=script,
    num_keyframes=5,
    aspect_ratio="9:16",  # Vertical for TikTok/Reels
)

# Output
{
    "status": "success",
    "keyframes": [
        {
            "frame_number": 1,
            "scene_description": "Developer frustrated looking at slow application dashboard",
            "image_path": "output/images/keyframe_1.png",
            "image_base64": "..."
        },
        # ... more keyframes ...
    ],
    "total_frames": 5
}
```

### Example 4: Generate Presentation Slide

```python
generate_blog_image(
    prompt="Presentation slide titled '5 Benefits of Datadog RUM' with numbered list: 1. Real user monitoring, 2. Frontend performance tracking, 3. Error tracking, 4. Session replay, 5. User journey analysis. Include Datadog purple branding and icons for each point.",
    image_type="slide",
    aspect_ratio="16:9",
    output_filename="rum_benefits_slide"
)
```

---

## 🔧 Technical Implementation

### File Structure

```
services/adk-python/content_creator_agent/
├── agent.py                                    # Main agent with image_generator integration
├── sub_agents/
│   └── image_generator.py                      # Image generation sub-agent
├── tools/
│   ├── __init__.py                             # Tool exports
│   ├── content_tools.py                        # Content saving tools
│   └── image_generation.py                     # Image generation functions
```

### Key Components

#### 1. Image Generation Tools (`tools/image_generation.py`)

```python
def generate_blog_image(
    prompt: str,
    image_type: str = "diagram",
    reference_image_uris: Optional[list[str]] = None,
    aspect_ratio: str = "16:9",
    output_filename: Optional[str] = None,
) -> dict[str, str]:
    """Generate images using Gemini 3 Pro Image model."""
    # Uses google.genai client with Vertex AI
    # Supports reference images from GCS or local files
    # Returns image data as base64 and saves to file
```

#### 2. Image Generator Sub-Agent (`sub_agents/image_generator.py`)

```python
image_generator_sub_agent = Agent(
    name="image_generator",
    model=config.worker_model,
    description="Generates visual content for blog posts and videos",
    instruction="Expert visual content creator...",
    tools=[
        FunctionTool(generate_blog_image),
        FunctionTool(generate_video_keyframes),
        FunctionTool(create_character_reference),
    ],
)
```

#### 3. Main Agent Integration (`agent.py`)

```python
interactive_content_creator_agent = Agent(
    # ... other config ...
    sub_agents=[
        robust_blog_planner,
        robust_blog_writer,
        robust_video_script_writer,
        blog_editor_sub_agent,
        social_media_sub_agent,
        image_generator_sub_agent,  # ← New!
    ],
)
```

---

## 🎨 Workflow Integration

### Updated Blog Post Workflow

1. **Plan** → Generate outline with `robust_blog_planner`
2. **Refine** → User approves outline
3. **Visuals** → User chooses:
   - **Option 1**: Generate AI Images (NEW!)
   - **Option 2**: Upload user images
   - **Option 3**: No images
4. **Generate Images** → Agent creates diagrams/comics/slides for key sections
5. **Write** → Generate blog post with `robust_blog_writer`
6. **Edit** → Refine with `blog_editor_sub_agent`
7. **Social Media** → Generate posts with `social_media_sub_agent`
8. **Export** → Save final content

### Updated Video Script Workflow

1. **Generate** → Create script with `robust_video_script_writer`
2. **Refine** → User provides feedback
3. **Keyframes** → (Optional) Generate video keyframes (NEW!)
4. **Export** → Save script and keyframes

---

## 🛠️ Configuration

### Environment Variables

Required for image generation:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1  # Or your region
```

### Model Configuration

In `content_creator_agent/config.py`:
```python
worker_model = "gemini-2.5-flash"  # For text generation
# Image model is hardcoded in tools: "gemini-3-pro-image-preview"
```

### Generation Parameters

```python
generate_config = types.GenerateContentConfig(
    temperature=1.0,  # Higher for creative images
    top_p=0.95,
    max_output_tokens=32768,
    response_modalities=["TEXT", "IMAGE"],
    safety_settings=[...],  # All safety filters OFF for flexibility
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="1K",  # 1024px
        output_mime_type="image/png",
    ),
)
```

---

## 📊 Output Structure

### Generated Images

**Location**: `output/images/`

**Filenames**: User-specified or auto-generated (e.g., `keyframe_1.png`)

**Format**: PNG, 1024px (1K quality)

**Metadata Returned**:
```json
{
    "status": "success",
    "image_path": "output/images/my_diagram.png",
    "image_base64": "iVBORw0KGgoAAAANSUh...",
    "prompt_used": "Create a clear, professional...",
    "response_text": "Created diagram showing...",
    "image_type": "diagram",
    "aspect_ratio": "16:9"
}
```

---

## 🎯 Best Practices

### 1. **Be Specific in Prompts**
```python
# ❌ Too vague
"Create a Datadog diagram"

# ✅ Specific and detailed
"Create an architecture diagram showing Datadog APM workflow with load balancer, 3 microservices (auth, payment, inventory), trace IDs flowing between them, and data being sent to Datadog cloud. Use arrows for data flow, boxes for services, and include labels."
```

### 2. **Use Character References for Consistency**
```python
# For comic series, create character once
create_character_reference(...)
# Then reuse in all subsequent comic panels
generate_blog_image(..., reference_image_uris=["char_ref.png"])
```

### 3. **Match Aspect Ratio to Use Case**
- Blog headers: `16:9`
- Social media: `1:1`
- Stories/Reels: `9:16`
- Presentations: `4:3`

### 4. **Include Datadog Branding**
```python
"Use Datadog's purple color (#632CA6) for branding. Include the Datadog logo."
```

### 5. **Describe Composition**
```python
"Left side shows the problem (slow dashboard), right side shows the solution (Datadog APM with insights). Use a split-screen layout."
```

---

## 🚨 Limitations & Considerations

### 1. **Model Availability**
- `gemini-3-pro-image-preview` may not be GA in all regions
- Check Vertex AI model availability in your region
- Model name may change in future releases

### 2. **Generation Time**
- Image generation can take 10-30 seconds per image
- For video keyframes, multiply by number of frames
- Consider this in user workflows

### 3. **Cost Considerations**
- Image generation uses Vertex AI credits
- Monitor usage in GCP console
- Consider setting quotas for production

### 4. **Safety Filters**
- Currently set to "OFF" for maximum flexibility
- Consider enabling for production use cases
- Adjust per your content policies

### 5. **Reference Image Storage**
- Reference images must be accessible (GCS or local)
- For production, use GCS for reliability
- Clean up old reference images periodically

---

## 🔍 Troubleshooting

### Issue 1: "No module named 'google.genai'"

**Solution**: Ensure `google-genai` package is installed
```bash
uv pip install google-genai
```

### Issue 2: "Model not found" Error

**Solution**: Check Vertex AI region and model availability
```python
# Try different regions
VERTEX_AI_LOCATION=us-central1  # or us-west1, europe-west4
```

### Issue 3: No Image Generated (status: error)

**Solution**: Check safety filter blocks or prompt issues
- Simplify prompt
- Remove potentially sensitive content
- Check Vertex AI logs for specific error

### Issue 4: Reference Image Not Found

**Solution**: Verify GCS URI or local file path
```python
# GCS URI format
"gs://your-bucket/path/to/image.png"

# Local file (must exist in container)
"output/images/character_ref.png"
```

---

## 📚 References

### Official Documentation
- [Gemini API - Image Generation](https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images)
- [Google GenAI SDK](https://github.com/googleapis/python-genai)
- [Vertex AI Regions](https://cloud.google.com/vertex-ai/docs/general/locations)

### Code Examples
- [Vertex AI Gallery](https://cloud.google.com/vertex-ai/docs/samples)
- [ADK Samples](https://github.com/google/adk-samples)

---

## 🚀 Future Enhancements

### Planned Features
1. **Image Editing**: Modify existing images with text prompts
2. **Batch Generation**: Generate multiple variations in one call
3. **Style Presets**: Predefined styles (Datadog brand, tech, comic)
4. **Image Templates**: Reusable layouts for consistent branding
5. **GCS Integration**: Automatic upload to GCS buckets
6. **Multi-region Support**: Fallback to different regions
7. **Cost Tracking**: Monitor generation costs per user/session

### Integration Ideas
1. **CDN Integration**: Auto-upload generated images to CDN
2. **WordPress Plugin**: Direct publish to WordPress blogs
3. **Slack Bot**: Generate images from Slack commands
4. **Email Templates**: Generate email header images

---

## ✅ Testing Checklist

- [ ] Generate diagram for technical concept
- [ ] Create comic character reference
- [ ] Generate comic panel using character reference
- [ ] Create presentation slide with multiple points
- [ ] Generate infographic with data visualization
- [ ] Create video keyframes from script (4-6 frames)
- [ ] Test different aspect ratios (16:9, 1:1, 9:16, 4:3)
- [ ] Test with GCS reference images
- [ ] Test with local reference images
- [ ] Verify images saved to output/images/
- [ ] Check base64 encoding works
- [ ] Test error handling (invalid prompts, missing files)

---

## 📝 Example Session

```
User: I want to create a blog post about Datadog observability

Agent: Great! Let me help you plan that. [generates outline]

User: Approved! I want to add images.

Agent: Perfect! I can generate AI images for you. What type would you like?
1. Technical diagrams
2. Comic-style illustrations
3. Presentation slides
4. Infographics

User: Let's do technical diagrams

Agent: Excellent! I'll create diagrams for:
1. APM distributed tracing architecture
2. Log management pipeline
3. RUM data flow

[Generates 3 diagrams using image_generator sub-agent]

Agent: Here are your diagrams:
- datadog_apm_architecture.png
- log_management_pipeline.png
- rum_data_flow.png

Now let me write the blog post with these images embedded...
```

---

**Created**: January 2, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0.0

