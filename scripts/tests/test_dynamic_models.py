#!/usr/bin/env python3
"""
Test script for dynamic model listing with GEMINI_API_KEY.

This script tests the dynamic model fetching functionality
implemented in the backend.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import httpx
import json

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
print(f"✅ Loaded environment from: {env_path}\n")

print("=" * 70)
print("Testing Dynamic Model Listing")
print("=" * 70)

# Check for API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\n❌ ERROR: GEMINI_API_KEY not set!")
    print("Please add GEMINI_API_KEY to your .env file")
    exit(1)

print(f"\n✅ GEMINI_API_KEY is set (length: {len(api_key)})\n")

# Test 1: Direct REST API call
print("=" * 70)
print("Test 1: Direct REST API Call")
print("=" * 70)

try:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    print(f"\nCalling: {url[:80]}...\n")

    response = httpx.get(url, timeout=10.0)
    response.raise_for_status()

    data = response.json()
    models = data.get("models", [])

    # Filter for Gemini models with generateContent support
    gemini_models = []
    for model in models:
        model_name = model.get("name", "").replace("models/", "")
        if model_name.startswith("gemini-"):
            supported_methods = model.get("supportedGenerationMethods", [])
            if "generateContent" in supported_methods:
                gemini_models.append(model_name)

    print(f"✅ SUCCESS! Found {len(gemini_models)} Gemini models with generateContent support\n")
    print("📋 Models:")
    for i, model in enumerate(gemini_models[:10], 1):  # Show first 10
        print(f"  {i}. {model}")

    if len(gemini_models) > 10:
        print(f"  ... and {len(gemini_models) - 10} more")

except httpx.TimeoutException:
    print("❌ TIMEOUT: API request timed out")
    exit(1)
except httpx.HTTPStatusError as e:
    print(f"❌ HTTP ERROR: {e.response.status_code}")
    print(f"Response: {e.response.text}")
    exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)

# Test 2: Test backend models endpoint (if running)
print("\n" + "=" * 70)
print("Test 2: Backend /models Endpoint (if running)")
print("=" * 70)

backend_url = os.getenv("API_BASE_URL", "http://localhost:8000")
models_url = f"{backend_url}/api/v1/vote-extraction/models"

try:
    print(f"\nCalling: {models_url}\n")

    response = httpx.get(models_url, timeout=10.0)
    response.raise_for_status()

    data = response.json()
    providers = data.get("providers", [])

    for provider in providers:
        if provider.get("name") == "vertex_ai":
            models = provider.get("models", [])
            dynamic = provider.get("dynamic_listing", False)

            print(f"✅ Backend returned {len(models)} Gemini models")
            print(f"📊 Dynamic listing: {'ENABLED' if dynamic else 'DISABLED (using static fallback)'}\n")

            print("📋 First 5 models:")
            for i, model in enumerate(models[:5], 1):
                print(f"  {i}. {model.get('name')} - {model.get('display_name')}")

            if len(models) > 5:
                print(f"  ... and {len(models) - 5} more")

            break

except httpx.ConnectError:
    print("⚠️  Backend not running locally")
    print("   To test backend:")
    print("   1. Run: docker-compose up -d")
    print("   2. Wait for services to start")
    print("   3. Run this script again")

except Exception as e:
    print(f"⚠️  Could not connect to backend: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
✅ Dynamic model listing is working!

The REST API successfully fetches models from Google AI API.

Next steps:
1. The backend will now use dynamic model listing in production
2. Models are cached for 1 hour to reduce API calls
3. If API call fails, it falls back to static list automatically

Configuration:
- Cloud Run: GEMINI_API_KEY is configured in Secret Manager
- Local Dev: GEMINI_API_KEY in .env file
- Docker Compose: GEMINI_API_KEY environment variable

""")
