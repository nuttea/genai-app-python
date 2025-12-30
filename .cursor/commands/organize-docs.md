# Organize Documentation and Scripts

## Overview
Systematically organize documentation files and test scripts into proper directories following the project's established structure.

## Project Organization Structure

### Documentation Structure (`docs/`)
```
docs/
├── getting-started/       Quick start and setup guides
├── deployment/           Deployment and Cloud Run guides
├── security/             Authentication and API key guides
├── monitoring/           Datadog and observability guides
├── features/             Feature documentation
├── troubleshooting/      Problem solving and fixes
├── investigations/       Research findings
├── reference/            Technical reference docs
└── archive/              Historical implementation summaries
```

### Scripts Structure (`scripts/`)
```
scripts/
├── tests/                        Test scripts
│   ├── README.md                 Index of test scripts
│   └── test_*.py                 Test scripts
│
└── *.sh                          Shell utility scripts
    ├── format-only.sh            Format code
    ├── lint-commit-push.sh       Complete workflow
    ├── quick-push.sh             Quick push
    └── check-services.sh         Service checks
```

## Steps

### 1. Analyze current file locations
Identify files that need to be organized:
- Look for markdown files (`.md`) in the root directory
- Look for shell scripts (`.sh`) in the root directory
- Look for test scripts (`test_*.py`) in the root or wrong directories
- Check for documentation that should be in `docs/` subdirectories
- Identify any miscategorized files

### 2. Determine correct destinations
For each file, decide the appropriate location based on:

**Documentation files:**
- Quickstarts → `docs/getting-started/`
- Deployment guides → `docs/deployment/`
- Troubleshooting → `docs/troubleshooting/`
- Investigations/research → `docs/investigations/`
- Feature docs → `docs/features/`
- Technical reference → `docs/reference/`
- Historical/deprecated → `docs/archive/`

**Test scripts:**
- All test scripts (`test_*.py`) → `scripts/tests/`
- Create/update `scripts/tests/README.md` index

**Shell scripts:**
- Utility scripts (`.sh`) → `scripts/`
- Examples: `format-only.sh`, `lint-commit-push.sh`, `quick-push.sh`
- Keep deployment/infrastructure scripts in appropriate locations

**Root directory exceptions (keep in root):**
- `README.md` - Main project overview
- `QUICKSTART.md` - Quick start guide
- `DOCUMENTATION_MAP.md` - Documentation navigation
- `AGENTS.md` - Cursor AI instructions
- `PRE-COMMIT-CHECKLIST.md` - Pre-commit guide
- `CURSOR_COMMANDS.md` - Custom commands guide
- `FIX_CI_FORMATTING.md` - CI/CD troubleshooting
- `BLACK_FORMATTING_SETUP.md` - Black setup
- `PROJECT_PLAN.md` - Project planning
- `CHANGELOG.md` - Version history
- Setup/config files (`.cursorrules`, etc.)

### 3. Move files systematically
For each file to move:

```bash
# Create target directory if needed
mkdir -p target/directory/

# Move the file
git mv source/file.md target/directory/file.md

# Or use regular mv for new/untracked files
mv source/file.md target/directory/file.md
```

### 4. Update references and indexes
After moving files:
- Update `docs/INDEX.md` to reflect new locations
- Update `DOCUMENTATION_MAP.md` if needed
- Update any internal links in moved files
- Update README files in subdirectories
- Update cross-references between documents

### 5. Commit the organization
```bash
git add -A
git commit -m "docs: Organize documentation and scripts into proper directories"
git push
```

## Organization Checklist

- [ ] Identified all misplaced files
- [ ] Created necessary directories
- [ ] Moved files to correct locations
- [ ] Updated `docs/INDEX.md`
- [ ] Updated `DOCUMENTATION_MAP.md`
- [ ] Updated README files in subdirectories
- [ ] Fixed internal document links
- [ ] Committed and pushed changes

## Best Practices

1. **Preserve git history**: Use `git mv` for tracked files
2. **Update indexes**: Keep documentation indexes current
3. **Fix broken links**: Update all cross-references after moving files
4. **Test links**: Verify all internal links still work
5. **One commit**: Make organization changes in a single, focused commit

## Common Patterns

**Moving documentation:**
```bash
git mv ROOT_DOC.md docs/subdirectory/
```

**Moving test scripts:**
```bash
mkdir -p scripts/tests
git mv test_*.py scripts/tests/
```

**Moving shell scripts:**
```bash
mkdir -p scripts
git mv *.sh scripts/
# Or selectively:
git mv format-only.sh lint-commit-push.sh quick-push.sh scripts/
```

**Creating directory README:**
```bash
cat > docs/subdirectory/README.md << 'EOF'
# Subdirectory Name

Brief description of contents.

## Files
- file1.md - Description
- file2.md - Description
EOF
```

## Example Organization Session

```bash
# 1. Create directories
mkdir -p docs/troubleshooting docs/investigations scripts/tests scripts

# 2. Move troubleshooting docs
git mv TROUBLESHOOTING_*.md docs/troubleshooting/

# 3. Move investigation docs
git mv *_FINDINGS.md docs/investigations/

# 4. Move test scripts
git mv test_*.py scripts/tests/

# 5. Move shell scripts
git mv format-only.sh lint-commit-push.sh quick-push.sh scripts/

# 6. Update indexes
# (Edit docs/INDEX.md and DOCUMENTATION_MAP.md)

# 7. Commit
git add -A
git commit -m "docs: Organize documentation and scripts"
git push
```

## Reference

See existing organization in:
- `docs/INDEX.md` - Full documentation index
- `DOCUMENTATION_MAP.md` - Master documentation map
- `scripts/tests/README.md` - Test scripts index
