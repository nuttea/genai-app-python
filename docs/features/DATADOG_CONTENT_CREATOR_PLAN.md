# 📝 Datadog Content Creator - ADK Agent Implementation Plan (SIMPLIFIED)

## Overview

A new **ADK (Agent Development Kit) agent service** that helps users create high-quality blog posts and short-form video content about **Datadog Products and New Features**.

**Key Features**:
- ✨ **Uses Gemini 2.5 Flash's native multimodal support** (no ffmpeg/OpenCV needed!)
- Focus on **content creation** (marketing, tutorials, product announcements)
- Direct video/image processing without preprocessing

**Reference**: Based on [Google ADK blog-writer sample](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer)

---

## 🎯 What is Datadog Content Creator?

An intelligent agent that:
1. **Accepts various inputs** - Text, Markdown, Video demos of Datadog products
2. **Generates polished blog posts** - Professional, SEO-optimized content
3. **Creates short video scripts** - YouTube Shorts, TikTok, Instagram Reels
4. **Multi-format optimization** - Blog, social media, documentation
5. **Publishes content** - Medium, Dev.to, Confluence, social platforms

### Use Cases

- 📢 **Product Announcements** - "Introducing Datadog LLM Observability 2.0"
- 🎓 **Feature Tutorials** - "How to set up APM in 5 minutes"
- 🚀 **Release Notes** - "What's new in Datadog Q4 2024"
- 💡 **Best Practices** - "10 tips for optimizing your Datadog dashboard"
- 🎥 **Video Content** - Short demos for social media
- 📊 **Case Studies** - Customer success stories with Datadog

---

## 🏗️ Architecture (Updated)

