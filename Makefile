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
install: ## Install all dependencies with uv
	@echo "Installing backend dependencies..."
	cd services/fastapi-backend && uv sync --no-dev
	@echo "Installing frontend dependencies..."
	cd frontend/streamlit && uv sync --no-dev
	@echo "✅ All dependencies installed"

install-backend: ## Install backend dependencies only
	cd services/fastapi-backend && uv sync --no-dev

install-frontend: ## Install frontend dependencies only
	cd frontend/streamlit && uv sync --no-dev

dev-install: ## Install development dependencies and git hooks
	cd services/fastapi-backend && uv sync
	cd frontend/streamlit && uv sync
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
	cd services/fastapi-backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-fastapi-prod: ## Run FastAPI backend in production mode
	cd services/fastapi-backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

run-streamlit: ## Run Streamlit frontend locally
	cd frontend/streamlit && uv run streamlit run app.py

run-content-creator: ## Run Content Creator service locally
	cd services/adk-content-creator && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

run-all: ## Run all services locally (FastAPI, Streamlit, Content Creator)
	@echo "Starting all services..."
	@make -j3 run-fastapi run-streamlit run-content-creator

# Testing
test: ## Run tests for FastAPI backend
	cd services/fastapi-backend && pytest

test-cov: ## Run tests with coverage
	cd services/fastapi-backend && pytest --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	cd services/fastapi-backend && pytest-watch

# Code Quality
lint: ## Run linters on backend (manual: cd services/fastapi-backend && uv run ruff check app/)
	@echo "🔍 To lint backend, run:"
	@echo "   cd services/fastapi-backend && uv run ruff check app/"

lint-frontend: ## Run linters on frontend (manual: cd frontend/streamlit && uv run ruff check .)
	@echo "🔍 To lint frontend, run:"
	@echo "   cd frontend/streamlit && uv run ruff check ."

lint-all: ## Run linters on all code (see PRE-COMMIT-CHECKLIST.md)
	@echo "🔍 To lint all code, run:"
	@echo ""
	@echo "Backend:"
	@echo "  cd services/fastapi-backend && uv run ruff check app/"
	@echo ""
	@echo "Frontend:"
	@echo "  cd frontend/streamlit && uv run ruff check ."
	@echo ""
	@echo "See PRE-COMMIT-CHECKLIST.md for more details"

lint-fix: ## Fix linting issues in backend (manual: cd services/fastapi-backend && uv run ruff check --fix app/)
	@echo "🔧 To fix backend linting issues, run:"
	@echo "   cd services/fastapi-backend && uv run ruff check --fix app/"

lint-fix-all: ## Fix linting issues in all code
	@echo "🔧 To fix linting issues, run:"
	@echo ""
	@echo "Backend:"
	@echo "  cd services/fastapi-backend && uv run ruff check --fix app/"
	@echo ""
	@echo "Frontend:"
	@echo "  cd frontend/streamlit && uv run ruff check --fix ."

format: ## Format backend code with black
	@./scripts/format.sh backend

format-frontend: ## Format frontend code with black
	@./scripts/format.sh frontend

format-all: ## Format all code with black (RUN THIS BEFORE COMMIT!)
	@./scripts/format.sh

format-check: ## Check backend formatting (manual: cd services/fastapi-backend && uv run black --check app/)
	@echo "🔍 To check backend formatting, run:"
	@echo "   cd services/fastapi-backend && uv run black --check app/"

format-check-all: ## Check all code formatting
	@echo "🔍 To check formatting, run:"
	@echo ""
	@echo "Backend:"
	@echo "  cd services/fastapi-backend && uv run black --check app/"
	@echo ""
	@echo "Frontend:"
	@echo "  cd frontend/streamlit && uv run black --check ."

typecheck: ## Run type checking on backend (manual: cd services/fastapi-backend && uv run mypy app/)
	@echo "🔍 To run type checking, run:"
	@echo "   cd services/fastapi-backend && uv run mypy app/"

