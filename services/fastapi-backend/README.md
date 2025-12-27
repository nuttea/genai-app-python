# FastAPI Backend with Vertex AI

Python FastAPI backend service integrated with Google Vertex AI for GenAI capabilities.

## Features

- ✅ RESTful API with FastAPI
- ✅ Google Vertex AI integration (Gemini models)
- ✅ Chat completions endpoint
- ✅ Text generation endpoint
- ✅ Streaming support (Server-Sent Events)
- ✅ **Vote extraction API** - Thai election form data extraction
- ✅ API key authentication
- ✅ Datadog APM with serverless-init
- ✅ LLM Observability with prompt tracking
- ✅ Health check endpoints
- ✅ Structured logging (JSON)
- ✅ Pydantic models for validation
- ✅ OpenAPI documentation (Swagger)
- ✅ Docker support

## Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Google Cloud Platform account
- Vertex AI API enabled
- gcloud CLI installed and authenticated (`gcloud auth application-default login`)

## Setup

### 1. Install Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Or with pip
pip install poetry
```

### 2. Install Dependencies

```bash
# Install dependencies with Poetry
poetry install

# Or create virtual environment and install
poetry shell
poetry install
```

### 3. Authenticate with GCP

```bash
# Authenticate with Application Default Credentials
gcloud auth application-default login

# Set your project
gcloud config set project your-gcp-project-id
```

### 4. Configure Environment

Create `.env` file:

```bash
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1
EOF
```

### 5. Run the Server

**Development (with auto-reload):**

```bash
# With Poetry
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or activate shell first
eval $(poetry env activate)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Using the startup script:**

```bash
./scripts/start.sh
```

**With Poetry directly:**

```bash
poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Dependency Management with Poetry

### Add New Dependencies

```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show installed packages
poetry show
```

### Export to requirements.txt

```bash
# For Docker or pip-based deployments
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Include dev dependencies
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
```

### Lock File

`poetry.lock` ensures reproducible builds. Commit it to version control.

## API Endpoints

### Health Checks

- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /api/v1/health` - API health check
- `GET /api/v1/ready` - API readiness check

### Chat Completion

- `POST /api/v1/chat/completions` - Generate chat completion

### Text Generation

- `POST /api/v1/generate` - Generate text from prompt
- `POST /api/v1/generate/stream` - Stream generated text

### Vote Extraction

- `POST /api/v1/vote-extraction/extract` - Extract data from election forms
- `GET /api/v1/vote-extraction/health` - Vote extraction service health

### Documentation

- `GET /docs` - Swagger UI (interactive API docs)
- `GET /redoc` - ReDoc (alternative documentation)
- `GET /openapi.json` - OpenAPI schema

## Development

### Using Poetry

```bash
# Enter Poetry shell
poetry shell

# Run development server
uvicorn app.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black app/

# Lint code
poetry run ruff check app/

# Type check
poetry run mypy app/

# Run all checks
poetry run black app/ && poetry run ruff check app/ && poetry run mypy app/
```

### Using Makefile (from project root)

```bash
# Run server
make run-fastapi

# Run tests
make test

# Code quality
make format
make lint
make typecheck
make check-all
```

## Docker

Build and run with Docker:

```bash
# Build image (uses Poetry)
docker build -t fastapi-backend .

# Run container
docker run -p 8000:8000 \
  -e GOOGLE_CLOUD_PROJECT=your-project \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  fastapi-backend
```

Or use Docker Compose from project root:

```bash
docker-compose up fastapi-backend
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | - | Yes |
| `VERTEX_AI_LOCATION` | GCP region | us-central1 | No |
| `FASTAPI_ENV` | Environment | development | No |
| `LOG_LEVEL` | Logging level | info | No |
| `DEFAULT_MODEL` | Default AI model | gemini-pro | No |
| `API_KEY` | API key for auth | - | No |
| `API_KEY_REQUIRED` | Enforce API key | false | No |
| `DD_API_KEY` | Datadog API key | - | No |
| `DD_SERVICE` | Service name | genai-fastapi-backend | No |
| `DD_ENV` | Environment | development | No |
| `DD_LLMOBS_ML_APP` | LLM app name | - | No |

See [../../docs/reference/environment-variables.md](../../docs/reference/environment-variables.md) for complete list.

## Project Structure

```
fastapi-backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── api/v1/              # API routes
│   ├── services/            # Business logic
│   ├── models/              # Pydantic models
│   ├── core/                # Core utilities
│   └── tests/               # Tests
├── Dockerfile               # Docker with serverless-init
├── pyproject.toml          # Poetry configuration
├── poetry.lock             # Locked dependencies
├── requirements.txt         # Generated from Poetry (for Docker)
└── README.md               # This file
```

## Troubleshooting

### Poetry Installation Issues

```bash
# Check Poetry version
poetry --version

# Update Poetry
poetry self update

# Clear cache
poetry cache clear pypi --all
```

### Dependency Conflicts

```bash
# Update lock file
poetry lock --no-update

# Resolve conflicts
poetry update package-name

# Fresh install
rm poetry.lock
poetry install
```

### Import Errors

```bash
# Ensure you're in Poetry environment
poetry shell

# Or run with Poetry
poetry run python -c "import app; print(app.__version__)"

# Reinstall dependencies
poetry install --sync
```

## License

See [../../LICENSE](../../LICENSE) file for details.
