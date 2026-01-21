"""
Tracer module for logging LLM calls to structured log files.
"""

import json
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from threading import Lock


class Tracer:
    """
    A tracer for logging LLM calls with structured data.
    
    This class provides functionality to log inputs, outputs, and metadata
    of LLM calls in a structured JSON Lines format, enabling tracing of
    data transformations and error identification.
    """
    
    def __init__(self, log_file: Union[str, Path] = ".tr-ai-cing/trace.jsonl", auto_flush: bool = True):
        """
        Initialize the Tracer.
        
        Args:
            log_file: Path to the log file (default: ".tr-ai-cing/trace.jsonl")
            auto_flush: Whether to flush after each write (default: True)
        """
        self.log_file = Path(log_file)
        self.auto_flush = auto_flush
        self._lock = Lock()
        self._span_stack: List[str] = []
        self._trace_id: Optional[str] = None
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def start_trace(self, trace_id: Optional[str] = None) -> str:
        """
        Start a new trace.
        
        Args:
            trace_id: Optional trace ID (generates one if not provided)
            
        Returns:
            The trace ID
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        self._trace_id = trace_id
        return trace_id
    
    def end_trace(self):
        """End the current trace."""
        self._trace_id = None
        self._span_stack.clear()
    
    @contextmanager
    def span(
        self,
        name: str,
        span_type: str = "llm_call",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for tracing a span (e.g., an LLM call).
        
        Args:
            name: Name of the span
            span_type: Type of span (default: "llm_call")
            metadata: Additional metadata to log
            
        Yields:
            A dictionary to store span data (inputs, outputs, etc.)
        """
        span_id = str(uuid.uuid4())
        parent_span_id = self._span_stack[-1] if self._span_stack else None
        
        # Initialize trace if not started
        if self._trace_id is None:
            self.start_trace()
        
        self._span_stack.append(span_id)
        
        span_data = {
            "span_id": span_id,
            "trace_id": self._trace_id,
            "parent_span_id": parent_span_id,
            "name": name,
            "type": span_type,
            "metadata": metadata or {},
            "start_time": datetime.now(timezone.utc).isoformat(),
        }
        
        start = time.time()
        error = None
        
        try:
            yield span_data
        except Exception as e:
            error = str(e)
            span_data["error"] = error
            raise
        finally:
            span_data["end_time"] = datetime.now(timezone.utc).isoformat()
            span_data["duration_ms"] = (time.time() - start) * 1000
            
            if error is None:
                span_data["status"] = "success"
            else:
                span_data["status"] = "error"
            
            self._write_log(span_data)
            self._span_stack.pop()
    
    def log_llm_call(
        self,
        name: str,
        input_data: Any,
        output_data: Any,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an LLM call with its input and output.
        
        Args:
            name: Name/description of the LLM call
            input_data: Input to the LLM
            output_data: Output from the LLM
            model: Model name (e.g., "gpt-4")
            provider: Provider name (e.g., "openai")
            metadata: Additional metadata
        """
        with self.span(name, span_type="llm_call", metadata=metadata) as span:
            span["input"] = input_data
            span["output"] = output_data
            if model:
                span["model"] = model
            if provider:
                span["provider"] = provider
    
    def _write_log(self, data: Dict[str, Any]):
        """
        Write a log entry to the file.
        
        Args:
            data: The data to log
        """
        with self._lock:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(data) + "\n")
                if self.auto_flush:
                    f.flush()


# Global tracer instance
_default_tracer: Optional[Tracer] = None


def get_default_tracer() -> Tracer:
    """Get or create the default global tracer."""
    global _default_tracer
    if _default_tracer is None:
        _default_tracer = Tracer()
    return _default_tracer


# Context variable for request-scoped tracers
_current_tracer: ContextVar[Optional[Tracer]] = ContextVar('current_tracer', default=None)


def get_current_tracer() -> Optional[Tracer]:
    """
    Get the tracer for the current context.
    
    This function retrieves the tracer instance that has been set for the 
    current context (e.g., current request in a web application). It's 
    thread-safe and async-safe, making it perfect for web applications
    with concurrent requests.
    
    Returns:
        Optional[Tracer]: The tracer instance for the current context, or None
            if no tracer has been set for this context.
    
    Example:
        ```python
        # In a web app request handler
        tracer = Tracer(log_file=f"trace_{request_id}.jsonl")
        set_current_tracer(tracer)
        
        # In any function called during the request
        tracer = get_current_tracer()
        if tracer:
            with tracer.span("my_operation"):
                tracer.log_llm_call(...)
        ```
    """
    return _current_tracer.get()


def set_current_tracer(tracer: Optional[Tracer]) -> None:
    """
    Set the tracer for the current context.
    
    This function sets a tracer instance for the current context. The tracer
    will be automatically available to all code running in the same context
    (e.g., the same request, the same async task) without needing to pass it
    as a parameter.
    
    Args:
        tracer: The tracer instance to set for this context, or None to clear it.
    
    Example:
        ```python
        # At the start of a request
        tracer = Tracer(log_file=f"trace_{request_id}.jsonl")
        set_current_tracer(tracer)
        tracer.start_trace(trace_id=request_id)
        
        try:
            # Process the request - all functions can access the tracer
            result = process_request(data)
        finally:
            tracer.end_trace()
            set_current_tracer(None)  # Clean up
        ```
    """
    _current_tracer.set(tracer)


def get_tracer() -> Tracer:
    """
    Get a tracer instance, checking context first, then falling back to default.
    
    This is a convenience function that:
    1. First checks if a tracer has been set for the current context
    2. If not, falls back to the default global tracer
    
    This allows code to work in both context-based and global tracer scenarios
    without modification.
    
    Returns:
        Tracer: A tracer instance (either from context or the default)
    
    Example:
        ```python
        # Works whether you're using context tracers or the default tracer
        tracer = get_tracer()
        with tracer.span("my_operation"):
            tracer.log_llm_call(...)
        ```
    """
    tracer = get_current_tracer()
    if tracer is None:
        tracer = get_default_tracer()
    return tracer


def trace_llm_call(
    name: str,
    input_data: Any,
    output_data: Any,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    tracer: Optional[Tracer] = None
):
    """
    Convenience function to log an LLM call using the context or default tracer.
    
    This function will first check if a tracer is set in the current context,
    then fall back to the default tracer if not. This makes it work seamlessly
    in both context-based and global tracer scenarios.
    
    Args:
        name: Name/description of the LLM call
        input_data: Input to the LLM
        output_data: Output from the LLM
        model: Model name
        provider: Provider name
        metadata: Additional metadata
        tracer: Optional tracer instance (uses context/default if not provided)
    """
    if tracer is None:
        tracer = get_tracer()
    
    tracer.log_llm_call(
        name=name,
        input_data=input_data,
        output_data=output_data,
        model=model,
        provider=provider,
        metadata=metadata
    )
