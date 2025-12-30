# 📝 Datadog Content Creator - Quick Reference

**Full Plan**: [DATADOG_CONTENT_CREATOR_PLAN.md](./DATADOG_CONTENT_CREATOR_PLAN.md)

---

## 🎯 What It Does

Create high-quality blog posts and short video content about Datadog products:

| Content Type | Input | Output |
|--------------|-------|--------|
| 📢 Product Announcement | Text + Screenshots | Blog + Video Script + Social |
| 🎓 Feature Tutorial | Video Demo | Blog + Short Video Script |
| 🚀 Release Notes | Markdown Changelog | Blog + Video Series |
| 💡 Best Practices | Text Outline | Blog + Tip Videos |
| 🎥 Video Content | Any input | 60s YouTube Shorts/TikTok/Reels |

---

## 🏗️ Architecture Overview

```
User Input (Text/Markdown/Video) 
    ↓
Streamlit UI 
    ↓
FastAPI Backend 
    ↓
ADK Agent → Video Processing + Transcription
    ↓
Vertex AI (Gemini)
    ↓
Multi-Format Output:
  - 📄 Blog Post (Markdown/HTML)
  - 🎥 Video Script (60s with scenes)
  - 📱 Social Media Posts
```

---

## 📁 New Service Structure

```
services/adk-content-creator/     # 🆕 NEW
├── app/
│   ├── agent/                    # ADK Agent logic
│   ├── services/
│   │   ├── video_processor.py    # 🆕 Video analysis
│   │   ├── transcript_service.py # 🆕 Transcription
│   │   └── image_analyzer.py     # 🆕 Screenshot analysis
│   └── models/
│       ├── video_script.py       # 🆕 Script structure
│       └── social_post.py        # 🆕 Social content

frontend/streamlit/pages/
└── 2_📝_Content_Creator.py       # 🆕 NEW UI
```

---

## 🛠️ Tech Stack

- **ADK**: Google Agent Development Kit
- **LLM**: Vertex AI (Gemini 2.5 Flash + Vision)
- **Video**: Speech-to-Text, ffmpeg, OpenCV
- **API**: FastAPI
- **UI**: Streamlit
- **Storage**: Cloud Storage (uploads)
- **Deploy**: Cloud Run

---

## 📋 Implementation Timeline (7 Weeks)

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Foundation | Project setup, media processing |
| 2 | Input Processing | Video upload, transcription, analysis |
| 3 | Content Generation | Blog + video script generation |
| 4 | UI | Streamlit page with all features |
| 5 | Video Scripts | Scene breakdown, timing, visuals |
| 6-7 | Testing | Tests, CI/CD, deployment |

---

## 🔑 Key Features

### Input Types ✅
- ✍️ Text/Markdown description
- 🎥 Video demo (MP4, MOV, AVI)
- 📸 Screenshots (PNG, JPG)
- 📄 Existing drafts

### Output Formats ✅
- 📄 **Blog Post** (Markdown, HTML, SEO metadata)
- 🎥 **Short Video Script** (60s with scene breakdown)
- 📱 **Social Media** (LinkedIn, Twitter, Instagram)

### Video Script Components ✅
- **Hook** (0-5s): Attention grabber
- **Intro** (5-15s): Problem/context
- **Demo** (15-50s): Show the feature
- **CTA** (50-60s): Call to action
- **Visuals**: Screen recordings, B-roll, text overlays

---

## 🚀 Usage Example (After Implementation)

### API
```bash
POST /api/v1/generate
{
  "content_type": "feature_tutorial",
  "input": {
    "type": "video",
    "video_url": "gs://bucket/demo.mp4",
    "additional_notes": "Show new APM dashboard features"
  },
  "outputs": {
    "blog": true,
    "video_script": true,
    "social": true
  },
  "options": {
    "video_length": 60,
    "platform": ["YouTube Shorts", "TikTok"],
    "tone": "professional"
  }
}
```

### UI Workflow
1. Open Streamlit → "📝 Content Creator" page
2. Select content type (e.g., "Feature Tutorial")
3. Upload video demo OR paste text
4. Choose output formats:
   - ☑️ Blog Post
   - ☑️ Short Video Script (60s)
   - ☑️ Social Media Posts
5. Configure style (tone, audience, SEO)
6. Click "Generate Content"
7. Preview, edit, download, or publish

---

## 💰 Costs

- **Vertex AI**: ~$0.01 per content generation
- **Speech-to-Text**: ~$0.024 per minute of video
- **Cloud Storage**: ~$0.02/GB for uploads
- **Cloud Run**: ~$0.50 per 1K requests

**Total**: ~$10-50/month depending on usage

---

## 🔐 Required Secrets

Add to Google Secret Manager:
- `GOOGLE_CLOUD_PROJECT`
- `MEDIUM_TOKEN` (optional)
- `DEVTO_TOKEN` (optional)
- `CONFLUENCE_TOKEN` (optional)

---

## 📊 Example Video Script Output

```json
{
  "title": "Set Up Datadog APM in 60 Seconds",
  "platform": "YouTube Shorts",
  "duration": 60,
  "scenes": [
    {
      "timing": "0:00-0:05",
      "voiceover": "Want to monitor your app's performance? Here's how!",
      "visual": "Show Datadog dashboard",
      "text_overlay": "APM Setup in 60s ⚡"
    },
    {
      "timing": "0:05-0:15",
      "voiceover": "First, install the Datadog agent. Just one command!",
      "visual": "Screen recording: Terminal",
      "text_overlay": "pip install ddtrace"
    },
    {
      "timing": "0:15-0:25",
      "voiceover": "Add one line to your Python app...",
      "visual": "Screen recording: Code editor",
      "text_overlay": "from ddtrace import tracer"
    },
    {
      "timing": "0:25-0:50",
      "voiceover": "And boom! Instant insights into your app's performance.",
      "visual": "Show APM dashboard with metrics",
      "text_overlay": null
    },
    {
      "timing": "0:50-0:60",
      "voiceover": "Try it free today. Link in bio!",
      "visual": "Datadog logo + CTA",
      "text_overlay": "Try Free 👉 datadog.com"
    }
  ],
  "hashtags": ["#Datadog", "#APM", "#DevOps", "#Monitoring"],
  "thumbnail_suggestion": "Split screen: Before (confused dev) / After (happy dev with dashboard)"
}
```

---

## 🎯 Use Cases

1. **Product Launch** - Announce new Datadog features with blog + video
2. **Tutorial Series** - Create step-by-step guides from video demos
3. **Release Notes** - Transform changelog into engaging content
4. **Social Media** - Repurpose long content into bite-sized videos
5. **Documentation** - Convert video demos into written tutorials

---

## 🔗 Resources

- **Full Plan**: [DATADOG_CONTENT_CREATOR_PLAN.md](./DATADOG_CONTENT_CREATOR_PLAN.md)
- **Google ADK Samples**: https://github.com/google/adk-samples
- **Vertex AI**: https://cloud.google.com/vertex-ai/docs
- **Speech-to-Text**: https://cloud.google.com/speech-to-text

---

**Ready to implement?** Start with Phase 1 in the full plan! 🚀

