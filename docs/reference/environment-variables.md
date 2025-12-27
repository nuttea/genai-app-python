# Environment Variables Template

Create a `.env` file in the project root with these variables:

## Minimal Configuration (Recommended)

```bash
# Required: Your GCP Project ID
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# Optional: GCP Region (default: us-central1)
VERTEX_AI_LOCATION=us-central1
```

**That's it!** When using `gcloud auth application-default login`, you don't need to set `GOOGLE_APPLICATION_CREDENTIALS`.

## Quick Setup

```bash
# Create .env file
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-actual-project-id
VERTEX_AI_LOCATION=us-central1
EOF

# Authenticate with GCP
gcloud auth application-default login
```

## Full Configuration (Optional)

For advanced configuration, you can also set:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1
# GOOGLE_APPLICATION_CREDENTIALS=""  # Not needed with ADC

# FastAPI Configuration
FASTAPI_ENV=development
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=info

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# API Configuration
API_V1_PREFIX=/api/v1
API_TITLE="GenAI FastAPI Backend"
API_VERSION=0.1.0
API_KEY=

# Vertex AI Model Configuration
DEFAULT_MODEL=gemini-pro
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1024
DEFAULT_TOP_P=0.95
DEFAULT_TOP_K=40

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=false

# Development
DEBUG=false
RELOAD=true
```

## Authentication Methods

### Method 1: Application Default Credentials (Recommended for Development)

```bash
# One-time setup
gcloud auth application-default login

# No environment variable needed!
# Credentials stored at: ~/.config/gcloud/application_default_credentials.json
```

### Method 2: Service Account Key (Production/CI/CD)

```bash
# Set path to service account key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## Docker-specific Configuration

When using Docker Compose, the gcloud credentials are automatically mounted:

```yaml
volumes:
  - ${HOME}/.config/gcloud:/root/.config/gcloud:ro
```

No additional configuration needed!

## Validation

Check your configuration:

```bash
# Verify project is set
echo $GOOGLE_CLOUD_PROJECT

# Check credentials
gcloud auth application-default print-access-token

# Test API
curl http://localhost:8000/health
```

## Security Notes

- ✅ Never commit `.env` files to version control
- ✅ The `.gitignore` already excludes `.env` files
- ✅ Use `.env.example` as a template only
- ✅ Application Default Credentials are more secure than key files
- ✅ For production, use service accounts with minimal permissions

## Environment-Specific Examples

### Local Development

```bash
GOOGLE_CLOUD_PROJECT=my-dev-project
VERTEX_AI_LOCATION=us-central1
LOG_LEVEL=debug
DEBUG=true
RELOAD=true
```

### Staging

```bash
GOOGLE_CLOUD_PROJECT=my-staging-project
VERTEX_AI_LOCATION=us-central1
LOG_LEVEL=info
DEBUG=false
RELOAD=false
```

### Production

```bash
GOOGLE_CLOUD_PROJECT=my-prod-project
VERTEX_AI_LOCATION=us-central1
LOG_LEVEL=warning
DEBUG=false
RELOAD=false
RATE_LIMIT_PER_MINUTE=100
API_KEY=your-secure-api-key
```

## Troubleshooting

### "GOOGLE_CLOUD_PROJECT not set"

```bash
# Set in .env file
echo "GOOGLE_CLOUD_PROJECT=your-project-id" >> .env

# Or export directly
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### "Could not determine credentials"

```bash
# Re-authenticate
gcloud auth application-default login

# Verify credentials exist
ls -la ~/.config/gcloud/application_default_credentials.json
```

### Docker not finding credentials

```bash
# Ensure gcloud config exists
ls -la ~/.config/gcloud/

# Restart Docker containers
docker-compose down
docker-compose up
```

## See Also

- [AUTHENTICATION.md](docs/AUTHENTICATION.md) - Detailed authentication guide
- [GETTING_STARTED.md](docs/GETTING_STARTED.md) - Full setup instructions
- [QUICKSTART.md](QUICKSTART.md) - 5-minute quick start

---

**Quick Start**: Create `.env` with your `GOOGLE_CLOUD_PROJECT`, run `gcloud auth application-default login`, and you're ready to go!