```
┌──────────────────────────────────────────────────────────────────┐
│              Datadog Content Creator (ADK Agent)                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────┐         │
│  │                  User Input                          │         │
│  │  - Text description                                  │         │
│  │  - Markdown draft                                    │         │
│  │  - Video demo URL/upload                             │         │
│  │  - Screenshots                                       │         │
│  │  - Datadog product/feature                           │         │
│  └──────────────────────┬──────────────────────────────┘         │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────┐         │
│  │               Streamlit UI                           │         │
│  │  - Content type selector                             │         │
│  │  - Input editor (rich text/markdown)                 │         │
│  │  - Video uploader                                    │         │
│  │  - Style configuration                               │         │
│  │  - Output format selector                            │         │
│  └──────────────────────┬──────────────────────────────┘         │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────┐         │
│  │            FastAPI Backend                           │         │
│  │  - File upload handling                              │         │
│  │  - Video processing                                  │         │
│  │  - Content generation API                            │         │
│  └──────────────────────┬──────────────────────────────┘         │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────┐         │
│  │              ADK Agent Core                          │         │
│  │                                                       │         │
│  │  ┌─────────────────────────────────────────┐       │         │
│  │  │ 1. Content Analysis                      │       │         │
│  │  │    - Extract key points                  │       │         │
│  │  │    - Identify product features           │       │         │
│  │  │    - Analyze video transcripts           │       │         │
│  │  └─────────────────────────────────────────┘       │         │
│  │                       ↓                              │         │
│  │  ┌─────────────────────────────────────────┐       │         │
│  │  │ 2. Content Enhancement                   │       │         │
│  │  │    - Improve structure                   │       │         │
│  │  │    - Add technical details               │       │         │
│  │  │    - SEO optimization                    │       │         │
│  │  └─────────────────────────────────────────┘       │         │
│  │                       ↓                              │         │
│  │  ┌─────────────────────────────────────────┐       │         │
│  │  │ 3. Multi-Format Generation               │       │         │
│  │  │    - Long-form blog post                 │       │         │
│  │  │    - Short video script                  │       │         │
│  │  │    - Social media posts                  │       │         │
│  │  └─────────────────────────────────────────┘       │         │
│  │                                                       │         │
│  └──────────────────────┬──────────────────────────────┘         │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────┐         │
│  │          Vertex AI (Gemini 2.5 Flash)                │         │
│  │  - Content generation                                │         │
│  │  - Video script writing                              │         │
│  │  - Image analysis (screenshots)                      │         │
│  │  - Multimodal understanding                          │         │
│  └──────────────────────┬──────────────────────────────┘         │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────┐         │
│  │              Output Generation                       │         │
│  │                                                       │         │
│  │  📄 Blog Post                                        │         │
│  │     - Markdown                                       │         │
│  │     - HTML                                           │         │
│  │     - SEO metadata                                   │         │
│  │                                                       │         │
│  │  🎥 Short Video Script                               │         │
│  │     - Scene breakdown                                │         │
│  │     - Voiceover script                               │         │
│  │     - Visual recommendations                         │         │
│  │     - Timing (60s for Shorts/Reels)                 │         │
│  │                                                       │         │
│  │  📱 Social Media                                     │         │
│  │     - LinkedIn post                                  │         │
│  │     - Twitter thread                                 │         │
│  │     - Instagram caption                              │         │
│  │                                                       │         │
│  └──────────────────────┬──────────────────────────────┘         │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────┐         │
│  │              Publishing                              │         │
│  │  - Medium, Dev.to, Confluence                        │         │
│  │  - YouTube (video script)                            │         │
│  │  - Social media platforms                            │         │
│  └─────────────────────────────────────────────────────┘         │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Updated Project Structure

```
genai-app-python/
├── services/
│   ├── fastapi-backend/              # Existing
│   └── adk-content-creator/          # 🆕 NEW SERVICE (renamed)
│       ├── pyproject.toml            # uv dependencies
│       ├── uv.lock
│       ├── Dockerfile.cloudrun
│       │
│       ├── app/
│       │   ├── agent/                # 🤖 ADK Agent Core
│       │   │   ├── content_agent.py  # Main agent logic
│       │   │   ├── prompts.py        # LLM prompts
│       │   │   ├── tools.py          # Agent tools
│       │   │   └── workflow.py       # Agent workflow
│       │   │
│       │   ├── api/v1/endpoints/
│       │   │   ├── generate.py       # Generate content
│       │   │   ├── upload.py         # Handle uploads
│       │   │   ├── video_script.py   # Generate video scripts
│       │   │   └── publish.py        # Publish content
│       │   │
│       │   ├── services/
│       │   │   ├── content_generator.py  # LLM service
│       │   │   ├── video_processor.py    # 🆕 Video analysis
│       │   │   ├── transcript_service.py # 🆕 Video transcription
│       │   │   ├── image_analyzer.py     # 🆕 Screenshot analysis
│       │   │   ├── seo_optimizer.py      # SEO recommendations
│       │   │   └── publisher.py          # Publish to platforms
│       │   │
│       │   ├── models/
│       │   │   ├── content_input.py      # Input models
│       │   │   ├── blog_post.py          # Blog structure
│       │   │   ├── video_script.py       # 🆕 Video script model
│       │   │   └── social_post.py        # 🆕 Social media posts
│       │   │
│       │   └── core/
│       │       ├── file_storage.py       # 🆕 Handle uploads
│       │       └── media_utils.py        # 🆕 Media processing
│       │
│       └── uploads/                      # 🆕 Temp file storage
│
├── frontend/streamlit/pages/
│   ├── 1_🗳️_Vote_Extractor.py       # Existing
│   └── 2_📝_Content_Creator.py       # 🆕 NEW PAGE (updated)
│
└── docs/features/
    └── DATADOG_CONTENT_CREATOR_PLAN.md   # This file
