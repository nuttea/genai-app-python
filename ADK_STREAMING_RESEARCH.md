# ADK Streaming Research: Vertex AI SDK & Google ADK Integration

## 🔍 Research Summary

**Date**: January 2, 2026  
**Goal**: Investigate best practices for streaming responses with Google ADK API servers and Vertex AI SDK

---

## 📚 Key Findings from Google ADK Documentation

### 1. ADK Supports Token-Level Streaming

According to the official [ADK documentation](https://github.com/google/adk-docs/blob/main/docs/runtime/api-server.md), ADK **does support token-level streaming** when `streaming: true` is passed in the `/run_sse` request.

#### Example from Documentation:

**Request**:
```json
{
  "appName": "my_sample_agent",
  "userId": "u_123",
  "sessionId": "s_123",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "Tell me a long story about a dragon."}]
  },
  "streaming": true
}
```

**Expected Token-Level Response**:
```text
data: {"event_type": "token", "token": "Once"}
data: {"event_type": "token", "token": " upon"}
data: {"event_type": "token", "token": " a"}
data: {"event_type": "token", "token": " time"}
...
data: {"event_type": "end_of_stream"}
```

---

## 🤔 Current vs Expected Behavior

### What We Currently Receive

Our ADK backend sends **full accumulated text** in each SSE event:

```json
data: {"content":{"parts":[{"text":"Hello"}],...}}
data: {"content":{"parts":[{"text":"Hello world"}],...}}
data: {"content":{"parts":[{"text":"Hello world, how"}],...}}
```

### What Documentation Shows

Token-level streaming should send **individual tokens**:

```json
data: {"event_type": "token", "token": "Hello"}
data: {"event_type": "token", "token": " world"}
data: {"event_type": "token", "token": ","}
data: {"event_type": "token", "token": " how"}
```

---

## 🧩 Why the Difference?

### Possible Reasons:

1. **ADK Version**: Different ADK versions may have different streaming implementations
   - Our current version may use message-level streaming
   - Newer versions might support token-level streaming

2. **Backend Model**: Streaming behavior depends on the underlying model
   - Vertex AI Gemini models may stream differently than other backends
   - Token-level streaming may require specific model configuration

3. **Configuration**: Additional RunConfig settings may be needed
   - `StreamingMode.SSE` configuration
   - Model-specific streaming parameters

4. **Multi-Agent Architecture**: Our implementation uses sub-agents and Loop Agents
   - Complex agent workflows may aggregate responses before streaming
   - Sub-agent responses might be buffered

---

## ✅ Our Current Solution (Frontend Fix)

Since ADK sends accumulated text, we implemented a **frontend solution** that:

1. **Tracks Previous Text**: Maintains a `previousText` variable
2. **Calculates Delta**: Extracts only new text from each event
3. **Streams Incrementally**: Sends only new tokens to Vercel AI SDK

```typescript
let previousText = '';

if (currentText.startsWith(previousText)) {
  const newText = currentText.slice(previousText.length);
  controller.enqueue(encoder.encode(newText));
  previousText = currentText;
}
```

**Result**: ✅ **Works perfectly** - Provides ChatGPT-like incremental streaming

---

## 🔧 Potential Backend Improvements

### Option 1: Upgrade ADK Version (Recommended for Investigation)

Check if newer ADK versions support true token-level streaming:

```python
# In services/adk-python/pyproject.toml
[project.dependencies]
google-adk = ">=1.18.0"  # Current version, check for updates
```

**Action**: Review ADK changelog for streaming improvements

---

### Option 2: Configure RunConfig with StreamingMode

Add explicit streaming configuration to the agent:

```python
# In content_creator_agent/agent.py
from google.adk import RunConfig, StreamingMode

interactive_content_creator_agent = Agent(
    name="interactive_content_creator",
    model=config.worker_model,
    description="...",
    instruction="...",
    # ... existing config ...
)

# Configure run settings for streaming
run_config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    max_llm_calls=200,
)
```

**Note**: This may require passing `run_config` through the FastAPI app setup

---

### Option 3: Model-Specific Configuration

Configure Gemini model with streaming parameters:

```python
from google.genai import types

interactive_content_creator_agent = Agent(
    name="interactive_content_creator",
    model=config.worker_model,
    generate_content_config=types.GenerateContentConfig(
        # Streaming-optimized settings
        temperature=0.7,
        top_p=0.95,
        top_k=40,
    ),
    # ... rest of config ...
)
```

---

### Option 4: Check ADK get_fast_api_app Configuration

Review if additional parameters can be passed to `get_fast_api_app`:

```python
# In main_adk.py
app: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
    # Potential additional params to investigate:
    # streaming_mode=StreamingMode.SSE,
    # run_config=custom_run_config,
)
```

---

## 📊 Comparison: Current vs Ideal

| Aspect | Current (Accumulated Text) | Ideal (Token-Level) |
|--------|---------------------------|---------------------|
| **SSE Events** | Full text each time | Individual tokens |
| **Network Usage** | Higher (duplicate data) | Lower (only new tokens) |
| **Frontend Complexity** | Delta calculation needed | Direct streaming |
| **Latency** | Slightly higher | Lower |
| **User Experience** | ✅ Good (with fix) | ✅ Excellent (native) |

---

## 🎯 Recommendations

### Short-Term (Current State)
✅ **Keep the frontend solution** - It works perfectly and provides excellent UX
- ✅ Incremental streaming implemented
- ✅ ChatGPT-like experience
- ✅ Production-ready

### Medium-Term (Investigation)
🔍 **Research ADK token-level streaming**:
1. Check ADK Python version and changelog
2. Review ADK GitHub issues for streaming discussions
3. Test with different Gemini model configurations
4. Experiment with RunConfig and StreamingMode

### Long-Term (Optimization)
🚀 **If token-level streaming becomes available**:
1. Update ADK configuration
2. Simplify frontend implementation
3. Reduce network bandwidth
4. Improve perceived latency

---

## 📖 ADK Streaming Documentation Links

### Official Documentation
- **ADK API Server**: https://github.com/google/adk-docs/blob/main/docs/runtime/api-server.md
- **RunConfig**: https://github.com/google/adk-docs/blob/main/docs/runtime/runconfig.md
- **ADK Python Agents**: https://github.com/google/adk-python/blob/main/AGENTS.md

### Related Resources
- **ADK Samples**: https://github.com/google/adk-samples
- **Blog Writer Sample**: https://github.com/google/adk-samples/tree/main/python/agents/blog-writer
- **ADK Live (Bidirectional Streaming)**: Uses `runner.run_live(...)` for real-time audio/video

---

## 🧪 Testing Token-Level Streaming

### Test Script (To Be Created)

```python
# services/adk-python/test_streaming.py
"""
Test script to verify token-level streaming from ADK.
"""
import asyncio
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def test_token_streaming():
    agent = Agent(
        name="test_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant."
    )
    
    runner = Runner(
        app_name="test_app",
        agent=agent,
        session_service=InMemorySessionService()
    )
    
    message = types.Content(
        role='user',
        parts=[types.Part(text="Tell me a story about AI agents.")]
    )
    
    print("Testing streaming...")
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=message
    ):
        print(f"Event type: {type(event)}")
        print(f"Event content: {event}")
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"Text: {part.text}")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_token_streaming())
```

**Usage**:
```bash
cd services/adk-python
uv run python test_streaming.py
```

---

## 🔍 Investigation Checklist

- [ ] Check current `google-adk` version in `pyproject.toml`
- [ ] Review ADK Python changelog for streaming updates
- [ ] Test with `RunConfig(streaming_mode=StreamingMode.SSE)`
- [ ] Experiment with different Gemini model versions
- [ ] Check if sub-agents affect streaming behavior
- [ ] Test with simpler single-agent setup
- [ ] Review ADK GitHub issues for streaming discussions
- [ ] Compare behavior with official ADK samples

---

## 💡 Key Insights

### 1. ADK's Design Philosophy
ADK is designed to handle **multi-agent workflows** with function calling, which may require buffering responses from sub-agents before streaming to the client.

### 2. Vertex AI Streaming
Vertex AI Gemini models support token-level streaming, but ADK's abstraction layer may aggregate tokens into message-level events for easier handling of complex workflows.

### 3. Frontend vs Backend Streaming
- **Backend streaming**: ADK → FastAPI → SSE events
- **Frontend streaming**: SSE events → Delta calculation → Vercel AI SDK
- **Our approach**: Handle streaming transformation on frontend for maximum compatibility

---

## ✅ Conclusion

### Current State
Our **frontend solution** successfully provides incremental streaming by:
- Tracking accumulated text from ADK SSE events
- Calculating deltas (new text only)
- Streaming incremental updates to the UI

**Result**: ✅ **Production-ready** with excellent UX

### Future Investigation
Potential to improve by:
- Enabling true token-level streaming in ADK (if available)
- Simplifying frontend implementation
- Reducing network bandwidth
- Further optimizing perceived latency

### Recommendation
**Keep the current implementation** as it works excellently, while investigating ADK's token-level streaming capabilities for future optimization.

---

## 📚 Related Documentation

- `VERCEL_AI_SDK_IMPLEMENTATION.md` - Vercel AI SDK integration
- `STREAMING_FIX_SUMMARY.md` - Incremental streaming fix details
- `VERCEL_AI_SDK_TEST_SUCCESS.md` - Testing results
- `frontend/nextjs/app/api/chat/route.ts` - API route implementation

---

**Research Date**: January 2, 2026  
**Status**: ✅ Current solution working perfectly, future optimization opportunities identified

