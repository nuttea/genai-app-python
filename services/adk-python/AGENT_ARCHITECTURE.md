```
# Datadog Content Creator - Agent Architecture

Following ADK blog-writer sample pattern: https://github.com/google/adk-samples/tree/main/python/agents/blog-writer

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                   🤖 interactive_content_creator_agent                       │
│                         (Main Orchestrator)                                 │
│                                                                             │
└──────────────┬──────────────────────────────────────────────────────────────┘
               │
               ├──────────────────────────────────────────────────────────────┐
               │                                                              │
               │  ┌────────────────────────────────────────────────────────┐ │
               │  │   robust_blog_planner (Loop Agent)                     │ │
               │  │                                                        │ │
               │  │   ┌──────────────────────────────────────────────┐   │ │
               │  │   │  🤖 blog_planner                             │   │ │
               │  │   │  (Generate outline)                          │◄──┼─┤
               │  │   └──────────────────────────────────────────────┘   │ │
               │  │                      │                                │ │
               │  │                      ▼                                │ │
               │  │   ┌──────────────────────────────────────────────┐   │ │
               │  │   │  🔧 validate_blog_outline                    │   │ │
               │  │   │  (Check quality)                             │   │ │
               │  │   └──────────────────────────────────────────────┘   │ │
               │  │                      │                                │ │
               │  │                      ▼                                │ │
               │  │              Loop until valid                         │ │
               │  └────────────────────────────────────────────────────────┘ │
               │                                                              │
               ├──────────────────────────────────────────────────────────────┤
               │                                                              │
               │  ┌────────────────────────────────────────────────────────┐ │
               │  │   robust_blog_writer (Loop Agent)                      │ │
               │  │                                                        │ │
               │  │   ┌──────────────────────────────────────────────┐   │ │
               │  │   │  🤖 blog_writer                              │   │ │
               │  │   │  (Write post)                                │◄──┼─┤
               │  │   └──────────────────────────────────────────────┘   │ │
               │  │                      │                                │ │
               │  │                      ▼                                │ │
               │  │   ┌──────────────────────────────────────────────┐   │ │
               │  │   │  🔧 validate_blog_post                       │   │ │
               │  │   │  (Check quality)                             │   │ │
               │  │   └──────────────────────────────────────────────┘   │ │
               │  │                      │                                │ │
               │  │                      ▼                                │ │
               │  │              Loop until valid                         │ │
               │  └────────────────────────────────────────────────────────┘ │
               │                                                              │
               ├──────────────────────────────────────────────────────────────┤
               │                                                              │
               │  ┌────────────────────────────────────────────────────────┐ │
               │  │   robust_video_script_writer (Loop Agent)              │ │
               │  │                                                        │ │
               │  │   ┌──────────────────────────────────────────────┐   │ │
               │  │   │  🤖 video_script_writer                      │   │ │
               │  │   │  (Write script)                              │◄──┼─┤
               │  │   └──────────────────────────────────────────────┘   │ │
               │  │                      │                                │ │
               │  │                      ▼                                │ │
               │  │   ┌──────────────────────────────────────────────┐   │ │
               │  │   │  🔧 validate_video_script                    │   │ │
               │  │   │  (Check quality)                             │   │ │
               │  │   └──────────────────────────────────────────────┘   │ │
               │  │                      │                                │ │
               │  │                      ▼                                │ │
               │  │              Loop until valid                         │ │
               │  └────────────────────────────────────────────────────────┘ │
               │                                                              │
               ├──────────────────────────────────────────────────────────────┤
               │                                                              │
               │  🤖 blog_editor_sub_agent                                    │
               │  (Edit based on feedback)                                   │
               │                                                              │
               ├──────────────────────────────────────────────────────────────┤
               │                                                              │
               │  🤖 social_media_sub_agent                                   │
               │  (Generate social posts)                                    │
               │                                                              │
               ├──────────────────────────────────────────────────────────────┤
               │                                                              │
               │  🔧 save_content_to_file                                     │
               │  (Export as markdown)                                       │
               │                                                              │
               └──────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
                                  🔧 analyze_media_file
                                  (Process uploaded files)
```

## Agent Hierarchy

### 1. Main Agent
- **`interactive_content_creator_agent`** (Orchestrator)
  - Manages user workflow
  - Delegates to specialized agents
  - Handles user feedback loops
  - Coordinates content creation process

### 2. Loop Agents (Self-Correcting)
- **`robust_blog_planner`**
  - Generates blog outlines
  - Validates with `validate_blog_outline`
  - Loops until quality standards met
  - Uses `blog_planner_sub_agent`

- **`robust_blog_writer`**
  - Writes complete blog posts
  - Validates with `validate_blog_post`
  - Loops until quality standards met
  - Uses `blog_writer_sub_agent`

