# Examples

This directory contains example scripts and their generated outputs to demonstrate the tr-ai-cing package.

## Running Examples

### Basic Example
```bash
python basic_example.py
```

This demonstrates:
- Starting and ending traces
- Simple LLM call logging
- Nested spans for complex workflows
- Using the convenience function `trace_llm_call`

### Error Handling Example
```bash
python error_handling_example.py
```

This demonstrates:
- Automatic error capture in traces
- How errors are displayed in the visualization
- Retry patterns

### LangGraph Example
```bash
python langgraph_example.py
```

This demonstrates:
- Tracing LangGraph workflows with multiple nodes
- Capturing agent state transitions
- Tracking routing decisions in conditional edges
- Visualizing the complete graph execution flow
- Hierarchical span relationships in agent workflows

## Generated Files

After running the examples, you'll see:
- `*.jsonl` - Structured log files in JSON Lines format
- `*.html` - Interactive HTML visualizations

Open the HTML files in your browser to explore the interactive trace visualizations!

## Note

The example output files (`.jsonl` and `.html`) are included in the repository to show what the package generates. When you run the examples yourself, these files will be regenerated with new trace IDs and timestamps.
