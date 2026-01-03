# Datadog LLM Observability Guides

This directory contains comprehensive guides for implementing and using Datadog LLM Observability (LLMObs) in your AI applications.

## 📚 Available Guides

### Core Concepts

1. **[Tracing LLM Applications](./sources/00_TRACING_LLM_APPLICATIONS.md)**
   - Introduction to LLM Observability
   - Why trace LLM applications
   - Key concepts and terminology
   - Getting started with LLMObs

2. **[Instrumenting Spans](./sources/01_INSTRUMENTING_SPANS.md)**
   - Different span types (LLM, Workflow, Agent, Tool, Task, Embedding, Retrieval)
   - Span annotation methods
   - Using decorators vs manual annotation
   - Best practices for span instrumentation

3. **[Visualizing Traces and Spans](./sources/02_VISUALIZING_TRACES_AND_SPANS.md)**
   - How to view traces in Datadog
   - Understanding the trace waterfall
   - Analyzing span performance
   - Using filters and search

4. **[Evaluation Metric Types](./03_EVALUATION_METRIC_TYPES.md)** ⭐ NEW
   - Understanding `score` vs `categorical` metric types
   - Common evaluation labels (accuracy, toxicity, relevance, etc.)
   - Choosing the right metric type for your use case
   - Implementation examples and best practices
   - Visualization and monitoring strategies

### Advanced Topics

5. **[Additional Topics](./sources/99_ADDITIONAL_TOPICS.md)**
   - Advanced configuration
   - Custom integrations
   - Performance optimization
   - Troubleshooting

## 🎯 Quick Start

### For Backend Developers

Start with these guides in order:
1. Read [Tracing LLM Applications](./sources/00_TRACING_LLM_APPLICATIONS.md) for overview
2. Follow [Instrumenting Spans](./sources/01_INSTRUMENTING_SPANS.md) to add tracing
3. Learn [Evaluation Metric Types](./03_EVALUATION_METRIC_TYPES.md) to add quality metrics
4. Check [Visualizing Traces](./sources/02_VISUALIZING_TRACES_AND_SPANS.md) to analyze your data

### For ML Engineers

Focus on evaluation and quality metrics:
1. [Evaluation Metric Types](./03_EVALUATION_METRIC_TYPES.md) - Choose score vs categorical
2. [Instrumenting Spans](./sources/01_INSTRUMENTING_SPANS.md) - Add evaluation annotations
3. [Visualizing Traces](./sources/02_VISUALIZING_TRACES_AND_SPANS.md) - Monitor model performance

### For Data Scientists

Understand how to track experiments:
1. [Evaluation Metric Types](./03_EVALUATION_METRIC_TYPES.md) - Define quality metrics
2. [Additional Topics](./sources/99_ADDITIONAL_TOPICS.md) - Prompt versioning and A/B testing

## 🔗 Related Documentation

### Implementation Examples

- **[Vote Extraction LLMObs Implementation](../../docs/features/VOTE_EXTRACTION_LLMOBS_SPANS.md)**
  - Real-world production example
  - Complete span architecture
  - Annotation patterns and code snippets

- **[User Feedback Integration Plan](../../docs/features/USER_FEEDBACK_LLMOBS_PLAN.md)**
  - How to collect user feedback
  - Submitting feedback as evaluations
  - Frontend and backend integration

### Datadog Official Documentation

- [LLM Observability Overview](https://docs.datadoghq.com/llm_observability/)
- [Python SDK Documentation](https://docs.datadoghq.com/llm_observability/setup/sdk/python/)
- [Submit Custom Evaluations](https://docs.datadoghq.com/llm_observability/evaluations/submit_evaluations/)
- [LLM Observability Terms](https://docs.datadoghq.com/llm_observability/terms/)

## 📊 Images and Diagrams

All guide images are stored in `sources/images/`:
- Span type visualizations
- Trace waterfall examples
- Prompt version tracking screenshots
- And more...

## 🤝 Contributing

When adding new guides:

1. Place source guides in `sources/` directory
2. Use descriptive filenames with number prefixes (e.g., `04_NEW_TOPIC.md`)
3. Update this README.md with a link and description
4. Include practical code examples
5. Add related documentation links

## 📝 Guide Standards

All guides should include:

- **Clear objectives**: What will the reader learn?
- **Code examples**: Real, working code snippets
- **Best practices**: Do's and don'ts
- **Visual aids**: Diagrams, screenshots, tables
- **Related links**: Cross-references to other docs

---

**Last Updated**: January 2026  
**Maintained By**: GenAI App Team

