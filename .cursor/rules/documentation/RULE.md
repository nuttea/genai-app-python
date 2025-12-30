# Documentation Rules

## Scope
**Paths**: `docs/**/*.md`, `*.md`, `scripts/tests/README.md`

## Documentation Structure

### Organization
```
Root/
├── README.md                 Core: Project overview
├── QUICKSTART.md             Core: 5-minute setup
├── DOCUMENTATION_MAP.md      Core: Master navigation
├── PROJECT_PLAN.md           Core: Architecture
├── PROJECT_STRUCTURE.md      Core: Structure
├── AGENTS.md                 Core: AI agent instructions
│
└── docs/
    ├── INDEX.md              Full documentation index
    ├── getting-started/      Quickstarts and setup
    ├── deployment/           Cloud Run and production
    ├── security/             Auth and API keys
    ├── monitoring/           Datadog and observability
    ├── features/             Feature documentation
    ├── troubleshooting/      Problem-solving guides
    ├── investigations/       Research findings
    ├── reference/            Technical reference
    └── archive/              Historical documentation
```

## Writing Style

### ✅ Good Documentation
```markdown
# Feature Name

## Overview
Brief description of what this feature does and why it exists.

## Quick Start (5 minutes)
1. First step with command
   ```bash
   command example
   ```
2. Second step
3. Third step

## How It Works
Detailed explanation with examples.

## Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| VAR_NAME | value | What it does |

## Common Issues
### Issue: Error message
**Solution**: How to fix it

## Related Documentation
- [Link to related doc](./path.md)
```

### ❌ Bad Documentation
```markdown
# Feature

This feature does things.

## Setup
Run commands.

## Usage
Use it.
```

## Documentation Types

### Quick Start Guides (5-10 min)
**Purpose**: Get users productive fast
**Format**:
- Start with prerequisites
- Step-by-step numbered instructions
- Include copy-paste commands
- Show expected output
- End with verification step

**Example**:
```markdown
# Feature Quickstart

## Prerequisites
- Docker installed
- GCP account

## Steps

1. **Configure environment**
   ```bash
   export VAR=value
   ```

2. **Run setup**
   ```bash
   ./setup.sh
   ```

   Expected output:
   ```
   ✅ Setup complete
   ```

3. **Verify**
   ```bash
   curl http://localhost:8000/health
   ```

## Next Steps
- [Full documentation](./FEATURE.md)
- [Troubleshooting](../troubleshooting/)
```

### Complete Guides (30-60 min)
**Purpose**: Comprehensive understanding
**Format**:
- Introduction and context
- Architecture/design decisions
- Step-by-step with explanations
- Configuration options
- Best practices
- Troubleshooting
- Examples and use cases
- Related documentation

### Troubleshooting Guides
**Purpose**: Solve specific problems
**Format**:
```markdown
# Troubleshooting: Problem Name

## Symptoms
- Error message or behavior
- When it occurs
- Impact

## Root Cause
Why this happens

## Solution
Step-by-step fix with commands

## Prevention
How to avoid it in the future

## Related Issues
- Link to similar problems
```

### Investigation Reports
**Purpose**: Document research findings
**Format**:
```markdown
# Investigation: Topic

## Summary
TL;DR of findings

## Question
What we were investigating

## Approach
How we investigated

## Findings
1. Finding with evidence
2. Finding with evidence

## Conclusion
What we learned and decided

## Recommendations
What to do based on findings
```

## Code Examples

### ✅ Good Code Examples
```markdown
## Example: API Call

```python
import httpx

