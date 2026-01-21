# Assessment of Tracer Usage Across Examples

This document analyzes how the Tracer is currently used in the existing examples and compares it to the three architectural options provided.

## Current Examples Analysis

### 1. basic_example.py
**Current Approach:**
```python
tracer = Tracer(log_file="examples/example_trace.jsonl")
# Tracer is used directly within the main function
# No function parameters - everything in main()
```

**Issue:** All logic is in the `main()` function. No separation of concerns.

**Better Approach:** Use Option 1 (Global Singleton) or Option 3 (Dependency Injection)

---

### 2. error_handling_example.py
**Current Approach:**
```python
tracer = Tracer(log_file="examples/error_trace.jsonl")
# Similar to basic_example - all in main()
```

**Issue:** Same as basic_example - no separation of concerns.

**Better Approach:** Use Option 1 (Global Singleton) or Option 3 (Dependency Injection)

---

### 3. langgraph_example.py
**Current Approach:**
```python
def analyze_input(state: AgentState, tracer: Tracer) -> AgentState:
    # tracer is passed as a parameter

def search_node(state: AgentState, tracer: Tracer) -> AgentState:
    # tracer is passed as a parameter

def run_langgraph_workflow(user_input: str, tracer: Tracer):
    # tracer is passed as a parameter
    state = analyze_input(state, tracer)
    state = search_node(state, tracer)
```

**Issue:** ❌ **This is the problem we're solving!** The tracer is passed around to every function.

**Better Approach:** 
- For production web apps: Use **Option 2 (Context Variable)**
- For testability: Use **Option 3 (Dependency Injection)**
- For simplicity: Use **Option 1 (Global Singleton)**

---

## Comparison: Old vs New Approaches

### Existing Langgraph Example (Current)

```python
# ❌ Tracer passed everywhere
def analyze_input(state: AgentState, tracer: Tracer) -> AgentState:
    with tracer.span("analyze_input"):
        tracer.log_llm_call(...)
    return state

def run_workflow(user_input: str, tracer: Tracer):
    state = analyze_input(state, tracer)  # Must pass tracer
```

**Problems:**
- Must pass tracer to every function
- Function signatures become cluttered
- Hard to refactor and maintain
- Doesn't scale well

---

### NEW: Option 1 - Global Singleton

```python
# ✅ No tracer parameter needed
from tracing import get_default_tracer

def analyze_input(state: AgentState) -> AgentState:
    tracer = get_default_tracer()  # Get global instance
    with tracer.span("analyze_input"):
        tracer.log_llm_call(...)
    return state

def run_workflow(user_input: str):
    state = analyze_input(state)  # No tracer parameter!
```

**Benefits:**
- Clean function signatures
- No parameter passing
- Easy to implement

**Trade-offs:**
- Global state (testing harder)
- Not ideal for concurrent requests

---

### NEW: Option 2 - Context Variable (RECOMMENDED for Web Apps)

```python
# ✅ Context-aware, thread-safe
from contextvars import ContextVar

_current_tracer = ContextVar('tracer', default=None)

def get_current_tracer():
    return _current_tracer.get()

def set_current_tracer(tracer):
    _current_tracer.set(tracer)

# In your request handler
def handle_request(request_id: str, data: str):
    tracer = Tracer(log_file=f"trace_{request_id}.jsonl")
    set_current_tracer(tracer)  # Set for this context
    return run_workflow(data)

def analyze_input(state: AgentState) -> AgentState:
    tracer = get_current_tracer()  # Automatically gets the right one
    with tracer.span("analyze_input"):
        tracer.log_llm_call(...)
    return state

def run_workflow(user_input: str):
    state = analyze_input(state)  # No tracer parameter!
```

**Benefits:**
- Thread-safe and async-safe
- Perfect for web applications
- Each request has isolated trace
- No parameter passing

**Trade-offs:**
- Requires Python 3.7+
- Need to understand context variables

---

### NEW: Option 3 - Dependency Injection

