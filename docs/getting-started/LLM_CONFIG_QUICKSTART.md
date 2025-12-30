# LLM Configuration Quick Start

Quick guide to using custom LLM models and parameters for vote extraction.

## 🎯 What You Can Configure

- **Provider**: Google Vertex AI (OpenAI/Anthropic coming soon)
- **Model**: Different Gemini models (Flash, Pro, 1.5, 2.0)
- **Temperature**: 0.0 (deterministic) to 2.0 (creative)
- **Max Tokens**: Output length limit
- **Top P / Top K**: Advanced sampling parameters

## 🚀 Quick Start (Frontend)

### 1. Enable Custom Config

In Streamlit sidebar:
1. Check ☑ **"Use custom model configuration"**
2. Select provider and model
3. Adjust parameters if needed
4. Upload files and extract

### 2. Use Different Model

```
Provider: Google Vertex AI
Model: Gemini 1.5 Pro ← Choose here
```

### 3. Adjust Temperature

```
🔧 Advanced Parameters
Temperature: 0.0 ← Lower = more consistent
```

## 💻 Quick Start (API)

### Default Configuration (Recommended)

```bash
curl -X POST http://api/api/v1/vote-extraction/extract \
  -H "X-API-Key: your-key" \
  -F "files=@form.jpg"
```

### Custom Model

```bash
curl -X POST http://api/api/v1/vote-extraction/extract \
  -H "X-API-Key: your-key" \
  -F "files=@form.jpg" \
  -F 'llm_config_json={"model":"gemini-1.5-pro-002","temperature":0.0}'
```

### Full Configuration

```bash
curl -X POST http://api/api/v1/vote-extraction/extract \
  -H "X-API-Key: your-key" \
  -F "files=@form.jpg" \
  -F 'llm_config_json={
    "provider": "vertex_ai",
    "model": "gemini-1.5-pro-002",
    "temperature": 0.1,
    "max_tokens": 8192,
    "top_p": 0.95,
    "top_k": 40
  }'
```

## 📋 Available Models

### Vertex AI (Supported ✅)

Models are fetched dynamically from [Gemini API](https://ai.google.dev/api/models):

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| **gemini-2.5-flash** | ⚡⚡⚡ | ⭐⭐⭐ | **Default - Fast & Accurate** |
| gemini-2.0-flash-exp | ⚡⚡⚡ | ⭐⭐⭐ | Experimental features |
| gemini-1.5-flash-002 | ⚡⚡⚡ | ⭐⭐⭐ | Stable version |
| gemini-1.5-pro-002 | ⚡⚡ | ⭐⭐⭐⭐ | Complex forms |

The full list is fetched automatically from Google's API.

### Coming Soon

- **OpenAI**: GPT-4o, GPT-4o-mini
- **Anthropic**: Claude 3.5 Sonnet, Haiku

## 🎨 Parameter Guide

### Temperature

```
0.0  ━━━━━━━━━━━ ← Default (fully deterministic, exact same output)
0.1  ━━━━━━━━━  Slight variation
0.5  ━━━━━      Moderate creativity
1.0  ━━━        High variation
2.0  ━          Random (not recommended)
```

**Recommendation**: Use 0.0 (default) for structured data extraction to ensure consistency

### Max Tokens

```
1024   = Short responses
4096   = Medium responses
8192   = Default (recommended)
16384+ = Very long outputs
```

### Top P (Nucleus Sampling)

```
0.9 = More focused
0.95 = Default (balanced)
1.0 = Full diversity
```

### Top K

```
20 = Very focused
40 = Default (balanced)
100 = Maximum diversity
```

## 🧪 Common Use Cases

### Experiment: Compare Models

```python
# Test 1: Flash 2.5 (default)
config_flash = {"model": "gemini-2.5-flash", "temperature": 0.0}
result1 = extract(files, config_flash)

# Test 2: Pro
config_pro = {"model": "gemini-1.5-pro-002", "temperature": 0.0}
result2 = extract(files, config_pro)

# Compare quality in Datadog
```

### Experiment: Temperature Sweep

```python
for temp in [0.0, 0.1, 0.2, 0.5]:
    config = {"model": "gemini-2.5-flash", "temperature": temp}
    result = extract(files, config)
    # Compare consistency
```

### Production: Optimized Config (Default)

```python
config = {
    "provider": "vertex_ai",
    "model": "gemini-2.5-flash",  # Latest stable, fast
    "temperature": 0.0,  # Fully deterministic
    "max_tokens": 8192,  # Sufficient
    "top_p": 0.95,  # Default
    "top_k": 40  # Default
}
```

## 📊 View in Datadog

### Filter by Model

```
service:genai-fastapi-backend model:gemini-1.5-pro-002
```

### Compare Configurations

```
Tags:
- model: gemini-2.0-flash-exp
- model: gemini-1.5-pro-002

Metric: extraction_quality
```

## ⚡ API Endpoints

### List Available Models

```bash
curl http://api/api/v1/vote-extraction/models
```

**Response**: All providers, models, and defaults

### Extract with Config

```bash
POST /api/v1/vote-extraction/extract
- files: multipart/form-data
- llm_config_json: optional JSON string
```

## 🔧 Troubleshooting

### Config Not Applied?

✅ Check JSON format
✅ Verify model name spelling
✅ Ensure provider is "vertex_ai"
✅ Check backend logs

### Timeout?

✅ Use Flash model (faster)
✅ Reduce max_tokens
✅ Increase client timeout

### Inconsistent Results?

✅ Lower temperature (0.0-0.1)
✅ Use same model consistently
✅ Check for form quality issues

## 📚 Full Documentation

See `docs/features/LLM_CONFIGURATION.md` for:
- Complete API reference
- All configuration options
- Best practices
- Performance comparison
- Integration examples

## 🎯 Next Steps

1. **Start Simple**: Use default config
2. **Experiment**: Try different models in sidebar
3. **Evaluate**: Compare results in Datadog
4. **Optimize**: Choose best config for your use case
5. **Automate**: Implement A/B testing with evaluations

---

**Total setup time: ~2 minutes to first custom extraction!** ⚡
