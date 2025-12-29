#!/usr/bin/env python3
"""Debug script to investigate why models.list() returns empty."""

import os
from google import genai

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("VERTEX_AI_LOCATION", "us-central1")

print("=" * 60)
print("Debugging Models API")
print("=" * 60)
print(f"Project: {project}")
print(f"Location: {location}\n")

# Test 1: Vertex AI - List ALL models (no filter)
print("Test 1: Vertex AI client.models.list() - ALL models")
print("-" * 60)
try:
    client_vertex = genai.Client(
        vertexai=True,
        project=project,
        location=location
    )
    
    print("Calling client.models.list()...")
    models_list = list(client_vertex.models.list())
    print(f"Number of models returned: {len(models_list)}")
    
    if models_list:
        print("\n📋 All models:")
        for i, m in enumerate(models_list, 1):
            print(f"\n  {i}. {m.name}")
            print(f"     Display: {m.display_name if hasattr(m, 'display_name') else 'N/A'}")
            print(f"     Base ID: {m.base_model_id if hasattr(m, 'base_model_id') else 'N/A'}")
            if hasattr(m, 'supported_actions'):
                print(f"     Actions: {m.supported_actions}")
            if hasattr(m, 'input_token_limit'):
                print(f"     Input Tokens: {m.input_token_limit}")
            if hasattr(m, 'output_token_limit'):
                print(f"     Output Tokens: {m.output_token_limit}")
    else:
        print("  ❌ No models returned (empty list)")
        
        # Try to list what's available
        print("\n  Trying to get specific model info...")
        try:
            model_info = client_vertex.models.get(model="gemini-2.5-flash")
            print(f"  ✅ gemini-2.5-flash exists: {model_info.name}")
        except Exception as e:
            print(f"  ❌ Error getting gemini-2.5-flash: {e}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test 2: Google AI API (if GEMINI_API_KEY set)")
print("-" * 60)

if os.getenv("GEMINI_API_KEY"):
    try:
        client_ai = genai.Client()  # Uses GEMINI_API_KEY
        
        models_list = list(client_ai.models.list())
        print(f"Number of models: {len(models_list)}")
        
        if models_list:
            print("\nSample models:")
            for m in models_list[:5]:
                print(f"  - {m.base_model_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("  GEMINI_API_KEY not set, skipping")

print("\n" + "=" * 60)
print("Test 3: Direct model access (Vertex AI)")
print("-" * 60)

# Try to use a known model directly without listing
known_models = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-exp", 
    "gemini-1.5-flash-002",
    "gemini-1.5-pro-002"
]

client_vertex = genai.Client(
    vertexai=True,
    project=project,
    location=location
)

for model_name in known_models:
    try:
        # Try to get model info
        model_info = client_vertex.models.get(model=model_name)
        print(f"  ✅ {model_name}: {model_info.display_name if hasattr(model_info, 'display_name') else 'Available'}")
    except Exception as e:
        print(f"  ❌ {model_name}: {str(e)[:80]}")

print("\n" + "=" * 60)
print("Conclusion")
print("=" * 60)
print("""
If Test 1 returns 0 models but Test 3 shows models are available:
  → models.list() may not work with Vertex AI
  → Use static list of known models instead
  → Models still work for inference (generateContent)

If Test 2 (Google AI API) returns models:
  → Could use Google AI API for listing
  → But continue using Vertex AI for inference
  
Recommendation:
  → Use static/hardcoded list of Gemini models
  → Update list manually when new models are released
""")

