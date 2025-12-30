# Git Hooks

This directory contains git hooks for the project.

## ⚠️ Note

Due to the corporate environment setup (scfw wrapper), automatic git hooks may not work correctly.

**Instead, please follow the manual pre-commit checklist**: See [`PRE-COMMIT-CHECKLIST.md`](../PRE-COMMIT-CHECKLIST.md)

## Pre-commit Hook (Optional)

The `pre-commit` hook is provided but may require environment-specific adjustments.

### Installation (If Supported)

```bash
make install-hooks
```

Or manually:
```bash
chmod +x .git-hooks/pre-commit
ln -sf ../../.git-hooks/pre-commit .git/hooks/pre-commit
```

### What it attempts to do

1. Runs `./format.sh` to format all code with Black
2. Stages the formatted files
3. Proceeds with the commit

### If the hook doesn't work

The hook uses `scfw run poetry` which may not work in all environments. In that case:

1. **Disable the hook**:
   ```bash
   rm .git/hooks/pre-commit
   ```

2. **Use manual formatting** (Recommended):
   Follow the checklist in [`PRE-COMMIT-CHECKLIST.md`](../PRE-COMMIT-CHECKLIST.md)

3. **Or bypass the hook**:
   ```bash
   git commit --no-verify -m "your message"
   ```
   ⚠️ **Not recommended** - Always format your code!

## Manual Formatting Commands

```bash
# Backend
cd services/fastapi-backend
poetry run black app/
cd ../..

# Frontend
cd frontend/streamlit
poetry run black .
cd ../..
```

Or use the one-liner from `PRE-COMMIT-CHECKLIST.md`.

## Black Configuration

Black is configured in each service's `pyproject.toml`:
- Line length: 100 characters
- Target Python version: 3.11
