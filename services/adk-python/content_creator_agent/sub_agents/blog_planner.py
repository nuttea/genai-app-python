"""
Blog Planner Sub-Agent.

Generates detailed blog post outlines for Datadog content.
"""

import logging

from google.adk.agents import Agent

logger = logging.getLogger(__name__)

# Create the blog planner sub-agent
blog_planner_sub_agent = Agent(
    name="blog_planner",
    model="gemini-2.5-flash",
    description="Generates a detailed blog post outline.",
    instruction="""You are a specialized blog post planner for Datadog. Your goal is to create a comprehensive,
    logical, and engaging outline for a technical blog post.
    
    The outline should include:
    - A compelling title.
    - A brief introduction/summary.
    - Main sections with clear headings and subheadings.
    - Key points to cover in each section.
    - A conclusion.
    
    Generate the outline in a clear, structured Markdown format.
    """,
)

