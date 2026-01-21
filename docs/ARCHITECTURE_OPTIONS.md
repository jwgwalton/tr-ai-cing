# Tracer Architecture Options

This document provides three different architectural patterns for using the Tracer in applications with multiple LLM calls across different parts of the codebase, **without needing to pass the tracer around as a parameter**.

## Problem Statement

When building LLM applications with calls scattered across multiple modules and functions, passing a tracer instance as a parameter to every function becomes cumbersome and error-prone. This document presents three architectural options to solve this problem.

## Current Approach (What We Want to Avoid)

```python
# ❌ Current approach - passing tracer everywhere
def function_a(data, tracer):
    with tracer.span("function_a"):
        return function_b(data, tracer)  # Must pass tracer

def function_b(data, tracer):
    with tracer.span("function_b"):
        return function_c(data, tracer)  # Must pass tracer

def function_c(data, tracer):
    with tracer.span("function_c"):
        tracer.log_llm_call(...)
```

## Option 1: Global Singleton Pattern

**File:** `examples/architecture_option1_global_singleton.py`

### Overview
Uses a global singleton tracer instance that can be accessed from anywhere using `get_default_tracer()`.

### Example Usage

```python
from tracing import get_default_tracer

def extract_entities(text: str) -> dict:
    tracer = get_default_tracer()  # Get global instance
    
    with tracer.span("extract_entities"):
        tracer.log_llm_call(...)
    
    return result

def classify_sentiment(text: str) -> str:
    tracer = get_default_tracer()  # Same global instance
    
    with tracer.span("classify_sentiment"):
        tracer.log_llm_call(...)
    
    return result
```

### Pros
- ✅ Simple to use - minimal code changes
- ✅ No need to pass tracer as parameter
- ✅ Good for simple, single-threaded applications
- ✅ Quick to implement and get started

### Cons
- ❌ Global state can complicate testing
- ❌ Not ideal for multi-tenant applications
- ❌ Potential thread-safety issues with concurrent requests
- ❌ Less flexible for advanced use cases

### When to Use
- Simple applications with single user/tenant
- Prototyping and development environments
- Command-line tools and scripts
- Single-threaded batch processing

### When NOT to Use
- Web applications with concurrent requests
- Multi-tenant SaaS applications
- Microservices that need request isolation

---

## Option 2: Context Variable Pattern

**File:** `examples/architecture_option2_context_variable.py`

### Overview
Uses Python's `contextvars` module to store the tracer in a context variable that automatically propagates through function calls and async tasks while maintaining isolation between concurrent executions.

**Now built into the package!** Just import `get_current_tracer()` and `set_current_tracer()` - no manual setup required.

### Example Usage

```python
from tracing import Tracer, get_current_tracer, set_current_tracer

# In your request handler
def handle_request(request_id: str, message: str):
    # Create and set tracer for this request/context
    tracer = Tracer(log_file=f"trace_{request_id}.jsonl")
    set_current_tracer(tracer)  # Built-in function!
    
    tracer.start_trace(trace_id=request_id)
    
    # All nested calls automatically get the same tracer
    result = process_message(message)
    
    tracer.end_trace()
    set_current_tracer(None)  # Clean up
    return result

# In nested functions - no tracer parameter needed!
def process_message(message: str):
    tracer = get_current_tracer()  # Built-in function!
    if tracer:
        with tracer.span("process_message"):
            entities = extract_entities(message)  # No tracer parameter
            sentiment = classify_sentiment(message)  # No tracer parameter
            return {"entities": entities, "sentiment": sentiment}

def extract_entities(text: str):
    tracer = get_current_tracer()  # Gets tracer from context
    if tracer:
        with tracer.span("extract_entities"):
            tracer.log_llm_call(...)
```

### Pros
- ✅ Thread-safe and async-safe
- ✅ Perfect for concurrent request handling
- ✅ Each request has isolated trace
- ✅ No need to pass tracer as parameter
- ✅ Works seamlessly with async/await
- ✅ Easy to test - context is isolated per execution
- ✅ **Built into the package - zero setup required!**

### Cons
- ❌ Requires Python 3.7+

### When to Use
- **Web applications** (FastAPI, Flask, Django)
- **Multi-tenant SaaS** applications
- **Async applications** with async/await
- **Production environments** with high concurrency
- **Microservices** that handle multiple concurrent requests

### When NOT to Use
- Python < 3.7 (contextvars not available)
- Very simple scripts where global singleton is sufficient

---

## Option 3: Dependency Injection Pattern

**File:** `examples/architecture_option3_dependency_injection.py`

### Overview
Uses dependency injection to provide the tracer through class constructors or function parameters, making dependencies explicit and easy to test.

### Example Usage

