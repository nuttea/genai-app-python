# 📂 Project Structure

Complete overview of the GenAI Application Platform project organization.

## 🗂️ Directory Structure

```
genai-app-python/
│
├── 📄 README.md                           Main project overview
├── 🚀 QUICKSTART.md                       5-minute quick start
├── 📋 PROJECT_PLAN.md                     Architecture & roadmap
├── 📚 DOCUMENTATION_SUMMARY.md            Documentation organization
├── 📂 PROJECT_STRUCTURE.md                This file
│
├── 📁 services/                           Backend Services
│   └── fastapi-backend/
│       ├── app/                           Application code
│       │   ├── api/v1/                    API routes
│       │   │   ├── endpoints/             Endpoint handlers
│       │   │   │   ├── chat.py            Chat completion
│       │   │   │   ├── generate.py        Text generation
│       │   │   │   ├── health.py          Health checks
│       │   │   │   └── vote_extraction.py Vote extraction API
│       │   │   └── router.py              Route aggregation
│       │   ├── services/                  Business logic
│       │   │   ├── vertex_ai.py           Vertex AI integration
│       │   │   ├── genai_service.py       GenAI service layer
│       │   │   └── vote_extraction_service.py  Vote extraction
│       │   ├── models/                    Pydantic models
│       │   │   ├── requests.py            Request models
│       │   │   ├── responses.py           Response models
│       │   │   └── vote_extraction.py     Vote extraction models
│       │   ├── core/                      Core utilities
│       │   │   ├── logging.py             Structured logging
│       │   │   └── security.py            API key validation
│       │   ├── tests/                     Test suite
│       │   ├── config.py                  Configuration
│       │   └── main.py                    FastAPI application
│       ├── Dockerfile                     Docker with serverless-init
│       ├── cloudbuild.yaml                CI/CD configuration
│       ├── requirements.txt               Python dependencies
│       ├── pyproject.toml                 Project configuration
│       └── README.md                      Backend documentation
│
├── 📁 frontend/                           Frontend Applications
│   └── streamlit/
│       ├── pages/                         Multi-page app
│       │   └── 1_🗳️_Vote_Extractor.py   Vote extraction page
│       ├── .streamlit/                    Configuration
│       │   ├── config.toml                App settings
│       │   └── secrets.toml.example       Secrets template
│       ├── app.py                         Main application
│       ├── Dockerfile                     Container config
│       ├── requirements.txt               Dependencies
│       ├── setup.sh                       Setup script
│       └── README.md                      Frontend documentation
│
├── 📁 infra/                              Infrastructure
│   └── cloud-run/                         Cloud Run deployment
│       ├── deploy-all.sh                  Deploy everything
│       ├── deploy-backend.sh              Deploy FastAPI
│       ├── deploy-frontend.sh             Deploy Streamlit
│       ├── setup-api-key.sh               API key setup
│       └── setup-datadog-secrets.sh       Datadog setup
│
├── 📁 docs/                               📚 Documentation
│   ├── INDEX.md                           Complete index
│   ├── NAVIGATION.md                      Quick navigation
│   ├── README.md                          Documentation overview
│   │
│   ├── getting-started/                   🚀 Setup & Development
│   │   ├── GETTING_STARTED.md
│   │   └── DEVELOPMENT.md
│   │
│   ├── deployment/                        ☁️ Cloud Deployment
│   │   ├── quickstart.md
│   │   └── CLOUD_RUN_DEPLOYMENT.md
│   │
│   ├── security/                          🔐 Authentication & Security
│   │   ├── api-key-quickstart.md
│   │   ├── API_KEY_SETUP.md
│   │   └── AUTHENTICATION.md
│   │
│   ├── monitoring/                        📊 Observability
│   │   ├── quickstart.md
│   │   └── DATADOG_SETUP.md
│   │
│   ├── features/                          🎯 Feature Guides
│   │   └── vote-extractor.md
│   │
│   ├── reference/                         📋 Reference
│   │   ├── environment-variables.md
│   │   └── features.md
│   │
│   └── archive/                           📦 Historical
│       └── (Implementation summaries)
│
├── 📁 notebooks/                          🔬 Jupyter Notebooks
│   └── google-vertex-genai.ipynb          Vertex AI experiments
│
├── 🐳 docker-compose.yml                  Local orchestration
├── 🛠️ Makefile                            Development commands
├── 🔍 check-services.sh                   Service diagnostics
├── 📝 LICENSE                             License file
└── ⚙️ static-analysis.datadog.yml         Datadog config
```

## 📊 File Counts

