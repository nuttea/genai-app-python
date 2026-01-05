# LLM Observability Guides

Practical guides for implementing Datadog LLM Observability in our Thai election vote extraction application.

## 📚 Guide Series

### Part 01: Instrumenting Our Vote Extraction Application
**[01_INSTRUMENTING_VOTE_EXTRACTION.md](./01_INSTRUMENTING_VOTE_EXTRACTION.md)**

Learn how we've instrumented our application with Datadog LLMObs:
- ✅ Span kinds (workflow, task, llm, tool, etc.)
- ✅ Decorators vs manual instrumentation
- ✅ Custom APM spans for LLM judge
- ✅ Annotation best practices
- ✅ Real code examples from our codebase

**Key Topics:**
- `@workflow` for vote extraction orchestration
- `@task` for data preparation
- Auto-instrumented LLM calls
- Custom `tracer.trace()` for fine-grained control
- Retry logic and error tracking

---

### Part 02: Visualizing and Monitoring Our Application
**[02_VISUALIZING_AND_MONITORING.md](./02_VISUALIZING_AND_MONITORING.md)**

Master Datadog's visualization and monitoring tools:
- ✅ Span list vs flame graph views
- ✅ Debugging real-world scenarios
- ✅ Custom dashboards and alerts
- ✅ Cost optimization strategies
- ✅ Correlation with APM and RUM

**Key Topics:**
- Debugging slow extractions
- Troubleshooting LLM judge failures
- Tracking token costs
- Setting up monitors
- Advanced trace analysis

---

## 📖 Source Materials

The **[sources/](./sources/)** directory contains educational materials from Datadog's LLM Observability course:

- **[00_TRACING_LLM_APPLICATIONS.md](./sources/00_TRACING_LLM_APPLICATIONS.md)** - Introduction and concepts
- **[01_INSTRUMENTING_SPANS.md](./sources/01_INSTRUMENTING_SPANS.md)** - Span kinds and instrumentation
- **[02_VISUALIZING_TRACES_AND_SPANS.md](./sources/02_VISUALIZING_TRACES_AND_SPANS.md)** - Visualization techniques
- **[99_ADDITIONAL_TOPICS.md](./sources/99_ADDITIONAL_TOPICS.md)** - Advanced topics (prompts, evaluations, agents)

---

## 🎯 Quick Start

### 1. Read the Theory
Start with source materials to understand concepts:
```bash
# Read in order:
guides/llmobs/sources/00_TRACING_LLM_APPLICATIONS.md
guides/llmobs/sources/01_INSTRUMENTING_SPANS.md
guides/llmobs/sources/02_VISUALIZING_TRACES_AND_SPANS.md
```

### 2. See Practical Implementation
Apply concepts to our codebase:
```bash
# Read our implementation guides:
guides/llmobs/01_INSTRUMENTING_VOTE_EXTRACTION.md
guides/llmobs/02_VISUALIZING_AND_MONITORING.md
```

### 3. Explore the Code
Check actual implementations:
```bash
# Vote extraction service (main workflow)
services/fastapi-backend/app/services/vote_extraction_service.py

# LLM judge evaluator (custom spans)
services/fastapi-backend/app/services/experiments_service.py

# Configuration
services/fastapi-backend/app/config.py
```

### 4. View in Datadog
Access your traces and dashboards:
```
https://app.datadoghq.com/llm/
↳ Select service: vote-extractor
↳ Filter environment: prod or dev
```

---

## 📊 What You'll Learn

### Instrumentation (Part 01)
- **Span Kinds**: When to use workflow, task, llm, tool, etc.
- **Decorators**: `@workflow`, `@task`, `@llm`, `@tool`
- **Manual Instrumentation**: `tracer.trace()` for custom spans
- **Annotations**: `LLMObs.annotate()` and `span.set_tag()`
- **Error Tracking**: Capturing and tracing errors

### Monitoring (Part 02)
- **Visualization**: Span lists and flame graphs
- **Debugging**: Real-world troubleshooting scenarios
- **Dashboards**: Custom metrics and KPIs
- **Alerts**: Proactive monitoring
- **Cost Optimization**: Reducing LLM expenses

---

## 🔧 Practical Use Cases

### Debugging Performance Issues
```
Problem: Extraction taking >5 seconds
Solution: Use flame graph to identify bottleneck
Result: Found LLM call using 95% of time, optimized config
```

### Tracking Costs
```
Problem: Monthly LLM costs increasing
Solution: Dashboard showing token usage by model
Result: Identified expensive LLM judge, reduced 71%
```

### Monitoring Quality
```
Problem: LLM judge giving low scores
Solution: Trace showing empty responses and retries
Result: Fixed API timeout and improved prompts
```

---

## 📈 Key Metrics We Track

### Performance
- **P50/P95/P99 Latency**: Response time percentiles
- **Error Rate**: Failed extractions
- **Throughput**: Extractions per minute

### Quality
- **LLM Judge Score**: Average evaluation score
- **Validation Pass Rate**: Schema compliance
- **Empty Response Rate**: LLM API failures

