# 📚 Documentation Index

Complete guide to all documentation for the GenAI Application Platform.

## 🚀 Quick Start Guides (5-10 minutes)

Start here if you're new to the project:

1. **[QUICKSTART.md](../QUICKSTART.md)** ⭐ START HERE
   - 5-minute setup for local development
   - Get the app running quickly
   - Test with sample requests

2. **[deployment/quickstart.md](deployment/quickstart.md)**
   - 10-minute Cloud Run deployment
   - Production-ready in minutes
   - Automatic HTTPS and scaling

3. **[security/api-key-quickstart.md](security/api-key-quickstart.md)**
   - 2-minute API key setup
   - Secure your endpoints
   - Local and Cloud Run

4. **[monitoring/quickstart.md](monitoring/quickstart.md)**
   - 2-minute Datadog setup
   - Enable full observability
   - APM and LLM tracking

## 📖 Complete Guides (30-60 minutes)

Comprehensive documentation for deep dives:

### Getting Started
- **[getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md)**
  - Detailed setup instructions
  - Prerequisites and requirements
  - GCP configuration
  - Troubleshooting

- **[getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md)**
  - Development workflow
  - Code organization
  - Testing strategies
  - Best practices
  - Git workflow

### Deployment
- **[deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md)**
  - Complete Cloud Run guide
  - Manual and automated deployment
  - CI/CD setup with Cloud Build
  - Cost optimization
  - Custom domains
  - Rollback strategies
  - Monitoring and logging

### Security
- **[security/AUTHENTICATION.md](security/AUTHENTICATION.md)**
  - GCP authentication methods
  - Application Default Credentials (ADC)
  - Service accounts
  - Workload Identity
  - Troubleshooting auth issues

- **[security/API_KEY_SETUP.md](security/API_KEY_SETUP.md)**
  - API key authentication
  - Secret Manager integration
  - Key rotation
  - Usage tracking
  - Security best practices

### Monitoring
- **[monitoring/DATADOG_SETUP.md](monitoring/DATADOG_SETUP.md)**
  - Datadog APM setup
  - LLM Observability
  - serverless-init configuration
  - Dashboard creation
  - Alerting
  - Cost optimization

### Features
- **[features/vote-extractor.md](features/vote-extractor.md)**
  - Thai election form extraction
  - User guide
  - Best practices
  - Troubleshooting
  - API integration
  - Batch processing

### Reference
- **[reference/environment-variables.md](reference/environment-variables.md)**
  - All environment variables
  - Configuration options
  - Default values
  - Examples for different environments

- **[reference/features.md](reference/features.md)**
  - Complete feature list
  - Implemented vs planned
  - Technical details
  - Use cases

## 🏗️ Architecture & Planning

- **[PROJECT_PLAN.md](../PROJECT_PLAN.md)**
  - Overall architecture
  - Technology stack
  - Project phases
  - Future roadmap
  - Timeline estimates

## 📁 Documentation by Category

### For Users
1. [QUICKSTART.md](../QUICKSTART.md) - Get started fast
2. [features/vote-extractor.md](features/vote-extractor.md) - Use the vote extractor
3. API documentation at `/docs` endpoint

