"""Simple test script to verify the core infrastructure."""

import sys
import os

# Force mock provider for testing
os.environ["LLM_PROVIDER"] = "mock"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.llm import get_llm
from core.nodes.planner import planner_node
from core.nodes.actor import actor_node
from core.nodes.auditor import auditor_node

def test_basic_flow():
    """Test a basic flow through the nodes without LangGraph."""
    print("=== Testing Basic Node Flow ===\n")
    
    # Initialize state
    state: AgentState = {
        "messages": [{"role": "user", "content": "Create a file named test.txt with content 'Hello World'"}],
        "plan": [],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None
    }
    
    # Step 1: Planner
    print("Step 1: Running Planner...")
    planner_updates = planner_node(state)
    state.update(planner_updates)
    print(f"Plan generated: {state['plan']}\n")
    
    # Step 2: Execute plan
    for i, step in enumerate(state['plan']):
        print(f"Step {i+2}: Executing {step['role']}...")
        
        if step['role'] == "Actor":
            actor_updates = actor_node(state)
            state.update(actor_updates)
        elif step['role'] == "Auditor":
            auditor_updates = auditor_node(state)
            state.update(auditor_updates)
        
        print(f"Current state: step_index={state['current_step_index']}\n")
    
    print("=== Test Complete ===")
    print(f"Final state: {state}")

if __name__ == "__main__":
    test_basic_flow()
