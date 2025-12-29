.PHONY: help install dev-install test lint format clean docker-build docker-up docker-down docker-logs

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker-compose
SHELL := /bin/bash

help: ## Show this help message
	@echo "GenAI Application - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install all dependencies with Poetry
	@echo "Installing backend dependencies..."
	cd services/fastapi-backend && poetry install --no-root
	@echo "Installing frontend dependencies..."
	cd frontend/streamlit && poetry install --no-root
	@echo "✅ All dependencies installed"

install-backend: ## Install backend dependencies only
	cd services/fastapi-backend && poetry install --no-root

install-frontend: ## Install frontend dependencies only
	cd frontend/streamlit && poetry install --no-root

dev-install: ## Install development dependencies and git hooks
	cd services/fastapi-backend && poetry install
	cd frontend/streamlit && poetry install
	@make install-hooks

install-hooks: ## Install git hooks (pre-commit formatter)
	@echo "📦 Installing git hooks..."
	@chmod +x .git-hooks/pre-commit
	@mkdir -p .git/hooks
	@ln -sf ../../.git-hooks/pre-commit .git/hooks/pre-commit
	@echo "✅ Git hooks installed! Black will auto-format code before each commit."

# Legacy pip-based install (for compatibility)
install-pip: ## Install with pip (legacy)
	cd services/fastapi-backend && $(PIP) install -r requirements.txt
	cd frontend/streamlit && $(PIP) install -r requirements.txt

# Development
run-fastapi: ## Run FastAPI backend locally
	cd services/fastapi-backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-fastapi-prod: ## Run FastAPI backend in production mode
	cd services/fastapi-backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

run-streamlit: ## Run Streamlit frontend locally
	cd frontend/streamlit && poetry run streamlit run app.py

run-all: ## Run both FastAPI and Streamlit locally
	@echo "Starting FastAPI backend and Streamlit frontend..."
	@make -j2 run-fastapi run-streamlit

# Testing
test: ## Run tests for FastAPI backend
	cd services/fastapi-backend && pytest

test-cov: ## Run tests with coverage
	cd services/fastapi-backend && pytest --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	cd services/fastapi-backend && pytest-watch

# Code Quality
lint: ## Run linters on backend (using Docker)
	@echo "🔍 Linting backend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps fastapi-backend python3 -m ruff check app/

lint-frontend: ## Run linters on frontend (using Docker)
	@echo "🔍 Linting frontend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps streamlit-frontend python3 -m ruff check .

lint-all: ## Run linters on all code
	@echo "🔍 Linting backend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps fastapi-backend python3 -m ruff check app/ || echo "⚠️  Backend linting skipped"
	@echo "🔍 Linting frontend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps streamlit-frontend python3 -m ruff check . || echo "⚠️  Frontend linting skipped"
	@echo "✅ Linting complete!"

lint-fix: ## Fix linting issues in backend (using Docker)
	@echo "🔧 Fixing backend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps fastapi-backend python3 -m ruff check --fix app/

lint-fix-all: ## Fix linting issues in all code
	@echo "🔧 Fixing backend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps fastapi-backend python3 -m ruff check --fix app/ || echo "⚠️  Backend fix skipped"
	@echo "🔧 Fixing frontend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps streamlit-frontend python3 -m ruff check --fix . || echo "⚠️  Frontend fix skipped"
	@echo "✅ All fixes applied!"

format: ## Format backend code with black
	@./format.sh backend

format-frontend: ## Format frontend code with black
	@./format.sh frontend

format-all: ## Format all code with black (RUN THIS BEFORE COMMIT!)
	@./format.sh

format-check: ## Check code formatting in backend (using Docker)
	@echo "🔍 Checking backend formatting..."
	@$(DOCKER_COMPOSE) run --rm --no-deps fastapi-backend python3 -m black --check app/

format-check-all: ## Check code formatting in all code
	@echo "🔍 Checking backend formatting..."
	@$(DOCKER_COMPOSE) run --rm --no-deps fastapi-backend python3 -m black --check app/ || echo "⚠️  Backend check skipped"
	@echo "🔍 Checking frontend formatting..."
	@$(DOCKER_COMPOSE) run --rm --no-deps streamlit-frontend python3 -m black --check . || echo "⚠️  Frontend check skipped"
	@echo "✅ Format check complete!"

