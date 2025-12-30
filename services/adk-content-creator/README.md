# Datadog Content Creator - ADK Agent Service

An intelligent ADK (Agent Development Kit) agent that creates high-quality blog posts and short-form video content about Datadog products and features.

## 🎯 What It Does

Transforms various inputs into professional marketing and educational content:

- **Inputs**: Text, Markdown, Video demos, Screenshots
- **Outputs**: 
  - 📄 Blog posts (SEO-optimized)
  - 🎥 60-second video scripts (YouTube Shorts, TikTok, Reels)
  - 📱 Social media posts (LinkedIn, Twitter, Instagram)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- uv (fast Python package installer)
- Google Cloud Project with Vertex AI enabled
- Cloud Storage bucket for file uploads

### Installation

```bash
# Install dependencies
uv sync --all-extras

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the service
uv run uvicorn app.main:app --reload --port 8002
```

### Environment Variables

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
CLOUD_STORAGE_BUCKET=content-uploads

# Optional
DEFAULT_MODEL=gemini-2.5-flash
DEFAULT_TEMPERATURE=0.7
PORT=8002
```

## 📖 API Endpoints

### Health & Info

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /info` - Service capabilities

### Content Generation (Coming Soon)

- `POST /api/v1/generate` - Generate content
- `POST /api/v1/upload` - Upload files
- `GET /api/v1/preview/{id}` - Preview content
- `POST /api/v1/publish` - Publish content

## 🛠️ Development

### Run Tests

```bash
uv run pytest tests/ -v --cov=app
```

### Format Code

```bash
uv run black app/
uv run isort app/
```

### Lint Code

```bash
uv run ruff check app/
```

## 🏗️ Project Structure

```
adk-content-creator/
├── app/
│   ├── agent/          # ADK agent core
│   ├── api/v1/         # API endpoints
│   ├── services/       # Business logic
│   ├── models/         # Data models
│   ├── core/           # Core utilities
│   └── tests/          # Tests
├── uploads/            # Temporary file storage
├── pyproject.toml      # Dependencies
└── README.md           # This file
```

## 📚 Documentation

- **Full Plan**: [DATADOG_CONTENT_CREATOR_PLAN.md](../../docs/features/DATADOG_CONTENT_CREATOR_PLAN.md)
- **Quick Reference**: [DATADOG_CONTENT_CREATOR_QUICKREF.md](../../docs/features/DATADOG_CONTENT_CREATOR_QUICKREF.md)

## 🔐 Security

- Uses Google Cloud Application Default Credentials
- Supports optional API key authentication
- File uploads validated and scanned
- Rate limiting on API endpoints

## 📊 Monitoring

Integrated with Datadog for:
- APM tracing
- Performance metrics
- Error tracking
- Cost monitoring

## 📝 License

See root LICENSE file.

## 🤝 Contributing

See root project documentation for contribution guidelines.

---

**Status**: 🚧 In Development  
**Version**: 0.1.0  
**Created**: December 30, 2024

