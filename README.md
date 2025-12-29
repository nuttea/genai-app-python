# GenAI Application Platform

A comprehensive GenAI application platform built with **Python FastAPI**, **Google Vertex AI**, and modern cloud-native technologies. Features production-ready vote extraction for Thai election forms with full observability.

## 🚀 Quick Start

Get started in 5 minutes! See **[QUICKSTART.md](QUICKSTART.md)** ⭐

## ⚠️ Before You Commit

**Always format your code with Black before committing!**

See **[PRE-COMMIT-CHECKLIST.md](PRE-COMMIT-CHECKLIST.md)** for detailed instructions.

Quick command:
```bash
cd services/fastapi-backend && poetry run black app/ && cd ../.. && cd frontend/streamlit && poetry run black . && cd ../..
```

```bash
# 1. Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# 2. Authenticate with GCP
gcloud auth application-default login

# 3. Create .env file
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
EOF

# 4. Start services (uses Poetry)
docker-compose up -d

# 5. Access
open http://localhost:8501  # Streamlit UI
open http://localhost:8000/docs  # API Docs
```

## 📋 Project Overview

This project is a **production-ready** GenAI platform featuring:

- **🔌 FastAPI Backend** - Python API with Google Vertex AI (Gemini 2.5 Flash)
- **🖥️ Streamlit Frontend** - Interactive multi-page web UI
- **🗳️ Vote Extractor** - Thai election form (S.S. 5/18) data extraction
- **🔐 Security** - API key authentication with Secret Manager
- **📊 Observability** - Datadog APM with LLM tracking
- **☁️ Cloud Run Ready** - Serverless deployment with auto-scaling

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  GenAI Application Platform                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐         ┌──────────────┐         ┌─────────┐ │
│  │  Streamlit   │ X-API-  │   FastAPI    │  Auth   │ Google  │ │
│  │   Frontend   │─Key────▶│   Backend    │────────▶│ Vertex  │ │
│  │  (Port 8501) │         │  (Port 8000) │         │   AI    │ │
│  └──────┬───────┘         └──────┬───────┘         └─────────┘ │
│         │                        │                               │
│         │                        ▼                               │
│         │               ┌─────────────────┐                     │
│         │               │  Datadog APM    │                     │
│         └──────────────▶│  - Traces       │                     │
│                         │  - Logs         │                     │
│                         │  - LLM Obs      │                     │
│                         └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### Backend API ✅
- ✅ RESTful API with FastAPI
- ✅ Google Vertex AI integration (Gemini 2.5 Flash)
- ✅ Chat completion endpoint
- ✅ Text generation with streaming
- ✅ **Vote extraction API** - Multi-page document processing
- ✅ API key authentication
- ✅ Comprehensive error handling
- ✅ OpenAPI/Swagger documentation
- ✅ Datadog APM with serverless-init

### Frontend UI ✅
- ✅ Multi-page Streamlit application
- ✅ **Vote Extractor** - Upload and process election forms
- ✅ Image preview and validation
- ✅ Results visualization (4 tabs)
- ✅ Data export (CSV, JSON)
- ✅ Real-time processing
- ✅ API key integration

### Security ✅
- ✅ API key authentication
- ✅ Secret Manager integration
- ✅ GCP Application Default Credentials
- ✅ CORS configuration
- ✅ Request validation

### Observability ✅
- ✅ Datadog APM (full distributed tracing)
- ✅ Datadog LLM Observability (track all AI calls)
- ✅ Log-trace correlation
- ✅ Continuous profiling
- ✅ Structured JSON logging

### Deployment ✅
- ✅ Docker containerization
- ✅ Docker Compose for local dev
- ✅ Google Cloud Run (serverless)
- ✅ CI/CD with Cloud Build
- ✅ Auto-scaling (0 to ∞)
- ✅ HTTPS included

## 🛠️ Technology Stack

**Backend:**
- Python 3.11, FastAPI, Uvicorn
- **Poetry** - Dependency management
- Google Vertex AI SDK (`google-genai`)
- Datadog APM (ddtrace)
- Pydantic validation

**Frontend:**
- Streamlit 1.31.1
- **Poetry** - Dependency management
- httpx, Pillow, pandas

