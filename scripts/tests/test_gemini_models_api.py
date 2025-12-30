#!/usr/bin/env python3
"""Test script to verify Gemini models API is working with Vertex AI.

Usage:
    # Make sure your .env file has:
    # GOOGLE_CLOUD_PROJECT=your-project-id
    # VERTEX_AI_LOCATION=us-central1

    # Load environment and run:
    source .env
    python test_gemini_models_api.py

    # Or with poetry:
    cd services/fastapi-backend
    poetry run python ../../test_gemini_models_api.py
"""

import os
import sys
from google import genai

print("=" * 60)
print("Testing Gemini Models API with Vertex AI")
print("=" * 60)

# Get Vertex AI configuration from environment
project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("VERTEX_AI_LOCATION", "us-central1")

print(f"Project: {project}")
print(f"Location: {location}")

if not project:
    print("\n❌ ERROR: GOOGLE_CLOUD_PROJECT environment variable not set!")
    print("Please set it in your .env file or export it:")
    print("  export GOOGLE_CLOUD_PROJECT=your-project-id")
    sys.exit(1)

print()

try:
    # Initialize client with Vertex AI backend
    # This is the same configuration used in vote_extraction_service.py
    client = genai.Client(
        vertexai=True,
        project=project,
        location=location
    )
    print("✅ Client initialized successfully with Vertex AI\n")

    # Alternative: Use Google AI API instead of Vertex AI
    # client = genai.Client()  # Uses GEMINI_API_KEY env var

    print("Listing ALL models (no filter):\n")
    all_models = []
    for m in client.models.list():
        all_models.append(m)
        print(f"  - {m.name}")
        print(f"    Display: {m.display_name if hasattr(m, 'display_name') else 'N/A'}")
        print(f"    Base ID: {m.base_model_id if hasattr(m, 'base_model_id') else 'N/A'}")
        if hasattr(m, 'supported_actions'):
            print(f"    Actions: {m.supported_actions}")
        if hasattr(m, 'input_token_limit'):
            print(f"    Input Tokens: {m.input_token_limit}")
        if hasattr(m, 'output_token_limit'):
            print(f"    Output Tokens: {m.output_token_limit}")
        print()

    print(f"\nTotal models returned: {len(all_models)}")

    # Now filter by generateContent
    print("\n" + "=" * 60)
    print("Filtering for models that support generateContent:\n")
    generate_models = []
    for m in all_models:
        if hasattr(m, 'supported_actions') and "generateContent" in m.supported_actions:
            print(f"  - {m.base_model_id if hasattr(m, 'base_model_id') else m.name}")
            generate_models.append(m)

    print(f"\nTotal models supporting generateContent: {len(generate_models)}")

    print("\n" + "=" * 60)
    print("Filtering for models that support embedContent:\n")
    embed_models = []
    for m in all_models:
        if hasattr(m, 'supported_actions') and "embedContent" in m.supported_actions:
            print(f"  - {m.base_model_id if hasattr(m, 'base_model_id') else m.name}")
            embed_models.append(m)

    print(f"\nTotal models supporting embedContent: {len(embed_models)}")

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
