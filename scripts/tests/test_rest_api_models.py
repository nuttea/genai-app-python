#!/usr/bin/env python3
"""
Test Gemini REST API for listing models.

Uses the direct REST API endpoint instead of the Python SDK.
Reference: https://ai.google.dev/api/rest/generativelanguage/models/list
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
print(f"✅ Loaded environment from: {env_path}\n")

print("=" * 70)
print("Testing Gemini REST API for Model Listing")
print("=" * 70)

# Check for API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\n❌ ERROR: GEMINI_API_KEY not set!")
    exit(1)

print(f"\n✅ GEMINI_API_KEY is set (length: {len(api_key)})\n")

# ============================================================================
# Method 1: List models via REST API
# ============================================================================
print("=" * 70)
print("Method 1: REST API - /v1beta/models")
print("=" * 70)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print(f"\nCalling: {url[:80]}...\n")

try:
    response = requests.get(url, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        models = data.get('models', [])

        print(f"✅ SUCCESS! Found {len(models)} models\n")

        if models:
            print("📋 Available Models:")
            print("-" * 70)

            for i, model in enumerate(models, 1):
                name = model.get('name', 'Unknown')
                display_name = model.get('displayName', 'Unknown')
                description = model.get('description', 'No description')

                print(f"\n{i}. {name}")
                print(f"   Display Name: {display_name}")

                # Truncate long descriptions
                if len(description) > 100:
                    description = description[:100] + "..."
                print(f"   Description: {description}")

                # Show supported generation methods
                if 'supportedGenerationMethods' in model:
                    methods = model['supportedGenerationMethods']
                    print(f"   Supported Methods: {', '.join(methods)}")

                # Show input/output token limits
                if 'inputTokenLimit' in model:
                    print(f"   Input Token Limit: {model['inputTokenLimit']:,}")
                if 'outputTokenLimit' in model:
                    print(f"   Output Token Limit: {model['outputTokenLimit']:,}")

            # ================================================================
            # Filter by generation method
            # ================================================================
            print("\n" + "=" * 70)
            print("Models Supporting 'generateContent'")
            print("=" * 70)

            generate_models = [
                m for m in models
                if 'generateContent' in m.get('supportedGenerationMethods', [])
            ]

            print(f"\n✅ {len(generate_models)} models support text generation:\n")
            for m in generate_models:
                print(f"  - {m.get('name')}")
                print(f"    ({m.get('displayName')})")

            # ================================================================
            # Filter by embedding method
            # ================================================================
            print("\n" + "=" * 70)
            print("Models Supporting 'embedContent'")
            print("=" * 70)

            embed_models = [
                m for m in models
                if 'embedContent' in m.get('supportedGenerationMethods', [])
            ]

            print(f"\n✅ {len(embed_models)} models support embeddings:\n")
            for m in embed_models:
                print(f"  - {m.get('name')}")
                print(f"    ({m.get('displayName')})")

        else:
            print("⚠️ No models found in response")
            print(f"\nRaw response: {data}")

    else:
        print(f"❌ Request failed!")
        print(f"Response: {response.text[:500]}")

except requests.exceptions.Timeout:
    print("❌ Request timed out")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# Method 2: Get specific model details
# ============================================================================
print("\n" + "=" * 70)
print("Method 2: REST API - Get Specific Model Info")
print("=" * 70)

model_name = "models/gemini-2.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}?key={api_key}"

print(f"\nCalling: {url[:80]}...\n")

try:
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        model = response.json()
        print(f"✅ Model found: {model.get('displayName')}")
        print(f"\nDetails:")
        print(f"  Name: {model.get('name')}")
        print(f"  Display Name: {model.get('displayName')}")
        print(f"  Description: {model.get('description', 'N/A')[:150]}...")
        print(f"  Supported Methods: {', '.join(model.get('supportedGenerationMethods', []))}")
        print(f"  Input Token Limit: {model.get('inputTokenLimit', 'N/A'):,}")
        print(f"  Output Token Limit: {model.get('outputTokenLimit', 'N/A'):,}")
        print(f"  Temperature: {model.get('temperature', 'N/A')}")
        print(f"  Top-K: {model.get('topK', 'N/A')}")
        print(f"  Top-P: {model.get('topP', 'N/A')}")
    else:
        print(f"❌ Model not found or error: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
The REST API approach:
  - Direct HTTP calls to Google's API
  - Returns actual model list (unlike SDK)
  - Provides detailed model information
  - Requires API key in URL parameter

If REST API returns models successfully:
  ✅ We CAN get dynamic model list!
  ✅ Could integrate this into our backend
  ✅ Would need to transform REST response to our format

If REST API also returns empty:
  ❌ Google may have disabled model listing
  ❌ Static list remains the best approach
  ✅ All known models still work for generation
""")
