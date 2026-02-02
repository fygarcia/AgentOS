"""Test the Planner node with Pydantic AI."""

import sys
import os

# Use Ollama for testing
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["ENABLE_OBSERVABILITY"] = "true"  # Enable to see traces

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.nodes.planner import planner_node

def test_planner_pydantic():
    """Test the Pydantic AI-based Planner node."""
    print("=== Testing Pydantic AI Planner Node ===\n")
    
    # Initialize state
    state: AgentState = {
        "messages": [{"role": "user", "content": "Create a file named test.txt with content 'Hello World'"}],
        "plan": [],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None
    }
    
    # Run planner
    try:
        updates = planner_node(state)
        state.update(updates)
        
        print(f"\n✅ Planner executed successfully!")
        print(f"📝 Plan generated: {len(state['plan'])} steps")
        
        for i, step in enumerate(state['plan'], 1):
            print(f"\n  Step {i}:")
            print(f"    Role: {step['role']}")
            print(f"    Instruction: {step['instruction']}")
        
        # Verify structure
        assert isinstance(state['plan'], list), "Plan should be a list"
        assert len(state['plan']) > 0, "Plan should have at least one step"
        
        for step in state['plan']:
            assert 'role' in step, "Each step should have a 'role'"
            assert 'instruction' in step, "Each step should have an 'instruction'"
            assert step['role'] in ['Actor', 'Auditor'], f"Role must be Actor or Auditor, got {step['role']}"
        
        print(f"\n✅ All assertions passed!")
        print(f"\n=== Planner Test Complete ===")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Planner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import time
    start_time = time.time()
    success = test_planner_pydantic()
    end_time = time.time()
    print(f"\n✅ Time taken: {end_time - start_time} seconds")
    sys.exit(0 if success else 1)
    print(f"\n✅ Time taken: {time.time() - start_time:.2f} seconds")