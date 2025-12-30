# Directory Structure

This document describes the directory structure of the ADK Content Creator service, following the [official Google ADK blog-writer sample](https://github.com/google/adk-samples/blob/main/python/agents/blog-writer/).

## Structure

```
services/adk-content-creator/
├── agents/                          # Main Python package for the agent
│   ├── __init__.py                  # Exports all agents, tools, and config
│   ├── agent.py                     # Main interactive_content_creator_agent (orchestrator)
│   ├── config.py                    # Agent configuration (models, settings)
│   ├── loop_agents.py               # Self-correcting loop agents with validation
│   ├── sub_agents/                  # Individual sub-agents (specialized workers)
│   │   ├── __init__.py              # Exports all sub-agents
│   │   ├── blog_planner.py          # Generates blog post outlines
│   │   ├── blog_writer.py           # Writes complete blog posts
│   │   ├── blog_editor.py           # Edits blog posts based on feedback
│   │   ├── video_script_writer.py   # Generates 60-second video scripts
│   │   └── social_media_writer.py   # Generates platform-specific social media posts
│   ├── tools.py                     # Custom tools (save_content_to_file, analyze_media_file)
│   └── validation_tools.py          # Validation functions for loop agents
├── app/                             # FastAPI application code
│   ├── api/v1/endpoints/            # API route handlers
│   ├── core/                        # Core utilities
│   ├── models/                      # Pydantic models
│   ├── services/                    # Business logic
│   ├── config.py                    # Application settings
│   └── main.py                      # Hybrid FastAPI app (custom + ADK)
├── main_adk.py                      # Full ADK FastAPI app (get_fast_api_app)
├── pyproject.toml                   # uv dependencies (PEP 621)
├── Dockerfile                       # Local development Dockerfile
├── Dockerfile.cloudrun              # Production Cloud Run Dockerfile
└── README.md                        # Project documentation
```

## Agent Architecture

### Main Agent

- **`interactive_content_creator_agent`** (`agents/agent.py`)
  - The main orchestrator agent that interacts with users
  - Manages the workflow of creating content
  - Delegates tasks to appropriate sub-agents
  - Handles user feedback and iterations

### Loop Agents (Self-Correcting)

Loop agents wrap sub-agents with validation logic for self-correction:

- **`robust_blog_planner`** (`agents/loop_agents.py`)
  - Generates blog post outlines
  - Validates outline quality using `validate_blog_outline`
  - Retries up to 3 times if validation fails

- **`robust_blog_writer`** (`agents/loop_agents.py`)
  - Writes complete blog posts
  - Validates post quality using `validate_blog_post`
  - Ensures technical accuracy and Datadog references

- **`robust_video_script_writer`** (`agents/loop_agents.py`)
  - Generates 60-second video scripts
  - Validates script format using `validate_video_script`
  - Ensures proper timing and structure

### Sub-Agents (Specialized Workers)

Sub-agents are defined in `agents/sub_agents/` directory:

- **`blog_planner_sub_agent`** (`blog_planner.py`)
  - Generates detailed blog post outlines
  - Focuses on structure and logical flow

- **`blog_writer_sub_agent`** (`blog_writer.py`)
  - Writes complete blog posts based on approved outlines
  - Includes code examples and technical details

- **`blog_editor_sub_agent`** (`blog_editor.py`)
  - Edits and revises blog posts based on user feedback
  - Maintains technical accuracy and brand voice

- **`video_script_writer_sub_agent`** (`video_script_writer.py`)
  - Generates 60-second video scripts for social media
  - Optimized for YouTube Shorts, TikTok, Instagram Reels

- **`social_media_sub_agent`** (`social_media_writer.py`)
  - Generates platform-specific social media posts
  - Supports LinkedIn, Twitter/X, Instagram

## Tools

Custom tools defined in `agents/tools.py`:

- **`save_content_to_file`**: Saves generated content to a file
- **`analyze_media_file`**: Analyzes uploaded media files for content insights

## Validation Tools

Validation functions defined in `agents/validation_tools.py`:

- **`validate_blog_outline`**: Checks outline structure and completeness
- **`validate_blog_post`**: Validates blog post quality and Datadog references
- **`validate_video_script`**: Validates video script format and timing

## Configuration

Agent configuration defined in `agents/config.py`:

- LLM models for different agents
- Google Cloud project settings
- Datadog LLM Observability settings
- Output directories and other settings

## Workflow

The `interactive_content_creator_agent` follows this workflow:

1. **Analyze Media (Optional)**: If user provides files, analyze them for context
2. **Plan**: Generate blog post outline using `robust_blog_planner`
3. **Refine**: User provides feedback to refine the outline
4. **Write**: Write blog post using `robust_blog_writer`
5. **Edit**: User provides feedback, `blog_editor_sub_agent` revises
6. **Social Media**: Generate social media posts using `social_media_sub_agent`
7. **Export**: Save final content using `save_content_to_file` tool

## Comparison to Official Sample

This structure closely follows the [Google ADK blog-writer sample](https://github.com/google/adk-samples/blob/main/python/agents/blog-writer/):

| Official Sample | Our Implementation |
|----------------|-------------------|
| `blogger_agent/` | `agents/` |
| `blogger_agent/agent.py` | `agents/agent.py` |
| `blogger_agent/sub_agents/` | `agents/sub_agents/` |
| `blogger_agent/sub_agents/blog_planner.py` | `agents/sub_agents/blog_planner.py` |
| `blogger_agent/sub_agents/blog_writer.py` | `agents/sub_agents/blog_writer.py` |
| `blogger_agent/sub_agents/blog_editor.py` | `agents/sub_agents/blog_editor.py` |
| `blogger_agent/sub_agents/social_media_writer.py` | `agents/sub_agents/social_media_writer.py` |
| `blogger_agent/tools.py` | `agents/tools.py` |
| `blogger_agent/config.py` | `agents/config.py` |

**Additional Features** in our implementation:
- `agents/loop_agents.py` - Self-correcting loop agents
- `agents/validation_tools.py` - Validation functions
- `agents/sub_agents/video_script_writer.py` - Video script generation
- `app/` - Custom FastAPI application with additional endpoints
- `main_adk.py` - Full ADK integration with `get_fast_api_app()`

## References

- [Google ADK blog-writer sample](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer)
- [Google ADK blog-writer README](https://raw.githubusercontent.com/google/adk-samples/main/python/agents/blog-writer/README.md)
- [ADK Documentation](https://google.github.io/adk-docs/)

