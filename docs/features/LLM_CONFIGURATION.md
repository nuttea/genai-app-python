# LLM Configuration Feature

Dynamic provider, model, and parameter configuration for vote extraction.

## Overview

The application now supports configurable LLM providers, models, and generation parameters. This enables:
- **Experimentation**: Test different models and parameters
- **A/B Testing**: Compare extraction quality across models
- **Cost Optimization**: Choose models based on performance/cost tradeoffs
- **Future-proofing**: Easy addition of new providers (OpenAI, Anthropic)

## Features

### Backend API

#### 1. LLM Configuration Model

New `LLMConfig` Pydantic model in `app/models/vote_extraction.py`:

```python
class LLMConfig(BaseModel):
    provider: str = "vertex_ai"  # vertex_ai, openai, anthropic
    model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.1  # 0.0-2.0
    max_tokens: int = 8192  # Max output tokens
    top_p: float = 0.95  # Nucleus sampling
    top_k: int = 40  # Top-k sampling (Vertex AI)
```

#### 2. Models Listing Endpoint

**GET** `/api/v1/vote-extraction/models`

Returns available providers and models:

```json
{
  "providers": [
    {
      "name": "vertex_ai",
      "display_name": "Google Vertex AI",
      "models": [
        {
          "name": "gemini-2.0-flash-exp",
          "display_name": "Gemini 2.0 Flash (Experimental)",
          "context_window": 1048576,
          "max_output_tokens": 8192
        },
        {
          "name": "gemini-1.5-flash-002",
          "display_name": "Gemini 1.5 Flash",
          "context_window": 1048576,
          "max_output_tokens": 8192
        },
        {
          "name": "gemini-1.5-pro-002",
          "display_name": "Gemini 1.5 Pro",
          "context_window": 2097152,
          "max_output_tokens": 8192
        }
      ],
      "default_model": "gemini-2.0-flash-exp",
      "supported": true
    },
    {
      "name": "openai",
      "display_name": "OpenAI",
      "models": [...],
      "supported": false,
      "note": "Coming soon"
    },
    {
      "name": "anthropic",
      "display_name": "Anthropic",
      "models": [...],
      "supported": false,
      "note": "Coming soon"
    }
  ],
  "default_config": {
    "provider": "vertex_ai",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.1,
    "max_tokens": 8192,
    "top_p": 0.95,
    "top_k": 40
  }
}
```

#### 3. Updated Extract Endpoint

**POST** `/api/v1/vote-extraction/extract`

Now accepts optional `llm_config_json` form field:

```python
# Example request with custom config
files = [("files", open("form.jpg", "rb"))]
data = {
    "llm_config_json": json.dumps({
        "provider": "vertex_ai",
        "model": "gemini-1.5-pro-002",
        "temperature": 0.0,
        "max_tokens": 8192
    })
}
headers = {"X-API-Key": "your-api-key"}

response = requests.post(
    "http://api/api/v1/vote-extraction/extract",
    files=files,
    data=data,
    headers=headers
)
```

#### 4. Service Layer Updates

`VoteExtractionService.extract_from_images()` now accepts `llm_config` parameter:

```python
result = await vote_extraction_service.extract_from_images(
    image_files=image_files,
    image_filenames=image_filenames,
    llm_config=llm_config  # Optional
)
```

### Frontend (Streamlit)

#### Sidebar Configuration UI

New sidebar in Vote Extractor page with:

1. **Quick Toggle**
   - Checkbox to enable custom configuration
   - Shows current default when disabled

2. **Provider Selection**
   - Dropdown with supported providers
   - Filtered to show only working providers

3. **Model Selection**
   - Dropdown with available models for selected provider
   - Shows model display names (user-friendly)

4. **Advanced Parameters** (Expandable)
   - Temperature slider (0.0-2.0)
   - Max tokens input
   - Top P slider (0.0-1.0)
   - Top K input

5. **Status Display**
   - Current selection shown
   - Success message when custom config enabled

#### Screenshot

```
⚙️ LLM Configuration
Optional: Customize the AI model used for extraction

□ Use custom model configuration

ℹ️ Using default: gemini-2.0-flash-exp
   Temperature: 0.1
```

When enabled:

```
⚙️ LLM Configuration
Optional: Customize the AI model used for extraction

☑ Use custom model configuration

Provider: [Google Vertex AI ▼]
Model: [Gemini 2.0 Flash (Experimental) ▼]

🔧 Advanced Parameters ▶
   Temperature: 0.1
   Max Tokens: 8192
   Top P: 0.95
   Top K: 40

✅ Using: Gemini 2.0 Flash (Experimental)
```

## Usage Examples

### Example 1: Default Configuration

```python
# No config specified = use defaults
uploaded_files = [...]
result = process_extraction(uploaded_files)
# Uses: gemini-2.0-flash-exp, temp=0.1
```