**Infrastructure:**
- Docker & Docker Compose
- Google Cloud Run
- Google Secret Manager
- Cloud Build (CI/CD)

**Monitoring:**
- Datadog APM & LLM Observability
- Google Cloud Logging & Monitoring

## 📖 Documentation

### 🚀 Quick Starts (5-10 minutes)
- **[QUICKSTART.md](QUICKSTART.md)** ⭐ - Get started in 5 minutes
- **[docs/deployment/quickstart.md](docs/deployment/quickstart.md)** - Deploy to Cloud Run
- **[docs/security/api-key-quickstart.md](docs/security/api-key-quickstart.md)** - Setup API keys
- **[docs/monitoring/quickstart.md](docs/monitoring/quickstart.md)** - Enable Datadog

### 📚 Complete Guides
- **[docs/INDEX.md](docs/INDEX.md)** - Complete documentation index
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Architecture and roadmap
- **[docs/getting-started/](docs/getting-started/)** - Setup and development
- **[docs/deployment/](docs/deployment/)** - Cloud Run deployment
- **[docs/security/](docs/security/)** - Authentication and API keys
- **[docs/monitoring/](docs/monitoring/)** - Datadog observability
- **[docs/features/](docs/features/)** - Feature guides
- **[docs/reference/](docs/reference/)** - Configuration reference

## 🚀 Usage

### Local Development

```bash
# Run backend only
make run-fastapi

# Run frontend only
make run-streamlit

# Run everything with Docker
make docker-up

# View logs
make docker-logs
```

### Cloud Run Deployment

```bash
cd infra/cloud-run

# Quick deploy (no security)
./deploy-all.sh

# Production deploy (with API key and Datadog)
export API_KEY=$(openssl rand -hex 32)
export DD_API_KEY=your-datadog-api-key
./setup-api-key.sh
./setup-datadog-secrets.sh
export API_KEY_REQUIRED=true
./deploy-all.sh
```

## 🗳️ Vote Extractor Feature

Extract structured data from Thai election documents (Form S.S. 5/18):

1. Upload multiple image pages (JPG, PNG)
2. AI automatically extracts:
   - Form information (Province, District, Date)
   - Ballot statistics (Used, Valid, Void, No Vote)
   - Vote results (All candidates with counts)
3. Validate and export (CSV, JSON)

**Guide**: [docs/features/vote-extractor.md](docs/features/vote-extractor.md)

## 🔐 Security

- **API Key Authentication** - Protect endpoints with X-API-Key header
- **Secret Manager** - Secure storage for keys
- **GCP ADC** - No service account keys needed locally
- **HTTPS** - Automatic SSL in Cloud Run

**Setup**: [docs/security/api-key-quickstart.md](docs/security/api-key-quickstart.md)

## 📊 Monitoring & Observability

### Datadog Integration

- **APM** - Full distributed tracing with ddtrace
- **LLM Observability** - Track all Gemini API calls (tokens, costs, performance)
- **Log Correlation** - Link logs to traces
- **Profiling** - CPU and memory analysis

**Setup**: [docs/monitoring/quickstart.md](docs/monitoring/quickstart.md)

### Metrics Tracked

- Request rate, latency, errors
- Token usage and costs
- Model performance
- Service dependencies

## 🚢 Deployment

### Google Cloud Run (Recommended)

```bash
cd infra/cloud-run
export GOOGLE_CLOUD_PROJECT=your-project-id
./deploy-all.sh
```

**Features:**
- ✅ Serverless - Auto-scaling from 0 to ∞
- ✅ Pay per use - $0 when idle
- ✅ HTTPS included - Automatic SSL
- ✅ Global deployment - Fast worldwide

**Cost**: ~$0.10-0.50 per 1000 requests (2M free/month)

**Guide**: [docs/deployment/quickstart.md](docs/deployment/quickstart.md)

## 🛠️ Development Commands

```bash
# Development
make run-fastapi          # Run backend locally
make run-streamlit        # Run frontend locally
make test                 # Run tests
make format lint          # Code quality

# Docker
make docker-up            # Start all services
make docker-logs          # View logs
make docker-down          # Stop services

# Deployment
make deploy-all           # Deploy to Cloud Run
make check-services       # Check service status

# Monitoring
make datadog-logs         # Open Datadog traces

# Help
make help                 # Show all commands
```

