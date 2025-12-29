# 🎯 Cursor Custom Commands

Quick commands for Cursor AI to format, lint, commit, and push code efficiently.

## 📝 Two Ways to Use

### 1. Cursor Slash Commands (Native Integration) ⭐ NEW!
Type in Cursor Agent chat:
- `/lint-commit-push` - Complete workflow with Cursor AI
- `/format-only` - Format code without committing
- `/quick-push` - Auto-commit and push

**How it works**: Commands are plain **Markdown files** (`.md`) stored in `.cursor/commands/` that Cursor automatically detects

**Requires**: Cursor 0.41+ with custom commands support

### 2. Shell Scripts & Make Commands (Works Everywhere)
Run in terminal or via Cursor:
- `make lint-commit-push MSG="message"` or `./lint-commit-push.sh "message"`
- `make format-only` or `./format-only.sh`
- `make quick-push` or `./quick-push.sh`

**Requires**: Poetry, Black, Ruff installed

---

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

## 🎯 Using Cursor Slash Commands (Native Integration)

Cursor's [custom slash commands](https://cursor.com/docs/agent/chat/commands) provide the most integrated experience:

### How to Use

1. Open Cursor Agent: `Cmd/Ctrl + L`
2. Type `/` to see available commands
3. Select your command or type it directly (e.g., `/lint-commit-push`)
4. Cursor AI will execute the workflow and ask for input when needed

### Available Slash Commands

**`/lint-commit-push`** - Complete Workflow
```
1. Opens in Cursor Agent chat
2. Formats code with Black
3. Lints with Ruff
4. Asks for your commit message
5. Commits and pushes
6. Shows summary and CI/CD link
```

**`/format-only`** - Format Without Committing
```
1. Formats all code
2. Shows what was formatted
3. Reminds you of next steps
```

**`/quick-push`** - Auto-Generated Message
```
1. Formats code
2. Analyzes changes
3. Generates commit message
4. Commits and pushes
5. Shows result
```

### Benefits of Slash Commands

✅ **Native Cursor integration** - Works directly in Agent chat  
✅ **Interactive** - AI asks clarifying questions  
✅ **Visual feedback** - See each step in real-time  
✅ **No terminal needed** - Everything happens in Cursor  
✅ **Team sharing** - Commands stored in `.cursor/commands/`

---

## 📋 Comparison

| Method | Format | Lint | Custom Message | Auto Message | Commit | Push | Interactive |
|--------|--------|------|----------------|--------------|--------|------|-------------|
| **Slash Commands** (`/lint-commit-push`) | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ In Cursor |
| **Shell Script** (`./lint-commit-push.sh`) | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | Terminal only |
| **Make** (`make lint-commit-push`) | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | Terminal only |
| `/format-only` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ In Cursor |
| `/quick-push` | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ In Cursor |

**Recommendation**: Use **slash commands** (`/lint-commit-push`) for the best Cursor-native experience!

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

