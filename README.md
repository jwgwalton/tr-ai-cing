# tr-ai-cing 🔍

A monitoring and observability platform for LLM applications. Track, trace, and visualize your LLM calls with ease!

## Overview

This project consists of two main components:

1. **Logging Tool**: Structured logging of LLM calls to JSON Lines files, capturing inputs, outputs, metadata, and execution traces
2. **Visualization Component**: Interactive HTML visualizations showing the DAG (Directed Acyclic Graph) of LLM calls with detailed insights

## Features

- ✨ **Simple API**: Easy-to-use context managers and functions for tracing
- 📊 **Structured Logging**: JSON Lines format for easy parsing and analysis
- 🔄 **Trace Hierarchies**: Support for nested spans to represent complex workflows
- 🎨 **Beautiful Visualizations**: Interactive HTML output with expandable trace details
- ⚡ **Performance Tracking**: Automatic timing of operations
- 🐛 **Error Tracking**: Automatic capture of errors and exceptions
- 🔗 **DAG Visualization**: See parent-child relationships between LLM calls

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from tracing import Tracer, Visualizer

# Create a tracer
tracer = Tracer(log_file="my_trace.jsonl")

# Start a trace
tracer.start_trace()

# Log an LLM call
with tracer.span("summarize_text"):
    tracer.log_llm_call(
        name="text_summarization",
        input_data="Summarize this text...",
        output_data="Summary: ...",
        model="gpt-4",
        provider="openai"
    )

# End the trace
tracer.end_trace()

# Generate visualization
visualizer = Visualizer(log_file="my_trace.jsonl")
visualizer.generate_html("trace_visualization.html")
```

### Nested Traces

```python
from tracing import Tracer

tracer = Tracer()
tracer.start_trace()

# Create a parent span
with tracer.span("complex_workflow", span_type="workflow"):
    # Child span 1
    with tracer.span("step_1"):
        tracer.log_llm_call(
            name="entity_extraction",
            input_data="Extract entities from: ...",
            output_data="Entities: ...",
            model="gpt-3.5-turbo"
        )
    
    # Child span 2
    with tracer.span("step_2"):
        tracer.log_llm_call(
            name="sentiment_analysis",
            input_data="Analyze sentiment: ...",
            output_data="Sentiment: positive",
            model="gpt-3.5-turbo"
        )

tracer.end_trace()
```

### Error Handling

Errors are automatically captured in the trace:

```python
with tracer.span("risky_operation"):
    try:
        # Your LLM call that might fail
        result = call_llm_api()
    except Exception as e:
        # Error is automatically logged
        raise
```

## API Reference

### Tracer

#### `Tracer(log_file="trace.jsonl", auto_flush=True)`

Create a new tracer instance.

- `log_file`: Path to the log file (default: "trace.jsonl")
- `auto_flush`: Whether to flush after each write (default: True)

#### Methods

- `start_trace(trace_id=None)`: Start a new trace
- `end_trace()`: End the current trace
- `span(name, span_type="llm_call", metadata=None)`: Context manager for tracing a span
- `log_llm_call(name, input_data, output_data, model=None, provider=None, metadata=None)`: Log an LLM call

### Visualizer

#### `Visualizer(log_file)`

Create a visualizer for trace logs.

- `log_file`: Path to the trace log file

#### Methods

- `load_traces()`: Load traces from the log file
- `generate_html(output_file="trace_visualization.html")`: Generate HTML visualization

## Log Format

Traces are logged in JSON Lines format. Each line is a JSON object with the following structure:

```json
{
  "span_id": "unique-span-id",
  "trace_id": "unique-trace-id",
  "parent_span_id": "parent-id-or-null",
  "name": "operation_name",
  "type": "llm_call",
  "start_time": "2024-01-20T12:00:00.000000",
  "end_time": "2024-01-20T12:00:01.500000",
  "duration_ms": 1500.0,
  "status": "success",
  "input": "input data",
  "output": "output data",
  "model": "gpt-4",
  "provider": "openai",
  "metadata": {},
  "error": null
}
```

## Architecture Patterns

For applications with multiple LLM calls across different parts of your codebase, you don't need to pass the tracer around! See our [Architecture Options Guide](docs/ARCHITECTURE_OPTIONS.md) for three different patterns:

1. **Global Singleton Pattern** - Simple, quick to implement
2. **Context Variable Pattern** - Perfect for web apps with concurrent requests
3. **Dependency Injection Pattern** - Best for large, testable applications

Each pattern includes complete examples and guidance on when to use it.

## Examples

Check out the `examples/` directory for more detailed examples:

- `basic_example.py`: Basic usage with simple and nested traces
- `error_handling_example.py`: Error handling and retry patterns
- `langgraph_example.py`: Tracing LangGraph workflows with multiple nodes and routing
- `architecture_option1_global_singleton.py`: Global singleton pattern example
- `architecture_option2_context_variable.py`: Context variable pattern for web apps
- `architecture_option3_dependency_injection.py`: Dependency injection pattern

Run an example:
```bash
python examples/langgraph_example.py
python examples/architecture_option2_context_variable.py
```

## Testing

Run the test suite:

```bash
pytest
```

With coverage:
```bash
pytest --cov=tracing --cov-report=html
```

## Use Cases

- **Debugging**: Trace the flow of data through your LLM application
- **Performance Analysis**: Identify slow operations and bottlenecks
- **Error Tracking**: Quickly identify where and why LLM calls fail
- **Workflow Visualization**: Understand complex multi-step LLM workflows
- **Audit Logging**: Keep records of all LLM interactions

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License
