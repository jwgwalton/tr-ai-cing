"""
Visualizer module for generating HTML visualizations of trace logs.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class Visualizer:
    """
    A visualizer for creating HTML representations of trace logs.
    
    This class reads structured log files and generates interactive HTML
    visualizations showing the DAG of LLM calls with their inputs and outputs.
    """
    
    def __init__(self, log_file: Union[str, Path]):
        """
        Initialize the Visualizer.
        
        Args:
            log_file: Path to the trace log file
        """
        self.log_file = Path(log_file)
        self.spans: List[Dict[str, Any]] = []
        self.traces: Dict[str, List[Dict[str, Any]]] = {}
    
    def load_traces(self):
        """Load traces from the log file."""
        self.spans = []
        self.traces = {}
        
        if not self.log_file.exists():
            return
        
        with open(self.log_file, "r") as f:
            for line in f:
                if line.strip():
                    span = json.loads(line)
                    self.spans.append(span)
                    
                    trace_id = span.get("trace_id")
                    if trace_id:
                        if trace_id not in self.traces:
                            self.traces[trace_id] = []
                        self.traces[trace_id].append(span)
    
    def generate_html(self, output_file: Union[str, Path] = "trace_visualization.html"):
        """
        Generate an HTML visualization of the traces.
        
        Args:
            output_file: Path to the output HTML file
        """
        self.load_traces()
        
        html = self._generate_html_content()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(html)
        
        return output_path
    
    def _generate_html_content(self) -> str:
        """Generate the HTML content."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tr-ai-cing - Trace Visualization</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 tr-ai-cing - Trace Visualization</h1>
            <p class="subtitle">LLM Application Observability</p>
        </header>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{len(self.traces)}</div>
                <div class="stat-label">Traces</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(self.spans)}</div>
                <div class="stat-label">Total Spans</div>
            </div>
        </div>
        
        {self._generate_traces_html()}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        return html
    
    def _generate_traces_html(self) -> str:
        """Generate HTML for all traces."""
        if not self.traces:
            return '<div class="no-data">No traces found. Start tracing your LLM calls!</div>'
        
        traces_html = []
        for trace_id, spans in self.traces.items():
            traces_html.append(self._generate_trace_html(trace_id, spans))
        
        return "\n".join(traces_html)
    
    def _generate_trace_html(self, trace_id: str, spans: List[Dict[str, Any]]) -> str:
        """Generate HTML for a single trace."""
        # Build parent-child relationships
        span_map = {span["span_id"]: span for span in spans}
        root_spans = [s for s in spans if not s.get("parent_span_id")]
        
        trace_html = f"""
        <div class="trace-container">
            <div class="trace-header">
                <h2>Trace: {trace_id[:8]}...</h2>
                <span class="span-count">{len(spans)} span(s)</span>
            </div>
            <div class="trace-dag">
                {self._generate_dag_html(root_spans, span_map)}
            </div>
        </div>
        """
        return trace_html
    
    def _generate_dag_html(
        self,
        spans: List[Dict[str, Any]],
        span_map: Dict[str, Dict[str, Any]],
        level: int = 0
    ) -> str:
        """Generate HTML for the DAG structure."""
        if not spans:
            return ""
        
        html_parts = []
        for span in spans:
            # Get child spans
            children = [
                s for s in span_map.values()
                if s.get("parent_span_id") == span["span_id"]
            ]
            
            status_class = span.get("status", "unknown")
            error = span.get("error")
            
            html_parts.append(f"""
            <div class="span-node" style="margin-left: {level * 40}px;">
                <div class="span-header status-{status_class}" onclick="toggleSpan(this)">
                    <span class="toggle-icon">▶</span>
                    <span class="span-name">{span.get('name', 'Unknown')}</span>
                    <span class="span-type">{span.get('type', 'unknown')}</span>
                    <span class="span-duration">{span.get('duration_ms', 0):.2f}ms</span>
                    <span class="span-status">{status_class}</span>
                </div>
                <div class="span-details" style="display: none;">
                    <div class="detail-section">
                        <strong>Span ID:</strong> {span.get('span_id', 'N/A')}
                    </div>
                    {f'<div class="detail-section"><strong>Model:</strong> {span.get("model", "N/A")}</div>' if span.get("model") else ''}
                    {f'<div class="detail-section"><strong>Provider:</strong> {span.get("provider", "N/A")}</div>' if span.get("provider") else ''}
                    <div class="detail-section">
                        <strong>Start Time:</strong> {span.get('start_time', 'N/A')}
                    </div>
                    <div class="detail-section">
                        <strong>Duration:</strong> {span.get('duration_ms', 0):.2f}ms
                    </div>
                    {f'<div class="detail-section error-box"><strong>Error:</strong> {error}</div>' if error else ''}
                    {self._format_io_data(span.get('input'), 'Input')}
                    {self._format_io_data(span.get('output'), 'Output')}
                    {self._format_metadata(span.get('metadata'))}
                </div>
            </div>
            """)
            
            if children:
                html_parts.append(self._generate_dag_html(children, span_map, level + 1))
        
        return "\n".join(html_parts)
    
    def _format_io_data(self, data: Any, label: str) -> str:
        """Format input/output data for display."""
        if data is None:
            return ""
        
        formatted_data = json.dumps(data, indent=2) if not isinstance(data, str) else data
        return f"""
        <div class="detail-section">
            <strong>{label}:</strong>
            <pre class="io-data">{formatted_data}</pre>
        </div>
        """
    
    def _format_metadata(self, metadata: Optional[Dict[str, Any]]) -> str:
        """Format metadata for display."""
        if not metadata:
            return ""
        
        return f"""
        <div class="detail-section">
            <strong>Metadata:</strong>
            <pre class="io-data">{json.dumps(metadata, indent=2)}</pre>
        </div>
        """
    
    def _get_css(self) -> str:
        """Get the CSS styles."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .stat-box {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }
        
        .trace-container {
            margin: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .trace-header {
            background: #f8f9fa;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #667eea;
        }
        
        .trace-header h2 {
            font-size: 1.3em;
            color: #333;
        }
        
        .span-count {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .trace-dag {
            padding: 20px;
        }
        
        .span-node {
            margin-bottom: 10px;
        }
        
        .span-header {
            padding: 12px 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.2s;
        }
        
        .span-header:hover {
            background: #e9ecef;
            transform: translateX(2px);
        }
        
        .span-header.status-success {
            border-left-color: #28a745;
        }
        
        .span-header.status-error {
            border-left-color: #dc3545;
        }
        
        .toggle-icon {
            transition: transform 0.2s;
            font-size: 0.8em;
        }
        
        .span-header.expanded .toggle-icon {
            transform: rotate(90deg);
        }
        
        .span-name {
            font-weight: bold;
            flex: 1;
        }
        
        .span-type {
            background: #6c757d;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
        }
        
        .span-duration {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .span-status {
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
        }
        
        .status-success .span-status {
            background: #d4edda;
            color: #155724;
        }
        
        .status-error .span-status {
            background: #f8d7da;
            color: #721c24;
        }
        
        .span-details {
            margin-top: 10px;
            padding: 15px;
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        .detail-section {
            margin-bottom: 15px;
        }
        
        .detail-section:last-child {
            margin-bottom: 0;
        }
        
        .detail-section strong {
            color: #495057;
            display: block;
            margin-bottom: 5px;
        }
        
        .io-data {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            border: 1px solid #dee2e6;
        }
        
        .error-box {
            background: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #dc3545;
        }
        
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
            font-size: 1.2em;
        }
        """
    
    def _get_javascript(self) -> str:
        """Get the JavaScript code."""
        return """
        function toggleSpan(element) {
            const details = element.nextElementSibling;
            if (details && details.classList.contains('span-details')) {
                if (details.style.display === 'none') {
                    details.style.display = 'block';
                    element.classList.add('expanded');
                } else {
                    details.style.display = 'none';
                    element.classList.remove('expanded');
                }
            }
        }
        """
