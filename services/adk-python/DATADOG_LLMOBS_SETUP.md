# Datadog LLM Observability Setup

## Overview

Integrated [Datadog LLM Observability](https://docs.datadoghq.com/llm_observability/instrumentation/sdk/?tab=python) into the ADK Content Creator service to automatically track and monitor all LLM interactions.

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Datadog API Key (REQUIRED for LLMObs)
DD_API_KEY=your-datadog-api-key

# Datadog Site
DD_SITE=datadoghq.com

# Datadog Environment
DD_ENV=development

# LLM Observability Configuration
DD_LLMOBS_ENABLED=true
DD_LLMOBS_ML_APP=datadog-content-creator
DD_LLMOBS_AGENTLESS=true
```

### Settings (`app/config.py`)

```python
class Settings(BaseSettings):
    # Datadog LLM Observability
    dd_llmobs_enabled: bool = Field(default=True)
    dd_llmobs_ml_app: str = Field(default="datadog-content-creator")
    dd_llmobs_agentless: bool = Field(default=True)
    dd_api_key: Optional[str] = Field(default=None)
    dd_site: str = Field(default="datadoghq.com")
```

## Implementation

### 1. Initialize LLMObs with Auto-Instrumentation (`app/main.py`)

**All LLM integrations are automatically enabled by default!** No manual patching required.

```python
from ddtrace.llmobs import LLMObs

# Initialize on startup with auto-instrumentation
# Automatically patches: google_adk, google_genai, vertexai, langchain, openai, etc.
if settings.dd_llmobs_enabled and settings.dd_api_key:
    LLMObs.enable(
        ml_app=settings.dd_llmobs_ml_app,
        api_key=settings.dd_api_key,
        site=settings.dd_site,
        agentless_enabled=settings.dd_llmobs_agentless,
        env=settings.dd_env,
        service=settings.dd_service,
        # integrations_enabled=True by default (auto-instrumentation)
    )
```

Datadog automatically instruments **23 integrations** including:
- ✅ `google_adk` - Google ADK
- ✅ `google_genai` - Gemini API
- ✅ `vertexai` - Vertex AI
- ✅ `langchain`, `langgraph` - LangChain frameworks
- ✅ `openai`, `anthropic` - Other LLM providers
- ✅ `fastapi`, `requests`, `httpx` - HTTP frameworks
- ✅ And 16 more...

See [Datadog Auto-Instrumentation docs](https://docs.datadoghq.com/llm_observability/instrumentation/auto_instrumentation/?tab=python) for the full list.

### 2. Trace LLM Calls (`app/services/gemini_service.py`)

```python
from ddtrace.llmobs import LLMObs

async def generate_content(self, prompt: str, ...):
    # Start LLMObs span
    llm_span = LLMObs.llm(
        model_name=self.model,
        name="gemini.generate_content",
        model_provider="google",
        ml_app=settings.dd_llmobs_ml_app,
    )
    
    # Annotate with input
    LLMObs.annotate(
        span=llm_span,
        input_data=prompt,
        parameters={
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )
    
    # Generate content
    result = await self._generate(...)
    
    # Annotate with output
    LLMObs.annotate(
        span=llm_span,
        output_data=result[:1000],  # Truncate for observability
        metadata={"output_length": len(result)},
    )
    
    llm_span.finish()
    return result
```

### 3. Flush on Shutdown (`app/main.py`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    
    # Flush LLMObs data before shutdown
    if settings.dd_llmobs_enabled and settings.dd_api_key:
        LLMObs.flush()
```

## What Gets Tracked

### Automatic Tracking

- ✅ **Model Name**: `gemini-2.5-flash`
- ✅ **Model Provider**: `google`
- ✅ **Input Prompts**: Full prompt text
- ✅ **Output**: Generated content (truncated to 1000 chars)
- ✅ **Parameters**: Temperature, max_tokens, media files count
- ✅ **Metadata**: Output length, model info
- ✅ **Errors**: Exceptions and error messages
- ✅ **Latency**: Time taken for generation
- ✅ **Session ID**: Can be set from request context

### Span Types

According to [Datadog LLMObs SDK docs](https://docs.datadoghq.com/llm_observability/instrumentation/sdk/?tab=python):

1. **LLM Calls** (`LLMObs.llm()`) - Direct model interactions
2. **Workflows** (`LLMObs.workflow()`) - Multi-step processes
3. **Agents** (`LLMObs.agent()`) - Autonomous decision-making
4. **Tools** (`LLMObs.tool()`) - External tool calls
5. **Tasks** (`LLMObs.task()`) - Processing operations
6. **Embeddings** (`LLMObs.embedding()`) - Vector embeddings
7. **Retrievals** (`LLMObs.retrieval()`) - RAG retrievals

## Usage Examples

### Current Implementation

```python
# Automatically tracked when calling GeminiService
gemini_service = GeminiService()
result = await gemini_service.generate_content(
    prompt="Create a blog post about Datadog",
    temperature=0.7,
    max_tokens=8192,
)
# LLMObs automatically captures input, output, latency, parameters
```

### Future: Workflow Tracking

```python
from ddtrace.llmobs.decorators import workflow

@workflow(name="blog_post_generation")
async def generate_blog_post(request: BlogPostRequest):
    # Upload files
    media_uris = await upload_files(request.files)
    
    # Generate content
    content = await gemini_service.generate_content(...)
    
    # Post-process
    result = await format_blog_post(content)
    
    return result
```

### Future: Agent Tracking

```python
from ddtrace.llmobs.decorators import agent

@agent(name="content_creator_agent")
async def run_content_creator(user_input: str):
    # Agent decides what to do
    action = await decide_action(user_input)
    
    # Execute action
    result = await execute_action(action)
    
    return result
```

## Verification

### 1. Check Logs

```bash
docker logs genai-content-creator | grep -i llmobs
```

Expected output:
```
INFO - Datadog LLM Observability enabled: ml_app=datadog-content-creator, site=datadoghq.com, agentless=True
```

### 2. Test Generation

```bash
curl -X POST http://localhost:8002/api/v1/generate/blog-post \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test LLMObs",
    "description": "Testing Datadog LLM Observability",
    "style": "professional",
    "target_audience": "developers"
  }'
```

### 3. View in Datadog

1. Go to **LLM Observability** in Datadog UI
2. Filter by ML App: `datadog-content-creator`
3. View traces with:
   - Model: `gemini-2.5-flash`
   - Provider: `google`
   - Input prompts
   - Output content
   - Latency metrics
   - Parameters

## Agentless Mode

**Agentless mode** (`agentless_enabled=True`) means:

- ✅ **No Datadog Agent required** - Sends data directly to Datadog API
- ✅ **Simpler setup** - Just need `DD_API_KEY`
- ✅ **Cloud-friendly** - Perfect for Cloud Run, Lambda, etc.
- ✅ **Automatic batching** - SDK batches and sends data efficiently

**Note**: For production with high volume, consider using Datadog Agent for better performance.

## Cost Monitoring

LLMObs can track token usage and costs:

```python
# Future enhancement
LLMObs.annotate(
    span=llm_span,
    metrics={
        "input_tokens": 150,
        "output_tokens": 2500,
        "total_tokens": 2650,
    },
)
```

## Troubleshooting

### Issue: LLMObs not initializing

**Check 1**: Verify `DD_API_KEY` is set
```bash
docker exec genai-content-creator env | grep DD_API_KEY
```

**Check 2**: Check logs for initialization
```bash
docker logs genai-content-creator | grep -i "llm observability"
```

**Check 3**: Verify settings
```bash
curl http://localhost:8002/info | jq '.llmobs'
```

### Issue: Spans not appearing in Datadog

**Solution 1**: Ensure `DD_LLMOBS_ENABLED=true` in `.env`

**Solution 2**: Check API key is valid

**Solution 3**: Verify agentless mode is enabled:
```python
dd_llmobs_agentless: bool = Field(default=True)
```

**Solution 4**: Force flush (for testing):
```python
LLMObs.flush()  # Blocks until data is sent
```

### Issue: Missing input/output data

**Solution**: Check span annotations in `gemini_service.py`:
```python
LLMObs.annotate(
    span=llm_span,
    input_data=prompt,  # Must be set
    output_data=result,  # Must be set
)
```

## Production Deployment

### Cloud Run

Environment variables are automatically loaded from `.env` or set via:

```bash
gcloud run services update adk-content-creator \
  --set-env-vars="DD_LLMOBS_ENABLED=true" \
  --set-env-vars="DD_LLMOBS_ML_APP=datadog-content-creator" \
  --set-env-vars="DD_LLMOBS_AGENTLESS=true" \
  --set-secrets="DD_API_KEY=datadog-api-key:latest"
```

### GKE

Add to Kubernetes deployment:

```yaml
env:
  - name: DD_LLMOBS_ENABLED
    value: "true"
  - name: DD_LLMOBS_ML_APP
    value: "datadog-content-creator"
  - name: DD_LLMOBS_AGENTLESS
    value: "true"
  - name: DD_API_KEY
    valueFrom:
      secretKeyRef:
        name: datadog-secret
        key: api-key
```

## Benefits

### Observability

- 📊 **Track all LLM calls** - Every Gemini API call is traced
- 🔍 **Debug issues** - See exact prompts and responses
- ⚡ **Monitor latency** - Identify slow generations
- 💰 **Cost tracking** - Monitor token usage (future)
- 🎯 **Session tracking** - Group related requests

### Performance

- 📈 **Identify bottlenecks** - See which prompts are slow
- 🔧 **Optimize prompts** - Compare different prompt strategies
- 📉 **Reduce costs** - Find inefficient token usage
- ✅ **Quality monitoring** - Track output quality over time

### Compliance

- 📝 **Audit trail** - Full history of LLM interactions
- 🔒 **Security** - Monitor for sensitive data in prompts
- 📊 **Reporting** - Generate usage reports
- ✅ **Compliance** - Meet regulatory requirements

## Next Steps

1. ✅ Add `DD_API_KEY` to your `.env` file
2. ✅ Restart service: `docker-compose restart content-creator`
3. 🔜 Test generation and verify spans in Datadog
4. 🔜 Add workflow tracking for multi-step processes
5. 🔜 Add agent tracking for ADK agents
6. 🔜 Enable cost tracking with token counts

## References

- **Datadog LLMObs SDK**: https://docs.datadoghq.com/llm_observability/instrumentation/sdk/?tab=python
- **LLMObs Overview**: https://docs.datadoghq.com/llm_observability/
- **Python SDK Docs**: https://ddtrace.readthedocs.io/en/stable/integrations.html#llm-observability

---

**Status**: ✅ Configured and Ready  
**Date**: December 30, 2025  
**Next**: Add `DD_API_KEY` to `.env` and test

