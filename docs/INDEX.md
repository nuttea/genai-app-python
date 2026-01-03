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

5. **[getting-started/PRODUCTION_QUICKSTART.md](getting-started/PRODUCTION_QUICKSTART.md)**
   - Production deployment strategy
   - Branch management (main/prod)
   - Cloud Run revision tags

6. **[getting-started/LLM_CONFIG_QUICKSTART.md](getting-started/LLM_CONFIG_QUICKSTART.md)**
   - LLM model selection and configuration
   - Parameter tuning guide
   - Frontend integration

7. **[getting-started/LLMOBS_EVALUATIONS_QUICKSTART.md](getting-started/LLMOBS_EVALUATIONS_QUICKSTART.md)**
   - LLM Observability evaluations
   - Custom evaluations setup
   - Dataset management

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

- **[deployment/REUSABLE_WORKFLOWS_QUICKSTART.md](deployment/REUSABLE_WORKFLOWS_QUICKSTART.md)** ✅
  - Quick start for reusable GitHub Actions workflows
  - Template usage examples

- **[deployment/REUSABLE_WORKFLOWS_GUIDE.md](deployment/REUSABLE_WORKFLOWS_GUIDE.md)** ✅
  - Complete guide for reusable workflows
  - Best practices and patterns

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

- **[monitoring/DATADOG_LLMOBS_COMPLETE.md](monitoring/DATADOG_LLMOBS_COMPLETE.md)** ✅
  - Complete LLMObs implementation guide
  - Production setup and configuration

- **[monitoring/DATADOG_LLMOBS_LOCAL_SETUP.md](monitoring/DATADOG_LLMOBS_LOCAL_SETUP.md)** ✅
  - Local Docker Compose LLMObs setup
  - Development environment configuration

- **[monitoring/DATADOG_TRACE_AGENT_CONFIG.md](monitoring/DATADOG_TRACE_AGENT_CONFIG.md)** ✅
  - Trace agent configuration
  - Local and Cloud Run settings

### LLM Observability Guides

Comprehensive guides for implementing Datadog LLMObs:

- **[guides/llmobs/README.md](../guides/llmobs/README.md)** ⭐ START HERE
  - Index of all LLMObs guides
  - Quick start paths for different roles
  - Related documentation links

- **[guides/llmobs/sources/00_TRACING_LLM_APPLICATIONS.md](../guides/llmobs/sources/00_TRACING_LLM_APPLICATIONS.md)**
  - Introduction to LLM Observability
  - Why trace LLM applications
  - Key concepts and terminology

- **[guides/llmobs/sources/01_INSTRUMENTING_SPANS.md](../guides/llmobs/sources/01_INSTRUMENTING_SPANS.md)**
  - Span types (LLM, Workflow, Agent, Tool, Task, Embedding, Retrieval)
  - Using decorators vs manual annotation
  - Best practices for instrumentation

- **[guides/llmobs/sources/02_VISUALIZING_TRACES_AND_SPANS.md](../guides/llmobs/sources/02_VISUALIZING_TRACES_AND_SPANS.md)**
  - Viewing traces in Datadog
  - Understanding the trace waterfall
  - Using filters and search

- **[guides/llmobs/03_EVALUATION_METRIC_TYPES.md](../guides/llmobs/03_EVALUATION_METRIC_TYPES.md)** 🆕
  - Score vs Categorical metric types
  - Common evaluation labels (accuracy, toxicity, relevance, etc.)
  - Choosing the right metric type
  - Implementation examples and best practices
  - Visualization and monitoring strategies

- **[guides/llmobs/sources/99_ADDITIONAL_TOPICS.md](../guides/llmobs/sources/99_ADDITIONAL_TOPICS.md)**
  - Advanced configuration
  - Custom integrations
  - Performance optimization

### Features
- **[features/vote-extractor.md](features/vote-extractor.md)**
  - Thai election form extraction
  - User guide
  - Best practices
  - Troubleshooting
  - API integration
  - Batch processing

- **[features/LLM_CONFIGURATION.md](features/LLM_CONFIGURATION.md)**
  - Dynamic LLM provider/model selection
  - Model parameter tuning
  - Configuration guide
  - Best practices

