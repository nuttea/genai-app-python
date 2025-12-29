# AI Agent Instructions - GenAI Application Platform

## Project Overview

This is a production-ready GenAI application platform for Thai election vote extraction using Google Vertex AI/Gemini models, deployed on Google Cloud Run with comprehensive Datadog observability.

## Core Technologies

- **Backend**: FastAPI (Python 3.11+) with Poetry
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
- Follow **PEP 8** with Black formatting
- Use **Pydantic** for data validation and settings
- **Async/await** for I/O operations
- **Poetry** for dependency management (no pip install directly)
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
├── pyproject.toml            # Poetry dependencies
└── Dockerfile.cloudrun       # Production Dockerfile
```

### Frontend Structure
```
frontend/streamlit/
├── app.py                    # Main Streamlit app
├── pages/                    # Multi-page app pages
├── pyproject.toml            # Poetry dependencies
└── Dockerfile                # Production Dockerfile
```

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
- **JSON parsing errors**: Check `max_tokens` limit (see `docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md`)
- **Model listing returns 0**: Expected with Vertex AI (see `docs/investigations/MODELS_API_FINDINGS.md`)
- **Docker startup errors**: Check `docker-compose.yml` overrides (see `docs/reference/DOCKER_FIX_LOCAL_DEV.md`)

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
- ✅ Write type hints for all functions
- ✅ Add docstrings for public APIs
- ✅ Write tests for new features
- ✅ Use Black for formatting
- ✅ Run linters before committing
- ✅ Keep functions small and focused

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

1. **Documentation**: Check `DOCUMENTATION_MAP.md` for navigation
2. **Troubleshooting**: See `docs/troubleshooting/`
3. **Investigations**: See `docs/investigations/`
4. **Tests**: Run `scripts/tests/` scripts
5. **Logs**: `docker logs genai-fastapi-backend --tail 100`

## Version Info

- **Python**: 3.11+
- **FastAPI**: Latest stable
- **Streamlit**: Latest stable
- **Gemini**: 2.5 Flash (default)
- **Datadog**: APM + LLMObs + RUM

---

**When in doubt, check the documentation first!**

**Priority order:**
1. `QUICKSTART.md` - Get started
2. `DOCUMENTATION_MAP.md` - Find relevant docs
3. `docs/troubleshooting/` - Fix issues
4. `docs/investigations/` - Understand findings