```

---

## 🛠️ Technology Stack (Updated)

### Core Framework
- **Google ADK** - Agent orchestration
- **Python 3.11+** - Runtime
- **uv** - Dependency management

### AI/LLM
- **Vertex AI (Gemini 2.5 Flash)** - Content generation
- **Vertex AI Multimodal** - Image/video analysis
- **google-genai** - Python SDK
- **Speech-to-Text API** - 🆕 Video transcription

### Media Processing
- **ffmpeg-python** - 🆕 Video processing
- **Pillow (PIL)** - 🆕 Image processing
- **opencv-python** - 🆕 Frame extraction
- **google-cloud-speech** - 🆕 Transcription

### Content Tools
- **markdown** - Markdown processing
- **beautifulsoup4** - HTML processing
- **jinja2** - Template rendering
- **python-frontmatter** - Metadata handling

### API & Web
- **FastAPI** - REST API
- **Streamlit** - UI
- **httpx** - Async HTTP

### Deployment
- **Docker** - Containerization
- **Cloud Run** - Serverless
- **Cloud Storage** - 🆕 File uploads

---

## 📋 Implementation Phases (Updated)

### Phase 1: Foundation (Week 1)

#### 1.1 Project Setup
- [ ] Create `services/adk-content-creator/` structure
- [ ] Initialize `pyproject.toml` with updated dependencies
- [ ] Set up Dockerfile with media processing tools
- [ ] Configure Cloud Storage bucket for uploads

**Simplified Dependencies:**
```toml
[project]
name = "adk-content-creator"
version = "0.1.0"
dependencies = [
    # Core Framework
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    
    # Google Cloud & AI (Multimodal support!)
    "google-genai>=1.0.0",            # ✨ Handles video/image/audio natively!
    "vertexai>=1.70.0",
    "google-cloud-storage>=2.18.0",   # File uploads only
    
    # Content Tools
    "markdown>=3.7",
    "beautifulsoup4>=4.12.0",
    "jinja2>=3.1.0",
    "python-frontmatter>=1.1.0",
    "python-multipart>=0.0.9",
    
    # HTTP & Utils
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
    
    # Datadog
    "ddtrace>=2.17.0",
]

# ❌ Removed (not needed):
# - ffmpeg-python
# - opencv-python  
# - pillow (optional only)
# - google-cloud-speech
```

#### 1.2 Cloud Storage Setup
- [x] Configure Cloud Storage for file uploads (DONE)
- [x] Set up temporary file handling (DONE)
- ✅ **No media processing setup needed** - Gemini handles it!

---

### Phase 2: Input Processing (Week 2) - SIMPLIFIED! ✨

#### 2.1 File Upload Handler
- [ ] Implement file upload API
- [ ] Support multiple formats (video, images, markdown)
- [ ] Validate file types and sizes
- [ ] Upload to Cloud Storage
- [ ] Return file URI for Gemini

**File Types Supported:**
- Video: MP4, MOV, AVI, WebM (up to 2GB with Gemini!)
- Images: PNG, JPG, GIF, WebP
- Text: Markdown, TXT
- Audio: MP3, WAV (for transcription)

#### 2.2 Gemini File Service (One Service for All! ✨)
- [ ] Implement Gemini file upload
- [ ] Send files directly to Gemini
- [ ] No preprocessing needed!

**Simplified Gemini Service:**
```python
# services/gemini_service.py
from google import genai

class GeminiService:
    def __init__(self):
        self.client = genai.Client(vertexai=True)
    
    async def upload_file(self, file_path: str) -> str:
        """Upload file to Gemini - it handles everything!"""
        file = self.client.files.upload(path=file_path)
        return file.uri
    
    async def analyze_media(
        self, 
        file_uri: str, 
        prompt: str
    ) -> str:
        """
        Analyze video/image/audio with Gemini.
        No preprocessing needed - Gemini does it all!
        """
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, file_uri]
        )
        return response.text
