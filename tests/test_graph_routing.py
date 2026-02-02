"""
TEST: LangGraph Routing Logic
==============================
Tests the router function that determines which node to execute next.

ARCHITECTURE:
The router examines the current state and decides:
- END: If all steps are complete
- "actor": If current step role is "Actor"  
- "auditor": If current step role is "Auditor"

TEST FLOW:
1. INPUT:  States with different step configurations
2. ROUTE:  Call route_step() function
3. OUTPUT: Verify correct routing decision

TESTED SCENARIOS:
- Empty plan → END
- Plan complete (index >= length) → END
- Actor step → "actor"
- Auditor step → "auditor"
- Mid-plan routing
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.graph import route_step
from langgraph.graph import END

def print_section(title, char="="):
    """Print a clear section header."""
    print(f"\n{char*70}")
    print(f"  {title}")
    print(f"{char*70}")

def print_test_case(num, description):
    """Print test case header."""
    print(f"\n[Test Case {num}] {description}")
    print("-" * 70)

def test_routing():
    """Test the LangGraph routing logic."""
    
    print_section("TEST: LangGraph Routing Logic")
    
    all_passed = True
    
    # ========================================================================
    # TEST CASE 1: Empty Plan → END
    # ========================================================================
    print_test_case(1, "Empty Plan Should Route to END")
    
    state1: AgentState = {
        "messages": [],
        "plan": [],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None
    }
    
    print(f"INPUT:  plan=[], current_step_index=0")
    route1 = route_step(state1)
    print(f"OUTPUT: {route1}")
    print(f"EXPECT: {END}")
    
    if route1 == END:
        print("✅ PASS: Empty plan correctly routes to END")
    else:
        print(f"❌ FAIL: Expected END, got {route1}")
        all_passed = False
    
    # ========================================================================
    # TEST CASE 2: Plan Complete → END
    # ========================================================================
    print_test_case(2, "Completed Plan Should Route to END")
    
    state2: AgentState = {
        "messages": [],
        "plan": [
            {"role": "Actor", "instruction": "Do something"},
            {"role": "Auditor", "instruction": "Check it"}
        ],
        "current_step_index": 2,  # Past the last step
        "tool_outputs": {},
        "final_response": None
    }
    
    print(f"INPUT:  plan=[2 steps], current_step_index=2")
    route2 = route_step(state2)
    print(f"OUTPUT: {route2}")
    print(f"EXPECT: {END}")
    
    if route2 == END:
        print("✅ PASS: Completed plan correctly routes to END")
    else:
        print(f"❌ FAIL: Expected END, got {route2}")
        all_passed = False
    
    # ========================================================================
    # TEST CASE 3: Actor Step → "actor"
    # ========================================================================
    print_test_case(3, "Actor Role Should Route to 'actor' Node")
    
    state3: AgentState = {
        "messages": [],
        "plan": [
            {"role": "Actor", "instruction": "Write code"},
            {"role": "Auditor", "instruction": "Verify"}
        ],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None
    }
    
    print(f"INPUT:  plan[0].role='Actor', current_step_index=0")
    route3 = route_step(state3)
    print(f"OUTPUT: {route3}")
    print(f"EXPECT: 'actor'")
    
    if route3 == "actor":
        print("✅ PASS: Actor role correctly routes to 'actor'")
    else:
        print(f"❌ FAIL: Expected 'actor', got {route3}")
        all_passed = False
    
    # ========================================================================
    # TEST CASE 4: Auditor Step → "auditor"
    # ========================================================================
    print_test_case(4, "Auditor Role Should Route to 'auditor' Node")
    
    state4: AgentState = {
        "messages": [],
        "plan": [
            {"role": "Actor", "instruction": "Write code"},
            {"role": "Auditor", "instruction": "Verify"}
        ],
        "current_step_index": 1,
        "tool_outputs": {},
        "final_response": None
    }
    
    print(f"INPUT:  plan[1].role='Auditor', current_step_index=1")
    route4 = route_step(state4)
    print(f"OUTPUT: {route4}")
    print(f"EXPECT: 'auditor'")
    
    if route4 == "auditor":
        print("✅ PASS: Auditor role correctly routes to 'auditor'")
    else:
        print(f"❌ FAIL: Expected 'auditor', got {route4}")
        all_passed = False
    
    # ========================================================================
    # TEST CASE 5: Multi-Step Plan → Correct Routing
    # ========================================================================
    print_test_case(5, "Multi-Step Plan Should Route Sequentially")
    
    state5: AgentState = {
        "messages": [],
        "plan": [
            {"role": "Actor", "instruction": "Step 1"},
            {"role": "Auditor", "instruction": "Step 2"},
            {"role": "Actor", "instruction": "Step 3"},
            {"role": "Auditor", "instruction": "Step 4"}
        ],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None
    }
    
    expected_sequence = ["actor", "auditor", "actor", "auditor", END]
    actual_sequence = []
    
    print(f"INPUT: plan=[Actor, Auditor, Actor, Auditor]")
    print(f"Testing sequential routing through all steps...\n")
    
    for i in range(5):
        state5["current_step_index"] = i
        route = route_step(state5)
        actual_sequence.append(route)
        print(f"  Step {i}: route={route}, expected={expected_sequence[i]}")
    
    print(f"\nACTUAL:   {actual_sequence}")
    print(f"EXPECTED: {expected_sequence}")
    
    if actual_sequence == expected_sequence:
        print("✅ PASS: Sequential routing works correctly")
    else:
        print("❌ FAIL: Sequential routing mismatch")
        all_passed = False
    
    # ========================================================================
    # FINAL RESULT
    # ========================================================================
    print_section("TEST SUMMARY")
    
    if all_passed:
        print("✅ All 5 test cases PASSED")
        print("✅ Routing logic is working correctly")
        print_section("TEST RESULT: PASSED ✅")
        return True
    else:
        print("❌ Some test cases FAILED")
        print_section("TEST RESULT: FAILED ❌")
        return False

if __name__ == "__main__":
    success = test_routing()
    sys.exit(0 if success else 1)
