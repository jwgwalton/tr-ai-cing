"""
Example showing error handling and tracing of failed LLM calls.
"""

from tracing import Tracer, Visualizer


def simulate_llm_call_with_error(prompt: str, should_fail: bool = False) -> str:
    """Simulate an LLM call that might fail."""
    if should_fail:
        raise ValueError("Simulated API error: Rate limit exceeded")
    return f"Response to: {prompt}"


def main():
    tracer = Tracer(log_file="examples/error_trace.jsonl")
    tracer.start_trace()
    
    print("Tracing LLM calls with errors...")
    
    # Successful call
    with tracer.span("successful_call", metadata={"attempt": 1}):
        try:
            prompt = "What is the capital of France?"
            response = simulate_llm_call_with_error(prompt, should_fail=False)
            tracer.log_llm_call(
                name="geography_question",
                input_data=prompt,
                output_data=response,
                model="gpt-4",
                provider="openai"
            )
            print("✓ Successful call traced")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Failed call
    with tracer.span("failed_call", metadata={"attempt": 1}):
        try:
            prompt = "What is quantum mechanics?"
            response = simulate_llm_call_with_error(prompt, should_fail=True)
            tracer.log_llm_call(
                name="physics_question",
                input_data=prompt,
                output_data=response,
                model="gpt-4",
                provider="openai"
            )
            print("✓ Successful call traced")
        except Exception as e:
            print(f"✗ Error traced: {e}")
            # Error is automatically logged by the span context manager
    
    # Retry after error
    with tracer.span("retry_call", metadata={"attempt": 2}):
        try:
            prompt = "What is quantum mechanics?"
            response = simulate_llm_call_with_error(prompt, should_fail=False)
            tracer.log_llm_call(
                name="physics_question_retry",
                input_data=prompt,
                output_data=response,
                model="gpt-4",
                provider="openai"
            )
            print("✓ Retry successful and traced")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    tracer.end_trace()
    print("\nTrace completed!")
    
    # Generate visualization
    print("\nGenerating visualization...")
    visualizer = Visualizer(log_file="examples/error_trace.jsonl")
    output_file = visualizer.generate_html("examples/error_visualization.html")
    print(f"Visualization saved to: {output_file}")
    print("Open the HTML file to see how errors are displayed!")


if __name__ == "__main__":
    main()
