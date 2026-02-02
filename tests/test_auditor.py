"""
TEST: Auditor Node
===================
Tests the Auditor node in isolation to verify it can validate task execution.

ARCHITECTURE:
- Uses mock LLM for predictable testing
- Auditor receives instruction and validates completion
- Returns audit result and increments step index

TEST FLOW:
1. INPUT: State with audit instruction
2. INTERMEDIATE: LLM generates audit response
3. OUTPUT: Updated state with incremented step index
"""

import sys
import os

# Force mock provider for testing
os.environ["LLM_PROVIDER"] = "mock"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.nodes.auditor import auditor_node

def print_section(title):
    """Print a clear section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_auditor():
    """Test the Auditor node with clear input/output visibility."""
    
    print_section("TEST: Auditor Node")
    
    # ========================================================================
    # STEP 1: DEFINE INPUT
    # ========================================================================
    print("\n[Step 1] 📝 INPUT - Initial State")
    print("-" * 70)
    
    instruction = "Verify hello.txt exists and contains correct text"
    
    state: AgentState = {
        "messages": [{"role": "user", "content": "Create a file named hello.txt in the folder ./tests/results"}],
        "plan": [
            {"role": "Actor", "instruction": "Write 'Agentic OS is Live' to hello.txt in the folder ./tests/results"},
            {"role": "Auditor", "instruction": instruction}
        ],
        "current_step_index": 1,  # Pointing to Auditor step
        "tool_outputs": {"step_0": "Success"},
        "final_response": None
    }
    
    print(f"Current Step Index: {state['current_step_index']}")
    print(f"Current Step Role:  {state['plan'][1]['role']}")
    print(f"Instruction:        {instruction}")
    print(f"Previous Outputs:   {state['tool_outputs']}")
    
    # ========================================================================
    # STEP 2: EXECUTE AUDITOR NODE
    # ========================================================================
    print_section("STEP 2: EXECUTE - Auditor Processing")
    print("-" * 70)
    print("Provider: MOCK")
    print("LLM Model: MockLLM (simulated auditor)")
    print("\nCalling auditor_node()...")
    print("-" * 70)
    
    # Run auditor (this will print MockLLM output)
    updates = auditor_node(state)
    
    # ========================================================================
    # STEP 3: INTERMEDIATE RESULTS
    # ========================================================================
    print_section("STEP 3: INTERMEDIATE - LLM Response")
    print("-" * 70)
    print("The MockLLM auditor response is shown above")
    print("(In production, OllamaLLM would generate audit verdict)")
    
    # ========================================================================
    # STEP 4: FINAL OUTPUT
    # ========================================================================
    print_section("STEP 4: OUTPUT - State Updates")
    print("-" * 70)
    
    state.update(updates)
    
    print(f"Updated Step Index: {state['current_step_index']}")
    print(f"Expected:           2 (moved to next step)")
    
    # ========================================================================
    # STEP 5: ASSERTIONS
    # ========================================================================
    print_section("STEP 5: VALIDATION")
    print("-" * 70)
    
    try:
        assert state['current_step_index'] == 2, \
            f"Expected step_index=2, got {state['current_step_index']}"
        
        assert 'current_step_index' in updates, \
            "Updates must contain 'current_step_index'"
        
        assert updates['current_step_index'] == 2, \
            "Updated index should be 2"
        
        print("✅ All assertions passed!")
        print("✅ Auditor correctly processed the step")
        print("✅ State correctly incremented to next step")
        
        print_section("TEST RESULT: PASSED ✅")
        return True
        
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
        print_section("TEST RESULT: FAILED ❌")
        return False

if __name__ == "__main__":
    success = test_auditor()
    sys.exit(0 if success else 1)