check-all: ## Show all code quality check commands
	@echo "🔍 Code Quality Checks"
	@echo ""
	@echo "1. Format Check:"
	@make format-check-all
	@echo ""
	@echo "2. Linting:"
	@make lint-all
	@echo ""
	@echo "3. Type Check:"
	@make typecheck

pre-commit: format-all ## ⭐ Format code before commit (RUN THIS BEFORE GIT COMMIT!)

# Cursor Custom Commands (Convenience Shortcuts)
lint-commit-push: ## 🚀 Format, lint, commit, and push (Usage: make lint-commit-push MSG="your message")
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a commit message"; \
		echo "Usage: make lint-commit-push MSG=\"your commit message\""; \
		exit 1; \
	fi
	@./scripts/lint-commit-push.sh "$(MSG)"

format-only: format-all ## 🎨 Format all code (alias for format-all)

quick-push: ## ⚡ Format and push with auto-generated message (use carefully!)
	@./scripts/quick-push.sh

# Docker
docker-build: ## Build all Docker images
	$(DOCKER_COMPOSE) build

docker-build-backend: ## Build FastAPI backend image
	$(DOCKER_COMPOSE) build fastapi-backend

docker-build-frontend: ## Build Streamlit frontend image
	$(DOCKER_COMPOSE) build streamlit-frontend

docker-build-content-creator: ## Build Content Creator image
	$(DOCKER_COMPOSE) build content-creator

docker-build-nextjs: ## Build Next.js frontend image
	$(DOCKER_COMPOSE) build nextjs-frontend

docker-up: ## Start all services with Docker Compose
	$(DOCKER_COMPOSE) up -d

docker-up-backend: ## Start only backend services (FastAPI + Content Creator)
	$(DOCKER_COMPOSE) up -d fastapi-backend content-creator

docker-up-full: ## Start all services including Next.js
	$(DOCKER_COMPOSE) up -d fastapi-backend streamlit-frontend content-creator nextjs-frontend

docker-down: ## Stop all services
	$(DOCKER_COMPOSE) down

docker-logs: ## View all Docker logs
	$(DOCKER_COMPOSE) logs -f

docker-logs-backend: ## View FastAPI backend logs
	$(DOCKER_COMPOSE) logs -f fastapi-backend

docker-logs-frontend: ## View Streamlit frontend logs
	$(DOCKER_COMPOSE) logs -f streamlit-frontend

docker-logs-content-creator: ## View Content Creator logs
	$(DOCKER_COMPOSE) logs -f content-creator

docker-logs-nextjs: ## View Next.js frontend logs
	$(DOCKER_COMPOSE) logs -f nextjs-frontend

docker-restart: ## Restart all services
	$(DOCKER_COMPOSE) restart

docker-restart-content-creator: ## Restart Content Creator service
	$(DOCKER_COMPOSE) restart content-creator

docker-restart-nextjs: ## Restart Next.js frontend service
	$(DOCKER_COMPOSE) restart nextjs-frontend

docker-clean: ## Remove all containers, networks, and volumes
	$(DOCKER_COMPOSE) down -v --remove-orphans

docker-shell-backend: ## Open shell in FastAPI backend container
	$(DOCKER_COMPOSE) exec fastapi-backend /bin/bash

docker-shell-frontend: ## Open shell in Streamlit frontend container
	$(DOCKER_COMPOSE) exec streamlit-frontend /bin/bash

docker-shell-content-creator: ## Open shell in Content Creator container
	$(DOCKER_COMPOSE) exec content-creator /bin/bash

docker-shell-nextjs: ## Open shell in Next.js frontend container
	$(DOCKER_COMPOSE) exec nextjs-frontend /bin/sh

docker-ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

docker-stats: ## Show container resource usage
	docker stats genai-fastapi-backend genai-streamlit-frontend genai-content-creator genai-nextjs-frontend

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
