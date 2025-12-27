# 🚀 Production Deployment Plan

Complete plan for deploying the GenAI Application Platform to production with full CI/CD, testing, and monitoring.

## 📋 Overview

This document outlines the production deployment strategy including:
- Unit testing and test coverage
- GitHub Actions CI/CD pipelines
- Workload Identity Federation for secure GCP access
- Code quality checks and linting
- Deployment strategies
- Monitoring and alerting

## 🧪 Testing Strategy

### Backend Testing (FastAPI)

**Test Coverage Goals:**
- Unit Tests: 80%+ coverage
- Integration Tests: All endpoints
- E2E Tests: Critical workflows

**Test Structure:**
```
services/fastapi-backend/app/tests/
├── unit/
│   ├── test_models.py           # Pydantic model tests
│   ├── test_services.py         # Service logic tests
│   └── test_utils.py            # Utility function tests
├── integration/
│   ├── test_api_chat.py        # Chat endpoint tests
│   ├── test_api_generate.py    # Generation endpoint tests
│   └── test_api_vote_extraction.py  # Vote extraction tests
├── e2e/
│   └── test_vote_extraction_workflow.py  # Full workflow tests
├── fixtures/
│   ├── sample_images/          # Test images
│   └── expected_outputs/       # Expected results
└── conftest.py                 # Shared fixtures
```

**Test Categories:**

1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test API endpoints
3. **E2E Tests** - Test complete workflows
4. **Performance Tests** - Test under load
5. **Security Tests** - Test authentication

### Frontend Testing (Streamlit)

**Test Structure:**
```
frontend/streamlit/tests/
├── test_app.py                 # Main app tests
├── test_vote_extractor.py      # Vote extractor page tests
├── test_utils.py               # Utility tests
└── fixtures/
    └── mock_responses.json     # Mock API responses
```

## 🔄 GitHub Actions Workflows

### Workflow 1: Backend CI/CD

**File**: `.github/workflows/backend-ci-cd.yml`

**Triggers:**
- Push to `main` branch (paths: `services/fastapi-backend/**`)
- Pull requests (paths: `services/fastapi-backend/**`)
- Manual workflow dispatch

**Jobs:**
1. **Test** - Run pytest with coverage
2. **Lint** - Run ruff and black
3. **Type Check** - Run mypy
4. **Security Scan** - Check for vulnerabilities
5. **Build** - Build Docker image
6. **Deploy** - Deploy to Cloud Run (main branch only)

### Workflow 2: Frontend CI/CD

**File**: `.github/workflows/frontend-ci-cd.yml`

**Triggers:**
- Push to `main` branch (paths: `frontend/streamlit/**`)
- Pull requests (paths: `frontend/streamlit/**`)
- Manual workflow dispatch

**Jobs:**
1. **Lint** - Run ruff and black
2. **Build** - Build Docker image
3. **Deploy** - Deploy to Cloud Run (main branch only)

### Workflow 3: Code Quality

**File**: `.github/workflows/code-quality.yml`

**Triggers:**
- All pull requests
- Push to main

**Jobs:**
1. **Pre-commit** - Run all pre-commit hooks
2. **Security** - Dependency scanning
3. **Datadog Static Analysis** - Code quality checks

### Workflow 4: Full Deployment

**File**: `.github/workflows/deploy-all.yml`

**Triggers:**
- Manual workflow dispatch
- Tagged releases (v*)

**Jobs:**
1. Deploy backend
2. Deploy frontend
3. Run smoke tests
4. Notify on success/failure

## 🔐 Workload Identity Federation Setup

### Architecture

```
GitHub Actions → Workload Identity Pool → Service Account → GCP Resources
```

**Benefits:**
- ✅ No service account keys
- ✅ Temporary credentials
- ✅ Audit trail
- ✅ Principle of least privilege

### Setup Steps

1. **Create Workload Identity Pool**
2. **Create Workload Identity Provider**
3. **Create Service Account**
4. **Grant IAM permissions**
5. **Configure GitHub secrets**
6. **Update workflows**

See detailed guide in [docs/deployment/workload-identity-federation.md](docs/deployment/workload-identity-federation.md)

### Required GitHub Secrets

```
GCP_PROJECT_ID                  # Your GCP project ID
GCP_WORKLOAD_IDENTITY_PROVIDER  # projects/PROJECT_NUMBER/locations/global/...
GCP_SERVICE_ACCOUNT_EMAIL       # github-actions@PROJECT.iam.gserviceaccount.com
GCP_REGION                      # us-central1
DD_API_KEY                      # Datadog API key
DD_RUM_CLIENT_TOKEN             # Datadog RUM client token
DD_RUM_APPLICATION_ID           # Datadog RUM application ID
API_KEY                         # Backend API key
```