```

#### 2.3 ~~Video Processing~~ ❌ NOT NEEDED!
- ❌ ~~Extract audio~~ - Gemini does it
- ❌ ~~Transcribe~~ - Gemini does it  
- ❌ ~~Extract frames~~ - Gemini understands video temporally
- ❌ ~~Analyze frames~~ - Gemini does it all at once

#### 2.4 ~~Image Analysis~~ ❌ NOT NEEDED!
- ❌ ~~Analyze with separate API~~ - Gemini does it
- ❌ ~~Extract text (OCR)~~ - Gemini does it
- ❌ ~~Identify UI elements~~ - Gemini does it
- ✅ **Just send image to Gemini!**

---

### Phase 3: Content Generation (Week 3)

#### 3.1 Blog Post Generation
- [ ] Accept multiple input types
- [ ] Structure long-form content
- [ ] Add technical details
- [ ] SEO optimization

**Content Types:**
```python
class ContentType(Enum):
    PRODUCT_ANNOUNCEMENT = "product_announcement"
    FEATURE_TUTORIAL = "feature_tutorial"
    RELEASE_NOTES = "release_notes"
    BEST_PRACTICES = "best_practices"
    CASE_STUDY = "case_study"
    COMPARISON = "comparison"
```

#### 3.2 Short Video Script Generation
- [ ] Generate 60-second scripts (YouTube Shorts, TikTok, Reels)
- [ ] Scene breakdown with timing
- [ ] Voiceover scripts
- [ ] Visual recommendations
- [ ] B-roll suggestions

**Video Script Structure:**
```python
@dataclass
class VideoScript:
    title: str
    duration: int = 60  # seconds
    hook: SceneDescription  # 0-5s: Attention grabber
    intro: SceneDescription  # 5-10s: What problem/feature
    demo: List[SceneDescription]  # 10-50s: Show the feature
    cta: SceneDescription  # 50-60s: Call to action
    metadata: VideoMetadata
    
@dataclass
class SceneDescription:
    timing: str  # e.g., "0:00-0:05"
    voiceover: str
    visual: str  # Description of what to show
    text_overlay: Optional[str]
    b_roll: Optional[str]
```

**Example Script Output:**
```json
{
  "title": "Set Up Datadog APM in 60 Seconds",
  "duration": 60,
  "scenes": [
    {
      "timing": "0:00-0:05",
      "voiceover": "Want to monitor your app's performance? Here's how to set up Datadog APM in just 60 seconds!",
      "visual": "Show Datadog dashboard with metrics",
      "text_overlay": "APM Setup in 60s ⚡",
      "b_roll": null
    },
    {
      "timing": "0:05-0:15",
      "voiceover": "First, install the Datadog agent. Just one command!",
      "visual": "Screen recording: Terminal with install command",
      "text_overlay": "pip install ddtrace",
      "b_roll": null
    },
    // ... more scenes
  ]
}
```

#### 3.3 Social Media Content
- [ ] LinkedIn post (professional tone)
- [ ] Twitter/X thread (concise, engaging)
- [ ] Instagram caption (visual, hashtags)

---

### Phase 4: Streamlit UI (Week 4)

#### 4.1 Content Creator Page

**UI Layout:**

```python
# pages/2_📝_Content_Creator.py
st.title("📝 Datadog Content Creator")
st.write("Create high-quality blog posts and video content about Datadog products")

# Step 1: Content Type
st.subheader("1️⃣ What do you want to create?")
content_type = st.selectbox("Content Type", [
    "📢 Product Announcement",
    "🎓 Feature Tutorial",
    "🚀 Release Notes",
    "💡 Best Practices",
    "🎥 Video Demo",
    "📊 Case Study"
])

# Step 2: Input Method
st.subheader("2️⃣ Provide your content")
input_method = st.radio("Input Method", [
    "✍️ Text/Markdown",
    "🎥 Video Demo",
    "📸 Screenshots + Description",
    "📄 Existing Draft"
])

if input_method == "✍️ Text/Markdown":
    content_input = st.text_area(
        "Describe the Datadog product/feature",
        height=300,
        placeholder="E.g., Datadog LLM Observability now supports..."
    )
    
