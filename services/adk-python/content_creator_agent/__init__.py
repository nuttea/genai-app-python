"""
ADK Agents for Datadog Content Creator.

Full ADK implementation following blog-writer sample pattern.
Reference: https://github.com/google/adk-samples/tree/main/python/agents/blog-writer
"""

# Main agent
from content_creator_agent.agent import interactive_content_creator_agent, root_agent

# Loop agents (self-correcting with validation)
from content_creator_agent.loop_agents import (
    robust_blog_planner,
    robust_blog_writer,
    robust_video_script_writer,
)

# Sub-agents (specialized workers)
from content_creator_agent.sub_agents.blog_planner import blog_planner_sub_agent
from content_creator_agent.sub_agents.blog_writer import blog_writer_sub_agent
from content_creator_agent.sub_agents.blog_editor import blog_editor_sub_agent
from content_creator_agent.sub_agents.video_script_writer import video_script_writer_sub_agent
from content_creator_agent.sub_agents.social_media_writer import social_media_sub_agent

# Tools
from content_creator_agent.tools import save_content_to_file, analyze_media_file
from content_creator_agent.validation_tools import (
    validate_blog_outline,
    validate_blog_post,
    validate_video_script,
)

# Config
from content_creator_agent.config import config

__all__ = [
    # Main agent
    "interactive_content_creator_agent",
    "root_agent",
    # Loop agents
    "robust_blog_planner",
    "robust_blog_writer",
    "robust_video_script_writer",
    # Sub-agents
    "blog_planner_sub_agent",
    "blog_writer_sub_agent",
    "blog_editor_sub_agent",
    "video_script_writer_sub_agent",
    "social_media_sub_agent",
    # Tools
    "save_content_to_file",
    "analyze_media_file",
    # Validation tools
    "validate_blog_outline",
    "validate_blog_post",
    "validate_video_script",
    # Config
    "config",
]
