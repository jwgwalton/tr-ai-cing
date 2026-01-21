"""
Minimal example showing context variable pattern with zero setup.

This demonstrates the absolute simplest way to use context variables
with the tracer - just import and use!
"""

from tracing import Tracer, get_current_tracer, set_current_tracer


def simulate_llm_call(prompt: str) -> str:
    """Simulate an LLM call."""
    return f"Response to: {prompt}"


def analyze_text(text: str) -> dict:
    """
    Analyze text - notice we don't need to pass a tracer parameter!
    The tracer is automatically available from the context.
    """
    tracer = get_current_tracer()
    
    if tracer:  # Only trace if a tracer is set
        with tracer.span("analyze_text"):
            result = simulate_llm_call(f"Analyze: {text}")
            tracer.log_llm_call(
                name="text_analysis",
                input_data=text,
                output_data=result,
                model="gpt-4"
            )
            return {"analysis": result}
    else:
        # No tracer, still works
        result = simulate_llm_call(f"Analyze: {text}")
        return {"analysis": result}


def process_request(request_id: str, data: str):
    """
    Simulate a web request handler.
    Just create a tracer, set it in context, and you're done!
    """
    # Step 1: Create a tracer for this request
    tracer = Tracer(log_file=f"examples/minimal_trace_{request_id}.jsonl")
    
    # Step 2: Set it in the context - that's it!
    set_current_tracer(tracer)
    
    # Step 3: Start the trace
    tracer.start_trace(trace_id=request_id)
    
    try:
        # Now all nested calls can access the tracer automatically
        result = analyze_text(data)
        
        # End trace
        tracer.end_trace()
        
        return result
    finally:
        # Clean up
        set_current_tracer(None)


if __name__ == "__main__":
    print("Minimal Context Variable Example")
    print("=" * 50)
    
    # Simulate multiple requests
    result1 = process_request("req-001", "Hello world")
    print(f"✓ Request 1: {result1}")
    
    result2 = process_request("req-002", "How are you?")
    print(f"✓ Request 2: {result2}")
    
    print("\n" + "=" * 50)
    print("Done! Check the trace files:")
    print("  - examples/minimal_trace_req-001.jsonl")
    print("  - examples/minimal_trace_req-002.jsonl")
    print("\nThat's it! No manual context variable setup required!")