async def call_api() -> dict:
    """Call backend API with proper error handling."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/api/v1/models")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"API call failed: {e}")
        raise
```

**Key points:**
- Use async/await for I/O
- Set timeouts
- Handle errors properly
```

### ❌ Bad Code Examples
```markdown
Example:
```python
response = requests.get(url)
data = response.json()
```
```

## Formatting Standards

### Headers
```markdown
# H1: Page Title (once per document)
## H2: Major Sections
### H3: Subsections
#### H4: Detailed Points (use sparingly)
```

### Code Blocks
```markdown
# ✅ Good - Language specified
```python
def example():
    pass
```

# ❌ Bad - No language
```
def example():
    pass
```
```

### Links
```markdown
# ✅ Good - Descriptive text
See [Deployment Guide](./DEPLOYMENT.md) for details.

# ✅ Good - Relative paths
[API Reference](../reference/api.md)

# ❌ Bad - "Click here"
For more info, [click here](./doc.md).

# ❌ Bad - Absolute paths
[Guide](/Users/name/project/docs/guide.md)
```

### Tables
```markdown
# ✅ Good - Clear headers and alignment
| Feature | Status | Notes |
|---------|--------|-------|
| Auth | ✅ Done | See security/ |
| Deploy | ✅ Done | See deployment/ |

# ❌ Bad - No alignment
|Feature|Status|
|---|---|
|Auth|Done|
```

### Emojis (Use Sparingly)
```markdown
# ✅ Good - Clear status indicators
- ✅ Completed feature
- ❌ Known issue
- ⚠️ Warning
- 🚀 Quick start
- 📚 Documentation
- 🔧 Configuration

# ❌ Bad - Overuse
🎉🎉🎉 Amazing Feature 🚀🚀🚀
This is 💯 the best! 😎
```

## Index Files

### Section README.md
```markdown
# Section Name

Brief description of this section.

## Contents

- **[FILE1.md](./FILE1.md)** - Description (5 min read)
- **[FILE2.md](./FILE2.md)** - Description (30 min read)

## Quick Access

### By Task
- Want to X? → [FILE1.md](./FILE1.md)
- Want to Y? → [FILE2.md](./FILE2.md)

## Related Documentation
- [Other Section](../other/)
```

## Maintenance

### When to Update Documentation

**Always update when:**
- ✅ Adding new features
- ✅ Changing APIs or interfaces
- ✅ Modifying configuration options
- ✅ Fixing bugs (add to troubleshooting)
- ✅ Making architectural changes

**Update locations:**
- ✅ Feature docs in `docs/features/`
- ✅ API changes in OpenAPI and `docs/api/`
- ✅ Config changes in `docs/reference/environment-variables.md`
- ✅ Troubleshooting if fix is not obvious
- ✅ Index files when adding/removing docs

### Documentation Checklist

For new features:
- [ ] Update or create feature documentation
- [ ] Add API documentation if applicable
- [ ] Update configuration reference
- [ ] Add examples and use cases
- [ ] Update relevant index files
- [ ] Link from `DOCUMENTATION_MAP.md`
- [ ] Add to `docs/INDEX.md`

## Common Patterns

### Prerequisites Section
```markdown
## Prerequisites

- **Required**:
  - Python 3.11+
  - Docker Desktop
  - GCP Account with billing enabled

- **Optional**:
  - `gcloud` CLI for deployment
  - Datadog account for monitoring
```

### Command Examples
```markdown
## Running Tests

```bash
# Backend tests
cd services/fastapi-backend
poetry run pytest tests/ -v

# Frontend tests
cd frontend/streamlit
poetry run pytest tests/ -v
```

Expected output:
```
===== test session starts =====
collected 10 items
tests/test_api.py ........ [ 80%]
tests/test_service.py ..   [100%]

===== 10 passed in 2.5s =====
```
```

### Related Documentation
```markdown
## Related Documentation

- **[Deployment Guide](../deployment/CLOUD_RUN_DEPLOYMENT.md)** - Deploy to Cloud Run
- **[Troubleshooting](../troubleshooting/)** - Common issues
- **[API Reference](../api/)** - API documentation
```

## Don't

- ❌ Don't use absolute file paths
- ❌ Don't forget code block language tags
- ❌ Don't write walls of text (use sections, lists, tables)
- ❌ Don't skip examples
- ❌ Don't forget to update indexes
- ❌ Don't use "click here" for links
- ❌ Don't overuse emojis
- ❌ Don't forget to test commands before documenting
- ❌ Don't leave broken links
- ❌ Don't document implementation details that change often
