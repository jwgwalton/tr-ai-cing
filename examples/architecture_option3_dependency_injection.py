"""
Architecture Option 3: Dependency Injection Pattern

This pattern uses dependency injection to provide the tracer where needed,
either through class constructors or function decorators.

PROS:
- Explicit dependencies make code easier to understand and test
- Full control over tracer lifecycle
- Easy to mock in tests
- Works well with dependency injection frameworks (FastAPI, etc.)
- Type hints make it clear what each function needs
- Good for large, well-structured applications

CONS:
- Requires more boilerplate code
- Need to wire up dependencies explicitly
- Can be verbose for deeply nested calls

WHEN TO USE:
- Large, well-structured applications
- When using DI frameworks (FastAPI, Django, etc.)
- When testability is a high priority
- When you want explicit, clear dependencies
- Teams that prefer explicit over implicit
"""

from typing import Protocol, Any, Optional
from dataclasses import dataclass
from tracing import Tracer


def simulate_llm_call(prompt: str, model: str = "gpt-4") -> str:
    """Simulate an LLM call."""
    return f"Response to: {prompt}"


# Define a protocol for anything that can trace (makes testing easier)
class TracerProtocol(Protocol):
    """Protocol for tracer interface."""
    def span(self, name: str, span_type: str = "llm_call", metadata: Optional[dict] = None):
        ...
    
    def log_llm_call(self, name: str, input_data: Any, output_data: Any,
                     model: Optional[str] = None, provider: Optional[str] = None, 
                     metadata: Optional[dict] = None):
        ...


# Option 3A: Class-based Dependency Injection
class EntityExtractor:
    """Service for extracting entities from text."""
    
    def __init__(self, tracer: Tracer):
        """Initialize with a tracer dependency."""
        self.tracer = tracer
    
    def extract(self, text: str) -> dict:
        """Extract entities from text."""
        with self.tracer.span("extract_entities"):
            prompt = f"Extract entities from: {text}"
            response = simulate_llm_call(prompt)
            self.tracer.log_llm_call(
                name="entity_extraction",
                input_data=prompt,
                output_data=response,
                model="gpt-4",
                provider="openai"
            )
        
        return {"entities": response}


class SentimentClassifier:
    """Service for classifying sentiment."""
    
    def __init__(self, tracer: Tracer):
        """Initialize with a tracer dependency."""
        self.tracer = tracer
    
    def classify(self, text: str) -> str:
        """Classify sentiment of text."""
        with self.tracer.span("classify_sentiment"):
            prompt = f"Classify sentiment: {text}"
            response = simulate_llm_call(prompt)
            self.tracer.log_llm_call(
                name="sentiment_analysis",
                input_data=prompt,
                output_data=response,
                model="gpt-3.5-turbo",
                provider="openai"
            )
        
        return response