- **[features/DATADOG_CONTENT_CREATOR_PLAN.md](features/DATADOG_CONTENT_CREATOR_PLAN.md)** 🆕
  - ADK Agent for content creation
  - Generate blog posts + video scripts from various inputs
  - Accept text, markdown, video demos
  - Create YouTube Shorts/TikTok/Reels scripts
  - Architecture and 7-week implementation plan

- **[features/DATADOG_CONTENT_CREATOR_QUICKREF.md](features/DATADOG_CONTENT_CREATOR_QUICKREF.md)** 🆕
  - Quick reference for Content Creator
  - Usage examples and workflows
  - Video script structure
  - Cost estimates

- **[features/ADK_ARTIFACTS_IMPLEMENTATION_COMPLETE.md](features/ADK_ARTIFACTS_IMPLEMENTATION_COMPLETE.md)** ✅
  - ADK Artifacts implementation complete
  - File upload and analysis
  - Multimodal support

- **[features/ADK_ARTIFACTS_BROWSER_TEST_RESULTS.md](features/ADK_ARTIFACTS_BROWSER_TEST_RESULTS.md)** ✅
  - Browser testing results for ADK Artifacts
  - File upload validation

- **[features/CONTENT_CREATOR_FILE_UPLOAD_TEST.md](features/CONTENT_CREATOR_FILE_UPLOAD_TEST.md)** ✅
  - File upload testing results
  - Frontend integration tests

- **[features/INTERACTIVE_SUGGESTED_ACTIONS.md](features/INTERACTIVE_SUGGESTED_ACTIONS.md)** ✅
  - Interactive content creator with contextual suggestions
  - Workflow-aware quick actions
  - Enhanced UX features

- **[features/VERCEL_AI_SDK_IMPLEMENTATION.md](features/VERCEL_AI_SDK_IMPLEMENTATION.md)** ✅
  - Vercel AI SDK integration
  - Streaming LLM responses
  - Beautiful markdown rendering

- **[features/GEMINI_3_PRO_IMAGE_SPECS.md](features/GEMINI_3_PRO_IMAGE_SPECS.md)** ✅
  - Gemini 3 Pro Image technical specs
  - API limits and constraints

- **[features/REFERENCE_IMAGES_FEATURE.md](features/REFERENCE_IMAGES_FEATURE.md)** ✅
  - Reference image upload feature
  - Multi-image support (up to 14)

### Troubleshooting
- **[troubleshooting/CORS_IAP_FIX.md](troubleshooting/CORS_IAP_FIX.md)**
  - CORS errors with "Redirect is not allowed for a preflight request"
  - Identity-Aware Proxy (IAP) conflicts
  - Cloud Run authentication issues
  - Complete diagnosis and fix steps

- **[troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md](troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md)**
  - JSON parsing errors (Unterminated string)
  - max_tokens configuration
  - Capacity guidelines
  - Solutions for multi-page extractions

- **[troubleshooting/DOCKER_BUILD_FIX.md](troubleshooting/DOCKER_BUILD_FIX.md)**
  - Docker build errors
  - README.md and dependency issues

- **[troubleshooting/FIX_SUMMARY.md](troubleshooting/FIX_SUMMARY.md)**
  - Recent fixes and improvements
  - Testing instructions

### Investigations
- **[investigations/MODELS_API_FINDINGS.md](investigations/MODELS_API_FINDINGS.md)**
  - Why `client.models.list()` returns 0 models
  - REST API vs Python SDK comparison
  - Static vs dynamic model listing

- **[investigations/INVESTIGATION_COMPLETE.md](investigations/INVESTIGATION_COMPLETE.md)**
  - Executive summary of findings
  - Validation of static model list approach

- **[investigations/OPTIONAL_DYNAMIC_MODELS.md](investigations/OPTIONAL_DYNAMIC_MODELS.md)**
  - Dynamic model listing with Google AI API
  - Trade-offs and considerations

- **[investigations/ADK_STREAMING_RESEARCH.md](investigations/ADK_STREAMING_RESEARCH.md)** ✅
  - ADK streaming capabilities research
  - Token-level vs accumulated text streaming
  - Performance analysis

- **[investigations/GOOGLE_ADK_CLIENT_EVALUATION.md](investigations/GOOGLE_ADK_CLIENT_EVALUATION.md)** ✅
  - Third-party ADK client evaluation
  - Comparison with manual SSE implementation