## 📊 Code Quality Checks

### Pre-commit Hooks

Already configured in `.pre-commit-config.yaml`:
- ✅ Trailing whitespace removal
- ✅ End of file fixer
- ✅ YAML/JSON validation
- ✅ Black formatting
- ✅ Ruff linting
- ✅ Import sorting

### CI/CD Checks

**Every PR must pass:**
- ✅ All tests (80%+ coverage)
- ✅ Black formatting
- ✅ Ruff linting (no errors)
- ✅ Mypy type checking (no errors)
- ✅ Security scan (no critical/high)
- ✅ Datadog Static Analysis

### Code Review Requirements

- ✅ 1+ approvals required
- ✅ All checks must pass
- ✅ No merge conflicts
- ✅ Branch up to date with main

## 🚢 Deployment Strategy

### Environments

1. **Development** - Local Docker Compose
2. **Staging** - Cloud Run (from `develop` branch)
3. **Production** - Cloud Run (from `main` branch / tags)

### Deployment Process

**Automated (via GitHub Actions):**
```
1. Push to main
2. Run all tests
3. Build Docker images
4. Push to Container Registry
5. Deploy to Cloud Run
6. Run smoke tests
7. Notify team
```

**Manual (via scripts):**
```bash
cd infra/cloud-run
./deploy-all.sh
```

### Rollback Strategy

**Automated:**
- GitHub Actions can revert failed deployments
- Cloud Run keeps all revisions

**Manual:**
```bash
# List revisions
gcloud run revisions list --service genai-fastapi-backend

# Rollback
gcloud run services update-traffic genai-fastapi-backend \
    --to-revisions PREVIOUS_REVISION=100
```

## 📈 Monitoring & Alerting

### Key Metrics to Monitor

**Application Health:**
- Uptime/availability
- Request rate
- Error rate
- Latency (p50, p95, p99)

**Business Metrics:**
- Vote extractions per day
- Success rate
- Average processing time
- User sessions (RUM)

**Cost Metrics:**
- Cloud Run costs
- Vertex AI token usage
- Datadog costs

### Alerts to Configure

**Critical (PagerDuty/SMS):**
- Service down (5+ minutes)
- Error rate > 10%
- Response time > 30s (p95)

**Warning (Slack):**
- Error rate > 5%
- Response time > 10s (p95)
- Token usage > 1M/hour

**Info (Email):**
- Deployment completed
- New version deployed
- Daily usage report

## 🔒 Security Checklist

### Before Production

- [ ] API key authentication enabled
- [ ] Secrets in Secret Manager (not env vars)
- [ ] CORS properly configured
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (if DB added)
- [ ] XSS prevention
- [ ] HTTPS only
- [ ] Security headers configured
- [ ] Dependency scanning enabled
- [ ] Container scanning enabled

### Ongoing

- [ ] Regular dependency updates
- [ ] Monthly security reviews
- [ ] Quarterly penetration testing
- [ ] Key rotation (90 days)
- [ ] Access audit (monthly)

## 💰 Cost Optimization

### Cloud Run

**Right-sizing:**
- Backend: 2 vCPU, 2GB RAM (adjust based on load)
- Frontend: 1 vCPU, 1GB RAM

**Auto-scaling:**
- Min instances: 0 (scale to zero)
- Max instances: 10 (prevent runaway costs)
- Concurrency: 80 (requests per instance)

**Optimization:**
```bash
# Set resource limits
gcloud run services update SERVICE \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5 \
    --min-instances 0 \
    --concurrency 80
```

### Vertex AI

**Token optimization:**
- Use appropriate models (gemini-2.5-flash for speed)
- Optimize prompts (shorter = cheaper)
- Cache common responses
- Set max_tokens appropriately

### Datadog

**Cost controls:**
- Sample traces (10-20% in high traffic)
- Set log retention (30-90 days)
- Archive old data
- Use filters to reduce ingestion

## 📅 Deployment Schedule

### Regular Deployments

- **Feature deployments**: As needed (via PR → main)
- **Security patches**: Within 24 hours
- **Dependency updates**: Weekly
- **Major releases**: Monthly

### Deployment Windows

- **Staging**: Anytime
- **Production**: Business hours (avoid weekends)
- **Emergency fixes**: Anytime with approval

### Release Process

1. Create release branch from main
2. Run full test suite
3. Deploy to staging
4. QA testing
5. Tag release (v1.2.3)
6. Deploy to production
7. Monitor for 1 hour
8. Update documentation

## 🎯 Success Criteria

### Performance

