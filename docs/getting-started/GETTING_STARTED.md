# Getting Started

This guide will help you set up and run the GenAI Application Platform.

## Prerequisites

### Required
- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Google Cloud Platform Account** - [Sign up](https://cloud.google.com/)
- **Git** - [Install Git](https://git-scm.com/downloads)

### Optional
- **Make** - For using Makefile commands (usually pre-installed on macOS/Linux)
- **Node.js 18+** - For future MCP server development

## GCP Setup

### 1. Install gcloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2. Create a GCP Project

```bash
# Using gcloud CLI
gcloud projects create your-project-id --name="GenAI Application"
gcloud config set project your-project-id
```

### 3. Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable other useful APIs
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
```

### 4. Authenticate with Application Default Credentials

```bash
# Login with your user account
gcloud auth application-default login

# This will:
# - Open a browser for authentication
# - Store credentials at ~/.config/gcloud/application_default_credentials.json
# - Allow all GCP SDKs to automatically use these credentials
```

**Why Application Default Credentials?**
- ✅ **More Secure**: No service account key files to manage
- ✅ **Convenient**: One authentication for all GCP tools
- ✅ **Automatic**: SDKs automatically discover credentials
- ✅ **Docker-Friendly**: Works seamlessly in containers

**Note**: For production deployments, you'll use service accounts instead. See [docs/AUTHENTICATION.md](./AUTHENTICATION.md) for details.

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd genai-app-python
```

### 2. Set Up Environment Variables

```bash
# Create .env file with your project ID
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
EOF
```

**That's it!** No need to set `GOOGLE_APPLICATION_CREDENTIALS` - the SDK automatically uses your Application Default Credentials from `gcloud auth application-default login`.

Required environment variables:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
# GOOGLE_APPLICATION_CREDENTIALS not needed with ADC!
```

### 3. Install Dependencies

**Using Make (Recommended):**
```bash
make install
```

**Manual Installation:**
```bash
cd services/fastapi-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using Make Commands

```bash
# Run FastAPI backend
make run-fastapi

# Access the API
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health check: http://localhost:8000/health
```

### Option 2: Using Docker Compose

```bash
# Build and start services
make docker-up

# Or without Make
docker-compose up -d

# View logs
make docker-logs

# Stop services
make docker-down
```

### Option 3: Direct Python Execution

```bash
cd services/fastapi-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the API

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

### Chat Completion

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! Tell me a joke."}
    ],
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### Text Generation

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a haiku about coding",
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### Streaming Example

```bash
curl -N -X POST http://localhost:8000/api/v1/generate/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Count from 1 to 10 slowly",
    "model": "gemini-pro"
  }'
```

## Development Workflow

### 1. Code Formatting

```bash
# Format code
make format

# Check formatting
make format-check
```

### 2. Linting

```bash
# Run linter
make lint

# Auto-fix issues
make lint-fix
```

### 3. Type Checking

```bash
make typecheck
```

### 4. Run All Checks

```bash
make check-all
```

### 5. Running Tests

```bash
# Run tests
make test

# Run tests with coverage
make test-cov
```

## Troubleshooting

### Authentication Errors

**Error**: "Could not automatically determine credentials"

**Solution**:
1. Re-authenticate with Application Default Credentials
2. Verify your GCP project is set correctly
3. Check that you have proper permissions

```bash
# Re-authenticate
gcloud auth application-default login

# Verify credentials file exists
ls -la ~/.config/gcloud/application_default_credentials.json

# Check project
echo $GOOGLE_CLOUD_PROJECT
gcloud config get-value project

# Verify you have the right permissions
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT \
    --flatten="bindings[].members" \
    --filter="bindings.members:user:$(gcloud config get-value account)"
```

**For detailed authentication setup**, see [docs/AUTHENTICATION.md](./AUTHENTICATION.md)

### Port Already in Use

**Error**: "Address already in use"

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### Import Errors

**Error**: "ModuleNotFoundError: No module named 'app'"

**Solution**:
```bash
# Make sure you're in the correct directory
cd services/fastapi-backend

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Docker Build Failures

**Error**: Docker build fails

**Solution**:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker logs
docker-compose logs fastapi-backend
```

## Next Steps

1. ✅ Explore the API documentation at http://localhost:8000/docs
2. ✅ Review the [PROJECT_PLAN.md](../PROJECT_PLAN.md) for architecture details
3. ✅ Check out the [API documentation](./api/) for endpoint details
4. ✅ Read about [deployment options](./DEPLOYMENT.md) (coming soon)
5. ✅ Experiment with different models and parameters

## Available Models

The following Vertex AI models are available:

- **gemini-pro** - Google's Gemini Pro model (recommended)
- **gemini-pro-vision** - Gemini Pro with vision capabilities
- **text-bison** - PaLM 2 for text generation
- **chat-bison** - PaLM 2 for chat

Check [Google's Vertex AI documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models) for the latest available models.

## Useful Commands

```bash
# Start everything
make docker-up

# View logs
make docker-logs

# Stop everything
make docker-down

# Clean everything
make clean-all

# Run tests
make test

# Format and lint
make format lint

# Quick start help
make quickstart
```

## Getting Help

- Check the [PROJECT_PLAN.md](../PROJECT_PLAN.md)
- Review the [FastAPI Backend README](../services/fastapi-backend/README.md)
- Look at example requests in the Swagger UI
- Check Docker logs: `make docker-logs`

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | Yes | - | Your GCP project ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | Yes | - | Path to service account key |
| `VERTEX_AI_LOCATION` | No | us-central1 | GCP region |
| `FASTAPI_ENV` | No | development | Environment name |
| `FASTAPI_PORT` | No | 8000 | Server port |
| `LOG_LEVEL` | No | info | Logging level |
| `DEFAULT_MODEL` | No | gemini-pro | Default AI model |
| `DEFAULT_TEMPERATURE` | No | 0.7 | Default temperature |
| `DEFAULT_MAX_TOKENS` | No | 1024 | Default max tokens |

---

**Ready to get started?** Run `make quickstart` for a quick command reference!