- **`robust_video_script_writer`**
  - Creates 60s video scripts
  - Validates with `validate_video_script`
  - Loops until quality standards met
  - Uses `video_script_writer_sub_agent`

### 3. Sub-Agents (Specialized Workers)
- **`blog_planner_sub_agent`** - Outline generation
- **`blog_writer_sub_agent`** - Blog post writing
- **`blog_editor_sub_agent`** - Content editing
- **`video_script_writer_sub_agent`** - Script writing
- **`social_media_sub_agent`** - Social media posts

### 4. Tools
- **`save_content_to_file`** - Export markdown files
- **`analyze_media_file`** - Process video/image/documents
- **`validate_blog_outline`** - Outline quality check
- **`validate_blog_post`** - Post quality check
- **`validate_video_script`** - Script quality check

## Workflow Examples

### Blog Post Creation

```
User: "Create a blog post about Datadog APM"
  ↓
Main Agent: Determines content type = blog post
  ↓
Main Agent → robust_blog_planner
  ↓
robust_blog_planner → blog_planner_sub_agent (generate outline)
  ↓
robust_blog_planner → validate_blog_outline (check quality)
  ↓
[Loop if validation fails, max 3 attempts]
  ↓
Main Agent: Presents outline to user
  ↓
User: "Looks good, write it"
  ↓
Main Agent → robust_blog_writer
  ↓
robust_blog_writer → blog_writer_sub_agent (write post)
  ↓
robust_blog_writer → validate_blog_post (check quality)
  ↓
[Loop if validation fails, max 3 attempts]
  ↓
Main Agent: Presents draft to user
  ↓
User: "Make it more technical"
  ↓
Main Agent → blog_editor_sub_agent (revise)
  ↓
Main Agent: Presents revised version
  ↓
User: "Perfect! Save it"
  ↓
Main Agent → save_content_to_file
  ↓
User receives file path
```

### Video Script Creation

```
User: "Create a 60s video about Datadog LLMObs"
  ↓
Main Agent: Determines content type = video script
  ↓
Main Agent → robust_video_script_writer
  ↓
robust_video_script_writer → video_script_writer_sub_agent (generate)
  ↓
robust_video_script_writer → validate_video_script (check)
  ↓
[Loop if validation fails, max 3 attempts]
  ↓
Main Agent: Presents script to user
  ↓
User: "Approve and save"
  ↓
Main Agent → save_content_to_file
  ↓
User receives file path
```

## Key Design Patterns

### 1. Loop Agents (Self-Correction)
Following ADK blog-writer pattern, loop agents:
- Generate content using sub-agents
- Validate output with validation tools
- Iterate automatically until quality standards met
- Maximum 3 attempts to prevent infinite loops

### 2. Separation of Concerns
- **Main Agent**: Workflow orchestration
- **Loop Agents**: Quality assurance
- **Sub-Agents**: Content generation
- **Tools**: Actions and validation

### 3. Validation-Driven Development
All generated content is validated:
- Outlines checked for structure
- Blog posts checked for completeness
- Scripts checked for timing/format

### 4. User-Centric Workflow
- Interactive feedback loops
- User approval at key stages
- Iterative refinement
- Clear export mechanism

## File Structure

```
agents/
├── agent.py                    # Main orchestrator
├── loop_agents.py              # Self-correcting agents
├── sub_agents.py               # Specialized workers
├── tools.py                    # Action tools
├── validation_tools.py         # Quality checks
├── config.py                   # Configuration
└── __init__.py                 # Exports
```

## Benefits of This Architecture

### 1. Quality Assurance
- ✅ Automatic validation
- ✅ Self-correction loops
- ✅ Consistent output quality

### 2. Modularity
- ✅ Easy to add new content types
- ✅ Independent agent testing
- ✅ Reusable components

### 3. Maintainability
- ✅ Clear separation of concerns
- ✅ Single responsibility principle
- ✅ Easy to debug

### 4. Scalability
- ✅ Add new loop agents
- ✅ Add new sub-agents
- ✅ Add new validation tools

## Comparison with ADK Blog-Writer

| Feature | ADK Blog-Writer | Content Creator |
|---------|----------------|-----------------|
| Main Agent | `interactive_blogger_agent` | `interactive_content_creator_agent` |
| Loop Agents | `robust_blog_planner`, `robust_blog_writer` | + `robust_video_script_writer` |
| Sub-Agents | 4 (planner, writer, editor, social) | 5 (+ video script writer) |
| Validation | Outline, post | + Video script |
| Content Types | Blog posts | Blog, video, social media |
| Domain | General technical | Datadog products |

## Next Steps

1. ✅ Architecture implemented
2. ⏭️ Test loop agents with validation
3. ⏭️ Test main agent workflow
4. ⏭️ Add more validation rules
5. ⏭️ Deploy with `main_adk.py`

---

**Reference**: [Google ADK blog-writer sample](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer)

**Status**: ✅ Complete ADK implementation with loop agents

