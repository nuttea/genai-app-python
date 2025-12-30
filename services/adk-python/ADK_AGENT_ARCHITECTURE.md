# ADK Agent Architecture - Main Agent with Sub-Agents

## Overview

Implemented a **hierarchical agent architecture** with a main orchestrator agent and three specialized sub-agents, inspired by the [Google ADK blog-writer sample](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Main Agent                            │
│              (content_creator / root_agent)              │
│                                                           │
│  Role: Orchestrator that delegates to sub-agents         │
│  Model: gemini-2.5-flash                                 │
│  Tools: create_blog_post, create_video_script,          │
│         create_social_media_post                         │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Blog Writer  │ │ Video Script │ │ Social Media │
│  Sub-Agent   │ │  Sub-Agent   │ │  Sub-Agent   │
├──────────────┤ ├──────────────┤ ├──────────────┤
│ Specialized  │ │ Specialized  │ │ Specialized  │
│ for blog     │ │ for video    │ │ for social   │
│ posts        │ │ scripts      │ │ media posts  │
│              │ │              │ │              │
│ Model:       │ │ Model:       │ │ Model:       │
│ gemini-2.5   │ │ gemini-2.5   │ │ gemini-2.5   │
│ -flash       │ │ -flash       │ │ -flash       │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Agent Files

### 1. Main Agent (`agents/content_creator.py`)

**Role**: Orchestrator that understands user requests and delegates to specialized sub-agents.

**Capabilities**:
- Analyzes user intent (blog, video, or social media?)
- Routes requests to appropriate sub-agent
- Provides unified interface for all content types
- Handles multi-modal inputs (text, video, images)

**Tools**:
```python
- create_blog_post()        → Delegates to blog_writer_agent
- create_video_script()     → Delegates to video_script_agent
- create_social_media_post() → Delegates to social_media_agent
```

**Instructions**:
- Understand content type needed
- Choose appropriate sub-agent
- Gather requirements
- Delegate and return results

### 2. Blog Writer Sub-Agent (`agents/blog_writer_agent.py`)

**Role**: Specialized agent for professional blog posts about Datadog products.

**Expertise**:
- Technical writing for developers
- SEO optimization
- Structured content (headings, sections, examples)
- Professional tone

**Output Format**:
- Markdown with proper structure
- Executive summary
- Code examples
- SEO-optimized titles

**Parameters**:
```python
- title: Blog post title
- description: Topic and key points
- style: professional | technical | casual
- target_audience: developers | managers | executives
- product: Specific Datadog product
```

### 3. Video Script Sub-Agent (`agents/video_script_agent.py`)

**Role**: Specialized agent for short-form video scripts (60s).

**Expertise**:
- YouTube Shorts, TikTok, Instagram Reels
- Hook-driven storytelling
- Visual cues and timing
- Mobile-first format

**Output Format**:
- Timing markers [MM:SS]
- Visual descriptions [VISUAL: ...]
- Screen recordings [SCREEN: ...]
- Audio cues [AUDIO: ...]

**Script Structure**:
```
Hook (0-3s)    → Grab attention
Problem (3-10s) → Identify pain point
Solution (10-40s) → Show Datadog feature
Demo (40-55s)   → Quick demonstration
CTA (55-60s)    → Call-to-action
```

**Parameters**:
```python
- title: Video title
- description: Topic and key points
- duration: 60 seconds (default)
- platform: youtube_shorts | tiktok | reels
- product: Specific Datadog product
```

### 4. Social Media Sub-Agent (`agents/social_media_agent.py`)

**Role**: Specialized agent for platform-specific social media posts.

**Expertise**:
- LinkedIn (professional, 1300 chars)
- Twitter/X (concise, 280 chars)
- Instagram (visual, 2200 chars)
- Hashtag optimization
- Engagement strategies

**Output Format**:
- Platform-optimized text
- Relevant hashtags
- Visual suggestions
- Engagement prompts

**Parameters**:
```python
- content: Key message
- platform: linkedin | twitter | instagram
- content_type: announcement | tip | case_study
- product: Specific Datadog product
```

## How It Works

### User Request Flow

```
1. User: "Create a blog post about Datadog LLM Observability"
   ↓
2. Main Agent (root_agent):
   - Analyzes: "User wants a blog post"
   - Decides: Use blog_writer_agent
   - Calls: create_blog_post(title="...", description="...")
   ↓
3. Blog Writer Sub-Agent:
   - Generates professional blog post
   - Applies SEO best practices
   - Returns markdown content
   ↓
4. Main Agent:
   - Receives blog post from sub-agent
   - Returns to user
```

### Example: Multi-Content Request

```
User: "Create content about Datadog APM for a product launch"
   ↓
Main Agent decides to use ALL sub-agents:
   ├─→ Blog Writer: Full announcement article
   ├─→ Video Script: 60s demo video
   └─→ Social Media: LinkedIn + Twitter posts
   ↓
Returns complete content package
```

## Benefits

### 1. Separation of Concerns
- ✅ Each agent has a single, focused responsibility
- ✅ Easier to maintain and update
- ✅ Clear boundaries between content types

### 2. Specialized Expertise
- ✅ Blog agent knows SEO and technical writing
- ✅ Video agent knows visual storytelling
- ✅ Social agent knows platform algorithms

### 3. Scalability
- ✅ Easy to add new sub-agents (e.g., podcast scripts, webinars)
- ✅ Main agent automatically routes to new sub-agents
- ✅ No changes to existing sub-agents

### 4. Testability
- ✅ Test each sub-agent independently
- ✅ Mock sub-agents for main agent testing
- ✅ Clear input/output contracts

### 5. Reusability
- ✅ Sub-agents can be used directly (not just via main agent)
- ✅ Can be deployed as separate services
- ✅ Can be called from other agents

## Usage

### Via ADK CLI

```bash
# Run main agent (orchestrator)
adk run agents/content_creator.py

# Run specific sub-agent directly
adk run agents/blog_writer_agent.py
adk run agents/video_script_agent.py
adk run agents/social_media_agent.py
```

### Via ADK Web UI

```bash
# Start web UI with all agents
adk web --port 8000

# Access at: http://localhost:8000
# Select agent: content_creator (main) or sub-agents
```

### Via FastAPI Integration

```python
from agents.content_creator import root_agent

# Main agent is registered in app/main.py
app = get_fast_api_app(agents=[root_agent])
```

### Programmatic Usage

```python
from agents.blog_writer_agent import blog_writer_agent
from agents.video_script_agent import video_script_agent
from agents.social_media_agent import social_media_agent

# Call sub-agents directly
blog_post = await blog_writer_agent(
    title="Getting Started with Datadog",
    description="Intro to APM and tracing",
    style="professional",
)

video_script = await video_script_agent(
    title="Datadog in 60 Seconds",
    description="Quick demo of key features",
    platform="youtube_shorts",
)

social_post = await social_media_agent(
    content="New feature announcement",
    platform="linkedin",
    content_type="announcement",
)
```

## File Structure

```
services/adk-content-creator/
├── agents/
│   ├── __init__.py                  # Exports all agents
│   ├── content_creator.py           # Main orchestrator agent
│   ├── blog_writer_agent.py         # Blog post sub-agent
│   ├── video_script_agent.py        # Video script sub-agent
│   └── social_media_agent.py        # Social media sub-agent
├── app/
│   ├── main.py                      # FastAPI app (registers root_agent)
│   ├── api/v1/endpoints/            # Custom API endpoints
│   │   ├── generate.py              # Content generation endpoints
│   │   └── upload.py                # File upload endpoints
│   └── services/
│       └── gemini_service.py        # Direct Gemini API calls
└── pyproject.toml
```

## Comparison with Monolithic Agent

### Before (Monolithic)

```python
# Single agent does everything
root_agent = Agent(
    tools=[create_blog, create_video, create_social],
    instruction="You can create blogs, videos, and social posts..."
)
# ❌ One agent, many responsibilities
# ❌ Complex instructions
# ❌ Hard to maintain
```

### After (Hierarchical)

```python
# Main agent delegates
root_agent = Agent(
    tools=[create_blog_post, create_video_script, create_social_post],
    instruction="Delegate to specialized sub-agents..."
)

# Sub-agents are focused
blog_writer_agent = Agent(
    instruction="You are an expert blog writer..."
)
# ✅ Clear separation
# ✅ Focused instructions
# ✅ Easy to maintain
```

## Inspired By

This architecture is inspired by the [Google ADK blog-writer sample](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer/blogger_agent), which demonstrates:
- Main agent as orchestrator
- Sub-agents for specialized tasks
- Tool-based delegation
- Clean separation of concerns

## Future Enhancements

### Additional Sub-Agents

1. **Podcast Script Agent**
   - Long-form audio content
   - Interview format
   - Show notes generation

2. **Webinar Agent**
   - Presentation scripts
   - Slide deck outlines
   - Q&A preparation

3. **Documentation Agent**
   - API documentation
   - User guides
   - Troubleshooting docs

4. **Email Campaign Agent**
   - Newsletter content
   - Drip campaigns
   - Personalized outreach

### Advanced Features

1. **Multi-Agent Collaboration**
   - Sub-agents communicate with each other
   - Blog agent asks video agent for visual ideas
   - Social agent repurposes blog content

2. **Feedback Loop**
   - Sub-agents learn from user feedback
   - Main agent improves routing decisions
   - Content quality improves over time

3. **A/B Testing**
   - Generate multiple variants
   - Track performance metrics
   - Optimize based on results

## Testing

### Test Main Agent Routing

```python
# Test that main agent delegates correctly
async def test_main_agent_blog_routing():
    result = await root_agent("Create a blog post about Datadog APM")
    assert "blog_writer_agent" in result.metadata["delegated_to"]

async def test_main_agent_video_routing():
    result = await root_agent("Create a 60-second video about Datadog")
    assert "video_script_agent" in result.metadata["delegated_to"]
```

### Test Sub-Agents Independently

```python
# Test blog writer
async def test_blog_writer():
    result = await blog_writer_agent(
        title="Test Post",
        description="Test description",
    )
    assert "# " in result  # Has markdown heading
    assert len(result) > 500  # Substantial content

# Test video script writer
async def test_video_script():
    result = await video_script_agent(
        title="Test Video",
        description="Test description",
    )
    assert "[0:00-0:03]" in result  # Has timing markers
    assert "[VISUAL:" in result  # Has visual cues
```

## Monitoring

### Datadog LLM Observability

All agents are automatically instrumented with Datadog LLMObs:

```
Main Agent Trace:
├── root_agent (workflow)
│   ├── create_blog_post (tool)
│   │   └── blog_writer_agent (llm)
│   │       └── gemini.generate_content
│   ├── create_video_script (tool)
│   │   └── video_script_agent (llm)
│   │       └── gemini.generate_content
│   └── create_social_media_post (tool)
│       └── social_media_agent (llm)
│           └── gemini.generate_content
```

**Metrics tracked**:
- Agent routing decisions
- Sub-agent latency
- Token usage per agent
- Error rates
- User satisfaction

---

**Status**: ✅ **Implemented**  
**Date**: December 30, 2025  
**Reference**: https://github.com/google/adk-samples/tree/main/python/agents/blog-writer  
**Next**: Test agent routing and sub-agent delegation

