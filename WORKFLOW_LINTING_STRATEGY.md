# GitHub Workflows Linting Strategy

## Overview

The GitHub Actions workflows have been optimized to **skip linting in development** and **enforce linting in production**, providing faster iteration while maintaining code quality gates.

---

## 🎯 Strategy

### Development Workflows (main branch)
**Goal:** Fast deployments for rapid iteration and testing

- ✅ **Tests** still run (backend only)
- ❌ **Linting** skipped
- ❌ **Type checking** skipped
- ❌ **Formatting checks** skipped

### Production Workflows (prod branch)
**Goal:** Comprehensive quality gates before production deployment

- ✅ **Tests** run (backend only)
- ✅ **Linting** enforced (ESLint, Ruff)
- ✅ **Type checking** enforced (TypeScript, optional mypy)
- ✅ **Formatting** enforced (Black, Prettier)

---

## 📋 Modified Workflows

### Frontend Workflows

#### `nextjs-frontend.yml` (Development)
**Before:**
```yaml
jobs:
  lint-and-test:  # Ran linting, type-check, prettier
    ...
  deploy:
    needs: [lint-and-test]
```

**After:**
```yaml
jobs:
  deploy:  # Direct deployment, no linting
    # Linting skipped for faster iteration
```

**Time Saved:** ~1-2 minutes per deployment

#### `nextjs-frontend-prod.yml` (Production)
**Before:**
```yaml
jobs:
  deploy:  # No quality checks
```

**After:**
```yaml
jobs:
  lint-and-test:  # NEW! Comprehensive checks
    - ESLint
    - TypeScript type-check
    - Prettier formatting check
    - Build verification
  deploy:
    needs: [lint-and-test]  # Quality gate
```

---

### Backend Workflows

#### `fastapi-backend.yml` (Development)
**Before:**
```yaml
jobs:
  test: ...
  lint:  # Black + Ruff checks
    ...
  deploy:
    needs: [test, lint]
```

**After:**
```yaml
jobs:
  test: ...  # Still runs
  # lint: ...  # COMMENTED OUT
  deploy:
    needs: [test]  # Only depends on tests
```

**Time Saved:** ~30-45 seconds per deployment

#### `fastapi-backend-prod.yml` (Production)
**Before:**
```yaml
jobs:
  deploy:  # No quality checks
```

**After:**
```yaml
jobs:
  lint:  # NEW! Quality gate
    - Black formatting check
    - Ruff linting
  deploy:
    needs: [lint]
```

---

### ADK Python Workflows

#### `adk-python.yml` (Development)
**Before:**
```yaml
jobs:
  lint:  # Black + Ruff checks
    ...
  deploy:
    needs: [lint]
```

**After:**
```yaml
jobs:
  # lint: ...  # COMMENTED OUT
  deploy:  # Direct deployment
```

**Time Saved:** ~30-45 seconds per deployment

#### `adk-python-prod.yml` (Production)
**Before:**
```yaml
jobs:
  deploy:  # No quality checks
```

**After:**
```yaml
jobs:
  lint:  # NEW! Quality gate
    - Black formatting check
    - Ruff linting
  deploy:
    needs: [lint]
```

---

## ⚡ Performance Impact

### Development (main branch)
| Workflow | Before | After | Time Saved |
|----------|--------|-------|------------|
| Next.js Frontend | ~6-7 min | ~4-5 min | **~2 min** |
| FastAPI Backend | ~4-5 min | ~3-4 min | **~45 sec** |
| ADK Python | ~3-4 min | ~2-3 min | **~45 sec** |

**Total time saved per full deployment:** ~3.5 minutes

### Production (prod branch)
| Workflow | Before | After | Time Added |
|----------|--------|-------|------------|
| Next.js Frontend | ~4-5 min | ~6-7 min | **+2 min** |
| FastAPI Backend | ~3-4 min | ~4-5 min | **+45 sec** |
| ADK Python | ~2-3 min | ~3-4 min | **+45 sec** |