class MessageProcessor:
    """Service for processing messages."""
    
    def __init__(
        self,
        tracer: Tracer,
        entity_extractor: EntityExtractor,
        sentiment_classifier: SentimentClassifier
    ):
        """Initialize with all dependencies."""
        self.tracer = tracer
        self.entity_extractor = entity_extractor
        self.sentiment_classifier = sentiment_classifier
    
    def process(self, message: str) -> dict:
        """Process a user message through multiple steps."""
        with self.tracer.span("process_user_message", span_type="workflow"):
            # Use injected dependencies
            entities = self.entity_extractor.extract(message)
            sentiment = self.sentiment_classifier.classify(message)
            
            # Final processing
            with self.tracer.span("generate_summary"):
                prompt = f"Summarize analysis for: {message}"
                summary = simulate_llm_call(prompt)
                self.tracer.log_llm_call(
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


# Option 3B: Factory Pattern for Dependency Injection
@dataclass
class ServiceContainer:
    """Container that holds all application services."""
    tracer: Tracer
    entity_extractor: EntityExtractor
    sentiment_classifier: SentimentClassifier
    message_processor: MessageProcessor
    
    @classmethod
    def create(cls, tracer: Tracer) -> 'ServiceContainer':
        """
        Factory method to create a fully-wired service container.
        
        This method constructs all services with their dependencies,
        ensuring everything is properly wired up.
        """
        entity_extractor = EntityExtractor(tracer)
        sentiment_classifier = SentimentClassifier(tracer)
        message_processor = MessageProcessor(
            tracer,
            entity_extractor,
            sentiment_classifier
        )
        
        return cls(
            tracer=tracer,
            entity_extractor=entity_extractor,
            sentiment_classifier=sentiment_classifier,
            message_processor=message_processor
        )


# Application using dependency injection
def main():
    """Main application demonstrating dependency injection pattern."""
    print("Dependency Injection Pattern Demo\n")
    
    # Create tracer
    tracer = Tracer(log_file="examples/option3_trace.jsonl")
    
    # Create service container with all dependencies wired up
    services = ServiceContainer.create(tracer)
    
    # Start trace
    trace_id = tracer.start_trace()
    print(f"Started trace: {trace_id}")
    
    # Process messages using the injected services
    messages = [
        "I love this product! John works at OpenAI.",
        "This is terrible and disappointing.",
        "The weather is nice today in San Francisco."
    ]
    
    results = []
    for message in messages:
        # Use the message processor with all its dependencies
        result = services.message_processor.process(message)
        results.append(result)
        print(f"✓ Processed: {message[:30]}...")
    
    # End trace
    tracer.end_trace()
    print("\nTrace completed!")
    
    # Generate visualization
    from tracing import Visualizer
    visualizer = Visualizer(log_file="examples/option3_trace.jsonl")
    output_file = visualizer.generate_html("examples/option3_visualization.html")
    print(f"Visualization saved to: {output_file}")
    
    print("\n" + "="*60)
    print("Benefits of this approach:")
    print("="*60)
    print("✓ Explicit dependencies - easy to understand what each class needs")
    print("✓ Easy to test - just inject mock tracers")
    print("✓ Type-safe - IDEs can help with autocomplete and type checking")
    print("✓ Flexible - can swap implementations easily")
    print("✓ Scales well for large applications with many services")


# Example: How to test with dependency injection
def example_test_with_mocking():
    """
    Example showing how dependency injection makes testing easier.
    
    This demonstrates creating a mock tracer for testing purposes.
    With DI, you can easily inject mock tracers for testing without
    modifying global state or using context variables.
    
    In real tests, you would use unittest.mock.Mock or pytest fixtures
    instead of this hand-rolled mock implementation.
    """
    # Create a mock tracer (in real tests, use unittest.mock or pytest fixtures)
    class MockTracer:
        """
        Simple mock tracer for testing.
        
        This captures spans and LLM calls for verification in tests.
        In production tests, use unittest.mock.Mock or pytest fixtures.
        """
        def __init__(self):
            self.spans = []
            self.calls = []
        
        def span(self, name: str, span_type: str = "llm_call", metadata: dict = None):
            from contextlib import contextmanager
            
            @contextmanager
            def mock_span():
                self.spans.append(name)
                yield {}
            
            return mock_span()
        
        def log_llm_call(self, **kwargs):
            self.calls.append(kwargs)
    
    # Inject mock tracer into service
    mock_tracer = MockTracer()
    extractor = EntityExtractor(mock_tracer)
    
    # Test the service
    result = extractor.extract("Test text")
    
    # Verify behavior
    assert len(mock_tracer.spans) == 1
    assert mock_tracer.spans[0] == "extract_entities"
    assert len(mock_tracer.calls) == 1
    
    print("\n" + "="*60)
    print("Test Example:")
    print("="*60)
    print("✓ Mock tracer injected successfully")
    print(f"✓ Captured {len(mock_tracer.spans)} spans")
    print(f"✓ Captured {len(mock_tracer.calls)} LLM calls")
    print("✓ Easy to verify behavior without affecting global state")


if __name__ == "__main__":
    main()
    print()
    example_test_with_mocking()
