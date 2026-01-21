"""
Architecture Option 2: Context Variable Pattern

This pattern uses Python's contextvars module to store the tracer in a context
variable that is automatically propagated through function calls and async tasks.

PROS:
- Thread-safe and async-safe
- No need to pass tracer as parameter
- Perfect for multi-tenant applications (each request has its own trace)
- Works seamlessly with async/await
- Easy to test (context is isolated per execution)
- Supports concurrent requests without interference

CONS:
- Requires Python 3.7+
- Slightly more complex setup than global singleton
- Developers need to understand context variables

WHEN TO USE:
- Web applications with concurrent requests (FastAPI, Flask, etc.)
- Multi-tenant applications
- Async applications
- Production environments with high concurrency
- When you need request-level isolation
"""

from contextvars import ContextVar
from typing import Optional
from tracing import Tracer


# Create a context variable to hold the current tracer
_current_tracer: ContextVar[Optional[Tracer]] = ContextVar('current_tracer', default=None)


def get_current_tracer() -> Tracer:
    """
    Get the tracer for the current context.
    
    If no tracer has been set for the current context, this will create
    a default tracer with default parameters (log_file="trace.jsonl").
    
    Returns:
        Tracer: The tracer instance for the current context
    """
    tracer = _current_tracer.get()
    if tracer is None:
        # Fallback: create a default tracer
        # Note: This will write to 'trace.jsonl' in the current directory
        tracer = Tracer()
        _current_tracer.set(tracer)
    return tracer


def set_current_tracer(tracer: Tracer) -> None:
    """Set the tracer for the current context."""
    _current_tracer.set(tracer)


def simulate_llm_call(prompt: str, model: str = "gpt-4") -> str:
    """Simulate an LLM call."""
    return f"Response to: {prompt}"


# Module 1: Text processing functions
def extract_entities(text: str) -> dict:
    """Extract entities from text using LLM."""
    # Get tracer from context - automatically isolated per request
    tracer = get_current_tracer()
    
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
    # Get tracer from context
    tracer = get_current_tracer()
    
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


# Module 2: Business logic
def process_user_message(message: str) -> dict:
    """Process a user message through multiple LLM steps."""
    tracer = get_current_tracer()
    
    with tracer.span("process_user_message", span_type="workflow"):
        # Call functions - they automatically get the same tracer from context
        entities = extract_entities(message)
        sentiment = classify_sentiment(message)
        
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


# Module 3: Request handlers (simulating web app behavior)
def handle_request(request_id: str, message: str, log_file: str) -> dict:
    """
    Handle a single request with its own isolated tracer.
    
    In a real web application, this would be called by your framework's
    middleware or request handler (e.g., FastAPI dependency, Flask before_request).
    """
    # Create a new tracer for this request/context
    tracer = Tracer(log_file=log_file)
    
    # Set it in the context variable
    set_current_tracer(tracer)
    
    # Start trace with request ID
    tracer.start_trace(trace_id=request_id)
    
    try:
        # Process the request - all nested calls will use this tracer
        result = process_user_message(message)
        
        # End trace
        tracer.end_trace()
        
        return {
            "status": "success",
            "request_id": request_id,
            "result": result
        }
    except Exception as e:
        tracer.end_trace()
        return {
            "status": "error",
            "request_id": request_id,
            "error": str(e)
        }


# Simulating concurrent requests
import threading
import time


def simulate_concurrent_request(request_id: str, message: str, delay: float):
    """
    Simulate a concurrent request with some processing delay.
    
    Note: In a real web application, the 'examples/' directory would typically
    be replaced with a configurable log directory from application settings.
    """
    # Each thread has its own context, so tracers won't interfere
    import os
    time.sleep(delay)
    
    # Use absolute path relative to current working directory
    log_dir = os.path.join(os.getcwd(), "examples")
    os.makedirs(log_dir, exist_ok=True)
    
    result = handle_request(
        request_id=request_id,
        message=message,
        log_file=os.path.join(log_dir, f"option2_request_{request_id}.jsonl")
    )
    print(f"✓ Request {request_id} completed: {result['status']}")



def main():
    """
    Main application demonstrating concurrent request handling.
    
    This simulates a web application handling multiple concurrent requests,
    each with its own isolated tracer.
    """
    print("Simulating concurrent requests with isolated tracers...\n")
    
    # Simulate 3 concurrent requests
    requests = [
        ("req-001", "I love this product! John works at OpenAI.", 0.1),
        ("req-002", "This is terrible and disappointing.", 0.05),
        ("req-003", "The weather is nice today in San Francisco.", 0.15),
    ]
    
    threads = []
    for request_id, message, delay in requests:
        thread = threading.Thread(
            target=simulate_concurrent_request,
            args=(request_id, message, delay)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all requests to complete
    for thread in threads:
        thread.join()
    
    print("\n✓ All concurrent requests completed successfully!")
    print("\nEach request has its own trace file:")
    print("  - examples/option2_request_req-001.jsonl")
    print("  - examples/option2_request_req-002.jsonl")
    print("  - examples/option2_request_req-003.jsonl")
    print("\nThis demonstrates how context variables provide isolation")
    print("between concurrent requests, preventing trace mixing.")
    
    # Generate visualization for one of the traces
    from tracing import Visualizer
    visualizer = Visualizer(log_file="examples/option2_request_req-001.jsonl")
    output_file = visualizer.generate_html("examples/option2_visualization.html")
    print(f"\nVisualization saved to: {output_file}")


if __name__ == "__main__":
    main()
