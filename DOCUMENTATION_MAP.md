# 📚 Documentation & Scripts Map

Complete overview of all documentation and test scripts in the GenAI Application Platform.

## 🗂️ Organization Structure

### Documentation (`docs/`)

```
docs/
├── INDEX.md                      ← Full documentation index
│
├── getting-started/              Quick start and getting started guides
├── deployment/                   Deployment and Cloud Run guides
├── security/                     Authentication and API key guides
├── monitoring/                   Datadog and observability guides
├── features/                     Feature documentation
├── troubleshooting/              Problem solving and fixes
├── investigations/               Research findings and investigations
├── reference/                    Technical reference docs
└── archive/                      Historical implementation summaries
```

### Test Scripts (`scripts/tests/`)

```
scripts/tests/
├── README.md                     ← Test scripts index
│
├── test_google_ai_api.py         Test Google AI API with SDK
├── test_rest_api_models.py       Test REST API directly (works!)
├── test_both_sdk_approaches.py   Compare SDKs
├── test_gemini_models_api.py     Test Vertex AI
├── test_dynamic_models.py        Test dynamic model listing
├── debug_models_api.py           Debug helper
└── test_list_all_models.sh       Shell script for quick testing
```

## 🚀 Quick Access

### I want to...

**Get started fast**
→ [`QUICKSTART.md`](./QUICKSTART.md)

**Deploy to production**
→ [`docs/getting-started/PRODUCTION_QUICKSTART.md`](./docs/getting-started/PRODUCTION_QUICKSTART.md)

**Configure LLM models**
→ [`docs/getting-started/LLM_CONFIG_QUICKSTART.md`](./docs/getting-started/LLM_CONFIG_QUICKSTART.md)

**Fix JSON parsing errors**
→ [`docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md`](./docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md)

**Understand why model listing returns 0**
→ [`docs/investigations/MODELS_API_FINDINGS.md`](./docs/investigations/MODELS_API_FINDINGS.md)

**Run test scripts**
→ [`scripts/tests/README.md`](./scripts/tests/README.md)

**Browse all documentation**
→ [`docs/INDEX.md`](./docs/INDEX.md)

## 📋 Documentation by Category

### 🌟 Essential (Start Here)
1. **[QUICKSTART.md](./QUICKSTART.md)** - Get running in 5 minutes
2. **[CURSOR_COMMANDS.md](./CURSOR_COMMANDS.md)** - 🎯 **NEW!** Cursor custom commands (lint, commit, push)
3. **[PRE-COMMIT-CHECKLIST.md](./PRE-COMMIT-CHECKLIST.md)** - ⚠️ Format before commit (REQUIRED!)
4. **[README.md](./README.md)** - Project overview
5. **[docs/INDEX.md](./docs/INDEX.md)** - Full documentation index

### 🚀 Quick Starts (5-10 min reads)
- **[Deployment](./docs/deployment/quickstart.md)** - Deploy to Cloud Run
- **[Production](./docs/getting-started/PRODUCTION_QUICKSTART.md)** - Production strategy
- **[API Keys](./docs/security/api-key-quickstart.md)** - Secure endpoints
- **[Monitoring](./docs/monitoring/quickstart.md)** - Datadog setup
- **[LLM Config](./docs/getting-started/LLM_CONFIG_QUICKSTART.md)** - Configure models
- **[LLMObs Evals](./docs/getting-started/LLMOBS_EVALUATIONS_QUICKSTART.md)** - Evaluations

### 📖 Complete Guides (30-60 min reads)
- **[Getting Started](./docs/getting-started/GETTING_STARTED.md)** - Detailed setup
- **[Development](./docs/getting-started/DEVELOPMENT.md)** - Development workflow
- **[Cloud Run](./docs/deployment/CLOUD_RUN_DEPLOYMENT.md)** - Full deployment guide
- **[Authentication](./docs/security/AUTHENTICATION.md)** - GCP auth
- **[Datadog](./docs/monitoring/DATADOG_SETUP.md)** - Full observability
- **[Vote Extractor](./docs/features/vote-extractor.md)** - Feature guide

### 🔧 Troubleshooting
- **[MAX_TOKENS](./docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md)** - JSON parsing errors
- **[Fix Summary](./docs/troubleshooting/FIX_SUMMARY.md)** - Recent fixes
- **[Troubleshooting Index](./docs/troubleshooting/README.md)** - All issues

### 🔍 Investigations & Research
- **[Model Listing Findings](./docs/investigations/MODELS_API_FINDINGS.md)** - Why .list() returns 0
- **[Investigation Summary](./docs/investigations/INVESTIGATION_COMPLETE.md)** - Executive summary
- **[Dynamic Models Option](./docs/investigations/OPTIONAL_DYNAMIC_MODELS.md)** - Alternative approach
- **[Investigations Index](./docs/investigations/README.md)** - All findings

