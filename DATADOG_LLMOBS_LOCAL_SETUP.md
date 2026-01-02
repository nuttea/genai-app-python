# Datadog LLM Observability - Local Docker Setup

## ✅ Status

**LLMObs is now ENABLED by default** in local Docker Compose for both services:
- ✅ **FastAPI Backend** - Vote Extractor (Gemini LLM calls)
- ✅ **ADK Python Service** - Multi-Agent Content Creator (Google ADK + Gemini)

---

## 🔧 What Was Changed

### 1. **FastAPI Backend** (`docker-compose.yml`)

**BEFORE** (Disabled):
```yaml
- DD_LLMOBS_ML_APP=${DD_LLMOBS_ML_APP:-}        # Empty
- DD_LLMOBS_ENABLED=${DD_LLMOBS_ENABLED:-0}     # Disabled (0)
```

**AFTER** (Enabled):
```yaml
# LLM Observability Configuration
- DD_LLMOBS_ENABLED=${DD_LLMOBS_ENABLED:-1}                        # ✅ ENABLED (1)
- DD_LLMOBS_ML_APP=${DD_LLMOBS_ML_APP:-fastapi-vote-extractor}     # ✅ ML App name
- DD_LLMOBS_AGENTLESS_ENABLED=${DD_LLMOBS_AGENTLESS_ENABLED:-1}    # ✅ Agentless mode
```

### 2. **ADK Python Service** (`docker-compose.yml`)

**BEFORE** (Missing):
```yaml
# Only basic APM tracing - NO LLMObs configuration
- DD_TRACE_ENABLED=${DD_TRACE_ENABLED:-1}
```

**AFTER** (Added):
```yaml
# LLM Observability Configuration
- DD_LLMOBS_ENABLED=${DD_LLMOBS_ENABLED:-1}                                # ✅ ENABLED (1)
- DD_LLMOBS_ML_APP=${DD_LLMOBS_ML_APP:-adk-python-content-creator}         # ✅ ML App name
- DD_LLMOBS_AGENTLESS_ENABLED=${DD_LLMOBS_AGENTLESS_ENABLED:-1}            # ✅ Agentless mode
```

---

## 🚀 How to Enable LLMObs

### Prerequisites

