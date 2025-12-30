# uv Dependency Management

Complete guide for using uv in the GenAI Application Platform.

## Why uv?

✅ **Fast** - 10-100x faster than pip and Poetry
✅ **Drop-in Replacement** - Compatible with pip and Poetry workflows
✅ **PEP 621 Compliant** - Uses standard `pyproject.toml` format
✅ **Simple** - Single binary, no complex setup
✅ **Modern** - Built in Rust for performance

## Installation

### Install uv

```bash
# Recommended: Official installer (Unix/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Alternative: pip
pip install uv

# Alternative: Homebrew (macOS)
brew install uv

# Verify installation
uv --version
```

**Note**: This project uses uv for all dependency management.

## Quick Start

### Backend (FastAPI)

```bash
cd services/fastapi-backend

# Install dependencies
uv sync

# Run in uv environment
uv run uvicorn app.main:app --reload

# Or sync without dev dependencies (production)
uv sync --no-dev
```

### Frontend (Streamlit)

```bash
cd frontend/streamlit

# Install dependencies
uv sync

# Run app
uv run streamlit run app.py

# Or sync without dev dependencies (production)
uv sync --no-dev
```

## Common Commands

### Managing Dependencies

```bash
# Add a package
uv add package-name

# Add development dependency
uv add --dev package-name

# Add with specific version
uv add "package-name==1.2.3"
uv add "package-name>=1.2.0"

# Remove a package
uv remove package-name

# Update packages
uv sync --upgrade              # All packages
uv sync --upgrade-package pkg  # Specific package

# Show installed packages
uv pip list
uv tree                        # Dependency tree
```

### Working with Environments

```bash
# Sync dependencies (creates/updates venv)
uv sync

# Run command in uv environment (without activating)
uv run python script.py
uv run pytest
uv run uvicorn app.main:app

# Activate environment manually (if needed)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Deactivate environment
deactivate
```

### Lock File

```bash
# uv.lock is automatically generated/updated
uv sync                      # Updates lock file

# Install from lock file (CI/CD)
uv sync --frozen             # Use exact versions from lock
```

## Project Setup

### Initialize New Project

```bash
# Create new project
uv init my-project

# Or initialize in existing directory
cd my-project
uv init
```

### Configure pyproject.toml

```toml
[project]
name = "fastapi-backend"
version = "0.1.0"
description = "FastAPI backend with Google Vertex AI"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.1.1",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Docker Integration

### Dockerfile with uv

```dockerfile
# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system \
    "fastapi>=0.109.0" \
    "uvicorn[standard]>=0.27.0" \
    # ... other dependencies
```

### Multi-stage Build

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip compile pyproject.toml -o requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

## Development Workflow

### Day-to-Day

```bash
# Morning - update dependencies
uv sync --upgrade

# Add new package
uv add new-package

# Run tests
uv run pytest

# Run linter
uv run ruff check app/

# Format code
uv run black app/

# Type check
uv run mypy app/
```

### Before Committing

```bash
# Run all checks
uv run black app/
uv run ruff check app/
uv run mypy app/
uv run pytest

# Sync dependencies (updates lock file)
uv sync

# Commit changes (including uv.lock)
git add pyproject.toml uv.lock
git commit -m "deps: update dependencies"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync --frozen
      - name: Run tests
        run: uv run pytest
```

## Troubleshooting

### "No module named 'package'"

```bash
# Reinstall dependencies
uv sync

# Or force reinstall
uv sync --reinstall
```

### Version Conflicts

```bash
# See dependency tree
uv tree

# Update problematic package
uv sync --upgrade-package package-name

# Force reinstall
uv sync --reinstall
```

### Lock File Issues

```bash
# Regenerate lock file
rm uv.lock
uv sync

# Or update existing
uv sync --upgrade
```

### Python Version Issues

```bash
# Use specific Python version
uv python pin 3.11

# Show active Python
uv python list
```

## Best Practices

### 1. Always Commit uv.lock

✅ Commit `uv.lock` to version control for reproducible builds.

### 2. Use Version Constraints Wisely

```toml
# Recommended for applications
package = ">=1.2.0"  # Minimum version

# Pin exact version (use sparingly)
package = "==1.2.3"
```

### 3. Organize Dependencies

```toml
[project]
dependencies = [
    # Production dependencies
]

[project.optional-dependencies]
dev = [
    # Development tools (testing, linting)
]
```

### 4. Keep uv Updated

```bash
# Update uv itself
uv self update

# Check for outdated packages
uv sync --upgrade --dry-run
```

### 5. Use uv.lock in CI/CD

```bash
# Reproducible builds
uv sync --frozen
```

## Migrating from Poetry

### Convert Existing Project

```bash
# 1. Install uv
pip install uv

# 2. Convert pyproject.toml from Poetry to PEP 621 format
# (Already done in this project)

# 3. Sync dependencies
uv sync

# 4. Test
uv run pytest
```

### Key Differences

| Poetry | uv |
|--------|-----|
| `poetry install` | `uv sync` |
| `poetry add pkg` | `uv add pkg` |
| `poetry run cmd` | `uv run cmd` |
| `poetry.lock` | `uv.lock` |
| `[tool.poetry]` | `[project]` (PEP 621) |

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)

---

**Quick Start**: `uv sync && uv run uvicorn app.main:app --reload` 🚀