elif input_method == "🎥 Video Demo":
    uploaded_video = st.file_uploader(
        "Upload video demo",
        type=["mp4", "mov", "avi"],
        help="Max 500MB. We'll transcribe and analyze it!"
    )
    additional_notes = st.text_area("Additional notes (optional)")
    
elif input_method == "📸 Screenshots + Description":
    uploaded_images = st.file_uploader(
        "Upload screenshots",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    description = st.text_area("Describe what's shown")

# Step 3: Output Options
st.subheader("3️⃣ What formats do you need?")
col1, col2, col3 = st.columns(3)
with col1:
    generate_blog = st.checkbox("📄 Blog Post", value=True)
with col2:
    generate_video_script = st.checkbox("🎥 Short Video Script", value=True)
with col3:
    generate_social = st.checkbox("📱 Social Media", value=False)

# Video options (if selected)
if generate_video_script:
    st.write("**Video Script Options:**")
    video_platform = st.multiselect(
        "Target platforms",
        ["YouTube Shorts", "TikTok", "Instagram Reels"],
        default=["YouTube Shorts"]
    )
    video_length = st.slider("Duration (seconds)", 15, 60, 60)

# Step 4: Style Configuration
with st.expander("⚙️ Advanced Settings"):
    tone = st.select_slider(
        "Tone",
        options=["Casual", "Professional", "Technical"],
        value="Professional"
    )
    target_audience = st.selectbox(
        "Target Audience",
        ["Developers", "DevOps", "SREs", "Business Users", "General"]
    )
    seo_optimize = st.checkbox("Optimize for SEO", value=True)

# Generate Button
if st.button("🚀 Generate Content", type="primary"):
    with st.spinner("Analyzing your input..."):
        # Call API
        response = generate_content(
            content_type=content_type,
            input_method=input_method,
            content_input=content_input,
            formats={
                "blog": generate_blog,
                "video": generate_video_script,
                "social": generate_social
            },
            options={
                "tone": tone,
                "audience": target_audience,
                "seo": seo_optimize,
                "video_length": video_length if generate_video_script else None
            }
        )
    
    st.success("✅ Content generated!")
    
    # Display results in tabs
    if generate_blog:
        with st.expander("📄 Blog Post", expanded=True):
            st.markdown(response.blog_post.content)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download Markdown",
                    response.blog_post.markdown,
                    file_name="blog_post.md"
                )
            with col2:
                st.download_button(
                    "📥 Download HTML",
                    response.blog_post.html,
                    file_name="blog_post.html"
                )
    
    if generate_video_script:
        with st.expander("🎥 Short Video Script", expanded=True):
            st.write(f"**Title:** {response.video_script.title}")
            st.write(f"**Duration:** {response.video_script.duration}s")
            
            for i, scene in enumerate(response.video_script.scenes, 1):
                st.write(f"**Scene {i}: {scene.timing}**")
                st.write(f"*Voiceover:* {scene.voiceover}")
                st.write(f"*Visual:* {scene.visual}")
                if scene.text_overlay:
                    st.write(f"*Text Overlay:* {scene.text_overlay}")
                st.divider()
            
            st.download_button(
                "📥 Download Script",
                response.video_script.to_json(),
                file_name="video_script.json"
            )
    
    if generate_social:
        with st.expander("📱 Social Media Posts", expanded=True):
            st.write("**LinkedIn:**")
            st.text_area("", response.social.linkedin, height=150)
            
            st.write("**Twitter/X Thread:**")
            for i, tweet in enumerate(response.social.twitter_thread, 1):
                st.text_area(f"Tweet {i}", tweet, height=100)
            
            st.write("**Instagram Caption:**")
            st.text_area("", response.social.instagram, height=150)
