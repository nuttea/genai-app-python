# AI Agent Instructions - GenAI Application Platform

## Project Overview

This is a production-ready GenAI application platform for Thai election vote extraction using Google Vertex AI/Gemini models, deployed on Google Cloud Run with comprehensive Datadog observability.

## Core Technologies

- **Backend**: FastAPI (Python 3.11+) with uv
- **Frontend**: Streamlit with Datadog RUM
- **LLM**: Google Vertex AI / Gemini 2.5 Flash
- **Infrastructure**: Google Cloud Run (serverless)
- **Monitoring**: Datadog APM, LLM Observability, RUM
- **CI/CD**: GitHub Actions with Workload Identity
- **Containerization**: Docker with multi-stage builds

## Architecture Principles

1. **Serverless-First**: All services run on Cloud Run for automatic scaling
2. **Observability-First**: Full Datadog integration (APM, LLMObs, RUM, Profiling)
3. **Security-First**: API key authentication, Secret Manager, Workload Identity
4. **Documentation-First**: Comprehensive docs with quickstarts and troubleshooting

## Code Style & Standards

### Python
- Use **type hints** for all function parameters and returns
- Follow **PEP 8** with **Black formatting** (Line length: 100, Python 3.11)
- **⚠️ CRITICAL**: Always run Black formatter before committing (see Pre-Commit Process below)
- Use **Pydantic** for data validation and settings
- **Async/await** for I/O operations
- **uv** for dependency management (fast Python package installer)
- **Structured logging** with JSON format for Datadog

### FastAPI Backend
- **Endpoints**: RESTful with clear versioning (`/api/v1/`)
- **Error handling**: HTTPException with structured error responses
- **Validation**: Pydantic models for request/response
- **Rate limiting**: Applied to sensitive endpoints
- **Health checks**: Always include `/health` endpoint
- **API docs**: Use FastAPI's automatic OpenAPI documentation

### Streamlit Frontend
- **Session state**: Proper use of `st.session_state` for state management
- **Caching**: Use `@st.cache_data` and `@st.cache_resource` appropriately
- **Error handling**: User-friendly error messages with `st.error()`
- **Loading states**: Show spinners/progress for long operations
- **Responsive design**: Mobile-friendly layouts

### LLM Integration
- **Default model**: `gemini-2.5-flash` (fast, cost-effective)
- **Temperature**: `0.0` for structured extraction (deterministic)
- **Max tokens**: `16384` default (supports up to 65536)
- **Structured output**: Always use `response_schema` for JSON responses
- **Error handling**: Retry with exponential backoff
- **Observability**: Datadog LLMObs tracing for all LLM calls

## File Patterns

### Never Modify
- `.github/workflows/*.yml` - CI/CD workflows (unless explicitly requested)
- `LICENSE` - Project license
- `.gitignore` - Git ignore patterns
- `static-analysis.datadog.yml` - Datadog static analysis config

### Always Update
- `docs/` - Keep documentation in sync with code changes
- Tests when adding new features
- `CHANGELOG.md` or commit messages with clear descriptions

### Backend Structure
```
services/fastapi-backend/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── core/                 # Core utilities (security, rate limiting, etc.)
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   ├── config.py             # Settings (environment-based)
│   └── main.py               # FastAPI app initialization
├── tests/                    # Pytest tests
├── pyproject.toml            # uv dependencies (PEP 621)
└── Dockerfile.cloudrun       # Production Dockerfile
```

### Frontend Structure
```
frontend/streamlit/
├── app.py                    # Main Streamlit app
├── pages/                    # Multi-page app pages
├── pyproject.toml            # uv dependencies (PEP 621)
└── Dockerfile                # Production Dockerfile
```

## ⚠️ Pre-Commit Process (REQUIRED)

**CRITICAL**: Always format code with Black before committing. CI/CD will fail if code is not formatted.

### 🚀 Quick Commands (Recommended)

Use these Cursor custom commands for the fastest workflow:

