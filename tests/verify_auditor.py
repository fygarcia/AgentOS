import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nodes.auditor import auditor_node

load_dotenv()

def verify_auditor():
    print("=" * 70)
    print("VERIFYING AUDITOR STRATEGIES")
    print("=" * 70)
    
    # Create a dummy file for testing
    test_file = "audit_test.txt"
    with open(test_file, "w") as f:
        f.write("Success")
        
    try:
        # Test 1: Verify file exists (Success Case)
        print("\n[Test 1] Verifying exists of 'audit_test.txt'")
        state = {
            "current_step_index": 1,
            "plan": [
                {"role": "Actor", "instruction": "Create file", "expected_outcome": "File created"},
                {"role": "Auditor", "instruction": f"Verify {test_file} exists", "expected_outcome": "File exists"}
            ],
            "tool_outputs": {"step_0": "File created successfully"}
        }
        
        auditor_node(state)
        print("✅ Test 1 ran (Check console output for PASS)")

        # Test 2: Verify file missing (Failure Case)
        print("\n[Test 2] Verifying 'missing_file.txt' exists (Should FAIL)")
        state["plan"][1]["instruction"] = "Verify missing_file.txt exists"
        
        auditor_node(state)
        print("✅ Test 2 ran (Check console output for FAIL)")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    verify_auditor()