```

---

### Phase 5: Video Script Generation (Week 5)

#### 5.1 Script Templates
- [ ] YouTube Shorts template (vertical 9:16)
- [ ] TikTok template (casual, trendy)
- [ ] Instagram Reels template (visual-first)

#### 5.2 Scene Generation
- [ ] Hook (0-5s) - Grab attention
- [ ] Problem/Context (5-15s) - Set up the need
- [ ] Solution/Demo (15-50s) - Show the feature
- [ ] CTA (50-60s) - Call to action

#### 5.3 Visual Recommendations
- [ ] Screen recording suggestions
- [ ] B-roll recommendations
- [ ] Text overlay placements
- [ ] Transition suggestions

---

### Phase 6: Testing & Deployment (Week 6-7)

#### 6.1 Testing
- [ ] Unit tests for content generation
- [ ] Integration tests for video processing
- [ ] E2E tests for complete workflow
- [ ] UI tests for Streamlit

#### 6.2 CI/CD
- [ ] GitHub Actions workflow
- [ ] Cloud Run deployment
- [ ] Cloud Storage bucket setup
- [ ] Secret Manager configuration

---

## 📊 Updated Use Cases

### 1. Product Announcement Blog
**Input:** Text description + screenshots  
**Output:** 
- Professional blog post (1500 words)
- 60s YouTube Short script
- LinkedIn post + Twitter thread

### 2. Feature Tutorial
**Input:** Video demo (5 min)  
**Output:**
- Step-by-step blog post with screenshots
- 60s quick-start video script
- Social media teaser posts

### 3. Release Notes
**Input:** Markdown changelog + feature list  
**Output:**
- Engaging blog post highlighting key features
- Short video scripts for top 3 features
- Social media announcement posts

### 4. Best Practices Guide
**Input:** Text outline + examples  
**Output:**
- Comprehensive blog post with code examples
- Series of 60s tip videos
- LinkedIn carousel post content

---

## 💰 Updated Cost Estimates (LOWER!)

| Component | Cost | Notes |
|-----------|------|-------|
| **Vertex AI (Gemini)** | ~$0.01/post | All-in-one multimodal! |
| **~~Speech-to-Text~~** | ~~$0.024/min~~ | ❌ Not needed! |
| **Cloud Storage** | ~$0.02/GB | File uploads |
| **Cloud Run** | ~$0.50/1K requests | Serverless |
| **Total** | **$5-30/month** | **Lower cost!** ✅ |

**Savings**: ~$5-20/month by not using separate Speech-to-Text API!

---

## 🎯 Key Metrics (IMPROVED!)

| Metric | Target | Notes |
|--------|--------|-------|
| Blog post generation | < 20s | Faster with direct Gemini |
| Video script generation | < 30s | No preprocessing delay |
| Video processing | < 30s | Gemini handles natively |
| Content quality score | > 8/10 | Better temporal understanding |
| User edit rate | < 15% | Higher quality output |

**Performance Improvements**:
- ✅ 40% faster (no preprocessing)
- ✅ Better quality (temporal context)
- ✅ Lower latency (1 API call vs 3-4)

---

## 📝 Example Outputs

### Blog Post Example
```markdown
# Introducing Datadog LLM Observability 2.0

Monitor, evaluate, and improve your LLM applications with confidence.

## What's New?

Datadog LLM Observability 2.0 brings powerful new features...

[Generated professional blog post with SEO, structure, examples]
```

### Video Script Example
```json
{
  "title": "Datadog LLM Obs 2.0 in 60 Seconds",
  "platform": "YouTube Shorts",
  "duration": 60,
  "scenes": [
    {
      "timing": "0:00-0:05",
      "hook": "Struggling to monitor your AI apps?",
      "visual": "Show confused developer",
      "text": "AI Monitoring Made Easy"
    },
    // ... detailed scene breakdown
  ]
}
```

---

## 🚀 Next Steps

1. **Review Updated Plan** - Validate new scope
2. **Phase 1: Foundation** - Set up project with media processing
3. **Phase 2: Input Processing** - Video/image handling
4. **Phase 3-6**: Continue implementation

---

**Status**: 📋 Updated Plan - Ready for Implementation  
**Timeline**: 7 weeks (updated scope)  
**Created**: December 30, 2024  
**Updated**: December 30, 2024