```bash
# Complete workflow: Format, lint, commit, and push
make lint-commit-push MSG="feat: Add new feature"

# Or using the script directly
./scripts/lint-commit-push.sh "feat: Add new feature"

# Format only (no commit)
make format-only

# Quick push with auto-generated message (for small changes)
make quick-push
```

📖 **See [CURSOR_COMMANDS.md](./CURSOR_COMMANDS.md) for detailed usage and examples.**

### Manual Process (Alternative)

If you prefer manual control or the scripts don't work:

**1. Format All Code (Required)**
```bash
# Backend
cd services/fastapi-backend
poetry run black app/
cd ../..

# Frontend
cd frontend/streamlit
poetry run black .
cd ../..
```

**2. Optional: Lint Check**
```bash
# Backend
cd services/fastapi-backend
poetry run ruff check --fix app/
cd ../..

# Frontend
cd frontend/streamlit
poetry run ruff check --fix .
cd ../..
```

**3. Commit & Push**
```bash
git add -A
git commit -m "your message"
git push
```

### Quick Reference

- **One-liner**: See `PRE-COMMIT-CHECKLIST.md` for copy-paste commands
- **Makefile**: `make pre-commit` (formats all code)
- **CI/CD Check**: `.github/workflows/fastapi-backend.yml` runs `black --check`

### If CI/CD Fails (Formatting Error)

If GitHub Actions fails with "Run Black (check only)" error:

1. Format the code locally (commands above)
2. Commit and push the formatting fix
3. CI/CD will automatically re-run and pass

See `FIX_CI_FORMATTING.md` for detailed troubleshooting.

### Important Files

- `PRE-COMMIT-CHECKLIST.md` - Manual formatting checklist
- `BLACK_FORMATTING_SETUP.md` - Complete Black setup documentation
- `FIX_CI_FORMATTING.md` - How to fix CI/CD formatting failures
- `.git-hooks/` - Optional pre-commit hooks (may not work in all environments)

## Common Tasks

### Adding a New API Endpoint
1. Create/update model in `app/models/`
2. Add business logic in `app/services/`
3. Create endpoint in `app/api/v1/endpoints/`
4. Add tests in `tests/`
5. Update documentation in `docs/api/`

### Adding a New Environment Variable
1. Add to `app/config.py` with Pydantic Field
2. Update `docker-compose.yml` for local dev
3. Update `.github/workflows/*.yml` for CI/CD
4. Document in `docs/reference/environment-variables.md`

### LLM Configuration Changes
1. Update `app/models/vote_extraction.py` for LLMConfig
2. Update frontend in `pages/1_🗳️_Vote_Extractor.py`
3. Test with different models/parameters
4. Document in `docs/features/LLM_CONFIGURATION.md`

### Troubleshooting Common Issues
- **CI/CD formatting failure**: Run Black formatter before committing (see `FIX_CI_FORMATTING.md`)
- **JSON parsing errors**: Check `max_tokens` limit (see `docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md`)
- **Model listing returns 0**: Expected with Vertex AI (see `docs/investigations/MODELS_API_FINDINGS.md`)
- **Docker startup errors**: Check `docker-compose.yml` overrides (see `docs/reference/DOCKER_FIX_LOCAL_DEV.md`)
- **Poetry/Black not working**: Check environment setup, may need `scfw run poetry` wrapper

## Testing

### Backend Tests
```bash
cd services/fastapi-backend
poetry run pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend/streamlit
poetry run pytest tests/ -v
```

### Integration Tests
```bash
# Start services
docker-compose up -d

# Run test scripts
python scripts/tests/test_dynamic_models.py
```

## Deployment

### Local Development
```bash
docker-compose up -d
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

### Cloud Run (via CI/CD)
- **Dev**: Push to `main` branch → deploys with `DD_ENV=dev`
- **Prod**: Merge `main` to `prod` → deploys with `DD_ENV=prod` and `--tag prod`

### Manual Deployment
```bash
# Backend
./infra/cloud-run/deploy-backend.sh