## 📁 Project Structure

```
genai-app-python/
├── services/
│   └── fastapi-backend/          # Python FastAPI + Vertex AI
│       ├── app/                  # Application code
│       ├── Dockerfile            # With serverless-init
│       └── cloudbuild.yaml       # CI/CD
│
├── frontend/
│   └── streamlit/                # Streamlit UI
│       ├── app.py                # Main app
│       ├── pages/                # Vote extractor, etc.
│       └── Dockerfile            # Container config
│
├── infra/
│   └── cloud-run/                # Deployment scripts
│       ├── deploy-all.sh         # Deploy everything
│       ├── setup-api-key.sh      # API key setup
│       └── setup-datadog-secrets.sh  # Datadog setup
│
├── docs/                         # Documentation
│   ├── INDEX.md                  # Documentation index
│   ├── getting-started/          # Setup guides
│   ├── deployment/               # Deployment guides
│   ├── security/                 # Security docs
│   ├── monitoring/               # Observability
│   ├── features/                 # Feature guides
│   └── reference/                # Configuration reference
│
├── docker-compose.yml            # Local development
├── Makefile                      # Development commands
├── QUICKSTART.md                 # ⭐ Start here!
├── PROJECT_PLAN.md               # Architecture
└── README.md                     # This file
```

## 🎯 Use Cases

1. **Thai Election Data Entry** - Automate vote counting from forms
2. **Document Extraction** - Extract structured data from images
3. **AI-powered Chat** - Conversational interfaces
4. **Text Generation** - Content creation with AI

## 💰 Cost Estimates

**Local Development**: $0

**Cloud Run (Production):**
- Free tier: 2 million requests/month
- After: ~$0.10-0.50 per 1000 requests
- Typical: $20-100/month for low-medium traffic
- Scales to $0 when idle

**Datadog:**
- Free trial: 14 days
- After: ~$31/month + spans
- Typical: $20-80/month

**Total Estimated**: $40-180/month for production deployment

## 🔮 Roadmap

**Current Phase**: ✅ Phase 1 Complete
- FastAPI Backend
- Streamlit Frontend
- Vote Extraction
- Cloud Run Deployment
- Datadog Integration

**Next Phases**: 🔜 Planned
- Phase 2: TypeScript MCP Server
- Phase 3: Next.js Frontend
- Phase 4: Jupyter Notebooks

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for complete roadmap.

## 📞 Support & Resources

### Documentation
- **📚 [docs/INDEX.md](docs/INDEX.md)** - Complete documentation index
- **🚀 [QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start
- **📋 [PROJECT_PLAN.md](PROJECT_PLAN.md)** - Architecture and planning

### Quick Guides
- **Deploy**: [docs/deployment/quickstart.md](docs/deployment/quickstart.md)
- **Secure**: [docs/security/api-key-quickstart.md](docs/security/api-key-quickstart.md)
- **Monitor**: [docs/monitoring/quickstart.md](docs/monitoring/quickstart.md)

### Service URLs (Local)
- Streamlit UI: http://localhost:8501
- FastAPI Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Commands
```bash
make help                 # Show all commands
./check-services.sh       # Check service status
docker-compose logs       # View logs
```

## 🤝 Contributing

This project follows best practices for:
- Code quality (Black, Ruff, Mypy)
- Testing (pytest)
- Documentation (comprehensive guides)
- Security (API keys, secret management)
- Monitoring (Datadog APM)

See [docs/getting-started/DEVELOPMENT.md](docs/getting-started/DEVELOPMENT.md) for development guidelines.

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🎉 Status

**✅ Production Ready**

- All core features implemented
- Fully documented (17 guides)
- Security enabled
- Monitoring integrated
- Cloud Run deployment ready
- CI/CD pipelines configured

**Current Version**: 0.1.0
**Last Updated**: December 27, 2024

---

**⭐ Start with [QUICKSTART.md](QUICKSTART.md) to get up and running in 5 minutes!**

**📚 Full documentation at [docs/INDEX.md](docs/INDEX.md)**
