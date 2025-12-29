# 🎯 Cursor Custom Commands

Quick commands for Cursor AI to format, lint, commit, and push code efficiently.

## 🚀 Available Commands

### 1. `lint-commit-push` - Complete Workflow

**Formats, lints, commits, and pushes in one command.**

```bash
# Using the script directly
./lint-commit-push.sh "feat: Add new feature"

# Using Make
make lint-commit-push MSG="feat: Add new feature"
```

**What it does**:
1. ✅ Formats all code with Black (backend + frontend)
2. 🔧 Lints and auto-fixes with Ruff
3. 📝 Commits all changes with your message
4. 🚀 Pushes to origin/main

**Use when**: You want to format, lint, commit, and push in one go.

---

### 2. `format-only` - Format Without Committing

**Formats code with Black but doesn't commit.**

```bash
# Using the script
./format-only.sh

# Using Make
make format-only
```

**What it does**:
- Formats backend code (services/fastapi-backend)
- Formats frontend code (frontend/streamlit)
- Shows next steps

**Use when**: You want to format code before reviewing changes.

---

### 3. `quick-push` - Auto-Generated Commit Message

**Formats and pushes with an automatically generated commit message.**

```bash
# Using the script
./quick-push.sh

# Using Make
make quick-push
```

**What it does**:
1. Formats code with Black
2. Analyzes changed files
3. Generates appropriate commit message:
   - "chore: Update workflow configuration" (for .yml files)
   - "docs: Update documentation" (for .md files)
   - "fix: Update backend code" (for backend changes)
   - "fix: Update frontend code" (for frontend changes)
   - "chore: Update code" (for other changes)
4. Commits and pushes

**Use when**: Making quick fixes where an auto-generated message is sufficient.

**⚠️ Use carefully**: For important changes, use `lint-commit-push` with a custom message.

---

## 📋 Comparison

| Command | Format | Lint | Custom Message | Auto Message | Commit | Push |
|---------|--------|------|----------------|--------------|--------|------|
| `lint-commit-push` | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| `format-only` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `quick-push` | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## 💡 Usage Examples

### Example 1: Adding a New Feature

```bash
# Make your code changes
# Then run:
make lint-commit-push MSG="feat: Add user authentication"
```

### Example 2: Fixing a Bug

```bash
# Make your code changes
# Then run:
./lint-commit-push.sh "fix: Resolve login timeout issue"
```

### Example 3: Quick Documentation Update

```bash
# Update some markdown files
# Then run:
make quick-push
# Auto-generates: "docs: Update documentation"
```

### Example 4: Format Before Reviewing

```bash
# Make your code changes
# Format to see the final diff:
make format-only

# Review changes with:
git diff

# Commit manually:
git add -A
git commit -m "your message"
git push
```

---

## 🛠️ Manual Commands (Alternative)

If you prefer manual control, use these commands:

```bash
# 1. Format backend
cd services/fastapi-backend && poetry run black app/ && cd ../..

# 2. Format frontend
cd frontend/streamlit && poetry run black . && cd ../..

# 3. Lint backend (optional)
cd services/fastapi-backend && poetry run ruff check --fix app/ && cd ../..

# 4. Lint frontend (optional)
cd frontend/streamlit && poetry run ruff check --fix . && cd ../..

# 5. Commit and push
git add -A
git commit -m "your message"
git push
```

Or use the one-liner from `PRE-COMMIT-CHECKLIST.md`.

---

## 📚 Related Documentation

- **[PRE-COMMIT-CHECKLIST.md](./PRE-COMMIT-CHECKLIST.md)** - Manual pre-commit steps
- **[BLACK_FORMATTING_SETUP.md](./BLACK_FORMATTING_SETUP.md)** - Black setup details
- **[FIX_CI_FORMATTING.md](./FIX_CI_FORMATTING.md)** - Fix CI/CD formatting failures
- **[Makefile](./Makefile)** - All available make commands

---

## ⚙️ Configuration

Scripts are located in project root:
- `lint-commit-push.sh` - Main workflow script
- `format-only.sh` - Format-only script
- `quick-push.sh` - Quick push script

All scripts are executable and can be run directly or via `make`.

---

## 🔧 Troubleshooting

### "poetry: command not found"

If you get this error, the scripts are trying to use Poetry in a shell that doesn't have it loaded.

**Solution**: Run commands in your interactive terminal (not via Cursor's shell).

### "No changes to commit"

The `quick-push` command will fail if there are no changes.

**Solution**: Make sure you have modified files before running.

### CI/CD Still Fails After Formatting

The scripts format code locally, but if CI/CD still fails:

1. Check that you actually pushed the formatted code
2. See `FIX_CI_FORMATTING.md` for troubleshooting
3. Verify formatting in your terminal:
   ```bash
   cd services/fastapi-backend && poetry run black --check app/
   ```

---

## 🎯 Best Practices

1. **Use `lint-commit-push`** for most commits (with meaningful messages)
2. **Use `format-only`** when you want to review changes first
3. **Use `quick-push` sparingly** for trivial updates
4. **Always include meaningful commit messages** for important changes
5. **Review the diff** before pushing if unsure

---

**Created**: December 29, 2024  
**Last Updated**: December 29, 2024