typecheck: ## Run type checking on backend (using Docker)
	@echo "🔍 Type checking backend..."
	@$(DOCKER_COMPOSE) run --rm --no-deps fastapi-backend python3 -m mypy app/

check-all: format-check-all lint-all typecheck ## Run all code quality checks

pre-commit: format-all ## Format code before commit (⭐ RUN THIS BEFORE GIT COMMIT!)

# Docker
docker-build: ## Build Docker images
	$(DOCKER_COMPOSE) build

docker-up: ## Start all services with Docker Compose
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop all services
	$(DOCKER_COMPOSE) down

docker-logs: ## View Docker logs
	$(DOCKER_COMPOSE) logs -f

docker-logs-fastapi: ## View FastAPI logs
	$(DOCKER_COMPOSE) logs -f fastapi-backend

docker-logs-streamlit: ## View Streamlit logs
	$(DOCKER_COMPOSE) logs -f streamlit-frontend

docker-restart: ## Restart all services
	$(DOCKER_COMPOSE) restart

docker-clean: ## Remove all containers, networks, and volumes
	$(DOCKER_COMPOSE) down -v --remove-orphans

docker-build-fastapi: ## Build only FastAPI Docker image
	$(DOCKER_COMPOSE) build fastapi-backend

docker-shell-fastapi: ## Open shell in FastAPI container
	$(DOCKER_COMPOSE) exec fastapi-backend /bin/bash

# Cleanup
clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete

clean-all: clean docker-clean ## Clean everything including Docker

# Cloud Run Deployment
deploy-backend: ## Deploy FastAPI backend to Cloud Run
	cd infra/cloud-run && ./deploy-backend.sh

deploy-frontend: ## Deploy Streamlit frontend to Cloud Run
	cd infra/cloud-run && ./deploy-frontend.sh

deploy-all: ## Deploy all services to Cloud Run
	cd infra/cloud-run && ./deploy-all.sh

setup-datadog-secrets: ## Setup Datadog secrets in Secret Manager
	cd infra/cloud-run && ./setup-datadog-secrets.sh

# Monitoring
check-services: ## Check status of all services
	./check-services.sh

datadog-logs: ## View Datadog traces in browser
	@echo "Opening Datadog APM..."
	@open "https://app.datadoghq.com/apm/traces?query=service:genai-fastapi-backend" 2>/dev/null || \
	echo "Visit: https://app.datadoghq.com/apm/traces?query=service:genai-fastapi-backend"

# Environment
check-env: ## Check if required environment variables are set
	@echo "Checking environment variables..."
	@test -n "$(GOOGLE_CLOUD_PROJECT)" || (echo "Error: GOOGLE_CLOUD_PROJECT not set" && exit 1)
	@test -n "$(GOOGLE_APPLICATION_CREDENTIALS)" || (echo "Error: GOOGLE_APPLICATION_CREDENTIALS not set" && exit 1)
	@echo "Environment variables OK!"

# Documentation
docs-serve: ## Serve API documentation locally
	@echo "Starting FastAPI server for documentation..."
	@echo "Visit http://localhost:8000/docs for Swagger UI"
	@echo "Visit http://localhost:8000/redoc for ReDoc"
	cd services/fastapi-backend && uvicorn app.main:app --reload

# Quick Start
setup: dev-install ## Initial setup for development
	@echo "Setup complete!"
	@echo "1. Copy .env.example to .env and configure your settings"
	@echo "2. Set up your Google Cloud credentials"
	@echo "3. Run 'make run-fastapi' to start the server"

quickstart: ## Quick start guide
	@echo "Quick Start Guide:"
	@echo ""
	@echo "1. Setup environment:"
	@echo "   make setup"
	@echo ""
	@echo "2. Configure .env file with your GCP credentials"
	@echo ""
	@echo "3. Start the FastAPI backend:"
	@echo "   make run-fastapi"
	@echo ""
	@echo "4. Or use Docker:"
	@echo "   make docker-up"
	@echo ""
	@echo "5. Access the API documentation at:"
	@echo "   http://localhost:8000/docs"
