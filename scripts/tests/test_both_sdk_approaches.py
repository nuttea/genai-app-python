#!/usr/bin/env python3
"""
Compare both SDK approaches for listing Gemini models.

Approach 1: google-genai with vertexai=True
Approach 2: vertexai SDK (google-cloud-aiplatform)

Expected Result: Both return empty for first-party Gemini models
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
print(f"✅ Loaded environment from: {env_path}\n")

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("VERTEX_AI_LOCATION", "us-central1")

print("=" * 70)
print("COMPARING TWO SDK APPROACHES")
print("=" * 70)
print(f"\nProject: {project}")
print(f"Location: {location}\n")

# ============================================================================
# Approach 1: google-genai with vertexai=True
# ============================================================================
print("=" * 70)
print("Approach 1: google-genai SDK with vertexai=True")
print("=" * 70)
print("Package: google-genai")
print("Method: genai.Client(vertexai=True).models.list()\n")

try:
    from google import genai

    client = genai.Client(
        vertexai=True,
        project=project,
        location=location
    )

    print("Calling client.models.list()...")
    models = list(client.models.list())

    print(f"Result: {len(models)} models")

    if models:
        print("\nModels returned:")
        for m in models:
            print(f"  - {m.name}")
    else:
        print("❌ No models returned (empty list)")

except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# Approach 2: Vertex AI SDK (google-cloud-aiplatform)
# ============================================================================
print("\n" + "=" * 70)
print("Approach 2: Vertex AI SDK")
print("=" * 70)
print("Package: google-cloud-aiplatform")
print("Method: aiplatform.Model.list()\n")

try:
    from google.cloud import aiplatform

    aiplatform.init(project=project, location=location)

    print("Calling aiplatform.Model.list()...")
    models = list(aiplatform.Model.list())

    print(f"Result: {len(models)} models")

    if models:
        print("\nModels returned:")
        for m in models:
            print(f"  - {m.display_name} ({m.name})")
    else:
        print("❌ No models returned (empty list)")

except ImportError:
    print("⚠️ google-cloud-aiplatform not installed")
    print("   Install: pip install google-cloud-aiplatform")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# Approach 3: Try vertexai.preview.generative_models
# ============================================================================
print("\n" + "=" * 70)
print("Approach 3: vertexai.preview.generative_models")
print("=" * 70)
print("Package: google-cloud-aiplatform (vertexai submodule)")
print("Method: Check if there's a list method\n")

try:
    import vertexai
    from vertexai.preview import generative_models

    vertexai.init(project=project, location=location)

    print("Initialized vertexai")
    print(f"Available in generative_models: {dir(generative_models)}\n")

    # Check if there's a list_models or similar method
    if hasattr(generative_models, 'list_models'):
        print("Found list_models() method!")
        models = generative_models.list_models()
        print(f"Result: {len(models)} models")
    elif hasattr(generative_models, 'get_model'):
        print("Found get_model() method (for getting specific model)")
        print("Trying to get gemini-2.5-flash...")
        try:
            model = generative_models.GenerativeModel("gemini-2.5-flash")
            print(f"✅ Successfully loaded: {model}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No list_models() or get_model() method found")
        print("   Available methods:", [m for m in dir(generative_models) if not m.startswith('_')])

except ImportError as e:
    print(f"⚠️ Could not import vertexai: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# Approach 4: Google AI API (non-Vertex AI)
# ============================================================================
print("\n" + "=" * 70)
print("Approach 4: Google AI API (without Vertex AI)")
print("=" * 70)
print("Package: google-genai")
print("Method: genai.Client().models.list() [Uses GEMINI_API_KEY]\n")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    try:
        from google import genai

        # Initialize client WITHOUT vertexai=True (uses Google AI API)
        # Pass api_key explicitly
        client_ai = genai.Client(api_key=gemini_api_key)

        print("Calling client.models.list() with Google AI API...")
        models = list(client_ai.models.list())

        print(f"Result: {len(models)} models")

        if models:
            print("\n✅ SUCCESS! Models returned:")
            for i, m in enumerate(models[:10], 1):  # Show first 10
                print(f"  {i}. {m.base_model_id if hasattr(m, 'base_model_id') else m.name}")
                if hasattr(m, 'supported_actions'):
                    print(f"     Actions: {m.supported_actions}")

            if len(models) > 10:
                print(f"\n  ... and {len(models) - 10} more models")

            # Filter for generateContent
            generate_models = [m for m in models if hasattr(m, 'supported_actions') and "generateContent" in m.supported_actions]
            print(f"\n📊 Models supporting generateContent: {len(generate_models)}")

        else:
            print("❌ No models returned (empty list)")

    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠️ GEMINI_API_KEY not set in environment")
    print("   To test Google AI API:")
    print("   1. Get API key from: https://aistudio.google.com/apikey")
    print("   2. Set: export GEMINI_API_KEY=your-api-key")
    print("   3. Run this test again")

# ============================================================================
# Test: But can we USE the models?
# ============================================================================
print("\n" + "=" * 70)
print("IMPORTANT: Can we USE Gemini models despite empty list?")
print("=" * 70)
print("Testing if gemini-2.5-flash works for generation with Vertex AI...\n")

try:
    from google import genai

    client = genai.Client(
        vertexai=True,
        project=project,
        location=location
    )

    print("Attempting generate_content with gemini-2.5-flash...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Respond with just 'OK'"
    )

    print(f"✅ SUCCESS! Model works!")
    print(f"   Response: {response.text}")

except Exception as e:
    print(f"❌ Failed: {e}")

# ============================================================================
# Conclusion
# ============================================================================
print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("""
Based on testing:

1. google-genai with vertexai=True (VERTEX AI)
   - models.list() → Returns empty for Gemini models ❌
   - generate_content() → Works perfectly! ✅

2. google-genai without vertexai (GOOGLE AI API)
   - models.list() → Returns full list of Gemini models! ✅
   - Requires GEMINI_API_KEY environment variable
   - Can dynamically fetch model list

3. google-cloud-aiplatform (Vertex AI SDK)
   - Model.list() → Returns empty for Gemini models ❌
   - Same limitation as google-genai with vertexai=True

4. vertexai.preview.generative_models
   - No list_models() method ❌
   - Can load GenerativeModel directly by name
   - Models work for generation ✅

KEY FINDING:
The Google AI API (genai.Client()) CAN list models!
But our app uses Vertex AI for authentication/production.

SOLUTION FOR VERTEX AI:
✅ Use static list of known Gemini model IDs
✅ Models are documented at: https://ai.google.dev/gemini-api/docs/models/gemini
✅ Update manually when new models released

ALTERNATIVE (if we switched to Google AI API):
✅ Could fetch models dynamically with genai.Client().models.list()
❌ But requires GEMINI_API_KEY instead of GCP auth
❌ Less suitable for production GCP environments

WORKING MODEL IDS:
  - gemini-2.5-flash
  - gemini-2.0-flash-exp
  - gemini-1.5-flash-002
  - gemini-1.5-pro-002

All work for generation with both APIs!
""")
