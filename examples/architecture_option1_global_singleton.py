"""
Architecture Option 1: Global Singleton Pattern

This pattern uses a global singleton tracer that can be accessed from anywhere
in the application without passing it around.

PROS:
- Simple to use - no need to pass tracer around
- Minimal code changes required
- Good for simple applications with single-threaded execution

CONS:
- Global state can make testing harder
- Not ideal for multi-tenant applications (different traces per tenant)
- Potential thread-safety issues with concurrent requests
- Less flexible for advanced use cases

WHEN TO USE:
- Simple applications with single user/tenant
- Prototyping and development
- Applications with simple linear execution flow
"""

from tracing import Tracer, get_default_tracer


def simulate_llm_call(prompt: str, model: str = "gpt-4") -> str:
    """Simulate an LLM call."""
    return f"Response to: {prompt}"


# Module 1: Text processing functions
def extract_entities(text: str) -> dict:
    """Extract entities from text using LLM."""
    # No need to pass tracer - use global singleton
    tracer = get_default_tracer()
    
    with tracer.span("extract_entities"):
        prompt = f"Extract entities from: {text}"
        response = simulate_llm_call(prompt)
        tracer.log_llm_call(
            name="entity_extraction",
            input_data=prompt,
            output_data=response,
            model="gpt-4",
            provider="openai"
        )
    
    return {"entities": response}


def classify_sentiment(text: str) -> str:
    """Classify sentiment of text."""
    # No need to pass tracer - use global singleton
    tracer = get_default_tracer()
    
    with tracer.span("classify_sentiment"):
        prompt = f"Classify sentiment: {text}"
        response = simulate_llm_call(prompt)
        tracer.log_llm_call(
            name="sentiment_analysis",
            input_data=prompt,
            output_data=response,
            model="gpt-3.5-turbo",
            provider="openai"
        )
    
    return response


# Module 2: Business logic that calls multiple LLM functions
def process_user_message(message: str) -> dict:
    """Process a user message through multiple LLM steps."""
    # No tracer parameter needed!
    tracer = get_default_tracer()
    
    with tracer.span("process_user_message", span_type="workflow"):
        # Call functions from different modules - no need to pass tracer
        entities = extract_entities(message)
        sentiment = classify_sentiment(message)
        
        # Final processing
        with tracer.span("generate_summary"):
            prompt = f"Summarize analysis for: {message}"
            summary = simulate_llm_call(prompt)
            tracer.log_llm_call(
                name="summary_generation",
                input_data=prompt,
                output_data=summary,
                model="gpt-4",
                provider="openai"
            )
        
        return {
            "entities": entities,
            "sentiment": sentiment,
            "summary": summary
        }


# Module 3: Application entry point
def main():
    """Main application entry point."""
    # Initialize global tracer once at application startup
    tracer = get_default_tracer()
    
    # Configure the log file if needed (optional)
    # The default tracer uses "trace.jsonl"
    # For custom configuration, you can create a new tracer and use it:
    # custom_tracer = Tracer(log_file="custom_trace.jsonl")
    # custom_tracer.start_trace()
    # Then use custom_tracer instead of the default one
    
    # Start trace
    trace_id = tracer.start_trace()
    print(f"Started trace: {trace_id}")
    
    # Process multiple messages - no need to pass tracer around
    results = []
    messages = [
        "I love this product! John works at OpenAI.",
        "This is terrible and disappointing.",
        "The weather is nice today in San Francisco."
    ]
    
    for message in messages:
        result = process_user_message(message)
        results.append(result)
        print(f"✓ Processed: {message[:30]}...")
    
    # End trace
    tracer.end_trace()
    print("\nTrace completed!")
    print(f"All {len(results)} messages processed successfully")
    
    # Generate visualization
    from tracing import Visualizer
    visualizer = Visualizer(log_file="trace.jsonl")
    output_file = visualizer.generate_html("examples/option1_visualization.html")
    print(f"Visualization saved to: {output_file}")


if __name__ == "__main__":
    main()
