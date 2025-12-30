#!/usr/bin/env python3
"""
Test Google AI API (non-Vertex AI) for listing models.

This uses GEMINI_API_KEY instead of GCP project authentication.
Reference: https://ai.google.dev/gemini-api/docs/models

Setup:
1. Get API key from: https://aistudio.google.com/apikey
2. Add to .env file: GEMINI_API_KEY=your-api-key
3. Run: python test_google_ai_api.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load .env file from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
print(f"✅ Loaded environment from: {env_path}\n")

print("=" * 70)
print("Testing Google AI API (Non-Vertex AI)")
print("=" * 70)

# Check for API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\n❌ ERROR: GEMINI_API_KEY environment variable not set!")
    print("\nTo use Google AI API:")
    print("  1. Visit: https://aistudio.google.com/apikey")
    print("  2. Create an API key")
    print("  3. Export it: export GEMINI_API_KEY=your-api-key")
    print("  4. Run this script again")
    exit(1)

print(f"\n✅ GEMINI_API_KEY is set (length: {len(api_key)})")
print()

# ============================================================================
# Initialize Google AI API Client
# ============================================================================
print("Initializing Google AI API client...")
print("(This uses GEMINI_API_KEY, not GCP project auth)\n")

try:
    # Initialize WITHOUT vertexai=True
    # Pass api_key explicitly
    client = genai.Client(api_key=api_key)
    print("✅ Client initialized successfully\n")

except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    exit(1)

# ============================================================================
# List All Models
# ============================================================================
print("=" * 70)
print("Listing ALL models from Google AI API")
print("=" * 70)

try:
    print("\nCalling client.models.list()...\n")

    all_models = []
    for model in client.models.list():
        all_models.append(model)

    print(f"✅ SUCCESS! Found {len(all_models)} models\n")

    # Display all models
    print("📋 All Available Models:")
    print("-" * 70)

    for i, m in enumerate(all_models, 1):
        print(f"\n{i}. {m.base_model_id}")
        print(f"   Display Name: {m.display_name}")
        if hasattr(m, 'description') and m.description:
            desc = m.description[:100] + "..." if len(m.description) > 100 else m.description
            print(f"   Description: {desc}")
        if hasattr(m, 'supported_actions'):
            print(f"   Supported Actions: {', '.join(m.supported_actions)}")
        if hasattr(m, 'input_token_limit'):
            print(f"   Input Token Limit: {m.input_token_limit:,}")
        if hasattr(m, 'output_token_limit'):
            print(f"   Output Token Limit: {m.output_token_limit:,}")

    # ========================================================================
    # Filter by Action Type
    # ========================================================================
    print("\n" + "=" * 70)
    print("Models Supporting 'generateContent'")
    print("=" * 70)

    generate_models = [
        m for m in all_models
        if hasattr(m, 'supported_actions') and "generateContent" in m.supported_actions
    ]

    print(f"\n✅ {len(generate_models)} models support text generation:\n")
    for m in generate_models:
        print(f"  - {m.base_model_id}")

    # ========================================================================
    # Filter for Embedding Models
    # ========================================================================
    print("\n" + "=" * 70)
    print("Models Supporting 'embedContent'")
    print("=" * 70)

    embed_models = [
        m for m in all_models
        if hasattr(m, 'supported_actions') and "embedContent" in m.supported_actions
    ]

    print(f"\n✅ {len(embed_models)} models support embeddings:\n")
    for m in embed_models:
        print(f"  - {m.base_model_id}")

    # ========================================================================
    # Test Generation with a Model
    # ========================================================================
    print("\n" + "=" * 70)
    print("Testing Generation with gemini-2.5-flash")
    print("=" * 70)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'Hello from Google AI API' if you can see this."
        )
        print(f"\n✅ Generation works!")
        print(f"Response: {response.text}\n")
    except Exception as e:
        print(f"\n❌ Generation failed: {e}\n")

except Exception as e:
    print(f"❌ Error listing models: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
✅ Google AI API CAN list Gemini models!

Advantages:
  - Dynamic model list
  - Up-to-date with latest models
  - Simple API key authentication

Disadvantages:
  - Requires GEMINI_API_KEY (not GCP auth)
  - API key management (rotation, secrets)
  - Less integrated with GCP services

For our application:
  - We use Vertex AI (vertexai=True) for production
  - Vertex AI uses GCP project authentication
  - Vertex AI models.list() returns empty
  - So we use a static model list

If we wanted dynamic listing, we could:
  - Use Google AI API for listing only
  - Use Vertex AI for inference
  - But this adds complexity

Current solution (static list) is simpler and more reliable.
""")