### Cost
- **Token Usage**: Daily/monthly tokens by model
- **Cost per Extraction**: Average cost per request
- **Monthly Budget**: Total LLM costs

---

## 🚀 Advanced Topics

### Experiments & Evaluations
See **[docs/features/LLMOBS_EVALUATIONS.md](../../docs/features/LLMOBS_EVALUATIONS.md)** for:
- Model comparison experiments
- Custom evaluators (exact match, accuracy, etc.)
- LLM-as-judge evaluation
- A/B testing with different models

### Prompt Version Tracking
See **[sources/99_ADDITIONAL_TOPICS.md](./sources/99_ADDITIONAL_TOPICS.md#prompts-version-tracking)** for:
- Tracking prompt changes over time
- Correlating prompt versions with quality
- Rolling back problematic prompts

### Agent Monitoring
See **[sources/99_ADDITIONAL_TOPICS.md](./sources/99_ADDITIONAL_TOPICS.md#preview-agent-monitoring)** for:
- Monitoring AI agent behavior
- Tool usage and selection
- Multi-step reasoning chains

---

## 📖 Related Documentation

### Project Documentation
- **[DOCUMENTATION_MAP.md](../../DOCUMENTATION_MAP.md)** - Master overview
- **[docs/INDEX.md](../../docs/INDEX.md)** - Full documentation index
- **[QUICKSTART.md](../../QUICKSTART.md)** - Getting started

### Feature Documentation
- **[LLMOBS_EVALUATIONS.md](../../docs/features/LLMOBS_EVALUATIONS.md)** - Experiments and evaluations
- **[LLM_CONFIGURATION.md](../../docs/features/LLM_CONFIGURATION.md)** - LLM config options
- **[VOTE_EXTRACTOR.md](../../docs/features/VOTE_EXTRACTOR.md)** - Vote extraction feature

### Monitoring Documentation
- **[DATADOG_LLMOBS.md](../../docs/monitoring/DATADOG_LLMOBS.md)** - LLMObs setup
- **[DATADOG_APM.md](../../docs/monitoring/DATADOG_APM.md)** - APM integration
- **[DATADOG_RUM.md](../../docs/monitoring/DATADOG_RUM.md)** - RUM correlation

---

## 🎓 Learning Path

### Beginner
1. Read source materials (sources/)
2. Understand span kinds and when to use them
3. Review our instrumentation examples
4. Explore traces in Datadog UI

### Intermediate
1. Implement custom spans in your code
2. Add meaningful annotations
3. Create dashboards for your metrics
4. Set up basic alerts

### Advanced
1. Optimize based on trace data
2. Build experiments and evaluations
3. Correlate LLMObs with APM/RUM
4. Implement cost optimization strategies

---

## 🔗 External Resources

### Datadog Documentation
- **[LLM Observability](https://docs.datadoghq.com/llm_observability/)**
- **[APM Tracing](https://docs.datadoghq.com/tracing/)**
- **[Python SDK](https://ddtrace.readthedocs.io/)**

### Datadog Blog Posts
- **[LLM Prompt Tracking](https://www.datadoghq.com/blog/llm-prompt-tracking/)**
- **[OpenAI Agents Monitoring](https://www.datadoghq.com/blog/openai-agents-llm-observability/)**
- **[Monitor AI Agents](https://www.datadoghq.com/blog/monitor-ai-agents/)**
- **[MCP Client Monitoring](https://www.datadoghq.com/blog/mcp-client-monitoring/)**

---

## 🛠️ Tools and Scripts

### Jupyter Notebooks
**[notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb](../../notebooks/datasets/01_prepare_vote_extraction_dataset.ipynb)**
- Experiment with different models
- Run evaluations with LLM judge
- Compare results in Datadog

### Test Scripts
**[scripts/tests/](../../scripts/tests/)**
- Test model API integration
- Validate extraction accuracy
- Debug LLM responses

---

## 💡 Pro Tips

### Instrumentation
- ✅ Use `@workflow` for high-level orchestration
- ✅ Use `@task` for pure data transformations
- ✅ Let auto-instrumentation handle LLM calls
- ✅ Use `tracer.trace()` for fine-grained control
- ✅ Add rich context with annotations

### Monitoring
- ✅ Start with flame graphs to find bottlenecks
- ✅ Use span lists for detailed debugging
- ✅ Set up alerts before problems occur
- ✅ Track costs alongside performance
- ✅ Correlate with APM and RUM

### Optimization
- ✅ Use cheaper models when possible
- ✅ Sample evaluations instead of 100%
- ✅ Cache embeddings and retrievals
- ✅ Reduce prompt sizes
- ✅ Set appropriate token limits

---

## 🤝 Contributing

To add new guides:
1. Follow the existing structure
2. Include real code examples from our codebase
3. Add screenshots or diagrams when helpful
4. Link to related documentation
5. Update this README with new content

---

## 📝 Feedback

Have questions or suggestions? Open an issue or contact the ML team.

---

**Last Updated**: January 5, 2026

**Maintained By**: ML Engineering Team
