"""
tr-ai-cing: A monitoring and observability platform for LLM applications.

This package provides tools for tracing and visualizing LLM application workflows.
"""

__version__ = "0.1.0"

from .tracer import (
    Tracer, 
    trace_llm_call, 
    get_default_tracer,
    get_current_tracer,
    set_current_tracer,
    get_tracer,
)
from .visualizer import Visualizer

__all__ = [
    "Tracer", 
    "trace_llm_call", 
    "get_default_tracer",
    "get_current_tracer",
    "set_current_tracer", 
    "get_tracer",
    "Visualizer",
]