1. **Datadog API Key** - Get from [Datadog](https://app.datadoghq.com/organization-settings/api-keys)
2. **Datadog Account** - Free trial or paid account

### Method 1: Environment Variables (Recommended)

**Create or update `.env` file in project root**:

```bash
# Datadog Configuration
DD_API_KEY=your_datadog_api_key_here
DD_SITE=datadoghq.com                    # or datadoghq.eu, us3.datadoghq.com, etc.
DD_ENV=development

# Optional: Override defaults
# DD_LLMOBS_ENABLED=1                     # Already enabled by default
# DD_LLMOBS_ML_APP=fastapi-vote-extractor # FastAPI backend ML app name
# DD_LLMOBS_ML_APP=adk-python-content-creator # ADK service ML app name
```

### Method 2: Export Environment Variables

**In your terminal** (before running `docker-compose up`):

```bash
export DD_API_KEY=your_datadog_api_key_here
export DD_SITE=datadoghq.com
export DD_ENV=development
```

### Method 3: Pass Inline

```bash
DD_API_KEY=your_key docker-compose up -d
```

---

## 🔍 Verify LLMObs is Working

### 1. **Check Container Logs**

**FastAPI Backend**:
```bash
docker logs genai-fastapi-backend --tail 50 | grep -i llmobs
```

**Expected Output**:
```
✅ Datadog LLM Observability enabled: ml_app=fastapi-vote-extractor
```

**ADK Python Service**:
```bash
docker logs genai-adk-python --tail 50 | grep -i llmobs
```

**Expected Output**:
```
✅ Datadog LLM Observability enabled: ml_app=adk-python-content-creator
```

### 2. **Check Datadog Dashboard**

1. Go to [Datadog LLM Observability](https://app.datadoghq.com/llm/)
2. Select **Applications** dropdown
3. You should see:
   - `fastapi-vote-extractor` (Vote Extractor service)
   - `adk-python-content-creator` (Content Creator service)

### 3. **Generate LLM Traffic**

**Test Vote Extractor**:
```bash
# Visit: http://localhost:3000/vote-extractor
# Upload an election document and extract votes
```

**Test Content Creator**:
```bash
# Visit: http://localhost:3000/content-creator/interactive
# Create a blog post or video script
```

### 4. **View Traces in Datadog**

Within 1-2 minutes, you should see:
- **LLM Spans** - Individual LLM API calls (input, output, tokens, latency)
- **Workflows** - Multi-step agent workflows (planning → writing → editing)
- **Metrics** - Token usage, latency, error rates
- **Costs** - Estimated LLM costs based on token usage

---

## 📊 LLMObs Features Enabled

### 1. **Automatic Instrumentation**
- ✅ Google Gemini API calls auto-traced
- ✅ Google ADK agent workflows auto-traced
- ✅ Input/output prompts captured
- ✅ Token counts tracked
- ✅ Latency metrics collected

### 2. **ML App Tracking**

**FastAPI Backend** (`ml_app=fastapi-vote-extractor`):
- Vote extraction LLM calls
- Document analysis
- Structured output generation
- Error tracking

**ADK Python Service** (`ml_app=adk-python-content-creator`):
- Multi-agent workflows
- Blog planning → writing → editing
- Video script generation
- Social media content creation
- Image generation (Gemini 3 Pro Image)

### 3. **Agentless Mode**
- ✅ No local Datadog Agent required
- ✅ Direct API submission to Datadog
- ✅ Perfect for Docker/Cloud Run
- ✅ Simplified local development

---

## 🎯 LLMObs Configuration Options

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DD_API_KEY` | *(required)* | Datadog API key |
| `DD_SITE` | `datadoghq.com` | Datadog site (US1) |
| `DD_ENV` | `development` | Environment name |
| `DD_LLMOBS_ENABLED` | `1` | Enable LLMObs (1=on, 0=off) |
| `DD_LLMOBS_ML_APP` | Service-specific | ML application name |
| `DD_LLMOBS_AGENTLESS_ENABLED` | `1` | Use agentless mode |
| `DD_TRACE_SAMPLE_RATE` | `1.0` | APM trace sample rate (100%) |

### Datadog Sites

| Region | Site Value |
|--------|------------|
| US1 (default) | `datadoghq.com` |
| US3 | `us3.datadoghq.com` |
| US5 | `us5.datadoghq.com` |
| EU1 | `datadoghq.eu` |
| AP1 | `ap1.datadoghq.com` |
| US1-FED | `ddog-gov.com` |

---

## 🔧 Troubleshooting

### Issue 1: "LLMObs not enabled" in logs

**Cause**: Missing `DD_API_KEY`

**Solution**:
```bash
# Check if DD_API_KEY is set
docker exec genai-adk-python env | grep DD_API_KEY

# If empty, set it in .env file or export it
export DD_API_KEY=your_key_here
docker-compose up -d
```

### Issue 2: No traces in Datadog

**Possible Causes**:
1. Wrong API key
2. Wrong Datadog site (US vs EU)
3. LLMObs not enabled

**Solutions**:
```bash
# 1. Verify API key is valid
curl -X GET "https://api.datadoghq.com/api/v1/validate" \
  -H "DD-API-KEY: ${DD_API_KEY}"

# 2. Check Datadog site matches your account
echo $DD_SITE

# 3. Restart services with fresh config
docker-compose down
docker-compose up -d

# 4. Check logs for errors
docker logs genai-adk-python --tail 100 | grep -i error
```

### Issue 3: "Failed to enable Datadog LLM Observability"

**Cause**: Network issues or invalid configuration

**Solution**:
```bash
# Check container network access
docker exec genai-adk-python curl -I https://api.datadoghq.com

# Check detailed error in logs
docker logs genai-adk-python --tail 200
```

---

## 🎓 Best Practices

### 1. **Development vs Production**

**Development** (Docker Compose):
```yaml
- DD_ENV=development
- DD_LLMOBS_ENABLED=1              # Always on for testing
- DD_TRACE_SAMPLE_RATE=1.0         # 100% sampling
```

**Production** (Cloud Run):
```yaml
- DD_ENV=production
- DD_LLMOBS_ENABLED=1              # Always on
- DD_TRACE_SAMPLE_RATE=0.1         # 10% sampling (optional)
```

### 2. **ML App Naming**

Use descriptive names that reflect the application purpose:
- ✅ `fastapi-vote-extractor` - Clear purpose
- ✅ `adk-python-content-creator` - Clear purpose
- ❌ `my-app` - Too generic
- ❌ `test` - Not descriptive

### 3. **Security**

**Never commit `DD_API_KEY` to git**:
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

**Use environment-specific keys**:
- Development: Read-only API key
- Production: Full-access API key

### 4. **Monitoring Costs**

LLMObs tracks token usage and estimates costs:
```python
# View in Datadog:
# LLM Observability → Applications → Costs Dashboard
# - Token usage by model
# - Estimated costs per request
# - Cost trends over time
```

---

## 📈 What You'll See in Datadog

### LLM Observability Dashboard

**Applications**:
- `fastapi-vote-extractor`
- `adk-python-content-creator`

**Traces** (examples):
```
fastapi-vote-extractor
├── POST /api/v1/extract_votes
│   └── llm.generate_content (gemini-2.5-flash)
│       ├── input_tokens: 1,245
│       ├── output_tokens: 387
│       ├── latency: 2.3s
│       └── cost: $0.0012

adk-python-content-creator
├── POST /run_sse
│   ├── agent: interactive_content_creator
│   ├── workflow: blog_creation
│   ├── sub_agent: robust_blog_planner (llm call)
│   ├── sub_agent: robust_blog_writer (llm call)
│   ├── sub_agent: blog_editor_sub_agent (llm call)
│   └── total_tokens: 8,932
```

**Metrics**:
- Request volume
- Token usage (input/output)
- Latency (p50, p95, p99)
- Error rates
- Cost estimates

---

## 🚀 Next Steps

1. **Start Services**:
   ```bash
   docker-compose up -d
   ```

2. **Verify LLMObs is Enabled**:
   ```bash
   docker logs genai-adk-python --tail 50 | grep -i llmobs
   docker logs genai-fastapi-backend --tail 50 | grep -i llmobs
   ```

3. **Generate Traffic**:
   - Visit http://localhost:3000/vote-extractor
   - Visit http://localhost:3000/content-creator/interactive

4. **View in Datadog**:
   - Go to https://app.datadoghq.com/llm/
   - Select your ML applications
   - Explore traces, metrics, and costs

---

## 📚 Documentation Links

- [Datadog LLM Observability](https://docs.datadoghq.com/llm_observability/)
- [Python Tracing](https://docs.datadoghq.com/tracing/setup_overview/setup/python/)
- [LLMObs SDK](https://docs.datadoghq.com/llm_observability/setup/)
- [Agentless Mode](https://docs.datadoghq.com/tracing/trace_collection/dd_libraries/python/#agentless-mode)

---

## ✅ Summary

**Before**:
- ❌ FastAPI Backend: LLMObs disabled (`DD_LLMOBS_ENABLED=0`)
- ❌ ADK Python Service: No LLMObs configuration

**After**:
- ✅ FastAPI Backend: LLMObs enabled by default (`DD_LLMOBS_ENABLED=1`)
- ✅ ADK Python Service: LLMObs enabled with full configuration
- ✅ Both services: Agentless mode for easy local dev
- ✅ Clear ML app names for easy identification

**To Enable**: Just add `DD_API_KEY` to your `.env` file and restart services!

---

**Created**: January 2, 2026  
**Status**: ✅ Production Ready  
**Services**: FastAPI Backend, ADK Python Service

