#!/bin/bash
# Quick test to list all models from Vertex AI

cd /Users/nuttee.jirattivongvibul/Projects/genai-app-python
source .env

echo "Testing Vertex AI models.list() - NO FILTERS"
echo "=============================================="
echo ""

python test_gemini_models_api.py

