# Cursor Project Rules

This directory contains project-specific rules for Cursor AI to follow when working on this codebase.

## Rules Structure

Each rule is in its own folder with a `RULE.md` file:

```
.cursor/rules/
├── backend/       # FastAPI backend development rules
├── frontend/      # Streamlit frontend development rules
├── llm/           # LLM integration patterns and best practices
├── datadog/       # Datadog observability standards
├── documentation/ # Documentation writing guidelines
└── testing/       # Testing standards and patterns
```

## Rule Categories

### 1. Backend (`backend/RULE.md`)
**Scope**: `services/fastapi-backend/**/*.py`

- FastAPI architecture patterns
- Pydantic models and validation
- Async/await patterns
- Error handling
- API endpoint structure
- Configuration management
- Logging standards

### 2. Frontend (`frontend/RULE.md`)
**Scope**: `frontend/streamlit/**/*.py`

- Streamlit component patterns
- Session state management
- Caching strategies
- Error handling and user feedback
- API integration
- Layout best practices
- Loading states

### 3. LLM Integration (`llm/RULE.md`)
**Scope**: `**/services/**/*llm*.py`, `**/services/**/*genai*.py`

- Vertex AI / Gemini configuration
- Model selection guidelines
- Token limits and capacity planning
- Structured output patterns
- Schema definitions
- Error handling
- Retry logic
- LLM Observability integration

### 4. Datadog (`datadog/RULE.md`)
**Scope**: All application code, Dockerfiles, workflows

- Required environment variables
- Structured logging patterns
- APM span tags
- LLM Observability setup
- RUM integration
- Custom metrics
- Environment-specific configuration
- Cost optimization

### 5. Documentation (`documentation/RULE.md`)
**Scope**: `docs/**/*.md`, `*.md`

- Documentation structure
- Writing style guidelines
- Quick start format
- Troubleshooting format
- Code examples
- Formatting standards
- Maintenance practices

### 6. Testing (`testing/RULE.md`)
**Scope**: `**/tests/**/*.py`, `scripts/tests/**/*.py`

- Test structure
- Pytest patterns
- Mocking strategies
- Integration tests
- Coverage requirements

## How to Use

### For AI Assistants

Rules are automatically applied when working on files matching the scope patterns.  
AI assistants should:
1. Read relevant rules based on file paths
2. Follow patterns and standards defined in rules
3. Reference examples in rules
4. Apply best practices consistently

### For Developers

Rules serve as:
- **Style guide** for the project
- **Reference** for common patterns
- **Standards** for code quality
- **Examples** of best practices

To view a rule:
```bash
cat .cursor/rules/backend/RULE.md
cat .cursor/rules/llm/RULE.md
```

## Rule Principles

### 1. Consistency
All rules enforce consistent patterns across the codebase:
- Type hints for all functions
- Pydantic for data validation
- Async/await for I/O operations
- Structured logging with JSON
- Comprehensive error handling

### 2. Observability
Strong emphasis on Datadog integration:
- Full APM tracing
- LLM Observability for all AI operations
- Structured logging
- Custom metrics for business events
- RUM for frontend monitoring

### 3. Production-Ready
Focus on production best practices:
- Error handling and retry logic
- Rate limiting and security
- Performance optimization
- Cost optimization
- Scalability patterns

### 4. Documentation
Everything should be documented:
- Docstrings for public APIs
- Comments for complex logic
- README for each module
- Examples in documentation
- Troubleshooting guides

## Relationship with AGENTS.md

**AGENTS.md** (root) provides:
- High-level project overview
- Quick reference for common tasks
- General guidelines and principles

**.cursor/rules/** provides:
- Detailed, domain-specific rules
- Code patterns and examples
- Scoped to specific file types
- Comprehensive best practices

## Adding New Rules

To add a new rule:

1. Create a new folder:
   ```bash
   mkdir -p .cursor/rules/new-category
   ```

2. Create `RULE.md` with structure:
   ```markdown
   # Rule Category Name
   
   ## Scope
   **Paths**: `pattern/**/*.ext`
   
   ## Standards
   
   ### Pattern Name
   ```✅ Good
   [example]
   ```
   
   ```❌ Bad
   [example]
   ```
   
   ## Don't
   - ❌ Anti-pattern 1
   - ❌ Anti-pattern 2
   ```

3. Update this README
4. Update `.cursor/rules.json` if needed

## Rule Updates

Rules should be updated when:
- ✅ New patterns are established
- ✅ Best practices evolve
- ✅ New tools or frameworks are adopted
- ✅ Common mistakes are identified
- ✅ Standards change

## Examples in Rules

All rules include:
- ✅ **Good examples** - Recommended patterns
- ❌ **Bad examples** - Anti-patterns to avoid
- Code snippets with explanations
- Real-world use cases

## Enforcement

Rules are enforced through:
1. **AI Assistant** - Follows rules automatically
2. **Code Review** - Humans check compliance
3. **Linting** - Automated checks where possible
4. **Documentation** - Visibility and education

---

**Version**: 1.0  
**Last Updated**: December 29, 2024

**For more information**, see:
- [AGENTS.md](../../AGENTS.md) - AI agent instructions
- [DOCUMENTATION_MAP.md](../../DOCUMENTATION_MAP.md) - Master documentation
- [docs/INDEX.md](../../docs/INDEX.md) - Full documentation index

