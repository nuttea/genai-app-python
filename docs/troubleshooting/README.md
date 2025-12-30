# Troubleshooting Guides

This directory contains troubleshooting guides for common issues and their solutions.

## 📚 Guides

### JSON Parsing Errors

**[TROUBLESHOOTING_MAX_TOKENS.md](./TROUBLESHOOTING_MAX_TOKENS.md)**
- **Issue:** `Invalid extraction response: Unterminated string`
- **Cause:** `max_tokens` limit too low causing JSON truncation
- **Solution:** Increased default from 8,192 to 16,384 tokens
- **Impact:** Now supports 10+ page documents reliably

**Quick Fix:**
```python
# Increase max_tokens in frontend or config
max_tokens = 16384  # Default
max_tokens = 32768  # For large documents
max_tokens = 65536  # Maximum (Gemini 2.5 Flash)
```

### Recent Fixes

**[FIX_SUMMARY.md](./FIX_SUMMARY.md)**
- Summary of the max_tokens fix
- Before/after comparison
- Testing instructions

## 🔍 Common Issues

### 1. Streamlit Secrets Error (Cloud Run)
**Symptoms:**
- `StreamlitSecretNotFoundError: No secrets found`
- "Valid paths for a secrets.toml file..." error
- App crashes on Cloud Run startup

**Solution:** → [STREAMLIT_SECRETS_CLOUD_RUN.md](./STREAMLIT_SECRETS_CLOUD_RUN.md)

### 2. Server Error 500 - JSON Parsing
**Symptoms:**
- "Unterminated string" errors
- "Expecting delimiter" errors
- Truncated JSON responses

**Solution:** → [TROUBLESHOOTING_MAX_TOKENS.md](./TROUBLESHOOTING_MAX_TOKENS.md)

### 3. Model Listing Returns Empty
**Symptoms:**
- `client.models.list()` returns 0 models
- Models work for inference but not listing

**Solution:** → [../investigations/MODELS_API_FINDINGS.md](../investigations/MODELS_API_FINDINGS.md)

### 4. Docker Startup Errors (Local Dev)
**Symptoms:**
- "datadog-init: no such file or directory"
- Container fails to start locally

**Solution:** → [../reference/DOCKER_FIX_LOCAL_DEV.md](../reference/DOCKER_FIX_LOCAL_DEV.md)

## 📊 Capacity Guidelines

| Document Size | Recommended max_tokens |
|--------------|----------------------|
| 1-2 pages | 8,192 (may work) |
| 3-4 pages | 16,384 (default) |
| 5-6 pages | 16,384 - 24,576 |
| 7-10 pages | 24,576 - 32,768 |
| 11+ pages | 32,768 - 65,536 |

## 🆘 Getting Help

1. **Check Logs:**
   ```bash
   docker logs genai-fastapi-backend --tail 100
   ```

2. **Verify Backend Health:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test Configuration:**
   ```bash
   python scripts/tests/test_dynamic_models.py
   ```

## 🔗 Related Documentation

- [LLM Configuration](../features/LLM_CONFIGURATION.md) - Adjusting model parameters
- [Reference Docs](../reference/) - Implementation details
- [Monitoring](../monitoring/) - Datadog observability

---

**Last Updated:** 2024-12-29
