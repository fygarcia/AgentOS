"""Test the full LangGraph workflow using the refactored engine."""

import sys
import os

# Force mock provider for testing
os.environ["LLM_PROVIDER"] = "mock"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import run_agent

def test_langgraph_workflow():
    """Test the complete LangGraph workflow with a simple task."""
    print("=== Testing L angGraph Workflow ===\n")
    
    # Run the agent with a simple task
    result = run_agent("Create a file named langgraph_test.txt with content 'LangGraph Works!'")
    
    print(f"\n=== Test Complete ===")
    
    # Check if file was created
    if os.path.exists("langgraph_test.txt"):
        with open("langgraph_test.txt", "r") as f:
            content = f.read()
        print(f"✓ File created successfully!")
        print(f"✓ Content: {content}")
    else:
        print("✗ File was not created")
    
    return result

if __name__ == "__main__":
    test_langgraph_workflow()