```python
from tracing import Tracer

# Define services with explicit dependencies
class EntityExtractor:
    def __init__(self, tracer: Tracer):
        self.tracer = tracer
    
    def extract(self, text: str) -> dict:
        with self.tracer.span("extract_entities"):
            self.tracer.log_llm_call(...)
        return result

class MessageProcessor:
    def __init__(
        self,
        tracer: Tracer,
        entity_extractor: EntityExtractor,
        sentiment_classifier: SentimentClassifier
    ):
        self.tracer = tracer
        self.entity_extractor = entity_extractor
        self.sentiment_classifier = sentiment_classifier
    
    def process(self, message: str) -> dict:
        with self.tracer.span("process_message"):
            entities = self.entity_extractor.extract(message)
            sentiment = self.sentiment_classifier.classify(message)
            return {"entities": entities, "sentiment": sentiment}

# Wire up dependencies once
tracer = Tracer(log_file="trace.jsonl")
entity_extractor = EntityExtractor(tracer)
sentiment_classifier = SentimentClassifier(tracer)
message_processor = MessageProcessor(tracer, entity_extractor, sentiment_classifier)

# Use the wired-up services
result = message_processor.process("Hello world")
```

### Pros
- ✅ Explicit dependencies - easy to understand
- ✅ Extremely easy to test with mocks
- ✅ Type hints provide IDE support
- ✅ Works well with DI frameworks (FastAPI, etc.)
- ✅ Scales well for large applications
- ✅ Clear separation of concerns

### Cons
- ❌ More boilerplate code
- ❌ Need to wire up dependencies explicitly
- ❌ Can be verbose for deeply nested calls

### When to Use
- **Large, well-structured applications**
- **When using DI frameworks** (FastAPI dependencies, Django apps)
- **High testability requirements**
- **Teams that prefer explicit over implicit**
- **Enterprise applications** with many services

### When NOT to Use
- Small scripts or prototypes
- When boilerplate is a concern
- Very simple applications

---

## Comparison Table

| Feature | Option 1: Global Singleton | Option 2: Context Variable | Option 3: Dependency Injection |
|---------|---------------------------|---------------------------|-------------------------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Very Easy | ⭐⭐⭐⭐ Easy | ⭐⭐⭐ Moderate |
| **Thread Safety** | ⭐⭐ Poor | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent |
| **Testability** | ⭐⭐ Poor | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Multi-tenant** | ⭐ Not Suitable | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent |
| **Async Support** | ⭐⭐ Poor | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good |
| **Code Clarity** | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Boilerplate** | ⭐⭐⭐⭐⭐ Minimal | ⭐⭐⭐⭐ Low | ⭐⭐⭐ Moderate |

---

## Decision Guide

### Choose **Option 1 (Global Singleton)** if:
- You're building a simple script or CLI tool
- You have a single-threaded application
- You're prototyping and want to get started quickly
- Your application has a single user/tenant

### Choose **Option 2 (Context Variable)** if:
- You're building a web application (FastAPI, Flask, Django)
- You need to handle concurrent requests
- You have a multi-tenant application
- You're using async/await extensively
- You want minimal code changes with good isolation

### Choose **Option 3 (Dependency Injection)** if:
- You're building a large, complex application
- Testability is a top priority
- You're already using a DI framework
- You want explicit, clear dependencies
- Your team prefers explicit over implicit patterns

---

## Hybrid Approaches

You can also combine these patterns:

### Context Variable + Dependency Injection
```python
# Use context variables for request-level isolation
# But inject services that use the context variable internally

class EntityExtractor:
    def extract(self, text: str) -> dict:
        tracer = get_current_tracer()  # From context
        with tracer.span("extract_entities"):
            tracer.log_llm_call(...)
```

This gives you the benefits of both: DI for testability and context variables for request isolation.

---

## Implementation Recommendations

1. **Start Simple**: Begin with Option 1 (Global Singleton) for prototyping
2. **Scale Up**: Move to Option 2 (Context Variable) when deploying to production web apps
3. **Enterprise Scale**: Use Option 3 (Dependency Injection) for large applications

### Migration Path

```
Prototype → Global Singleton (Option 1)
    ↓
Production Web App → Context Variable (Option 2)
    ↓
Large Enterprise App → Dependency Injection (Option 3)
```

---

## Examples

See the following example files for complete, runnable implementations:

- `examples/architecture_option1_global_singleton.py`
- `examples/architecture_option2_context_variable.py`
- `examples/architecture_option3_dependency_injection.py`

Run any example:
```bash
python examples/architecture_option1_global_singleton.py
python examples/architecture_option2_context_variable.py
python examples/architecture_option3_dependency_injection.py
```

---

## Additional Resources

- Python contextvars documentation: https://docs.python.org/3/library/contextvars.html
- Dependency Injection in Python: https://python-dependency-injector.ets-labs.org/
- FastAPI dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
