"""Minimal test to debug the actor node."""

import sys
import os

# Force mock provider for testing
os.environ["LLM_PROVIDER"] = "mock"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.nodes.actor import actor_node

def test_actor():
    """Test just the Actor node."""
    print("=== Testing Actor Node ===\n")
    
    # Initialize state with a pre-made plan
    state: AgentState = {
        "messages": [{"role": "user", "content": "Create a file named test.txt"}],
        "plan": [
            {"role": "Actor", "instruction": "Create a file named tests/results/test.txt with content 'Hello World'"}
        ],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None
    }
    
    # Run actor
    updates = actor_node(state)
    state.update(updates)
    
    print(f"\n=== Actor Test Complete ===")
    print(f"Tool outputs: {state['tool_outputs']}")

if __name__ == "__main__":
    test_actor()
