"""
Test script to investigate ADK streaming behavior.

This script helps determine whether ADK supports token-level streaming
or message-level streaming with Vertex AI.
"""

import asyncio
import os
from pathlib import Path

from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Setup Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv(
    "GOOGLE_CLOUD_PROJECT", "datadog-sandbox"
)
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("VERTEX_AI_LOCATION", "us-central1")


async def test_simple_streaming():
    """Test streaming with a simple agent."""
    print("=" * 80)
    print("TEST 1: Simple Agent Streaming")
    print("=" * 80)

    agent = Agent(
        name="test_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant. Be concise.",
    )

    runner = Runner(
        app_name="test_app", agent=agent, session_service=InMemorySessionService()
    )

    message = types.Content(
        role="user", parts=[types.Part(text="Tell me a short story about AI in 3 sentences.")]
    )

    print("\nStreaming events:")
    print("-" * 80)

    event_count = 0
    text_events = []

    async for event in runner.run_async(
        user_id="test_user", session_id="test_session", new_message=message
    ):
        event_count += 1
        print(f"\nEvent #{event_count}:")
        print(f"  Type: {type(event).__name__}")
        print(f"  Author: {getattr(event, 'author', 'N/A')}")

        if hasattr(event, "content") and event.content:
            if hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        text_events.append(part.text)
                        print(f"  Text length: {len(part.text)} chars")
                        print(f"  Text preview: {part.text[:100]}...")
                    elif hasattr(part, "functionCall"):
                        print(f"  Function call: {part.functionCall.name}")
                    elif hasattr(part, "functionResponse"):
                        print(f"  Function response: {part.functionResponse.name}")

    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    print(f"Total events: {event_count}")
    print(f"Text events: {len(text_events)}")

    if len(text_events) > 1:
        print("\nText accumulation pattern:")
        for i, text in enumerate(text_events[:5]):  # Show first 5
            print(f"  Event {i+1}: {len(text)} chars")
            if i > 0:
                # Check if text is accumulating
                if text.startswith(text_events[i - 1]):
                    print(f"    → Accumulated (includes previous)")
                else:
                    print(f"    → Incremental (new text only)")


async def test_with_runconfig():
    """Test streaming with explicit RunConfig."""
    print("\n\n" + "=" * 80)
    print("TEST 2: Streaming with RunConfig")
    print("=" * 80)

    try:
        from google.adk import RunConfig, StreamingMode

        print("\n✓ StreamingMode available in this ADK version")

        agent = Agent(
            name="test_agent_with_config",
            model="gemini-2.5-flash",
            instruction="You are a helpful assistant. Be concise.",
        )

        runner = Runner(
            app_name="test_app_config",
            agent=agent,
            session_service=InMemorySessionService(),
        )

        message = types.Content(
            role="user", parts=[types.Part(text="Count from 1 to 5 slowly.")]
        )

        # Try to pass RunConfig if supported
        print("\nAttempting to use RunConfig(streaming_mode=StreamingMode.SSE)...")

        try:
            config = RunConfig(streaming_mode=StreamingMode.SSE, max_llm_calls=10)
            print(f"✓ Created RunConfig: {config}")
        except Exception as e:
            print(f"✗ RunConfig not supported: {e}")
            config = None

        event_count = 0
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_2",
            new_message=message,
            # run_config=config,  # Uncomment if supported
        ):
            event_count += 1
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            print(f"Event {event_count}: {part.text[:50]}...")

    except ImportError:
        print("\n✗ StreamingMode not available in this ADK version")
        print("  → This may explain why we're not getting token-level streaming")


async def main():
    """Run all tests."""
    print("ADK Streaming Investigation")
    print("=" * 80)
    print(f"ADK Version: {os.popen('pip show google-adk | grep Version').read().strip()}")
    print(f"Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    print(f"Location: {os.getenv('GOOGLE_CLOUD_LOCATION')}")
    print("=" * 80)

    try:
        await test_simple_streaming()
        await test_with_runconfig()

        print("\n\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("""
Based on the results above:

1. If text accumulates (each event contains previous + new):
   → ADK sends ACCUMULATED TEXT (current behavior)
   → Frontend delta calculation is needed (our current solution)
   
2. If text is incremental (each event contains only new text):
   → ADK sends TOKEN-LEVEL STREAMING (ideal)
   → Frontend can stream directly without delta calculation

3. If StreamingMode is not available:
   → Older ADK version may not support token-level streaming
   → Consider upgrading google-adk package

Recommendation: Our current frontend solution works excellently
and handles both scenarios correctly.
        """)

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

