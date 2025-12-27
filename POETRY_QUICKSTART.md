# 📦 Poetry Quick Start

Get started with Poetry dependency management in 5 minutes!

## Why Poetry?

✅ Better dependency resolution
✅ Automatic virtual environment management
✅ Lock file for reproducible builds
✅ Simpler than pip + venv

## 1-Minute Install

```bash
# Install Poetry (installs latest 2.x version)
curl -sSL https://install.python-poetry.org | python3 -

# Verify (should show 2.2.1 or higher)
poetry --version
```

**Note**: This project uses Poetry 2.2.1

## 2-Minute Setup

```bash
# Backend
cd services/fastapi-backend
poetry install
eval $(poetry env activate)

# Frontend
cd frontend/streamlit
poetry install
eval $(poetry env activate)
```

## Quick Commands

```bash
# Install dependencies
poetry install

# Add new package
poetry add package-name

# Update packages
poetry update

# Run command
poetry run uvicorn app.main:app --reload
poetry run streamlit run app.py

# Enter shell
poetry shell
uvicorn app.main:app --reload  # Now in Poetry environment
```

## With Makefile

```bash
# Install everything
make install

# Run backend (with Poetry)
make run-fastapi

# Run frontend (with Poetry)
make run-streamlit

# All commands now use Poetry automatically
```

## Export requirements.txt (Optional)

```bash
# Backend
cd services/fastapi-backend
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Frontend
cd frontend/streamlit
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Benefits

**Before (pip + requirements.txt):**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # May have conflicts
```

**After (Poetry):**
```bash
poetry install                  # Auto-creates venv, resolves dependencies
eval $(poetry env activate)     # Activate (Poetry 2.0+)
```

**Dependency Management:**
- Before: Edit requirements.txt manually
- After: `poetry add package-name` (automatic)

**Reproducibility:**
- Before: requirements.txt (versions can drift)
- After: poetry.lock (exact versions locked)

## Full Guide

See [docs/getting-started/POETRY_SETUP.md](docs/getting-started/POETRY_SETUP.md) for complete documentation.

---

**Quick**: `poetry install && eval $(poetry env activate) && uvicorn app.main:app --reload` 🚀
