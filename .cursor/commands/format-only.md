# Format Code Only

## Overview
Format all Python code with Black without committing. Use this when you want to review changes before committing.

## Steps

### 1. Format backend code
```bash
cd services/fastapi-backend && poetry run black app/ && cd ../..
```

### 2. Format frontend code
```bash
cd frontend/streamlit && poetry run black . && cd ../..
```

### 3. Show results
Display a summary of what was formatted and remind the user of next steps.

## Next Steps for User
After formatting, the user should:

1. **Review changes:**
   ```bash
   git diff
   ```

2. **Stage changes:**
   ```bash
   git add -A
   ```

3. **Commit with a message:**
   ```bash
   git commit -m "your message"
   ```

4. **Push to remote:**
   ```bash
   git push
   ```

Or use `/lint-commit-push` to do all steps at once.

## Alternative Methods
The user can also use:
- Shell script: `./format-only.sh`
- Make command: `make format-only`

