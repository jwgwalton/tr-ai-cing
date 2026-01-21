"""
Tests for the example scripts.

These tests ensure that all example scripts run successfully and produce
the expected outputs without errors.
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path


@pytest.fixture
def examples_dir():
    """Get the examples directory path."""
    return Path(__file__).parent.parent / "examples"


@pytest.fixture
def temp_examples_dir(tmp_path):
    """Create a temporary directory for example outputs."""
    return tmp_path / "examples"


def test_basic_example_runs_successfully(examples_dir, tmp_path):
    """Test that basic_example.py runs without errors."""
    # Run the basic example
    result = subprocess.run(
        [sys.executable, str(examples_dir / "basic_example.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    assert "Started trace:" in result.stdout
    assert "Trace completed!" in result.stdout
    assert "Visualization saved to:" in result.stdout


def test_basic_example_creates_trace_file(examples_dir, tmp_path):
    """Test that basic_example.py creates a valid trace file."""
    # Run the basic example
    subprocess.run(
        [sys.executable, str(examples_dir / "basic_example.py")],
        cwd=tmp_path,
        capture_output=True
    )
    
    trace_file = tmp_path / "examples" / "example_trace.jsonl"
    assert trace_file.exists(), "Trace file was not created"
    
    # Verify trace file has valid JSON lines
    with open(trace_file, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0, "Trace file is empty"
        
        # Verify each line is valid JSON
        for line in lines:
            log_entry = json.loads(line)
            assert "span_id" in log_entry
            assert "trace_id" in log_entry
            assert "name" in log_entry
            assert "status" in log_entry


def test_basic_example_creates_visualization(examples_dir, tmp_path):
    """Test that basic_example.py creates an HTML visualization."""
    # Run the basic example
    subprocess.run(
        [sys.executable, str(examples_dir / "basic_example.py")],
        cwd=tmp_path,
        capture_output=True
    )
    
    html_file = tmp_path / "examples" / "trace_visualization.html"
    assert html_file.exists(), "HTML visualization was not created"
    
    # Verify it's a valid HTML file
    with open(html_file, "r") as f:
        content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "tr-ai-cing" in content


def test_error_handling_example_runs_successfully(examples_dir, tmp_path):
    """Test that error_handling_example.py runs without errors."""
    result = subprocess.run(
        [sys.executable, str(examples_dir / "error_handling_example.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    assert "Tracing LLM calls with errors..." in result.stdout
    assert "Trace completed!" in result.stdout


def test_error_handling_example_captures_errors(examples_dir, tmp_path):
    """Test that error_handling_example.py creates a valid trace file."""
    result = subprocess.run(
        [sys.executable, str(examples_dir / "error_handling_example.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )
    
    trace_file = tmp_path / "examples" / "error_trace.jsonl"
    assert trace_file.exists()
    
    # Verify trace file has valid JSON lines and spans
    with open(trace_file, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0, "Trace file is empty"
        
        # Verify each line is valid JSON
        for line in lines:
            log_entry = json.loads(line)
            assert "span_id" in log_entry
            assert "status" in log_entry
    
    # Verify the output shows error handling
    assert "Error traced:" in result.stdout or "Successful call traced" in result.stdout


def test_langgraph_example_runs_successfully(examples_dir, tmp_path):
    """Test that langgraph_example.py runs without errors."""
    result = subprocess.run(
        [sys.executable, str(examples_dir / "langgraph_example.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    assert "Started trace:" in result.stdout
    assert "Processing: What's the weather like today?" in result.stdout
    assert "Processing: What is the capital of France?" in result.stdout
    assert "Processing: Tell me about artificial intelligence" in result.stdout
    assert "Trace completed!" in result.stdout


def test_langgraph_example_creates_trace_file(examples_dir, tmp_path):
    """Test that langgraph_example.py creates a valid trace file."""
    subprocess.run(
        [sys.executable, str(examples_dir / "langgraph_example.py")],
        cwd=tmp_path,
        capture_output=True
    )
    
    trace_file = tmp_path / "examples" / "langgraph_trace.jsonl"
    assert trace_file.exists(), "Trace file was not created"
    
    # Verify trace file has valid JSON lines
    with open(trace_file, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0, "Trace file is empty"
        
        # Verify structure and hierarchy
        workflow_spans = []
        node_spans = []
        llm_call_spans = []
        
        for line in lines:
            log_entry = json.loads(line)
            span_type = log_entry.get("type")
            
            if span_type == "workflow":
                workflow_spans.append(log_entry)
            elif span_type == "agent_node":
                node_spans.append(log_entry)
            elif span_type == "llm_call":
                llm_call_spans.append(log_entry)
        
        # The example runs 3 scenarios, so should have 3 workflow spans
        # Note: Update this if the example changes the number of scenarios
        expected_workflows = 3
        assert len(workflow_spans) == expected_workflows, \
            f"Expected {expected_workflows} workflow spans, got {len(workflow_spans)}"
        
        # Should have agent node spans
        assert len(node_spans) > 0, "No agent node spans found"
        
        # Should have LLM call spans
        assert len(llm_call_spans) > 0, "No LLM call spans found"


def test_langgraph_example_has_correct_hierarchy(examples_dir, tmp_path):
    """Test that langgraph_example.py creates proper parent-child relationships."""
    subprocess.run(
        [sys.executable, str(examples_dir / "langgraph_example.py")],
        cwd=tmp_path,
        capture_output=True
    )
    
    trace_file = tmp_path / "examples" / "langgraph_trace.jsonl"
    
    with open(trace_file, "r") as f:
        spans = [json.loads(line) for line in f]
    
    # Build a map of span_id to span
    span_map = {span["span_id"]: span for span in spans}
    
    # Verify workflow spans have no parent
    workflow_spans = [s for s in spans if s["type"] == "workflow"]
    for workflow in workflow_spans:
        assert workflow["parent_span_id"] is None, "Workflow span should have no parent"
    
    # Verify agent nodes are children of workflow
    agent_nodes = [s for s in spans if s["type"] == "agent_node"]
    for node in agent_nodes:
        assert node["parent_span_id"] is not None, "Agent node should have a parent"
        parent = span_map.get(node["parent_span_id"])
        assert parent is not None, "Parent span not found"
        assert parent["type"] == "workflow", "Agent node parent should be workflow"
    
    # Verify LLM calls are children of agent nodes
    llm_calls = [s for s in spans if s["type"] == "llm_call"]
    for call in llm_calls:
        assert call["parent_span_id"] is not None, "LLM call should have a parent"
        parent = span_map.get(call["parent_span_id"])
        assert parent is not None, "Parent span not found"
        assert parent["type"] == "agent_node", "LLM call parent should be agent_node"


def test_langgraph_example_has_metadata(examples_dir, tmp_path):
    """Test that langgraph_example.py includes proper metadata."""
    subprocess.run(
        [sys.executable, str(examples_dir / "langgraph_example.py")],
        cwd=tmp_path,
        capture_output=True
    )
    
    trace_file = tmp_path / "examples" / "langgraph_trace.jsonl"
    
    with open(trace_file, "r") as f:
        spans = [json.loads(line) for line in f]
    
    # Find LLM call spans with metadata
    llm_calls = [s for s in spans if s["type"] == "llm_call"]
    
    # Verify at least some LLM calls have the "node" metadata
    has_node_metadata = any("node" in s.get("metadata", {}) for s in llm_calls)
    assert has_node_metadata, "No LLM calls with 'node' metadata found"


def test_langgraph_example_creates_visualization(examples_dir, tmp_path):
    """Test that langgraph_example.py creates an HTML visualization."""
    subprocess.run(
        [sys.executable, str(examples_dir / "langgraph_example.py")],
        cwd=tmp_path,
        capture_output=True
    )
    
    html_file = tmp_path / "examples" / "langgraph_visualization.html"
    assert html_file.exists(), "HTML visualization was not created"
    
    # Verify it's a valid HTML file with LangGraph-specific content
    with open(html_file, "r") as f:
        content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "tr-ai-cing" in content


def test_all_examples_output_to_correct_location(examples_dir, tmp_path):
    """Test that all examples output files to the examples/ directory."""
    # Define example configurations
    EXAMPLE_CONFIGS = [
        ("basic_example.py", "example_trace.jsonl", "trace_visualization.html"),
        ("error_handling_example.py", "error_trace.jsonl", "error_visualization.html"),
        ("langgraph_example.py", "langgraph_trace.jsonl", "langgraph_visualization.html"),
    ]
    
    for script, trace_file, html_file in EXAMPLE_CONFIGS:
        # Run the example
        subprocess.run(
            [sys.executable, str(examples_dir / script)],
            cwd=tmp_path,
            capture_output=True
        )
        
        # Check that files are in examples/ directory
        assert (tmp_path / "examples" / trace_file).exists(), \
            f"{script} did not create {trace_file} in examples/ directory"
        assert (tmp_path / "examples" / html_file).exists(), \
            f"{script} did not create {html_file} in examples/ directory"
