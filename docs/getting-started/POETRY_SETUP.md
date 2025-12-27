# Poetry Dependency Management

Complete guide for using Poetry in the GenAI Application Platform.

## Why Poetry?

✅ **Dependency Resolution** - Automatically resolves conflicts  
✅ **Lock File** - Reproducible builds with `poetry.lock`  
✅ **Virtual Environments** - Automatic venv management  
✅ **Easy Publishing** - Simple package building  
✅ **Modern Tools** - PEP 517/518 compliant  

## Installation

### Install Poetry

```bash
# Recommended: Official installer (installs latest 2.x)
curl -sSL https://install.python-poetry.org | python3 -

# Alternative: pip (specific version)
pip install poetry==2.2.1

# Alternative: Homebrew (macOS)
brew install poetry

# Verify installation (should show 2.2.1 or higher)
poetry --version
```

**Note**: This project requires Poetry 2.0+ (uses 2.2.1 in Docker)

### Configure Poetry

```bash
# Don't create virtualenv inside project (optional)
poetry config virtualenvs.in-project false

# Show config
poetry config --list
```

## Quick Start

### Backend (FastAPI)

```bash
cd services/fastapi-backend

# Install dependencies
poetry install

# Run in Poetry environment
poetry run uvicorn app.main:app --reload

# Or activate environment (Poetry 2.0+)
eval $(poetry env activate)
uvicorn app.main:app --reload
```

### Frontend (Streamlit)

```bash
cd frontend/streamlit

# Install dependencies
poetry install

# Run app
poetry run streamlit run app.py

# Or activate environment (Poetry 2.0+)
eval $(poetry env activate)
streamlit run app.py
```

## Common Commands

### Managing Dependencies

```bash
# Add a package
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Add with specific version
poetry add "package-name==1.2.3"
poetry add "package-name^1.2"  # Allows 1.2.x
poetry add "package-name~1.2.3"  # Allows 1.2.3 to <1.3.0

# Remove a package
poetry remove package-name

# Update packages
poetry update                    # All packages
poetry update package-name       # Specific package

# Show installed packages
poetry show
poetry show --tree              # With dependencies
poetry show package-name        # Details
```

### Working with Environments

```bash
# Activate virtual environment (Poetry 2.0+)
eval $(poetry env activate)

# Run command in Poetry environment (without activating)
poetry run python script.py
poetry run pytest
poetry run uvicorn app.main:app

# Deactivate environment
deactivate

# Show environment info
poetry env info
poetry env list

# Remove environment
poetry env remove python3.11
```

### Lock File

```bash
# Update lock file
poetry lock

# Update without upgrading packages
poetry lock --no-update

# Install from lock file (CI/CD)
poetry install --no-root
```

### Export

```bash
# Export to requirements.txt (for Docker, pip, etc.)
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Include dev dependencies
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# For specific groups
poetry export --only main --output requirements.txt
```

## Project Setup

### Initialize New Project

```bash
# Create new project
poetry new my-project

# Or initialize in existing directory
cd my-project
poetry init
```

### Configure pyproject.toml

```toml
[tool.poetry]
name = "fastapi-backend"
version = "0.1.0"
description = "FastAPI backend with Google Vertex AI"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Docker Integration

### Dockerfile with Poetry

```dockerfile
# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure poetry (no virtual env in container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .
```

### Multi-stage Build

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

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
poetry update

# Add new package
poetry add new-package

# Run tests
poetry run pytest

# Run linter
poetry run ruff check app/

# Format code
poetry run black app/

# Type check
poetry run mypy app/
```

### Before Committing

```bash
# Run all checks
poetry run black app/
poetry run ruff check app/
poetry run mypy app/
poetry run pytest

# Update lock file
poetry lock

# Commit changes (including poetry.lock)
git add pyproject.toml poetry.lock
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
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run pytest
```

### Cloud Build

Already configured in `cloudbuild.yaml` - uses Docker with Poetry.

## Troubleshooting

### "No module named 'package'"

```bash
# Reinstall dependencies
poetry install

# Or update
poetry update

# Check installed packages
poetry show
```

### Version Conflicts

```bash
# See dependency tree
poetry show --tree

# Update problematic package
poetry update package-name

# Force reinstall
poetry install --sync
```

### Lock File Issues

```bash
# Regenerate lock file
rm poetry.lock
poetry lock

# Or update existing
poetry lock --no-update
```

### Python Version Issues

```bash
# Use specific Python version
poetry env use python3.11
poetry env use /usr/bin/python3.11

# Show active Python
poetry env info
```

## Best Practices

### 1. Always Commit poetry.lock

✅ Commit `poetry.lock` to version control for reproducible builds.

### 2. Use Version Constraints Wisely

```toml
# Recommended for libraries
package = "^1.2.3"  # Allows 1.2.3 to <2.0.0

# Recommended for applications
package = "~1.2.3"  # Allows 1.2.3 to <1.3.0

# Pin exact version (use sparingly)
package = "==1.2.3"
```

### 3. Organize Dependencies

```toml
[tool.poetry.dependencies]
# Production dependencies

[tool.poetry.group.dev.dependencies]
# Development tools (testing, linting)

[tool.poetry.group.docs.dependencies]
# Documentation tools
```

### 4. Keep Poetry Updated

```bash
# Update Poetry itself
poetry self update

# Check for outdated packages
poetry show --outdated
```

### 5. Use poetry.lock in CI/CD

```bash
# Reproducible builds
poetry install --no-root
```

## Migrating from requirements.txt

### Convert Existing Project

```bash
# 1. Create pyproject.toml
poetry init

# 2. Add dependencies from requirements.txt
cat requirements.txt | while read pkg; do
    poetry add "$pkg"
done

# 3. Verify
poetry check

# 4. Test
poetry install
poetry run pytest
```

### Keep Both (Transition Period)

```bash
# Generate requirements.txt from Poetry
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Add to pre-commit or CI/CD
poetry export -f requirements.txt --output requirements.txt --without-hashes
git add requirements.txt
```

## Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry Commands](https://python-poetry.org/docs/cli/)
- [Dependency Specification](https://python-poetry.org/docs/dependency-specification/)
- [Managing Environments](https://python-poetry.org/docs/managing-environments/)

---

**Quick Start**: `poetry install && eval $(poetry env activate) && uvicorn app.main:app --reload` 🚀

