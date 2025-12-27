# GitHub Configuration

This directory contains GitHub-specific configuration files for CI/CD workflows.

## Planned Workflows

### Backend CI/CD
- Run tests on pull requests
- Deploy to Cloud Run on merge to main
- Security scanning
- Dependency updates

### Frontend CI/CD
- Build and test frontend
- Deploy to Cloud Run
- Preview deployments for PRs

### Code Quality
- Linting and formatting checks
- Type checking
- Test coverage reports

## Setup

GitHub Actions workflows will be added in future phases.

For now, use Cloud Build for CI/CD:
- [services/fastapi-backend/cloudbuild.yaml](../services/fastapi-backend/cloudbuild.yaml)
- [frontend/streamlit/cloudbuild.yaml](../frontend/streamlit/cloudbuild.yaml)

See [docs/deployment/CLOUD_RUN_DEPLOYMENT.md](../docs/deployment/CLOUD_RUN_DEPLOYMENT.md#cicd-with-cloud-build) for setup instructions.