### 📚 Reference
- **[Environment Variables](./docs/reference/environment-variables.md)** - All env vars
- **[Features List](./docs/reference/features.md)** - Feature catalog
- **[Dynamic Models Impl](./docs/reference/DYNAMIC_MODELS_IMPLEMENTATION.md)** - Implementation
- **[Google AI API Setup](./docs/reference/SETUP_GOOGLE_AI_API_KEY.md)** - API key config
- **[Docker Config](./docs/reference/DOCKER_FIX_LOCAL_DEV.md)** - Local dev setup

### 🧪 Test Scripts
- **[Tests Index](./scripts/tests/README.md)** - All test scripts
- **7 test scripts** for validating model listing, dynamic features, APIs

## 🎯 By Role

### For Users
1. [QUICKSTART.md](./QUICKSTART.md) - Get started
2. [Vote Extractor](./docs/features/vote-extractor.md) - Use the app
3. [LLM Config](./docs/getting-started/LLM_CONFIG_QUICKSTART.md) - Configure models

### For Developers
1. [QUICKSTART.md](./QUICKSTART.md) - Get started
2. [Getting Started](./docs/getting-started/GETTING_STARTED.md) - Setup
3. [Development](./docs/getting-started/DEVELOPMENT.md) - Workflow
4. [Test Scripts](./scripts/tests/README.md) - Testing

### For DevOps
1. [Deployment Quickstart](./docs/deployment/quickstart.md) - Deploy
2. [Production Quickstart](./docs/getting-started/PRODUCTION_QUICKSTART.md) - Production
3. [API Keys](./docs/security/api-key-quickstart.md) - Secure
4. [Monitoring](./docs/monitoring/quickstart.md) - Observe

### For Troubleshooters
1. [Troubleshooting Index](./docs/troubleshooting/README.md) - Common issues
2. [MAX_TOKENS Guide](./docs/troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md) - JSON errors
3. [Investigations](./docs/investigations/README.md) - Root causes

## 📊 Statistics

| Category | Count | Description |
|----------|-------|-------------|
| **Quick Starts** | 9 | Fast 5-10 min guides |
| **Complete Guides** | 3 | In-depth 30-60 min docs |
| **Troubleshooting** | 2 | Problem-solving guides |
| **Investigations** | 4 | Research findings |
| **Reference Docs** | 6 | Technical reference |
| **Deployment Docs** | 5 | Deployment and production |
| **Test Scripts** | 8 | Validation scripts |
| **Archive** | 14 | Historical summaries |
| **Root Docs** | 5 | Core project docs |

**Total:** 56 documentation files + 8 test scripts

**Root Directory (Core Docs):**
- README.md - Project overview
- QUICKSTART.md - 5-minute setup
- DOCUMENTATION_MAP.md - Master navigation
- PROJECT_PLAN.md - Architecture

## 🔗 Key Links

- **Main Index:** [`docs/INDEX.md`](./docs/INDEX.md)
- **Tests Index:** [`scripts/tests/README.md`](./scripts/tests/README.md)
- **Troubleshooting:** [`docs/troubleshooting/README.md`](./docs/troubleshooting/README.md)
- **Investigations:** [`docs/investigations/README.md`](./docs/investigations/README.md)

## 💡 Navigation Tips

1. **Start with** [`docs/INDEX.md`](./docs/INDEX.md) for full documentation overview
2. **Quick starts** are marked with ⭐ (5-10 minutes each)
3. **Troubleshooting?** Check [`docs/troubleshooting/`](./docs/troubleshooting/)
4. **Testing?** Check [`scripts/tests/`](./scripts/tests/)
5. **Research?** Check [`docs/investigations/`](./docs/investigations/)

## 📝 Recent Organization (Dec 29, 2024)

### What Changed
- ✅ Created `docs/troubleshooting/` directory
- ✅ Created `docs/investigations/` directory  
- ✅ Created `scripts/tests/` directory
- ✅ Moved 13 documentation files to proper locations
- ✅ Moved 7 test scripts to `scripts/tests/`
- ✅ Created README indexes for each section
- ✅ Updated main INDEX.md with new structure

### Before → After
```
Root/                          Root/
├── test_*.py (scattered)  →  ├── scripts/tests/ (organized)
├── *_FINDINGS.md (mixed)  →  ├── docs/investigations/ (organized)
└── TROUBLESHOOTING.md     →  └── docs/troubleshooting/ (organized)
```

## 🆘 Need Help?

**Can't find what you need?**

1. Check [`docs/INDEX.md`](./docs/INDEX.md) - Full documentation index
2. Check [`docs/troubleshooting/README.md`](./docs/troubleshooting/README.md) - Common issues
3. Check [`scripts/tests/README.md`](./scripts/tests/README.md) - Test scripts
4. Use Cmd/Ctrl+F to search this file or INDEX.md
5. Review logs: `docker logs genai-fastapi-backend --tail 100`

---

**Last Updated:** December 29, 2024

**🎉 Everything is now organized and documented!**