### Example 2: Use Gemini Pro

```python
llm_config = {
    "provider": "vertex_ai",
    "model": "gemini-1.5-pro-002",
    "temperature": 0.0,
    "max_tokens": 8192
}
result = process_extraction(uploaded_files, llm_config)
```

### Example 3: Higher Temperature for Experiments

```python
llm_config = {
    "provider": "vertex_ai",
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.5,  # Higher temp
    "max_tokens": 8192
}
result = process_extraction(uploaded_files, llm_config)
```

## Datadog Integration

LLM configuration is automatically logged and tracked:

```python
logger.info(
    f"Extracting with LLM config: provider={llm_config.provider}, "
    f"model={llm_config.model}, temp={llm_config.temperature}"
)
```

In Datadog LLMObs:
- Model name appears in trace metadata
- Temperature and parameters visible in span tags
- Easy filtering by model: `model:gemini-1.5-pro-002`

## Future Enhancements

### Phase 1: OpenAI Support (Planned)
- Add OpenAI client initialization
- Support GPT-4o and GPT-4o-mini
- Handle different API format

### Phase 2: Anthropic Support (Planned)
- Add Anthropic client initialization
- Support Claude 3.5 models
- Map parameters appropriately

### Phase 3: Model Comparison UI
- Side-by-side results
- Quality metrics
- Cost comparison
- Performance benchmarks

### Phase 4: Auto-selection
- Quality-based routing
- Cost optimization
- Fallback on failure

## Testing

### Manual Testing

1. **Test Default Configuration**
   ```bash
   # Upload files without config
   curl -X POST http://localhost:8000/api/v1/vote-extraction/extract \
     -H "X-API-Key: your-key" \
     -F "files=@form.jpg"
   ```

2. **Test Custom Configuration**
   ```bash
   curl -X POST http://localhost:8000/api/v1/vote-extraction/extract \
     -H "X-API-Key: your-key" \
     -F "files=@form.jpg" \
     -F 'llm_config_json={"model":"gemini-1.5-pro-002","temperature":0.0}'
   ```

3. **Test Models Endpoint**
   ```bash
   curl http://localhost:8000/api/v1/vote-extraction/models
   ```

### Integration Tests

Add tests for:
- Config validation
- Provider switching
- Parameter validation
- Default config fallback

## Performance Considerations

### Model Selection

| Model | Speed | Quality | Cost | Use Case |
|-------|-------|---------|------|----------|
| gemini-2.0-flash-exp | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | Production (fast) |
| gemini-1.5-flash-002 | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | Stable alternative |
| gemini-1.5-pro-002 | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰 | Complex forms |

### Temperature Guidelines

- **0.0-0.2**: Factual extraction (recommended)
- **0.3-0.7**: Moderate creativity
- **0.8-2.0**: High creativity (not recommended for structured data)

## Troubleshooting

### Config Not Applied

**Symptom**: Custom config ignored, uses default

**Solutions**:
1. Check JSON format in `llm_config_json`
2. Verify provider is supported
3. Check backend logs for parsing errors

### Invalid Model Error

**Symptom**: Error message about unsupported model

**Solutions**:
1. Verify model name matches available models
2. Check provider spelling
3. Confirm model is still available

### Timeout Issues

**Symptom**: Request times out with certain configs

**Solutions**:
1. Reduce `max_tokens` value
2. Use faster model (Flash vs Pro)
3. Increase client timeout

## API Reference

### LLMConfig Schema

```typescript
{
  provider: "vertex_ai" | "openai" | "anthropic",
  model: string,
  temperature: number,  // 0.0-2.0
  max_tokens: number,   // 1-32768
  top_p?: number,       // 0.0-1.0
  top_k?: number        // 1-100
}
```

### Models Endpoint Response

```typescript
{
  providers: Array<{
    name: string,
    display_name: string,
    models: Array<{
      name: string,
      display_name: string,
      context_window: number,
      max_output_tokens: number
    }>,
    default_model: string,
    supported: boolean,
    note?: string
  }>,
  default_config: LLMConfig
}
```

## Best Practices

1. **Start with Defaults**
   - Default config is optimized for accuracy
   - Only customize when needed

2. **Low Temperature for Extraction**
   - Keep temperature ≤ 0.2 for structured data
   - Higher temps may cause inconsistent output

3. **Model Selection**
   - Flash models: Fast, good for production
   - Pro models: Better for complex/unclear forms

4. **Parameter Tuning**
   - Test changes on sample data first
   - Monitor quality metrics in Datadog
   - Document successful configurations

5. **Datadog Tags**
   - Tag experiments with model/config
   - Compare results across configurations
   - Track cost and performance

---

**Ready for experimentation and evaluation!** 🚀
