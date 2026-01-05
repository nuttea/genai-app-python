#!/bin/bash
set -e

echo "🧪 Testing Validation Custom Evaluations Submission"
echo "=================================================="
echo ""

# Find a test image
TEST_IMAGE="services/fastapi-backend/tests/fixtures/test_form.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "⚠️  Test image not found at $TEST_IMAGE"
    echo "Looking for alternative test images..."
    
    # Look for any JPG files
    FOUND_IMAGE=$(find . -name "*.jpg" -o -name "*.png" | grep -v node_modules | head -1)
    
    if [ -z "$FOUND_IMAGE" ]; then
        echo "❌ No test images found. Please provide a test election form image."
        exit 1
    fi
    
    TEST_IMAGE="$FOUND_IMAGE"
    echo "✅ Using test image: $TEST_IMAGE"
fi

echo ""
echo "📤 Sending vote extraction request..."
echo "Using image: $TEST_IMAGE"
echo ""

# Make the request and capture response
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/vote-extraction/extract \
  -F "images=@$TEST_IMAGE" \
  -w "\nHTTP_STATUS:%{http_code}")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response Status: $HTTP_STATUS"
echo ""

if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ Request failed with status $HTTP_STATUS"
    echo "Response body:"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    exit 1
fi

echo "✅ Request succeeded!"
echo ""

# Parse response to get span context
SPAN_ID=$(echo "$BODY" | jq -r '.span_context.span_id // empty' 2>/dev/null)
TRACE_ID=$(echo "$BODY" | jq -r '.span_context.trace_id // empty' 2>/dev/null)

if [ -z "$SPAN_ID" ] || [ -z "$TRACE_ID" ]; then
    echo "⚠️  No span context in response"
else
    echo "📊 Span Context:"
    echo "  Span ID:  $SPAN_ID"
    echo "  Trace ID: $TRACE_ID"
    
    # Convert to hex for Datadog link
    TRACE_ID_HEX=$(python3 -c "print(format(int('$TRACE_ID'), '032x'))")
    echo "  Trace ID (hex): $TRACE_ID_HEX"
    echo "  Datadog Link: https://app.datadoghq.com/apm/trace/$TRACE_ID_HEX"
fi

echo ""
echo "📋 Checking backend logs for evaluation submissions..."
echo ""

# Wait a moment for logs to be written
sleep 2

# Check for evaluation-related logs
docker-compose logs fastapi-backend --tail 200 | grep -i "validation\|evaluation\|submit" | tail -20

echo ""
echo "🔍 Checking for LLMObs activity..."
echo ""

# Check for LLMObs-specific logs
docker-compose logs fastapi-backend --tail 200 | grep -i "llmobs\|evaluation_metric" | tail -20

echo ""
echo "=================================================="
echo "✅ Test complete!"
echo ""
echo "Next steps:"
echo "1. Check the logs above for evaluation submission messages"
echo "2. Visit the Datadog link to see the trace"
echo "3. Look for custom evaluations attached to the trace"
echo ""

