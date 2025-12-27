# 🔐 API Key Setup - Quick Start

Enable API key authentication in 2 minutes!

## Why API Keys?

✅ **Security** - Protect your backend from unauthorized access
✅ **Cost Control** - Prevent abuse and unexpected charges
✅ **Usage Tracking** - Know who's using your API
✅ **Production Ready** - Essential for public deployments

## 2-Minute Setup

### Local Development

```bash
# 1. Generate API key
export API_KEY=$(openssl rand -hex 32)
echo "API Key: $API_KEY"

# 2. Configure backend
cat >> .env <<EOF
API_KEY=${API_KEY}
API_KEY_REQUIRED=true
EOF

# 3. Configure frontend
cat > frontend/streamlit/.streamlit/secrets.toml <<EOF
API_BASE_URL = "http://fastapi-backend:8000"
API_KEY = "${API_KEY}"
EOF

# 4. Restart
docker-compose down
docker-compose up -d
```

### Cloud Run

```bash
# 1. Setup API key in Secret Manager
cd infra/cloud-run
export API_KEY=$(openssl rand -hex 32)
./setup-api-key.sh

# Save your API key!
echo "Your API Key: $API_KEY"

# 2. Deploy with API key required
export API_KEY_REQUIRED=true
./deploy-backend.sh
./deploy-frontend.sh
```

## Test It

```bash
# Without API key (should fail)
curl https://your-backend.run.app/api/v1/vote-extraction/health

# With API key (should succeed)
curl -H "X-API-Key: your-api-key" \
  https://your-backend.run.app/api/v1/vote-extraction/health
```

## Configuration Modes

### Mode 1: Open Access (Default)
```bash
API_KEY_REQUIRED=false
# or don't set API_KEY at all
```
- No authentication
- Good for: Development, internal use

### Mode 2: API Key Protected
```bash
API_KEY=your-secure-key-here
API_KEY_REQUIRED=true
```
- API key required for all endpoints
- Good for: Production, public deployment

## Using API Keys

### In Streamlit (Automatic)
```toml
# .streamlit/secrets.toml
API_KEY = "your-api-key"
```

### In curl
```bash
curl -H "X-API-Key: your-api-key" \
  https://api.example.com/api/v1/endpoint
```

### In Python
```python
import httpx

headers = {"X-API-Key": "your-api-key"}
response = httpx.post(url, headers=headers, files=files)
```

### In JavaScript
```javascript
const headers = {'X-API-Key': 'your-api-key'};
fetch(url, {method: 'POST', headers: headers, body: formData});
```

## Rotate API Keys

```bash
# 1. Generate new key
export API_KEY=$(openssl rand -hex 32)

# 2. Update Secret Manager
./setup-api-key.sh

# 3. Redeploy services
./deploy-backend.sh
./deploy-frontend.sh
```

## Security Tips

✅ **Generate strong keys**: Use `openssl rand -hex 32`
✅ **Store securely**: Use Secret Manager, not .env in production
✅ **Rotate regularly**: Every 90 days minimum
✅ **Monitor usage**: Check logs for failed attempts
✅ **Use HTTPS**: Always use HTTPS in production

❌ **Never commit** API keys to git
❌ **Don't share** between environments
❌ **Don't log** full API keys

## Troubleshooting

### "Missing API key" error

**Solution**: Add `X-API-Key` header to your requests

### "Invalid API key" error

**Solution**: Check your API key matches backend configuration

### Frontend can't connect

**Solution**:
```bash
# Verify secrets are configured
gcloud secrets list

# Redeploy frontend
./deploy-frontend.sh
```

## Full Documentation

See [docs/API_KEY_SETUP.md](docs/API_KEY_SETUP.md) for complete guide.

---

**Quick commands:**
```bash
# Setup
./setup-api-key.sh

# Deploy
export API_KEY_REQUIRED=true
./deploy-backend.sh
./deploy-frontend.sh

# Test
curl -H "X-API-Key: $API_KEY" https://your-backend.run.app/health
```

**Status**: ✅ API Key authentication is now fully implemented and ready to use!
