# 🚀 QuickStart Guide

Get up and running with the GenAI Application Platform in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Poetry installed (recommended) or pip
- [ ] Docker & Docker Compose installed
- [ ] GCP account with billing enabled
- [ ] Vertex AI API enabled

## 5-Minute Setup

### Step 1: Clone and Setup (1 min)

```bash
cd genai-app-python

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies with Poetry
make install

# Or manually
cd services/fastapi-backend
poetry install
eval $(poetry env activate)  # Poetry 2.0+

cd ../frontend/streamlit
poetry install
eval $(poetry env activate)  # Poetry 2.0+
```

### Step 2: Configure GCP (1 min)

```bash
# Set your GCP project
export PROJECT_ID="your-gcp-project-id"

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID

# Authenticate with Application Default Credentials (ADC)
gcloud auth application-default login

# This will open a browser for authentication and store credentials at:
# ~/.config/gcloud/application_default_credentials.json
```

**Why Application Default Credentials?**
- ✅ More secure (no key files to manage)
- ✅ Automatic credential discovery
- ✅ Works seamlessly with Docker
- ✅ Same credentials for all GCP tools

### Step 3: Configure Environment (30 sec)

```bash
# Create .env file with your project ID
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1
EOF
```

Or set environment variables directly:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export VERTEX_AI_LOCATION="us-central1"
# GOOGLE_APPLICATION_CREDENTIALS is not needed with ADC!
```

**Note**: No need to set `GOOGLE_APPLICATION_CREDENTIALS` - the SDK automatically finds credentials from `gcloud auth application-default login`.

### Step 4: Run the Application (30 sec)

**Option A: Local Development**
```bash
make run-fastapi

# Or
cd services/fastapi-backend
uvicorn app.main:app --reload
```

**Option B: Docker**
```bash
make docker-up

# Or
docker-compose up -d
```

### Step 5: Test It! (1 min)

```bash
# Health check
curl http://localhost:8000/health

# Generate text
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a haiku about AI",
    "model": "gemini-pro",
    "temperature": 0.7
  }'

# Chat completion
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! Tell me a joke."}
    ]
  }'
```

## 🎉 Success!

Your GenAI backend is now running!

**Access the API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs and try different endpoints
2. **Read the docs**: Check out [GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed setup
3. **Customize**: Modify `services/fastapi-backend/app/config.py` to adjust settings
4. **Deploy**: See [PROJECT_PLAN.md](PROJECT_PLAN.md) for deployment options

## Common Commands

```bash
# Development
make run-fastapi          # Run locally
make docker-up            # Run with Docker
make test                 # Run tests
make format lint          # Format and lint code

# Docker
make docker-logs          # View logs
make docker-down          # Stop services
make docker-clean         # Clean everything

# Cleanup
make clean                # Clean cache files
make clean-all            # Clean everything including Docker
```

## Troubleshooting

### "Could not determine credentials"

```bash
# Re-authenticate with Application Default Credentials
gcloud auth application-default login

# Verify credentials file exists
ls -la ~/.config/gcloud/application_default_credentials.json

# Verify project is set
echo $GOOGLE_CLOUD_PROJECT
gcloud config get-value project
```

### "Address already in use"

```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### "Module not found"

```bash
# Reinstall dependencies
cd services/fastapi-backend
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(fastapi.__version__)"
```

## Quick Examples

### Python Client

```python
import httpx

# Generate text
response = httpx.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "prompt": "Explain quantum computing in simple terms",
        "model": "gemini-pro",
        "max_tokens": 200
    }
)
print(response.json()["text"])
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8000/api/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Hello!' }
    ],
    model: 'gemini-pro'
  })
});

const data = await response.json();
console.log(data.content);
```

## Available Models

- `gemini-pro` - Google's Gemini Pro (recommended)
- `gemini-pro-vision` - Gemini with vision capabilities
- `text-bison` - PaLM 2 for text
- `chat-bison` - PaLM 2 for chat

## Project Structure

```
genai-app-python/
├── services/
│   └── fastapi-backend/     # ✅ Current: FastAPI + Vertex AI
├── frontend/                 # 🔜 Future: Next.js UI
├── notebooks/                # 🔜 Future: Jupyter notebooks
├── docs/                     # 📚 Documentation
├── docker-compose.yml        # 🐳 Docker orchestration
├── Makefile                  # 🛠️  Development commands
└── README.md                 # 📖 Main documentation
```

## 📚 Documentation

### Quick Guides
- 🚀 [Deploy to Cloud Run](docs/deployment/quickstart.md) - 10 minutes
- 🔐 [Setup API Keys](docs/security/api-key-quickstart.md) - 2 minutes
- 📊 [Enable Datadog](docs/monitoring/quickstart.md) - 2 minutes

### Complete Guides
- 📖 [Complete Documentation Index](docs/INDEX.md)
- 📋 [Getting Started](docs/getting-started/GETTING_STARTED.md)
- 👨‍💻 [Development Guide](docs/getting-started/DEVELOPMENT.md)
- 🏗️ [Project Plan & Architecture](PROJECT_PLAN.md)

### Feature Guides
- 🗳️ [Vote Extractor User Guide](docs/features/vote-extractor.md)

### Reference
- ⚙️ [Environment Variables](docs/reference/environment-variables.md)
- ✨ [Feature List](docs/reference/features.md)
- 🔧 Run `make help` for available commands

## What's Next?

The platform is designed to grow:

- **Phase 2**: TypeScript MCP Server
- **Phase 3**: Next.js Frontend
- **Phase 4**: Jupyter Notebooks

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the complete roadmap.

---

**Happy coding!** 🎉

For issues or questions, check the documentation or run `make help`.