# Frontend
./infra/cloud-run/deploy-frontend.sh
```

## Documentation

### Structure
- **Root**: Core project docs (README, QUICKSTART, PROJECT_PLAN)
- **docs/getting-started/**: Quick starts and setup guides
- **docs/deployment/**: Cloud Run and production deployment
- **docs/troubleshooting/**: Problem-solving guides
- **docs/investigations/**: Research findings
- **docs/reference/**: Technical reference
- **scripts/tests/**: Test scripts

### When to Update
- **New feature**: Add to `docs/features/`
- **API change**: Update `docs/api/` and OpenAPI docs
- **New config**: Update `docs/reference/environment-variables.md`
- **Bug fix**: Consider adding to `docs/troubleshooting/`
- **Investigation**: Document findings in `docs/investigations/`

## Best Practices

### Security
- ✅ Never commit secrets (use Secret Manager)
- ✅ Always validate user input with Pydantic
- ✅ Use API key authentication for sensitive endpoints
- ✅ Implement rate limiting on public endpoints
- ✅ Use CORS with specific origins (not `*` in production)

### Performance
- ✅ Use async/await for I/O operations
- ✅ Cache expensive operations (LLM model listing, etc.)
- ✅ Set appropriate timeouts (5s for API calls)
- ✅ Use Cloud Run min instances = 0 to save costs
- ✅ Monitor with Datadog and optimize based on metrics

### Observability
- ✅ Add Datadog span tags for important operations
- ✅ Use structured logging (JSON) for Datadog
- ✅ Set `DD_ENV`, `DD_VERSION`, `DD_SERVICE` for all deployments
- ✅ Enable LLMObs for all LLM interactions
- ✅ Use RUM for frontend monitoring

### Code Quality
- ✅ **Format with Black BEFORE every commit** (CI/CD requirement)
- ✅ Write type hints for all functions
- ✅ Add docstrings for public APIs
- ✅ Write tests for new features
- ✅ Run linters (Ruff) to catch code issues
- ✅ Keep functions small and focused
- ✅ Check `PRE-COMMIT-CHECKLIST.md` before committing

## Important Notes

### LLM Models
- **Vertex AI**: Use for production (GCP authentication, no API key needed)
- **Google AI API**: Optional for dynamic model listing (requires `GEMINI_API_KEY`)
- **Static list**: Recommended for reliability (see `docs/investigations/`)

### Token Limits
- **Default**: 16,384 tokens (handles 5-6 pages)
- **Maximum**: 65,536 tokens (Gemini 2.5 Flash)
- **Adjust**: Based on document size (see `docs/troubleshooting/`)

### Environment-Specific Behavior
- **Development** (`DD_ENV=dev`): Verbose logging, debug enabled
- **Production** (`DD_ENV=prod`): INFO logging, debug disabled
- **Local Docker**: Overrides for hot-reloading (no datadog-init)

## Getting Help

1. **Pre-Commit Issues**: Check `PRE-COMMIT-CHECKLIST.md` or `FIX_CI_FORMATTING.md`
2. **Documentation**: Check `DOCUMENTATION_MAP.md` for navigation
3. **Troubleshooting**: See `docs/troubleshooting/`
4. **Investigations**: See `docs/investigations/`
5. **Tests**: Run `scripts/tests/` scripts
6. **Logs**: `docker logs genai-fastapi-backend --tail 100`

## Version Info

- **Python**: 3.11+
- **FastAPI**: Latest stable
- **Streamlit**: Latest stable
- **Gemini**: 2.5 Flash (default)
- **Datadog**: APM + LLMObs + RUM

---

**When in doubt, check the documentation first!**

**Priority order:**
1. **Before committing**: `PRE-COMMIT-CHECKLIST.md` - Format code with Black
2. `QUICKSTART.md` - Get started
3. `DOCUMENTATION_MAP.md` - Find relevant docs
4. `FIX_CI_FORMATTING.md` - Fix CI/CD formatting failures
5. `docs/troubleshooting/` - Fix issues
6. `docs/investigations/` - Understand findings

**⚠️ REMEMBER**: Always format with Black before committing!
