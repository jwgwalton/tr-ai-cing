"""
Tests for the Visualizer class.
"""

import json
import pytest
from pathlib import Path
from tracing import Tracer, Visualizer


@pytest.fixture
def temp_log_file(tmp_path):
    """Create a temporary log file with test data."""
    log_file = tmp_path / "test_trace.jsonl"
    
    # Create sample trace data
    tracer = Tracer(log_file=log_file)
    tracer.start_trace(trace_id="test-trace-123")
    
    with tracer.span("parent_span", metadata={"test": "metadata"}):
        tracer.log_llm_call(
            name="test_llm_call",
            input_data="What is Python?",
            output_data="Python is a programming language",
            model="gpt-4",
            provider="openai"
        )
    
    tracer.end_trace()
    return log_file


@pytest.fixture
def visualizer(temp_log_file):
    """Create a Visualizer instance for testing."""
    return Visualizer(log_file=temp_log_file)


def test_visualizer_initialization(temp_log_file):
    """Test that visualizer initializes correctly."""
    visualizer = Visualizer(log_file=temp_log_file)
    assert visualizer.log_file == temp_log_file
    assert visualizer.spans == []
    assert visualizer.traces == {}


def test_load_traces(visualizer):
    """Test loading traces from log file."""
    visualizer.load_traces()
    
    assert len(visualizer.spans) > 0
    assert len(visualizer.traces) > 0
    assert "test-trace-123" in visualizer.traces


def test_load_traces_empty_file(tmp_path):
    """Test loading from an empty log file."""
    empty_file = tmp_path / "empty.jsonl"
    empty_file.touch()
    
    visualizer = Visualizer(log_file=empty_file)
    visualizer.load_traces()
    
    assert visualizer.spans == []
    assert visualizer.traces == {}


def test_load_traces_nonexistent_file(tmp_path):
    """Test loading from a nonexistent file."""
    nonexistent = tmp_path / "nonexistent.jsonl"
    
    visualizer = Visualizer(log_file=nonexistent)
    visualizer.load_traces()
    
    assert visualizer.spans == []
    assert visualizer.traces == {}


def test_generate_html(visualizer, tmp_path):
    """Test generating HTML visualization."""
    output_file = tmp_path / "test_output.html"
    result = visualizer.generate_html(output_file)
    
    assert output_file.exists()
    assert result == output_file
    
    # Verify HTML content
    with open(output_file, "r") as f:
        content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "tr-ai-cing" in content
        assert "Trace Visualization" in content


def test_html_contains_trace_data(visualizer, tmp_path):
    """Test that generated HTML contains trace data."""
    output_file = tmp_path / "test_output.html"
    visualizer.generate_html(output_file)
    
    with open(output_file, "r") as f:
        content = f.read()
        assert "test-trace-123" in content
        assert "test_llm_call" in content or "parent_span" in content


def test_html_has_proper_structure(visualizer, tmp_path):
    """Test that generated HTML has proper structure."""
    output_file = tmp_path / "test_output.html"
    visualizer.generate_html(output_file)
    
    with open(output_file, "r") as f:
        content = f.read()
        # Check for essential HTML elements
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "<style>" in content
        assert "<script>" in content
        assert "</html>" in content


def test_html_includes_css(visualizer, tmp_path):
    """Test that generated HTML includes CSS styling."""
    output_file = tmp_path / "test_output.html"
    visualizer.generate_html(output_file)
    
    with open(output_file, "r") as f:
        content = f.read()
        assert ".container" in content
        assert ".trace-container" in content
        assert ".span-node" in content


def test_html_includes_javascript(visualizer, tmp_path):
    """Test that generated HTML includes JavaScript."""
    output_file = tmp_path / "test_output.html"
    visualizer.generate_html(output_file)
    
    with open(output_file, "r") as f:
        content = f.read()
        assert "function toggleSpan" in content


def test_multiple_traces(tmp_path):
    """Test visualizing multiple traces."""
    log_file = tmp_path / "multi_trace.jsonl"
    tracer = Tracer(log_file=log_file)
    
    # Create first trace
    tracer.start_trace(trace_id="trace-1")
    tracer.log_llm_call("call1", "input1", "output1")
    tracer.end_trace()
    
    # Create second trace
    tracer.start_trace(trace_id="trace-2")
    tracer.log_llm_call("call2", "input2", "output2")
    tracer.end_trace()
    
    # Visualize
    visualizer = Visualizer(log_file=log_file)
    visualizer.load_traces()
    
    assert len(visualizer.traces) == 2
    assert "trace-1" in visualizer.traces
    assert "trace-2" in visualizer.traces