- ✅ 99.9% uptime
- ✅ < 500ms response time (p95) for API
- ✅ < 30s for vote extraction
- ✅ < 2s page load time (frontend)

### Quality

- ✅ 80%+ test coverage
- ✅ 0 critical security issues
- ✅ < 1% error rate
- ✅ All code reviewed

### Business

- ✅ 95%+ extraction accuracy
- ✅ Support 100+ extractions/day
- ✅ < 1% user-reported bugs

## 📚 Production Runbooks

### Incident Response

1. **Alert received** → Check Datadog
2. **Identify issue** → Review traces/logs
3. **Quick fix?** → Hotfix branch
4. **Not fixable?** → Rollback
5. **Post-incident** → Write postmortem

### Common Issues

**High Error Rate:**
1. Check Datadog error tracking
2. Review recent deployments
3. Check Vertex AI quotas
4. Review logs for patterns
5. Rollback if needed

**Slow Performance:**
1. Check Datadog APM traces
2. Identify bottlenecks
3. Check Vertex AI latency
4. Scale up if needed
5. Optimize code if needed

**High Costs:**
1. Check Cloud Run metrics
2. Review Vertex AI token usage
3. Check for runaway loops
4. Adjust scaling limits
5. Optimize prompts

## 🔧 Infrastructure as Code

### Terraform (Future)

```
infra/terraform/
├── main.tf              # Main configuration
├── cloud-run.tf         # Cloud Run services
├── secrets.tf           # Secret Manager
├── iam.tf               # IAM bindings
├── monitoring.tf        # Monitoring config
└── variables.tf         # Variables
```

### Benefits

- ✅ Version controlled infrastructure
- ✅ Reproducible environments
- ✅ Easy to create staging/prod
- ✅ Disaster recovery

## 📝 Documentation Requirements

### For Production

- [ ] API documentation (OpenAPI)
- [ ] User guide
- [ ] Admin guide
- [ ] Runbooks
- [ ] Architecture diagrams
- [ ] Disaster recovery plan
- [ ] Security procedures
- [ ] Incident response plan

### Keep Updated

- [ ] README.md
- [ ] CHANGELOG.md
- [ ] API versions
- [ ] Deployment guide
- [ ] Troubleshooting guide

## 🎓 Team Training

### Required Knowledge

**Developers:**
- FastAPI and Streamlit
- Google Vertex AI
- Docker and Poetry
- Git workflow
- Testing practices

**DevOps:**
- Cloud Run deployment
- GitHub Actions
- Workload Identity
- Monitoring (Datadog)
- Secret management

**SRE:**
- Incident response
- Performance optimization
- Cost optimization
- Security practices

## ✅ Production Readiness Checklist

### Code

- [ ] All tests passing (80%+ coverage)
- [ ] No critical linter errors
- [ ] Type checking passes
- [ ] Security scan clean
- [ ] Documentation complete

### Infrastructure

- [ ] Workload Identity configured
- [ ] Secrets in Secret Manager
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Logging enabled
- [ ] Backups configured (if applicable)

### Security

- [ ] API keys rotated
- [ ] IAM least privilege
- [ ] CORS configured
- [ ] Rate limiting enabled
- [ ] Input validation
- [ ] Security headers

### Monitoring

- [ ] Datadog APM enabled
- [ ] LLM Observability enabled
- [ ] RUM enabled
- [ ] Dashboards created
- [ ] Alerts configured
- [ ] On-call rotation set

### Documentation

- [ ] User guide published
- [ ] API docs accessible
- [ ] Runbooks written
- [ ] Architecture documented
- [ ] Incident response plan

### Compliance

- [ ] Data privacy reviewed
- [ ] Terms of service
- [ ] Privacy policy
- [ ] Data retention policy
- [ ] Audit logging enabled

## 🎯 Next Steps

1. **Implement unit tests** - See test examples
2. **Setup GitHub Actions** - Use workflow templates
3. **Configure Workload Identity** - Follow setup guide
4. **Enable monitoring** - Configure all alerts
5. **Document procedures** - Write runbooks
6. **Train team** - Knowledge transfer
7. **Dry run deployment** - Test in staging
8. **Go live** - Production deployment

## 📖 Related Documentation

- [Testing Guide](docs/testing/README.md)
- [GitHub Actions Setup](docs/deployment/github-actions.md)
- [Workload Identity Guide](docs/deployment/workload-identity-federation.md)
- [Monitoring Guide](docs/monitoring/DATADOG_SETUP.md)
- [Runbooks](docs/runbooks/)

---

**Status**: Planning Phase  
**Target Go-Live**: 2-4 weeks  
**Next Action**: Implement testing and CI/CD

