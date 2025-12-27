# 🧭 Documentation Navigation Guide

Quick reference for finding the right documentation.

## 📍 I'm looking for...

### Setup & Installation
| What | Document | Time |
|------|----------|------|
| Quick local setup | [../QUICKSTART.md](../QUICKSTART.md) | 5 min |
| Detailed setup | [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md) | 30 min |
| GCP authentication | [security/AUTHENTICATION.md](security/AUTHENTICATION.md) | 20 min |
| Environment config | [reference/environment-variables.md](reference/environment-variables.md) | 10 min |

### Deployment
| What | Document | Time |
|------|----------|------|
| Quick Cloud Run deploy | [deployment/quickstart.md](deployment/quickstart.md) | 10 min |
| Complete deployment guide | [deployment/CLOUD_RUN_DEPLOYMENT.md](deployment/CLOUD_RUN_DEPLOYMENT.md) | 60 min |
| CI/CD setup | [deployment/CLOUD_RUN_DEPLOYMENT.md#cicd](deployment/CLOUD_RUN_DEPLOYMENT.md) | 30 min |

### Security
| What | Document | Time |
|------|----------|------|
| Quick API key setup | [security/api-key-quickstart.md](security/api-key-quickstart.md) | 2 min |
| Complete API key guide | [security/API_KEY_SETUP.md](security/API_KEY_SETUP.md) | 20 min |
| GCP authentication | [security/AUTHENTICATION.md](security/AUTHENTICATION.md) | 30 min |

### Monitoring
| What | Document | Time |
|------|----------|------|
| Quick Datadog setup | [monitoring/quickstart.md](monitoring/quickstart.md) | 2 min |
| Complete Datadog guide | [monitoring/DATADOG_SETUP.md](monitoring/DATADOG_SETUP.md) | 45 min |
| APM configuration | [monitoring/DATADOG_SETUP.md#apm](monitoring/DATADOG_SETUP.md) | 20 min |
| LLM Observability | [monitoring/DATADOG_SETUP.md#llm](monitoring/DATADOG_SETUP.md) | 15 min |

### Features & Usage
| What | Document | Time |
|------|----------|------|
| Vote extractor guide | [features/vote-extractor.md](features/vote-extractor.md) | 15 min |
| API documentation | http://localhost:8000/docs | - |
| Feature list | [reference/features.md](reference/features.md) | 10 min |

### Development
| What | Document | Time |
|------|----------|------|
| Development workflow | [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md) | 45 min |
| Code organization | [getting-started/DEVELOPMENT.md#code-organization](getting-started/DEVELOPMENT.md) | 10 min |
| Testing guide | [getting-started/DEVELOPMENT.md#testing](getting-started/DEVELOPMENT.md) | 15 min |
| Best practices | [getting-started/DEVELOPMENT.md#best-practices](getting-started/DEVELOPMENT.md) | 20 min |

### Architecture & Planning
| What | Document | Time |
|------|----------|------|
| Project architecture | [../PROJECT_PLAN.md](../PROJECT_PLAN.md) | 30 min |
| Technology stack | [../PROJECT_PLAN.md#technology-stack](../PROJECT_PLAN.md) | 10 min |
| Future roadmap | [../PROJECT_PLAN.md#roadmap](../PROJECT_PLAN.md) | 15 min |

## 🎯 Common Tasks

### I want to...

**Get started locally**
1. [../QUICKSTART.md](../QUICKSTART.md)
2. [getting-started/GETTING_STARTED.md](getting-started/GETTING_STARTED.md)

**Deploy to production**
1. [deployment/quickstart.md](deployment/quickstart.md)
2. [security/api-key-quickstart.md](security/api-key-quickstart.md)
3. [monitoring/quickstart.md](monitoring/quickstart.md)

**Add a new feature**
1. [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md)
2. [../PROJECT_PLAN.md](../PROJECT_PLAN.md)

**Secure the API**
1. [security/api-key-quickstart.md](security/api-key-quickstart.md)
2. [security/API_KEY_SETUP.md](security/API_KEY_SETUP.md)

**Monitor in production**
1. [monitoring/quickstart.md](monitoring/quickstart.md)
2. [monitoring/DATADOG_SETUP.md](monitoring/DATADOG_SETUP.md)

**Troubleshoot issues**
1. Check service-specific README
2. [getting-started/GETTING_STARTED.md#troubleshooting](getting-started/GETTING_STARTED.md)
3. [deployment/CLOUD_RUN_DEPLOYMENT.md#troubleshooting](deployment/CLOUD_RUN_DEPLOYMENT.md)

## 📚 Documentation Index

For a complete, categorized list of all documentation, see:

**[INDEX.md](INDEX.md)** - Complete documentation index with:
- All documents organized by category
- Learning paths by role
- Search by topic
- Time estimates

## 🗺️ Site Map

```
Root Level:
├── README.md                         Main project overview
├── QUICKSTART.md                     ⭐ Start here (5 min)
└── PROJECT_PLAN.md                   Architecture & planning

docs/ (organized documentation):
├── INDEX.md                          Complete index
├── NAVIGATION.md                     This file
├── README.md                         Documentation overview
│
├── getting-started/                  Setup & development
├── deployment/                       Cloud Run deployment
├── security/                         Auth & API keys
├── monitoring/                       Datadog observability
├── features/                         Feature guides
├── reference/                        Configuration reference
└── archive/                          Implementation summaries
```

## 💡 Tips

1. **Start with QUICKSTART** - Get hands-on experience first
2. **Use quick starts** - Fast results before deep dives
3. **Follow learning paths** - Structured progression in INDEX.md
4. **Keep docs open** - Reference while working
5. **Check troubleshooting** - Most common issues covered

## 🔗 Related Resources

- **Service READMEs**:
  - [services/fastapi-backend/README.md](../services/fastapi-backend/README.md)
  - [frontend/streamlit/README.md](../frontend/streamlit/README.md)

- **Scripts**:
  - [infra/cloud-run/](../infra/cloud-run/) - Deployment scripts
  - [check-services.sh](../check-services.sh) - Service diagnostics

- **Main README**: [../README.md](../README.md)

---

**🎯 Quick Links:**
- 📚 [Complete Index](INDEX.md)
- 🚀 [Quick Start](../QUICKSTART.md)
- 🏗️ [Architecture](../PROJECT_PLAN.md)
- 💻 [Development](getting-started/DEVELOPMENT.md)

