"""
Tests for the Tracer class.
"""

import json
import pytest
from pathlib import Path
from tracing import Tracer


@pytest.fixture
def temp_log_file(tmp_path):
    """Create a temporary log file path."""
    return tmp_path / "test_trace.jsonl"


@pytest.fixture
def tracer(temp_log_file):
    """Create a Tracer instance for testing."""
    return Tracer(log_file=temp_log_file)


def test_tracer_initialization(temp_log_file):
    """Test that tracer initializes correctly."""
    tracer = Tracer(log_file=temp_log_file)
    assert tracer.log_file == temp_log_file
    assert tracer.auto_flush is True


def test_start_trace(tracer):
    """Test starting a trace."""
    trace_id = tracer.start_trace()
    assert trace_id is not None
    assert tracer._trace_id == trace_id


def test_start_trace_with_custom_id(tracer):
    """Test starting a trace with a custom ID."""
    custom_id = "my-custom-trace-id"
    trace_id = tracer.start_trace(trace_id=custom_id)
    assert trace_id == custom_id
    assert tracer._trace_id == custom_id


def test_end_trace(tracer):
    """Test ending a trace."""
    tracer.start_trace()
    tracer.end_trace()
    assert tracer._trace_id is None
    assert len(tracer._span_stack) == 0


def test_log_llm_call(tracer, temp_log_file):
    """Test logging an LLM call."""
    tracer.start_trace()
    
    tracer.log_llm_call(
        name="test_call",
        input_data="What is AI?",
        output_data="AI is artificial intelligence",
        model="gpt-4",
        provider="openai",
        metadata={"user": "test_user"}
    )
    
    # Verify log file was created and contains data
    assert temp_log_file.exists()
    
    with open(temp_log_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        
        log_entry = json.loads(lines[0])
        assert log_entry["name"] == "test_call"
        assert log_entry["input"] == "What is AI?"
        assert log_entry["output"] == "AI is artificial intelligence"
        assert log_entry["model"] == "gpt-4"
        assert log_entry["provider"] == "openai"
        assert log_entry["metadata"]["user"] == "test_user"
        assert log_entry["status"] == "success"


def test_span_context_manager(tracer, temp_log_file):
    """Test using span as a context manager."""
    tracer.start_trace()
    
    with tracer.span("test_span", span_type="custom") as span:
        span["input"] = "test input"
        span["output"] = "test output"
    
    assert temp_log_file.exists()
    
    with open(temp_log_file, "r") as f:
        log_entry = json.loads(f.read())
        assert log_entry["name"] == "test_span"
        assert log_entry["type"] == "custom"
        assert log_entry["input"] == "test input"
        assert log_entry["output"] == "test output"
        assert log_entry["status"] == "success"
        assert "duration_ms" in log_entry


def test_span_with_error(tracer, temp_log_file):
    """Test that errors are logged correctly in spans."""
    tracer.start_trace()
    
    with pytest.raises(ValueError):
        with tracer.span("error_span") as span:
            raise ValueError("Test error")
    
    with open(temp_log_file, "r") as f:
        log_entry = json.loads(f.read())
        assert log_entry["status"] == "error"
        assert "Test error" in log_entry["error"]


def test_nested_spans(tracer, temp_log_file):
    """Test nested spans create parent-child relationships."""
    tracer.start_trace()
    
    with tracer.span("parent") as parent_span:
        parent_span["data"] = "parent data"
        
        with tracer.span("child") as child_span:
            child_span["data"] = "child data"
    
    with open(temp_log_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 2
        
        # Child completes first, so it's written first
        child = json.loads(lines[0])
        parent = json.loads(lines[1])
        
        assert child["name"] == "child"
        assert child["parent_span_id"] is not None
        
        assert parent["name"] == "parent"
        assert parent["parent_span_id"] is None


def test_auto_trace_initialization(tracer, temp_log_file):
    """Test that trace is auto-initialized if not started."""
    # Don't start trace explicitly
    with tracer.span("auto_trace_span"):
        pass
    
    assert temp_log_file.exists()
    
    with open(temp_log_file, "r") as f:
        log_entry = json.loads(f.read())
        assert "trace_id" in log_entry
        assert log_entry["trace_id"] is not None