**Quality gates added:** Comprehensive linting before production

---

## 🛡️ Code Quality Assurance

### How Quality is Maintained

1. **Local Development:**
   - Pre-commit hooks still enforce formatting (Black, Prettier)
   - Manual linting available: `make lint` or `npm run lint`

2. **Development Branch:**
   - Fast deployments for testing
   - Code quality maintained by developers

3. **Production Branch:**
   - **All quality checks enforced**
   - Deployment fails if any check fails
   - Guarantees production code quality

---

## 📝 Linting Commands Reference

### Frontend (Next.js)
```bash
# ESLint
npm run lint

# TypeScript type checking
npm run type-check

# Prettier formatting
npm run format-check

# All checks
npm run lint && npm run type-check && npm run format-check
```

### Backend (FastAPI)
```bash
# Black formatting
uv run black --check app/

# Ruff linting
uv run ruff check app/

# All checks
uv run black --check app/ && uv run ruff check app/
```

### ADK Python
```bash
# Black formatting
uv run black --check .

# Ruff linting
uv run ruff check .

# All checks
uv run black --check . && uv run ruff check .
```

---

## 🚀 Deployment Flow

### Development (Fast Iteration)
```
1. Push to main branch
2. ✅ Tests run (backend only)
3. ⏭️  Linting skipped
4. 🚀 Deploy to Cloud Run (dev)
```

### Production (Quality Gate)
```
1. Merge main → prod
2. ✅ Linting runs (all checks)
3. ✅ Tests run (if applicable)
4. ❌ Deployment BLOCKED if lint fails
5. 🚀 Deploy to Cloud Run (prod) with tag
```

---

## 🎯 Best Practices

### For Developers

1. **Use pre-commit hooks**
   ```bash
   # Already configured in the project
   ./scripts/lint-commit-push.sh "your message"
   ```

2. **Run linting locally before committing**
   ```bash
   make lint  # Backend
   npm run lint  # Frontend
   ```

3. **Don't rely on CI for linting**
   - Linting should be done locally
   - CI is a safety net, not the primary check

### For Production Deployments

1. **Always merge through pull requests**
2. **Review lint failures in prod workflow**
3. **Fix any issues before retry**
4. **Don't bypass quality gates**

---

## 📊 Comparison

### Before (Linting in Dev & Prod)
- ✅ Consistent quality checks
- ❌ Slower dev iterations
- ❌ Wasted CI time on experimental code

### After (Linting in Prod Only)
- ✅ Fast dev iterations
- ✅ Production quality guaranteed
- ✅ Efficient CI resource usage
- ✅ Better developer experience

---

## 🔧 Troubleshooting

### "My dev deployment is failing without lint errors"
- Check test failures (tests still run in dev)
- Check Docker build errors
- Check Cloud Run deployment errors

### "My prod deployment is failing with lint errors"
- Run linting locally to see all errors
- Fix formatting: `black app/` or `npm run format`
- Fix linting: `ruff check --fix app/` or `npm run lint`
- Commit and push fixes

### "I want to enable linting in dev"
1. Uncomment the lint job in dev workflow
2. Add it back to `needs:` in deploy job
3. Commit and push

---

## 📚 Related Documentation

- `AGENTS.md` - Project guidelines
- `PRE-COMMIT-CHECKLIST.md` - Local linting process
- `BLACK_FORMATTING_SETUP.md` - Black formatter setup
- `.github/workflows/README.md` - Workflows documentation

---

## ✅ Summary

**Development Strategy:**
- ⚡ Fast deployments
- 🧪 Focus on functionality testing
- 🚀 Quick iteration cycles

**Production Strategy:**
- 🛡️ Comprehensive quality checks
- ✅ All linting enforced
- 🎯 Zero-compromise code quality

**Result:**
- ⚡ 3.5 minutes saved per dev deployment
- 🛡️ Production code quality maintained
- 🚀 Better developer experience

