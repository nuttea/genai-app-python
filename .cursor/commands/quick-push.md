# Quick Push with Auto-Generated Message

## Overview
Quick format, commit, and push with an automatically generated commit message based on changed files. Use carefully - for important changes, use `/lint-commit-push` with a custom message instead.

## Steps

### 1. Format code with Black

**Backend:**
```bash
cd services/fastapi-backend && poetry run black app/ && cd ../..
```

**Frontend:**
```bash
cd frontend/streamlit && poetry run black . && cd ../..
```

### 2. Analyze changed files
Check what files have changed to generate an appropriate commit message:

```bash
git diff --name-only
```

### 3. Generate commit message
Based on the changed files:
- If `.yml` or `.yaml` files: `"chore: Update workflow configuration"`
- If `.md` files: `"docs: Update documentation"`
- If `services/fastapi-backend` files: `"fix: Update backend code"`
- If `frontend/streamlit` files: `"fix: Update frontend code"`
- Otherwise: `"chore: Update code"`

### 4. Commit and push
```bash
git add -A
git commit -m "<generated message>"
git push origin main
```

### 5. Show result
Display:
- The generated commit message
- Latest commit: `git log -1 --oneline`

## Warning
⚠️ **Use carefully**: This auto-generates commit messages. For important changes, use `/lint-commit-push` with a custom message that properly describes your changes.

## Alternative Methods
The user can also use:
- Shell script: `./scripts/quick-push.sh`
- Make command: `make quick-push`

