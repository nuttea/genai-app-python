# GenAI Application Project Plan

## Overview
A comprehensive GenAI application platform using Google Vertex AI, structured as a monorepo to support multiple services and components.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      GenAI Platform                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Next.js    │  │   FastAPI    │  │ TypeScript   │      │
│  │   Frontend   │◄─┤   Backend    │◄─┤ MCP Server   │      │
│  │              │  │              │  │              │      │
│  └──────────────┘  └──────┬───────┘  └──────────────┘      │
│                           │                                  │
│                           ▼                                  │
│                    ┌──────────────┐                         │
│                    │  Vertex AI   │                         │
│                    │  Google Cloud│                         │
│                    └──────────────┘                         │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │   Jupyter Notebooks (Prototyping & Research)    │        │
│  └─────────────────────────────────────────────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Proposed Project Structure

```
genai-app-python/
├── README.md                          # Main project documentation
├── PROJECT_PLAN.md                    # This file
├── docker-compose.yml                 # Orchestrate all services
├── .gitignore                         # Global gitignore
├── .env.example                       # Example environment variables
│
├── services/                          # All backend services
│   │
│   ├── fastapi-backend/              # Python FastAPI + Vertex AI
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── pyproject.toml            # Poetry or modern Python packaging
│   │   ├── .env.example
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py               # FastAPI entry point
│   │   │   ├── config.py             # Configuration management
│   │   │   ├── api/                  # API routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── v1/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── endpoints/
│   │   │   │   │   │   ├── chat.py
│   │   │   │   │   │   ├── generate.py
│   │   │   │   │   │   └── health.py
│   │   │   │   │   └── router.py
│   │   │   ├── services/             # Business logic
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vertex_ai.py     # Vertex AI integration
│   │   │   │   └── genai_service.py
│   │   │   ├── models/               # Pydantic models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── requests.py
│   │   │   │   └── responses.py
│   │   │   ├── core/                 # Core utilities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── security.py
│   │   │   │   └── logging.py
│   │   │   └── tests/
│   │   │       ├── __init__.py
│   │   │       ├── conftest.py
│   │   │       └── test_api/
│   │   └── scripts/
│   │       └── start.sh
│   │
│   └── mcp-server/                   # TypeScript MCP Server (Future)
│       ├── Dockerfile
│       ├── package.json
│       ├── tsconfig.json
│       ├── src/
│       │   ├── index.ts
│       │   ├── server.ts
│       │   └── handlers/
│       └── tests/
│
├── frontend/                          # Next.js Frontend (Future)
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   └── public/
│
├── notebooks/                         # Jupyter Notebooks for prototyping
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── research/
│   │   └── vertex_ai_exploration.ipynb
│   ├── experiments/
│   └── data/
│
├── shared/                            # Shared utilities and types
│   ├── python/
│   │   └── common/
│   └── typescript/
│       └── types/
│
├── infra/                            # Infrastructure as Code
│   ├── kubernetes/
│   │   ├── fastapi-deployment.yaml
│   │   ├── mcp-deployment.yaml
│   │   └── frontend-deployment.yaml
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── gcp.tf
│   │   └── variables.tf
│   └── scripts/
│       └── deploy.sh
│
├── docs/                             # Documentation
│   ├── api/
│   │   └── openapi.yaml
│   ├── architecture.md
│   ├── deployment.md
│   └── development.md
│
└── .github/                          # CI/CD
    └── workflows/
        ├── fastapi-ci.yml
        ├── mcp-ci.yml
        └── frontend-ci.yml
```

## Phase 1: FastAPI Backend with Vertex AI (Current)

### Technology Stack
- **Framework**: FastAPI
- **Server**: Uvicorn
- **GenAI SDK**: Google Vertex AI Python SDK
- **Container**: Docker
- **Python Version**: 3.11+
- **Dependencies**: 
  - `fastapi`
  - `uvicorn[standard]`
  - `google-cloud-aiplatform`
  - `pydantic`
  - `python-dotenv`
  - `httpx`

### Key Features to Implement
1. **Health Check Endpoint**: `/health` and `/ready`
2. **Chat Completion**: `/api/v1/chat/completions`
3. **Text Generation**: `/api/v1/generate`
4. **Streaming Support**: Server-Sent Events (SSE)
5. **Error Handling**: Comprehensive error responses
6. **Logging**: Structured logging
7. **CORS**: Configurable CORS middleware
8. **Authentication**: API key validation (optional)

