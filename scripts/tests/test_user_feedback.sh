#!/bin/bash
set -e

# Test User Feedback Submission to Datadog LLMObs
echo "🧪 Testing User Feedback Submission..."
echo ""

# Source API key
source .env

# Step 1: Extract votes to get span_id and trace_id
echo "📝 Step 1: Extracting votes to get span context..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/vote-extraction/extract \
  -H "X-API-Key: $API_KEY" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page1.jpg" \
  -F "files=@assets/ss5-18-images/บางบำหรุ1_page2.jpg")

# Extract span_id and trace_id
SPAN_ID=$(echo $RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['span_context']['span_id'])")
TRACE_ID=$(echo $RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['span_context']['trace_id'])")

echo "  ✅ Span ID: $SPAN_ID"
echo "  ✅ Trace ID: $TRACE_ID"
echo ""

# Convert to hex for Datadog URL
TRACE_ID_HEX=$(python3 -c "print(format(int('$TRACE_ID'), '032x'))")
echo "  🔗 Datadog Trace: https://app.datadoghq.com/apm/trace/$TRACE_ID_HEX"
echo ""

# Step 2: Submit user feedback (rating)
echo "📝 Step 2: Submitting user feedback (rating: 5 stars)..."
FEEDBACK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/feedback/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"span_id\": \"$SPAN_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"ml_app\": \"vote-extractor\",
    \"feature\": \"vote-extraction\",
    \"feedback_type\": \"rating\",
    \"rating\": 5,
    \"comment\": \"Great accuracy! The extraction worked perfectly.\",
    \"user_id\": \"test_user_123\",
    \"session_id\": \"test_session_456\"
  }")

echo "  Response: $FEEDBACK_RESPONSE"
echo ""

# Step 3: Submit thumbs feedback
echo "📝 Step 3: Submitting thumbs feedback (thumbs up)..."
THUMBS_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/feedback/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"span_id\": \"$SPAN_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"ml_app\": \"vote-extractor\",
    \"feature\": \"vote-extraction\",
    \"feedback_type\": \"thumbs\",
    \"thumbs\": \"up\",
    \"user_id\": \"test_user_123\",
    \"session_id\": \"test_session_456\"
  }")

echo "  Response: $THUMBS_RESPONSE"
echo ""

# Step 4: Submit comment feedback
echo "📝 Step 4: Submitting comment feedback..."
COMMENT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/feedback/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"span_id\": \"$SPAN_ID\",
    \"trace_id\": \"$TRACE_ID\",
    \"ml_app\": \"vote-extractor\",
    \"feature\": \"vote-extraction\",
    \"feedback_type\": \"comment\",
    \"comment\": \"The ballot statistics section could be more accurate.\",
    \"user_id\": \"test_user_123\",
    \"session_id\": \"test_session_456\"
  }")

echo "  Response: $COMMENT_RESPONSE"
echo ""

# Step 5: Check logs for submission confirmation
echo "📝 Step 5: Checking backend logs..."
sleep 2
docker logs genai-fastapi-backend --tail 50 2>&1 | grep -E "(Submitted feedback|sent.*LLMObs evaluation_metric)" | tail -10
echo ""

echo "✅ Test completed!"
echo ""
echo "📊 View results in Datadog LLMObs:"
echo "   https://app.datadoghq.com/llm"
echo ""
echo "🔗 View this trace:"
echo "   https://app.datadoghq.com/apm/trace/$TRACE_ID_HEX"
echo ""
echo "📝 Expected evaluations:"
echo "   - user_rating (score: 5)"
echo "   - user_thumbs (categorical: up)"
echo "   - user_comment (categorical: to_be_reviewed)"
echo ""

