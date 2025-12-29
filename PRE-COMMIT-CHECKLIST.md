# 📋 Pre-Commit Checklist

**⚠️ IMPORTANT**: Always run these commands before `git commit` and `git push`.

## 🎨 Format Code with Black (Required)

Run these commands from the project root:

###Backend
```bash
cd services/fastapi-backend
poetry run black app/
cd ../..
```

### Frontend
```bash
cd frontend/streamlit
poetry run black .
cd ../..
```

### Or use Make (if working)
```bash
make pre-commit
```

## 🔍 Optional: Lint Check

Check for code quality issues:

```bash
# Backend
cd services/fastapi-backend
poetry run ruff check app/
cd ../..

# Frontend
cd frontend/streamlit
poetry run ruff check .
cd ../..
```

Auto-fix linting issues:

```bash
# Backend
cd services/fastapi-backend
poetry run ruff check --fix app/
cd ../..

# Frontend
cd frontend/streamlit
poetry run ruff check --fix .
cd ../..
```

## ✅ Quick Reference

Before each commit:
```bash
# 1. Format backend
cd services/fastapi-backend && poetry run black app/ && cd ../..

# 2. Format frontend  
cd frontend/streamlit && poetry run black . && cd ../..

# 3. Git add and commit
git add -A
git commit -m "your message"
git push
```

## ⚡ One-Liner (Copy & Paste)

```bash
cd services/fastapi-backend && poetry run black app/ && cd ../.. && cd frontend/streamlit && poetry run black . && cd ../.. && echo "✅ Formatting complete!"
```

## 🚫 Skip Formatting (Not Recommended)

If you absolutely must skip formatting:
```bash
git commit --no-verify -m "your message"
```

## 📝 Configuration

Black is configured in each service's `pyproject.toml`:
- Line length: 100 characters
- Target Python: 3.11

## 💡 Tips

- Set up a shell alias for quick formatting:
  ```bash
  alias format-code='cd services/fastapi-backend && poetry run black app/ && cd ../.. && cd frontend/streamlit && poetry run black . && cd ../..'
  ```

- Or use VS Code's "Format on Save" feature with the Black extension

- Consider using a pre-commit hook (see `.git-hooks/README.md`) if your environment supports it

