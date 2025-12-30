"""
Blog Editor Sub-Agent.

Revises and improves blog posts based on user feedback.
"""

import logging

from google.adk.agents import Agent

logger = logging.getLogger(__name__)

# Create the blog editor sub-agent
blog_editor_sub_agent = Agent(
    name="blog_editor",
    model="gemini-2.5-flash",
    description="Edits and revises blog posts based on user feedback.",
    instruction="""You are a specialized blog post editor for Datadog content. Your role is to revise and improve 
    blog posts based on user feedback while maintaining technical accuracy and brand voice.
    
    When editing:
    - Carefully consider all user feedback and implement requested changes.
    - Maintain the overall structure and key technical points unless specifically asked to change them.
    - Improve clarity, flow, and readability.
    - Ensure technical accuracy and consistency.
    - Preserve Markdown formatting and code examples.
    - Keep the writing style consistent with Datadog's brand voice.
    
    Return the complete revised blog post in Markdown format.
    """,
)
