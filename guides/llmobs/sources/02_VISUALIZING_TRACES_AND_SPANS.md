# Visualizing Traces and Spans

After you’ve instrumented your LLM application with the appropriate span kinds and annotations, you can use the powerful visualization tools in Datadog to help you understand and troubleshoot your application’s behavior.

In the details of each trace, you can see the order and duration of operations as a list of spans and also as a flame graph.

---

## Span List View

The span list shows operations in the order of execution. This view is especially useful when you want to:

- Scan the sequence of operations  
- Inspect input and output data for specific spans  
- View span annotations and metadata  
- Track data transformations through a pipeline  

*Trace details for an e-commerce customer support chatbot interaction visualized as a list of spans.*

In this view, each span kind is visually labeled with its type (workflow, task, retrieval, etc.). Different colors and icons for each type make it easy to see what kind of operation occurred at each step.

---

## Flame Graph View

The flame graph displays color-coded spans as horizontal bars, with longer operations appearing as wider bars. The hierarchical layout shows parent-child relationships among spans. This visualization is helpful for these common analysis tasks:

- Understand the execution flow of a request  
- Spot parallel operations that run simultaneously  
- Compare relative time spent on operations  
- Visualize nested call relationships and dependencies  

*Trace details for an e-commerce customer support chatbot interaction visualized as a flame graph.*

The flame graph makes it immediately apparent which operations are taking the most time and how they relate to each other in the execution hierarchy.

---

## Working with Span Details

When you click on any span in either view, you can see data related to that span, including:

- **Span metadata**: Service name, operation name, duration, and status  
- **Input/Output data**: The actual data processed by that operation  
- **Custom annotations**: Any metadata, metrics, or tags you added  
- **Error details**: Stack traces and error messages if the operation failed  
- **Span kind label**: Color-coded indicator of the operation type (agent, workflow, task, etc.)  

These span details provide context to debug issues, optimize performance, and understand your LLM application’s behavior.

---

## Put It into Practice in Datadog

In the following lab, you’ll build a RAG workflow for a simple chatbot app. As you build, you’ll instrument the application for LLM Observability, so you can monitor its evolving behavior and performance through the trace data sent to Datadog.