### For Developers
1. [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) - Setup
2. [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md) - Development
3. [reference/environment-variables.md](reference/environment-variables.md) - Configuration
4. [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Architecture

### For DevOps
1. [deployment/quickstart.md](deployment/quickstart.md) - Quick deploy
2. [deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md) - Full guide
3. [security/api-key-quickstart.md](security/api-key-quickstart.md) - API keys
4. [monitoring/quickstart.md](monitoring/quickstart.md) - Monitoring

### For Security Engineers
1. [security/AUTHENTICATION.md](security/AUTHENTICATION.md) - GCP auth
2. [security/API_KEY_SETUP.md](security/API_KEY_SETUP.md) - API keys
3. [security/api-key-quickstart.md](security/api-key-quickstart.md) - Quick setup

### For SREs / Platform Engineers
1. [monitoring/DATADOG_SETUP.md](monitoring/DATADOG_SETUP.md) - Observability
2. [monitoring/quickstart.md](monitoring/quickstart.md) - Quick setup
3. [deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md) - Production

## 📝 Documentation by Topic

### Setup & Installation
- [QUICKSTART.md](../QUICKSTART.md) ⭐ 5 minutes
- [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) - Detailed
- [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md) - Development

### Deployment & Operations
- [deployment/quickstart.md](deployment/quickstart.md) ⭐ 10 minutes
- [deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md) - Complete

### Security & Authentication
- [security/api-key-quickstart.md](security/api-key-quickstart.md) ⭐ 2 minutes
- [security/API_KEY_SETUP.md](security/API_KEY_SETUP.md) - Complete
- [security/AUTHENTICATION.md](security/AUTHENTICATION.md) - GCP auth

### Monitoring & Observability
- [monitoring/quickstart.md](monitoring/quickstart.md) ⭐ 2 minutes
- [monitoring/DATADOG_SETUP.md](monitoring/DATADOG_SETUP.md) - Complete

### Features & Usage
- [features/vote-extractor.md](features/vote-extractor.md) - Vote extraction
- [reference/features.md](reference/features.md) - All features

### Reference & Configuration
- [reference/environment-variables.md](reference/environment-variables.md) - Env vars
- [reference/features.md](reference/features.md) - Feature list
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Architecture

## 🗺️ Documentation Map

```
docs/
├── INDEX.md                          ← You are here
│
├── getting-started/
│   ├── GETTING_STARTED.md            # Detailed setup (30 min)
│   └── DEVELOPMENT.md                # Development guide (45 min)
│
├── deployment/
│   ├── quickstart.md                 # Quick deploy (10 min) ⭐
│   └── CLOUD_RUN_DEPLOYMENT.md       # Complete guide (60 min)
│
├── security/
│   ├── api-key-quickstart.md         # Quick setup (2 min) ⭐
│   ├── API_KEY_SETUP.md              # Complete guide (20 min)
│   └── AUTHENTICATION.md             # GCP auth (30 min)
│
├── monitoring/
│   ├── quickstart.md                 # Quick setup (2 min) ⭐
│   └── DATADOG_SETUP.md              # Complete guide (45 min)
│
├── features/
│   └── vote-extractor.md             # Vote extraction guide (30 min)
│
├── reference/
│   ├── environment-variables.md      # All env vars
│   └── features.md                   # Feature list
│
└── archive/                          # Historical/reference only
    ├── SETUP_COMPLETE.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── CLOUD_RUN_SETUP_COMPLETE.md
    ├── DATADOG_IMPLEMENTATION_SUMMARY.md
    └── FINAL_IMPLEMENTATION_SUMMARY.md
```

## 🎯 Learning Paths

### Path 1: User (Want to use the app)
1. [QUICKSTART.md](../QUICKSTART.md) - Get it running
2. [features/vote-extractor.md](features/vote-extractor.md) - Use the feature
3. API docs at http://localhost:8000/docs

**Time**: 15 minutes

### Path 2: Developer (Want to modify/extend)
1. [QUICKSTART.md](../QUICKSTART.md) - Get it running
2. [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) - Setup
3. [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md) - Development
4. [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Architecture

**Time**: 2 hours

### Path 3: DevOps (Want to deploy)
1. [deployment/quickstart.md](deployment/quickstart.md) - Quick deploy
2. [security/api-key-quickstart.md](security/api-key-quickstart.md) - Secure it
3. [monitoring/quickstart.md](monitoring/quickstart.md) - Monitor it
4. [deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md) - Production

**Time**: 1 hour

### Path 4: SRE (Want to operate in production)
1. [deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md) - Deploy
2. [monitoring/DATADOG_SETUP.md](monitoring/DATADOG_SETUP.md) - Observe
3. [security/API_KEY_SETUP.md](security/API_KEY_SETUP.md) - Secure
4. [security/AUTHENTICATION.md](security/AUTHENTICATION.md) - Auth

**Time**: 3 hours

## 📊 Documentation Statistics

- **Total Files**: 17 markdown documents
- **Total Content**: ~10,000+ lines
- **Categories**: 6 main categories
- **Quick Starts**: 4 guides
- **Complete Guides**: 8 guides
- **Reference**: 2 documents
- **Archive**: 5 summaries

## 🔍 Search by Topic

### Setup & Installation
- [QUICKSTART.md](../QUICKSTART.md)
- [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md)

### Docker
- [QUICKSTART.md](../QUICKSTART.md)
- [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md)
- [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md)

### Cloud Run
- [deployment/quickstart.md](deployment/quickstart.md)
- [deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md)

### API Keys
- [security/api-key-quickstart.md](security/api-key-quickstart.md)
- [security/API_KEY_SETUP.md](security/API_KEY_SETUP.md)

### Datadog
- [monitoring/quickstart.md](monitoring/quickstart.md)
- [monitoring/DATADOG_SETUP.md](monitoring/DATADOG_SETUP.md)

### GCP Authentication
- [security/AUTHENTICATION.md](security/AUTHENTICATION.md)

### Vote Extraction
- [features/vote-extractor.md](features/vote-extractor.md)

### Environment Variables
- [reference/environment-variables.md](reference/environment-variables.md)

### Development
- [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md)

### Architecture
- [PROJECT_PLAN.md](../PROJECT_PLAN.md)

## 💡 Tips for Reading

1. **⭐ Starred documents** are quick starts - read these first
2. **Time estimates** show expected reading/setup time
3. **Follow learning paths** based on your role
4. **Use search** (Cmd/Ctrl+F) to find specific topics
5. **Check archive/** for implementation details

## 🆘 Getting Help

**Can't find what you need?**

1. Check this INDEX for navigation
2. Use search in your editor
3. Check [PROJECT_PLAN.md](../PROJECT_PLAN.md) for architecture
4. Review relevant quick start guide
5. Check service logs for errors

**Common Questions:**
- "How do I start?" → [QUICKSTART.md](../QUICKSTART.md)
- "How do I deploy?" → [deployment/quickstart.md](deployment/quickstart.md)
- "How do I secure it?" → [security/api-key-quickstart.md](security/api-key-quickstart.md)
- "How do I monitor?" → [monitoring/quickstart.md](monitoring/quickstart.md)
- "How does it work?" → [PROJECT_PLAN.md](../PROJECT_PLAN.md)

## 📝 Documentation Updates

This documentation structure was organized on December 27, 2024.

**Changelog:**
- Organized into 6 main categories
- Created quick start guides
- Moved implementation summaries to archive
- Created this index for easy navigation

---

**Need to find something?** Use Cmd/Ctrl+F to search this index, or check the category that matches your needs!