- **[investigations/STREAMING_INVESTIGATION_SUMMARY.md](investigations/STREAMING_INVESTIGATION_SUMMARY.md)** ✅
  - Comprehensive streaming investigation summary
  - Best practices and recommendations

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

- **[reference/DYNAMIC_MODELS_IMPLEMENTATION.md](reference/DYNAMIC_MODELS_IMPLEMENTATION.md)**
  - Dynamic model listing implementation
  - Architecture and design decisions
  - Caching strategy
  - Performance metrics

- **[reference/SETUP_GOOGLE_AI_API_KEY.md](reference/SETUP_GOOGLE_AI_API_KEY.md)**
  - Google AI API key setup
  - Configuration for dynamic model listing
  - Secret Manager integration

- **[reference/DOCKER_FIX_LOCAL_DEV.md](reference/DOCKER_FIX_LOCAL_DEV.md)**
  - Docker Compose configuration
  - Local development overrides
  - Datadog serverless-init handling

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
- [features/DATADOG_CONTENT_CREATOR_PLAN.md](features/DATADOG_CONTENT_CREATOR_PLAN.md) 🆕 - Content Creator plan
- [features/DATADOG_CONTENT_CREATOR_QUICKREF.md](features/DATADOG_CONTENT_CREATOR_QUICKREF.md) 🆕 - Content Creator quickref
- [reference/features.md](reference/features.md) - All features

### Reference & Configuration
- [reference/environment-variables.md](reference/environment-variables.md) - Env vars
- [reference/features.md](reference/features.md) - Feature list
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Architecture

## 🗺️ Documentation Map

