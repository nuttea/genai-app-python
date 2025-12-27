# Poetry 2.0+ Migration Notes

## Important Changes in Poetry 2.0+

**Project uses Poetry 2.2.1**

### 1. Shell Command Deprecated

Poetry 2.0+ has deprecated the `poetry shell` command in favor of `poetry env activate`.

### 2. Application vs Library Mode

For applications (not libraries), use `package-mode = false` or `--no-root` flag.

### 3. New env activate Command

Poetry 2.0+ uses `poetry env activate` instead of `poetry shell`.

### Old Way (Poetry 1.x)
```bash
poetry shell
```

### New Way (Poetry 2.0+)
```bash
eval $(poetry env activate)
```

## Why the Change?

The new `poetry env activate` command:
- ✅ Doesn't spawn a new shell
- ✅ Activates in current shell
- ✅ More predictable behavior
- ✅ Better for scripting

## Usage

### Activate Environment

```bash
# Activate Poetry environment
eval $(poetry env activate)

# Now you can run commands directly
uvicorn app.main:app --reload
streamlit run app.py
pytest

# Deactivate
deactivate
```

### Alternative: Use poetry run

If you don't want to activate the environment, use `poetry run`:

```bash
# No activation needed
poetry run uvicorn app.main:app --reload
poetry run streamlit run app.py
poetry run pytest
```

## Updated Documentation

All documentation has been updated to use the new command:

- ✅ README.md
- ✅ QUICKSTART.md
- ✅ POETRY_QUICKSTART.md
- ✅ docs/getting-started/POETRY_SETUP.md
- ✅ services/fastapi-backend/README.md
- ✅ frontend/streamlit/README.md

## Quick Reference

### Backend Development

```bash
cd services/fastapi-backend
poetry install --no-root  # Application mode
eval $(poetry env activate)
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend/streamlit
poetry install --no-root  # Application mode
eval $(poetry env activate)
streamlit run app.py
```

**Note**: `--no-root` tells Poetry not to install the project itself, only dependencies. This is correct for applications.

### Without Activation

```bash
# Backend
cd services/fastapi-backend
poetry run uvicorn app.main:app --reload

# Frontend
cd frontend/streamlit
poetry run streamlit run app.py
```

## Shell-Specific

### Bash/Zsh
```bash
eval $(poetry env activate)
```

### Fish
```fish
eval (poetry env activate)
```

### PowerShell
```powershell
Invoke-Expression (poetry env activate)
```

## Troubleshooting

### Command Not Found

If you get "poetry: command not found":

```bash
# Check Poetry is installed
poetry --version

# If not, install
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Environment Not Activating

```bash
# Check environment exists
poetry env info

# Show environment path
poetry env info --path

# Manually activate (fallback)
source $(poetry env info --path)/bin/activate
```

## Resources

- [Poetry 2.0 Announcement](https://python-poetry.org/blog/announcing-poetry-2.0.0/)
- [Poetry env activate docs](https://python-poetry.org/docs/cli/#env-activate)

---

**Summary**: Use `eval $(poetry env activate)` instead of `poetry shell` in Poetry 2.0+ 🎉
