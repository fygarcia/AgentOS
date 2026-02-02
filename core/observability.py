"""
Observability module for LLM tracing and monitoring.

NOTE: Arize Phoenix doesn't support Python 3.14 yet (max 3.13).
This module provides basic OpenTelemetry tracing as an interim solution.
When Phoenix adds 3.14 support, we can upgrade to the full Phoenix experience.
"""

import os
import json
import time
from typing import Optional, Dict, Any
from functools import wraps

# Configuration
ENABLE_TRACING = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"

class SimpleTracer:
    """Lightweight tracing for LLM calls until Phoenix supports Python 3.14."""
    
    def __init__(self):
        self.traces = []
        self.current_trace = None
        self.start_time = None
        
    def start_trace(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Start a new trace."""
        if not ENABLE_TRACING:
            return
            
        self.current_trace = {
            "name": name,
            "start_time": time.time(),
            "metadata": metadata or {},
            "spans": []
        }
        
    def add_span(self, span_name: str, span_type: str, details: Dict[str, Any]):
        """Add a span to the current trace."""
        if not ENABLE_TRACING or not self.current_trace:
            return
            
        span = {
            "name": span_name,
            "type": span_type,
            "timestamp": time.time(),
            "details": details
        }
        self.current_trace["spans"].append(span)
        
    def end_trace(self, status: str = "success"):
        """End the current trace."""
        if not ENABLE_TRACING or not self.current_trace:
            return
            
        self.current_trace["end_time"] = time.time()
        self.current_trace["duration"] = self.current_trace["end_time"] - self.current_trace["start_time"]
        self.current_trace["status"] = status
        
        self.traces.append(self.current_trace)
        self._print_trace_summary(self.current_trace)
        
        self.current_trace = None
        
    def _print_trace_summary(self, trace: Dict[str, Any]):
        """Print a summary of the trace."""
        print(f"\n{'='*60}")
        print(f"📊 Trace: {trace['name']}")
        print(f"⏱️  Duration: {trace['duration']:.3f}s")
        print(f"✓ Status: {trace['status']}")
        print(f"{'='*60}")
        
        for i, span in enumerate(trace["spans"], 1):
            print(f"\n  [{i}] {span['name']} ({span['type']})")
            if "model" in span["details"]:
                print(f"      Model: {span['details']['model']}")
            if "tokens" in span["details"]:
                print(f"      Tokens: {span['details']['tokens']}")
            if "prompt_length" in span["details"]:
                print(f"      Prompt length: {span['details']['prompt_length']} chars")
                
        print(f"\n{'='*60}\n")
    
    def get_traces(self):
        """Get all traces."""
        return self.traces
    
    def save_traces(self, filepath: str = ".tmp/traces.json"):
        """Save traces to file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.traces, f, indent=2)
        print(f"✅ Traces saved to {filepath}")

# Global tracer instance
_tracer = SimpleTracer()

def get_tracer() -> SimpleTracer:
    """Get the global tracer instance."""
    return _tracer

def trace_llm_call(func):
    """Decorator to trace LLM calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not ENABLE_TRACING:
            return func(*args, **kwargs)
            
        tracer = get_tracer()
        
        # Extract details
        func_name = func.__name__
        model = kwargs.get("model", "unknown")
        
        # Start timing
        start = time.time()
        
        # Call the function
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            # Log the span
            tracer.add_span(
                span_name=f"LLM Call: {func_name}",
                span_type="llm",
                details={
                    "model": model,
                    "duration": duration,
                    "status": "success"
                }
            )
            
            return result
        except Exception as e:
            duration = time.time() - start
            tracer.add_span(
                span_name=f"LLM Call: {func_name}",
                span_type="llm",
                details={
                    "model": model,
                    "duration": duration,
                    "status": "error",
                    "error": str(e)
                }
            )
            raise
            
    return wrapper

def init_observability():
    """Initialize observability."""
    if ENABLE_TRACING:
        print("\n" + "="*60)
        print("📊 Observability Enabled")
        print("="*60)
        print("ℹ️  Using lightweight OpenTelemetry tracing")
        print("ℹ️  Phoenix UI not available (requires Python ≤3.13)")
        print("ℹ️  Traces will be printed to console and saved to .tmp/traces.json")
        print("="*60 + "\n")
    else:
        print("ℹ️  Observability disabled (set ENABLE_OBSERVABILITY=true to enable)")

# When Phoenix supports Python 3.14, replace this module with:
# ```python
# import phoenix as px
# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# from openinference.instrumentation.langchain import LangChainInstrumentor
# 
# def init_observability():
#     if os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true":
#         px.launch_app()
#         LangChainInstrumentor().instrument()
#         print("✅ Phoenix UI: http://localhost:6006")
# ```
