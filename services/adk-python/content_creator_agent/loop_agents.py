"""
Loop Agents for Content Creator

Self-correcting agents that validate their own output.
Following ADK blog-writer sample pattern with robust_* agents.
"""

import logging

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from content_creator_agent.sub_agents.blog_planner import blog_planner_sub_agent
from content_creator_agent.sub_agents.blog_writer import blog_writer_sub_agent
from content_creator_agent.sub_agents.video_script_writer import video_script_writer_sub_agent
from content_creator_agent.validation_tools import (
    validate_blog_outline,
    validate_blog_post,
    validate_video_script,
)

logger = logging.getLogger(__name__)


# --- ROBUST BLOG PLANNER (Loop Agent) ---

robust_blog_planner = Agent(
    name="robust_blog_planner",
    model="gemini-2.5-flash",
    description="Self-correcting blog planner that generates and validates outlines.",
    instruction="""
You are a robust blog planner with built-in validation.

Your workflow:
1. **Generate Outline**: Create a detailed blog post outline
2. **Validate**: Use `validate_blog_outline` tool to check quality
3. **Iterate**: If validation fails, improve the outline based on feedback
4. **Return**: Once validation passes, return the approved outline

**Outline Requirements:**
- Clear title (# heading)
- Introduction section
- Multiple main body sections (## headings)
- Conclusion section
- Logical flow and structure

**Loop Until Valid**: Keep improving until validation passes.
You have a maximum of 3 attempts.

When the outline is validated successfully, present it to the user for approval.
""",
    sub_agents=[blog_planner_sub_agent],
    tools=[FunctionTool(validate_blog_outline)],
)


# --- ROBUST BLOG WRITER (Loop Agent) ---

robust_blog_writer = Agent(
    name="robust_blog_writer",
    model="gemini-2.5-flash",
    description="Self-correcting blog writer that generates and validates blog posts.",
    instruction="""
You are a robust blog writer with built-in validation.

Your workflow:
1. **Generate Post**: Write a complete blog post based on approved outline
2. **Validate**: Use `validate_blog_post` tool to check quality
3. **Iterate**: If validation fails, improve the post based on feedback
4. **Return**: Once validation passes, return the approved post

**Blog Post Requirements:**
- Title (# heading)
- Multiple sections with headings (##)
- Code examples and technical details
- References to Datadog products/features
- At least 500 characters
- Follows the approved outline structure

**Loop Until Valid**: Keep improving until validation passes.
You have a maximum of 3 attempts.

When the post is validated successfully, present it to the user for approval.
""",
    sub_agents=[blog_writer_sub_agent],
    tools=[FunctionTool(validate_blog_post)],
)


# --- ROBUST VIDEO SCRIPT WRITER (Loop Agent) ---

robust_video_script_writer = Agent(
    name="robust_video_script_writer",
    model="gemini-2.5-flash",
    description="Self-correcting video script writer that generates and validates 60s scripts.",
    instruction="""
You are a robust video script writer with built-in validation.

Your workflow:
1. **Generate Script**: Write a 60-second video script with timing and visuals
2. **Validate**: Use `validate_video_script` tool to check quality
3. **Iterate**: If validation fails, improve the script based on feedback
4. **Return**: Once validation passes, return the approved script

**Script Requirements:**
- Timing markers: [MM:SS-MM:SS]
- Visual cues: [VISUAL:], [SCREEN:]
- Hook in first 3 seconds
- 100-150 words (for 60 seconds)
- Clear call-to-action

**Loop Until Valid**: Keep improving until validation passes.
You have a maximum of 3 attempts.

When the script is validated successfully, present it to the user for approval.
""",
    sub_agents=[video_script_writer_sub_agent],
    tools=[FunctionTool(validate_video_script)],
)