```python
# ✅ Explicit, testable, scalable
class AgentNode:
    def __init__(self, tracer: Tracer):
        self.tracer = tracer
    
    def analyze_input(self, state: AgentState) -> AgentState:
        with self.tracer.span("analyze_input"):
            self.tracer.log_llm_call(...)
        return state

class Workflow:
    def __init__(self, tracer: Tracer, agent_node: AgentNode):
        self.tracer = tracer
        self.agent_node = agent_node
    
    def run(self, user_input: str):
        state = self.agent_node.analyze_input(state)  # No tracer parameter!

# Wire up once
tracer = Tracer()
agent = AgentNode(tracer)
workflow = Workflow(tracer, agent)

# Use
workflow.run("Hello")
```

**Benefits:**
- Extremely testable (easy to mock)
- Explicit dependencies
- Scales well for large apps
- Type-safe

**Trade-offs:**
- More boilerplate
- Need to wire up dependencies

---

## Recommendation by Use Case

| Use Case | Current Example | Recommended Option | Why |
|----------|----------------|-------------------|-----|
| **Simple Scripts** | basic_example.py | Option 1: Global Singleton | Simplest, least code |
| **Error Handling** | error_handling_example.py | Option 1: Global Singleton | Simple use case |
| **LangGraph/Workflows** | langgraph_example.py | **Option 2: Context Variable** | Best for request isolation |
| **Web Applications** | N/A | **Option 2: Context Variable** | Thread-safe, request isolation |
| **Large Enterprise** | N/A | **Option 3: Dependency Injection** | Testable, scalable |
| **Multi-tenant SaaS** | N/A | **Option 2: Context Variable** | Each tenant isolated |

---

## Migration Guide

### From langgraph_example.py to Context Variable Pattern

**Before:**
```python
def analyze_input(state: AgentState, tracer: Tracer) -> AgentState:
    with tracer.span("analyze_input", span_type="agent_node"):
        # ...
    return state

def run_langgraph_workflow(user_input: str, tracer: Tracer):
    state = analyze_input(state, tracer)  # Pass tracer
```

**After:**
```python
# At the top of your module
from contextvars import ContextVar
from typing import Optional

_current_tracer: ContextVar[Optional[Tracer]] = ContextVar('current_tracer', default=None)

def get_current_tracer() -> Tracer:
    return _current_tracer.get()

def set_current_tracer(tracer: Tracer) -> None:
    _current_tracer.set(tracer)

# Updated functions - no tracer parameter!
def analyze_input(state: AgentState) -> AgentState:
    tracer = get_current_tracer()  # Get from context
    with tracer.span("analyze_input", span_type="agent_node"):
        # ...
    return state

def run_langgraph_workflow(user_input: str):
    state = analyze_input(state)  # No tracer parameter!

# In your main or request handler
def main():
    tracer = Tracer(log_file="trace.jsonl")
    set_current_tracer(tracer)  # Set for this context
    tracer.start_trace()
    
    run_langgraph_workflow("Hello")
    
    tracer.end_trace()
```

**Changes Required:**
1. Add context variable setup (3 lines)
2. Remove `tracer` parameter from all functions
3. Add `tracer = get_current_tracer()` at the start of functions that need it
4. Call `set_current_tracer(tracer)` at the entry point

**Benefits:**
- ✅ Functions have cleaner signatures
- ✅ Thread-safe for concurrent requests
- ✅ Easy to test with different tracers per test
- ✅ Scales to production web applications

---

## Summary

The existing examples demonstrate the problem: **passing the tracer around as a parameter is cumbersome and doesn't scale**.

The three new architectural options solve this problem in different ways:

1. **Global Singleton** - Best for simple scripts and prototypes
2. **Context Variable** - Best for production web apps and concurrent systems ⭐ **RECOMMENDED**
3. **Dependency Injection** - Best for large, complex, testable applications

For most production use cases, **Option 2 (Context Variable)** provides the best balance of:
- Ease of use (no parameter passing)
- Safety (thread-safe, async-safe)
- Flexibility (request-level isolation)
- Scalability (works in production)