```
docs/
├── INDEX.md                                ← You are here
│
├── getting-started/
│   ├── GETTING_STARTED.md                  # Detailed setup (30 min)
│   ├── DEVELOPMENT.md                      # Development guide (45 min)
│   ├── PRODUCTION_QUICKSTART.md            # Production deployment (5 min) ⭐
│   ├── LLM_CONFIG_QUICKSTART.md            # LLM configuration (5 min) ⭐
│   └── LLMOBS_EVALUATIONS_QUICKSTART.md    # LLMObs evaluations (5 min) ⭐
│
├── deployment/
│   ├── quickstart.md                           # Quick deploy (10 min) ⭐
│   ├── CLOUD_RUN_DEPLOYMENT.md                 # Complete guide (60 min)
│   ├── PRODUCTION_STRATEGY.md                  # Production strategy
│   ├── REUSABLE_WORKFLOWS_QUICKSTART.md        # ✅ Reusable workflows quickstart
│   └── REUSABLE_WORKFLOWS_GUIDE.md             # ✅ Complete reusable workflows guide
│
├── security/
│   ├── api-key-quickstart.md               # Quick setup (2 min) ⭐
│   ├── API_KEY_SETUP.md                    # Complete guide (20 min)
│   └── AUTHENTICATION.md                   # GCP auth (30 min)
│
├── monitoring/
│   ├── quickstart.md                           # Quick setup (2 min) ⭐
│   ├── DATADOG_SETUP.md                        # Complete guide (45 min)
│   ├── LLMOBS_NEXT_STEPS.md                    # LLMObs roadmap
│   ├── DATADOG_LLMOBS_COMPLETE.md              # ✅ Complete LLMObs implementation
│   ├── DATADOG_LLMOBS_LOCAL_SETUP.md           # ✅ Local Docker LLMObs setup
│   └── DATADOG_TRACE_AGENT_CONFIG.md           # ✅ Trace agent configuration
│
├── features/
│   ├── vote-extractor.md                            # Vote extraction guide (30 min)
│   ├── LLM_CONFIGURATION.md                         # LLM config guide
│   ├── DATADOG_CONTENT_CREATOR_PLAN.md              # 🆕 Content Creator implementation plan
│   ├── DATADOG_CONTENT_CREATOR_QUICKREF.md          # 🆕 Content Creator quick reference
│   ├── ADK_ARTIFACTS_IMPLEMENTATION_COMPLETE.md     # ✅ ADK Artifacts implementation
│   ├── ADK_ARTIFACTS_BROWSER_TEST_RESULTS.md        # ✅ ADK Artifacts testing
│   ├── CONTENT_CREATOR_FILE_UPLOAD_TEST.md          # ✅ File upload testing
│   ├── INTERACTIVE_SUGGESTED_ACTIONS.md             # ✅ Interactive UI enhancements
│   ├── VERCEL_AI_SDK_IMPLEMENTATION.md              # ✅ Vercel AI SDK integration
│   └── VERCEL_AI_SDK_TEST_SUCCESS.md                # ✅ Vercel AI SDK testing
│
├── troubleshooting/
│   ├── README.md                               # Troubleshooting index
│   ├── CORS_IAP_FIX.md                         # 🆕 CORS/IAP redirect errors
│   ├── TROUBLESHOOTING_MAX_TOKENS.md           # JSON parsing errors
│   ├── FIX_SUMMARY.md                          # Recent fixes
│   ├── STREAMING_FIX_SUMMARY.md                # ✅ Streaming fixes
│   ├── STREAMING_OPTIMIZATION_SUCCESS.md       # ✅ Streaming optimization
│   └── STREAMING_OPTIMIZATION_V2.md            # ✅ Advanced streaming optimizations
│
├── investigations/
│   ├── README.md                               # Investigation index
│   ├── MODELS_API_FINDINGS.md                  # Model listing findings
│   ├── INVESTIGATION_COMPLETE.md               # Investigation summary
│   ├── OPTIONAL_DYNAMIC_MODELS.md              # Dynamic models approach
│   ├── TEST_MODELS_API.md                      # Test results
│   ├── ADK_STREAMING_RESEARCH.md               # ✅ ADK streaming research
│   ├── GOOGLE_ADK_CLIENT_EVALUATION.md         # ✅ Third-party client evaluation
│   └── STREAMING_INVESTIGATION_SUMMARY.md      # ✅ Streaming investigation summary
│
├── reference/
│   ├── environment-variables.md            # All env vars
│   ├── features.md                         # Feature list
│   ├── DYNAMIC_MODELS_IMPLEMENTATION.md    # Dynamic models impl
│   ├── SETUP_GOOGLE_AI_API_KEY.md          # API key setup
│   ├── DOCKER_FIX_LOCAL_DEV.md             # Docker config
│   ├── DATADOG_BILLING_BILLABLE_UNITS.md   # Billing guide
│   ├── CURSOR_RULES_COMPLETE.md            # Cursor rules reference
│   └── PROJECT_STRUCTURE.md                # Project structure
│
└── archive/                                # Historical/reference only
    ├── Implementation summaries (setup, deployment, features)
    ├── Migration histories (ADK, workflows, documentation)
    ├── Specific fix summaries (auth, image creator, streaming)
    ├── Test results and investigations
    └── Progress reports and status updates
    
    Note: See docs/archive/ for 40+ historical documents

guides/llmobs/                              # 🆕 LLM Observability Guides
├── README.md                               # ⭐ LLMObs guides index
├── 03_EVALUATION_METRIC_TYPES.md           # 🆕 Score vs Categorical metrics
└── sources/
    ├── 00_TRACING_LLM_APPLICATIONS.md      # LLMObs introduction
    ├── 01_INSTRUMENTING_SPANS.md           # Span types and annotation
    ├── 02_VISUALIZING_TRACES_AND_SPANS.md  # Viewing traces in Datadog
    ├── 99_ADDITIONAL_TOPICS.md             # Advanced topics
    └── images/                             # Guide images and diagrams
```

**Test Scripts:**
```
scripts/tests/
├── README.md                           # Test scripts index
├── test_google_ai_api.py               # Google AI API test
├── test_rest_api_models.py             # REST API test
├── test_both_sdk_approaches.py         # SDK comparison
├── test_gemini_models_api.py           # Vertex AI test
├── test_dynamic_models.py              # Dynamic listing test
├── debug_models_api.py                 # Debug script
└── test_list_all_models.sh             # Shell script
```

