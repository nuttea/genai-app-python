# Cursor Custom Slash Commands

This directory contains custom slash commands for Cursor AI to streamline the development workflow.

## Available Commands

### `/lint-commit-push` - Complete Workflow ⭐ RECOMMENDED
**Usage**: Type `/lint-commit-push` in Cursor Agent chat

**What it does**:
1. Formats all code with Black (backend + frontend)
2. Lints with Ruff (auto-fixes issues)
3. Asks for commit message
4. Commits and pushes to origin/main

**Use when**: You want the complete workflow in one command

---

### `/format-only` - Format Without Committing
**Usage**: Type `/format-only` in Cursor Agent chat

**What it does**:
1. Formats all code with Black
2. Shows what was formatted
3. Suggests next steps for manual commit

**Use when**: You want to format code before reviewing changes

---

### `/quick-push` - Auto-Generated Commit Message
**Usage**: Type `/quick-push` in Cursor Agent chat

**What it does**:
1. Formats code with Black
2. Analyzes changed files
3. Generates appropriate commit message
4. Commits and pushes

**⚠️ Use carefully**: Auto-generates commit messages. For important changes, use `/lint-commit-push`

---

## How to Use

1. Open Cursor Agent (Cmd/Ctrl + L)
2. Type `/` to see available commands
3. Select your command or type it directly
4. Follow the prompts

## Command Files

- `lint-commit-push.json` - Complete workflow
- `format-only.json` - Format only
- `quick-push.json` - Quick push with auto-message

## Related

- **[CURSOR_COMMANDS.md](../../CURSOR_COMMANDS.md)** - Detailed guide for shell scripts
- **[PRE-COMMIT-CHECKLIST.md](../../PRE-COMMIT-CHECKLIST.md)** - Manual workflow
- **Shell scripts**: `lint-commit-push.sh`, `format-only.sh`, `quick-push.sh`
- **Makefile**: `make lint-commit-push MSG="msg"`, `make format-only`, `make quick-push`

## Documentation

See [Cursor Docs - Custom Slash Commands](https://cursor.com/docs/agent/chat/commands) for more information on creating custom commands.

---

**Last Updated**: December 29, 2024

