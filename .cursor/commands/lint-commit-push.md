# Lint, Commit, and Push

## Overview
Complete workflow to format code with Black, lint with Ruff, commit changes, and push to remote repository.

## Steps

### 1. Format code with Black
Format all Python code to ensure it passes CI/CD checks:

**Backend:**
```bash
cd services/fastapi-backend && poetry run black app/ && cd ../..
```

**Frontend:**
```bash
cd frontend/streamlit && poetry run black . && cd ../..
```

### 2. Lint code with Ruff
Auto-fix linting issues (optional but recommended):

**Backend:**
```bash
cd services/fastapi-backend && poetry run ruff check --fix app/ && cd ../..
```

**Frontend:**
```bash
cd frontend/streamlit && poetry run ruff check --fix . && cd ../..
```

### 3. Commit and push
Ask the user for a commit message if not provided, then:

```bash
git add -A
git commit -m "<user's commit message>"
git push origin main
```

### 4. Show summary
Display:
- Latest commit: `git log -1 --oneline`
- CI/CD link: https://github.com/nuttea/genai-app-python/actions

## Critical Requirements
- **Always format with Black before committing** - CI/CD will fail otherwise
- Ensure commit message is descriptive and follows conventions (feat:, fix:, docs:, etc.)
- Confirm all commands succeed before proceeding to the next step

## Alternative Methods
The user can also use:
- Shell script: `./lint-commit-push.sh "commit message"`
- Make command: `make lint-commit-push MSG="commit message"`