**Utility Scripts:**
```
scripts/
├── format-only.sh                      # Format code without commit
├── lint-commit-push.sh                 # Complete pre-commit workflow
├── quick-push.sh                       # Quick commit and push
├── check-services.sh                   # Service health checks
├── PERMISSION_FIX_GEMINI_IMAGE.sh      # Fix Gemini image permissions
└── QUICK_FIX_COMMANDS.sh               # Quick fix commands
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

- **Total Files**: 30+ markdown documents
- **Total Content**: ~15,000+ lines
- **Categories**: 9 main categories
- **Quick Starts**: 7 guides
- **Complete Guides**: 12 guides
- **Reference**: 5 documents
- **Troubleshooting**: 2 guides
- **Investigations**: 4 reports
- **Test Scripts**: 7 scripts
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

### Datadog Content Creator (ADK Agent)
- [features/DATADOG_CONTENT_CREATOR_PLAN.md](features/DATADOG_CONTENT_CREATOR_PLAN.md) 🆕
- [features/DATADOG_CONTENT_CREATOR_QUICKREF.md](features/DATADOG_CONTENT_CREATOR_QUICKREF.md) 🆕

### Environment Variables
- [reference/environment-variables.md](reference/environment-variables.md)

### Development
- [getting-started/DEVELOPMENT.md](getting-started/DEVELOPMENT.md)

### Architecture
- [PROJECT_PLAN.md](../PROJECT_PLAN.md)

### LLM Configuration
- [getting-started/LLM_CONFIG_QUICKSTART.md](getting-started/LLM_CONFIG_QUICKSTART.md)
- [features/LLM_CONFIGURATION.md](features/LLM_CONFIGURATION.md)

### Production Deployment
- [getting-started/PRODUCTION_QUICKSTART.md](getting-started/PRODUCTION_QUICKSTART.md)
- [deployment/PRODUCTION_STRATEGY.md](deployment/PRODUCTION_STRATEGY.md)

### LLM Observability
- [getting-started/LLMOBS_EVALUATIONS_QUICKSTART.md](getting-started/LLMOBS_EVALUATIONS_QUICKSTART.md)
- [monitoring/LLMOBS_NEXT_STEPS.md](monitoring/LLMOBS_NEXT_STEPS.md)
- [guides/llmobs/README.md](../guides/llmobs/README.md) ⭐ - Complete LLMObs guides
- [guides/llmobs/03_EVALUATION_METRIC_TYPES.md](../guides/llmobs/03_EVALUATION_METRIC_TYPES.md) 🆕 - Evaluation metric types
- [docs/features/VOTE_EXTRACTION_LLMOBS_SPANS.md](features/VOTE_EXTRACTION_LLMOBS_SPANS.md) - Production example
- [docs/features/USER_FEEDBACK_LLMOBS_PLAN.md](features/USER_FEEDBACK_LLMOBS_PLAN.md) 🆕 - User feedback plan

### Troubleshooting
- [troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md](troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md)
- [troubleshooting/FIX_SUMMARY.md](troubleshooting/FIX_SUMMARY.md)

### Model Listing
- [investigations/MODELS_API_FINDINGS.md](investigations/MODELS_API_FINDINGS.md)
- [investigations/INVESTIGATION_COMPLETE.md](investigations/INVESTIGATION_COMPLETE.md)
- [reference/DYNAMIC_MODELS_IMPLEMENTATION.md](reference/DYNAMIC_MODELS_IMPLEMENTATION.md)

### Test Scripts
- [../../scripts/tests/README.md](../../scripts/tests/README.md)

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
- "How do I deploy to production?" → [getting-started/PRODUCTION_QUICKSTART.md](getting-started/PRODUCTION_QUICKSTART.md)
- "How do I secure it?" → [security/api-key-quickstart.md](security/api-key-quickstart.md)
- "How do I monitor?" → [monitoring/quickstart.md](monitoring/quickstart.md)
- "How does it work?" → [PROJECT_PLAN.md](../PROJECT_PLAN.md)
- "How do I configure LLMs?" → [getting-started/LLM_CONFIG_QUICKSTART.md](getting-started/LLM_CONFIG_QUICKSTART.md)
- "CORS errors?" → [troubleshooting/CORS_IAP_FIX.md](troubleshooting/CORS_IAP_FIX.md)
- "JSON parsing errors?" → [troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md](troubleshooting/TROUBLESHOOTING_MAX_TOKENS.md)
- "Why no models listed?" → [investigations/MODELS_API_FINDINGS.md](investigations/MODELS_API_FINDINGS.md)
- "How to test?" → [../../scripts/tests/README.md](../../scripts/tests/README.md)

## 📝 Documentation Updates

This documentation structure was organized on December 27, 2024.

**Changelog:**
- Organized into 6 main categories
- Created quick start guides
- Moved implementation summaries to archive
- Created this index for easy navigation

---

**Need to find something?** Use Cmd/Ctrl+F to search this index, or check the category that matches your needs!