| Directory | Files | Purpose |
|-----------|-------|---------|
| **services/fastapi-backend/app/** | 23 | Backend application code |
| **frontend/streamlit/** | 7 | Frontend application |
| **infra/cloud-run/** | 5 | Deployment scripts |
| **docs/** | 20 | Documentation |
| **Root** | 8 | Configuration & entry points |
| **Total** | **63+** | Complete application |

## 🎯 Key Directories

### `/services/fastapi-backend/`
**Purpose**: Python FastAPI backend with Vertex AI

**Key Files:**
- `app/main.py` - FastAPI application entry point
- `app/config.py` - Configuration management
- `app/api/v1/endpoints/` - API endpoint handlers
- `app/services/` - Business logic
- `Dockerfile` - Docker with Datadog serverless-init

**Size**: ~1,500 lines of Python code

### `/frontend/streamlit/`
**Purpose**: Interactive web interface

**Key Files:**
- `app.py` - Main Streamlit application
- `pages/1_🗳️_Vote_Extractor.py` - Vote extraction page
- `.streamlit/config.toml` - App configuration
- `Dockerfile` - Container configuration

**Size**: ~300 lines of Python code

### `/infra/cloud-run/`
**Purpose**: Cloud Run deployment automation

**Key Files:**
- `deploy-all.sh` - Deploy both services
- `deploy-backend.sh` - Deploy FastAPI
- `deploy-frontend.sh` - Deploy Streamlit
- `setup-api-key.sh` - API key management
- `setup-datadog-secrets.sh` - Datadog configuration

**Size**: ~600 lines of shell scripts

### `/docs/`
**Purpose**: Comprehensive documentation

**Structure:**
- 6 category folders
- 20 markdown documents
- 3 navigation aids
- ~8,200 lines of documentation

## 🔧 Configuration Files

### Root Level
- `docker-compose.yml` - Local development orchestration
- `Makefile` - 40+ development commands
- `LICENSE` - Project license

### Backend
- `services/fastapi-backend/requirements.txt` - Python dependencies
- `services/fastapi-backend/pyproject.toml` - Project config
- `services/fastapi-backend/cloudbuild.yaml` - CI/CD

### Frontend
- `frontend/streamlit/requirements.txt` - Dependencies
- `frontend/streamlit/.streamlit/config.toml` - Streamlit config

### Hidden/Config
- `.gitignore` - Git ignore patterns
- `.pre-commit-config.yaml` - Pre-commit hooks
- `static-analysis.datadog.yml` - Datadog static analysis

## 🚀 Entry Points

### For Users
1. **[README.md](README.md)** - Project overview
2. **[QUICKSTART.md](QUICKSTART.md)** - Get started
3. **Streamlit UI** - http://localhost:8501

### For Developers
1. **[docs/INDEX.md](docs/INDEX.md)** - Documentation index
2. **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Architecture
3. **[docs/getting-started/DEVELOPMENT.md](docs/getting-started/DEVELOPMENT.md)** - Development guide

### For DevOps
1. **[docs/deployment/quickstart.md](docs/deployment/quickstart.md)** - Deploy
2. **[infra/cloud-run/](infra/cloud-run/)** - Deployment scripts
3. **[docker-compose.yml](docker-compose.yml)** - Local setup

## 📏 Code Organization Principles

### Backend (FastAPI)
**Pattern**: Layered Architecture
```
API Layer (endpoints) → Service Layer (business logic) → Models (validation)
```

**Benefits:**
- Clear separation of concerns
- Easy to test
- Maintainable
- Scalable

### Frontend (Streamlit)
**Pattern**: Page-based Multi-app
```
app.py (main) + pages/ (individual pages)
```

**Benefits:**
- Easy to add pages
- Independent page development
- Built-in navigation

### Infrastructure
**Pattern**: Script-based Deployment
```
infra/cloud-run/ contains all deployment logic
```

**Benefits:**
- Reproducible deployments
- Version controlled
- Easy to customize

## 🎨 Naming Conventions

### Files
- **Lowercase with hyphens**: `api-key-quickstart.md`
- **UPPERCASE for important**: `README.md`, `QUICKSTART.md`
- **Descriptive names**: `vote-extractor.md`, not `feature1.md`

### Directories
- **Lowercase with hyphens**: `getting-started/`
- **Descriptive**: `deployment/`, not `deploy/`
- **Plural for collections**: `services/`, `docs/`

### Python Modules
- **Lowercase with underscores**: `vote_extraction_service.py`
- **Descriptive**: `security.py`, not `sec.py`

## 💾 Size Summary

```
Total Project Size: ~65 MB
├── Code:           ~50 KB  (Python, config)
├── Dependencies:   ~60 MB  (Python packages, in venv)
├── Documentation:  ~200 KB (Markdown files)
└── Git:            ~5 MB   (Version control)
```

**Without dependencies**: ~300 KB (lean!)

## 🔍 Finding Files

### By Type
```bash
# Python files
find . -name "*.py" -not -path "./.venv/*"

# Documentation
find docs/ -name "*.md"

# Configuration
find . -name "*.yml" -o -name "*.yaml" -o -name "*.toml"

# Scripts
find . -name "*.sh"
```

### By Purpose
```bash
# API endpoints
ls services/fastapi-backend/app/api/v1/endpoints/

# Services
ls services/fastapi-backend/app/services/

# Streamlit pages
ls frontend/streamlit/pages/

# Deployment
ls infra/cloud-run/
```

## 🎯 Project Statistics

**Code:**
- Python files: 30+
- Lines of code: ~1,800
- Test files: 2
- Configuration files: 15+

**Documentation:**
- Markdown files: 20
- Total lines: ~8,200
- Quick starts: 4
- Complete guides: 10
- Reference docs: 2

**Infrastructure:**
- Dockerfiles: 3
- Cloud Build configs: 2
- Deployment scripts: 5
- Shell scripts: 8+

## ✨ Organization Benefits

**Before:**
- Cluttered root directory
- Hard to find documentation
- Unclear organization
- Mixed content

**After:**
- Clean root (3 MD files)
- Clear documentation hierarchy
- Easy navigation
- Purpose-based organization

**Improvement:**
- 78% less root clutter
- 6 clear doc categories
- 3 navigation aids
- 100% organized

---

**Navigate the project**:
- 📚 [Documentation Index](docs/INDEX.md)
- 🚀 [Quick Start](QUICKSTART.md)
- 🏠 [Main README](README.md)

**Last Updated**: December 27, 2024