### Docker Configuration
- Multi-stage build for optimization
- Non-root user for security
- Health checks
- Environment variable configuration
- Volume mounts for development

## Phase 2: MCP Server (Future)

### Technology Stack
- **Runtime**: Node.js / Bun
- **Language**: TypeScript
- **MCP SDK**: Model Context Protocol SDK
- **Communication**: WebSocket / HTTP

### Purpose
- Handle context management for AI models
- Provide structured context to the FastAPI backend
- Manage conversation history and state

## Phase 3: Next.js Frontend (Future)

### Technology Stack
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand / React Query
- **UI Components**: shadcn/ui or Radix UI

### Features
- Chat interface
- Real-time streaming responses
- Conversation history
- Model selection and configuration
- Responsive design

## Phase 4: Jupyter Notebooks (Future)

### Purpose
- Prototype new GenAI features
- Experiment with Vertex AI models
- Data analysis and visualization
- Model evaluation and testing

### Setup
- JupyterLab environment
- Shared Python packages with FastAPI
- Access to GCP credentials
- Git-friendly notebook format (optional: jupytext)

## Development Workflow

### Local Development
1. **FastAPI Backend**:
   ```bash
   cd services/fastapi-backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Docker Development**:
   ```bash
   docker-compose up fastapi-backend
   ```

3. **Full Stack** (when all services are ready):
   ```bash
   docker-compose up
   ```

### Environment Variables
- `GOOGLE_CLOUD_PROJECT`: GCP Project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `VERTEX_AI_LOCATION`: GCP region (e.g., us-central1)
- `FASTAPI_ENV`: development/staging/production
- `LOG_LEVEL`: debug/info/warning/error
- `CORS_ORIGINS`: Allowed CORS origins

## Testing Strategy

### Backend Testing
- **Unit Tests**: pytest
- **Integration Tests**: TestClient from FastAPI
- **E2E Tests**: pytest with actual Vertex AI calls (in staging)
- **Load Testing**: locust or k6

### Frontend Testing (Future)
- **Unit Tests**: Vitest
- **Component Tests**: React Testing Library
- **E2E Tests**: Playwright

## Deployment Strategy

### Container Registry
- Google Artifact Registry
- Docker Hub (alternative)

### Orchestration Options
1. **Development**: Docker Compose
2. **Production**:
   - Google Cloud Run (serverless, easiest)
   - Google Kubernetes Engine (GKE)
   - Self-hosted Kubernetes

### CI/CD Pipeline
- Build and test on every PR
- Automated Docker image builds
- Deploy to staging on merge to main
- Manual approval for production deployment

## Security Considerations

1. **Secrets Management**:
   - Use Google Secret Manager
   - Never commit credentials
   - Use service accounts with minimal permissions

2. **API Security**:
   - Rate limiting
   - API key authentication
   - Input validation
   - CORS configuration

3. **Container Security**:
   - Non-root users
   - Minimal base images
   - Regular security updates
   - Vulnerability scanning

## Monitoring & Observability

- **Logging**: Structured JSON logs
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Error Tracking**: Sentry or GCP Error Reporting
- **APM**: Google Cloud Monitoring

## Cost Optimization

1. Use Cloud Run for auto-scaling
2. Implement request caching
3. Set Vertex AI quotas and limits
4. Monitor API usage
5. Use spot instances for non-critical workloads

## Next Steps

1. ✅ Review and approve this project plan
2. Create the FastAPI backend structure
3. Implement Docker configuration
4. Set up local development environment
5. Create initial API endpoints
6. Integrate Vertex AI SDK
7. Add comprehensive documentation
8. Set up CI/CD pipeline
9. Deploy to staging environment
10. Plan for subsequent phases

## Timeline Estimation

- **Phase 1** (FastAPI Backend): 1-2 weeks
  - Initial setup: 2-3 days
  - API implementation: 3-5 days
  - Docker & deployment: 2-3 days
  - Testing & documentation: 2-3 days

- **Phase 2** (MCP Server): 1 week
- **Phase 3** (Frontend): 2-3 weeks
- **Phase 4** (Notebooks): 3-5 days

## Questions to Consider

1. Which Vertex AI models do you plan to use? (Gemini, PaLM, etc.)
2. Do you need authentication for the API?
3. What's your preferred GCP region?
4. Do you have a GCP project set up?
5. Any specific GenAI features you want to prioritize?
6. What's the expected API traffic/scale?

---

**Last Updated**: December 26, 2025
**Status**: Planning Phase

