import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.graph import create_graph
from core.config import config

load_dotenv()

def verify_intent():
    print("=" * 70)
    print("VERIFYING INTENT CLASSIFICATION ROUTING")
    print("=" * 70)
    
    # Use mock provider to avoid actual LLM calls for graph structure check
    # But we want to test the CLASSIFIER node logic which uses requests directly...
    # The classifier node hardcodes config.REASONING_MODEL and calls Ollama.
    # So we need Ollama running.
    
    print(f"Provider: {config.LLM_PROVIDER}")
    print(f"Ollama URL: {config.OLLAMA_BASE_URL}")
    
    app = create_graph()
    
    # Test 1: Simple Question (Should route to Responder)
    print("\n[Test 1] Input: 'What is the capital of France?'")
    try:
        inputs = {
            "messages": [{"role": "user", "content": "What is the capital of France?"}],
            "current_step_index": 0,
            "plan": []
        }
        
        # Run graph
        print("Running workflow...")
        for output in app.stream(inputs):
            for key, value in output.items():
                print(f"  -> Node '{key}' executed")
                if "intent_type" in value:
                    print(f"     Intent: {value['intent_type']}")
                if "final_response" in value:
                    print(f"     Response: {value['final_response'][:100]}...")
        
        print("✅ Test 1 Complete")
        
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")

    # Test 2: Task (Should route to Planner)
    print("\n[Test 2] Input: 'Create a file named france.txt'")
    try:
        inputs = {
            "messages": [{"role": "user", "content": "Create a file named france.txt"}],
            "current_step_index": 0,
            "plan": []
        }
        
        # Run graph
        print("Running workflow...")
        # We limit steps to avoid full execution if it works
        steps = 0
        for output in app.stream(inputs):
            steps += 1
            for key, value in output.items():
                print(f"  -> Node '{key}' executed")
                if key == "planner":
                    print("     ✅ Reached Planner! (Success)")
                    # We can stop here, we proved routing worked
            
            if steps > 2: 
                break
        
        print("✅ Test 2 Complete")
        
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")

if __name__ == "__main__":
    verify_intent()
