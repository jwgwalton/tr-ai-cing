"""
Basic example of using tr-ai-cing to trace LLM calls.
"""

from tracing import Tracer, trace_llm_call, Visualizer


def simulate_llm_call(prompt: str, model: str = "gpt-4") -> str:
    """Simulate an LLM call (replace with actual LLM API call)."""
    return f"Response to: {prompt}"


def main():
    # Create a tracer
    tracer = Tracer(log_file="examples/example_trace.jsonl")
    
    # Start a trace
    trace_id = tracer.start_trace()
    print(f"Started trace: {trace_id}")
    
    # Example 1: Simple LLM call
    with tracer.span("summarize_text", metadata={"user": "alice"}):
        prompt = "Summarize the following text: ..."
        response = simulate_llm_call(prompt)
        tracer.log_llm_call(
            name="text_summarization",
            input_data=prompt,
            output_data=response,
            model="gpt-4",
            provider="openai"
        )
    
    # Example 2: Nested LLM calls (parent-child relationship)
    with tracer.span("complex_workflow", span_type="workflow"):
        # First step: extract entities
        with tracer.span("extract_entities"):
            prompt1 = "Extract entities from: John works at OpenAI"
            response1 = simulate_llm_call(prompt1)
            tracer.log_llm_call(
                name="entity_extraction",
                input_data=prompt1,
                output_data=response1,
                model="gpt-3.5-turbo",
                provider="openai"
            )
        
        # Second step: classify sentiment
        with tracer.span("classify_sentiment"):
            prompt2 = "Classify sentiment: I love this product!"
            response2 = simulate_llm_call(prompt2)
            tracer.log_llm_call(
                name="sentiment_analysis",
                input_data=prompt2,
                output_data=response2,
                model="gpt-3.5-turbo",
                provider="openai"
            )
    
    # Example 3: Using the convenience function
    trace_llm_call(
        name="translation",
        input_data="Translate to French: Hello, world!",
        output_data="Bonjour, monde!",
        model="gpt-4",
        provider="openai",
        metadata={"source_lang": "en", "target_lang": "fr"},
        tracer=tracer
    )
    
    # End the trace
    tracer.end_trace()
    print("Trace completed!")
    
    # Generate visualization
    print("\nGenerating visualization...")
    visualizer = Visualizer(log_file="examples/example_trace.jsonl")
    output_file = visualizer.generate_html("examples/trace_visualization.html")
    print(f"Visualization saved to: {output_file}")
    print("Open the HTML file in your browser to view the trace!")


if __name__ == "__main__":
    main()
