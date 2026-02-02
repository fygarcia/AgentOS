import json
import requests
from core.state import AgentState
from core.config import config
from core.audit_strategies import (
    verify_file_exists,
    verify_file_content_contains,
    verify_file_does_not_exist,
    verify_tool_output_success
)

def auditor_node(state: AgentState):
    """
    Auditor Node: Verifies the result of previous actions using defined strategies.
    Uses LLM to select the appropriate strategy based on the instruction.
    """
    idx = state.get("current_step_index", 0)
    plan = state.get("plan", [])
    
    # Get previous output if available (from Actor)
    tool_outputs = state.get("tool_outputs", {})
    # Assuming the Actor ran at idx-1. 
    # But wait, Auditor runs AFTER Actor. 
    # If the plan is [Actor, Auditor], then when Auditor runs (at idx=1), 
    # it is verifying steps executed previously. 
    # The `current_step_index` points to THIS step (Auditor step).
    # So we are executing the Auditor step's instruction.
    
    if idx >= len(plan):
        return {}
    
    step = plan[idx]
    role = step.get("role")
    instruction = step.get("instruction")
    expected_outcome = step.get("expected_outcome", "")
    
    if role != "Auditor":
        return {}

    print(f"\n[Node] AUDITOR: {instruction}")
    print(f"       Outcome: {expected_outcome}")
    
    # Get output from the PREVIOUS step (usually Actor)
    # This is rough logic: assuming steps are linear Actor -> Auditor
    prev_step_idx = idx - 1
    prev_output = tool_outputs.get(f"step_{prev_step_idx}", "")
    
    print(f"       Checking Step {prev_step_idx} output: {prev_output[:50]}...")
    
    # Use LLM to decide strategy
    model = config.PARSER_MODEL
    base_url = config.OLLAMA_BASE_URL.rstrip('/')
    
    # List available strategies for the LLM
    strategies = [
        "verify_file_exists(path)",
        "verify_file_content_contains(path, substring)",
        "verify_file_does_not_exist(path)",
        "verify_tool_output_success()"
    ]
    
    prompt = f"""You are the Auditor. You need to verify the success of a task.
    
    Instruction: "{instruction}"
    Expected Outcome: "{expected_outcome}"
    Previous Step Output: "{prev_output}"
    
    Available Strategies:
    {json.dumps(strategies, indent=2)}
    
    Select the BEST strategy to verify this. 
    Return a JSON object with "strategy" and "args".
    
    Examples:
    - {{"strategy": "verify_file_exists", "args": {{"path": "hello.txt"}}}}
    - {{"strategy": "verify_file_content_contains", "args": {{"path": "hello.txt", "substring": "Success"}}}}
    - {{"strategy": "verify_tool_output_success", "args": {{}}}}
    
    JSON Response:
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        result_json = response.json()["response"]
        data = json.loads(result_json)
        
        strategy_name = data.get("strategy")
        args = data.get("args", {})
        
        print(f"[Auditor] Selected strategy: {strategy_name} params={args}")
        
        # specific hardcoded dispatch for safety
        if strategy_name == "verify_file_exists":
            result = verify_file_exists(args.get("path", ""))
        elif strategy_name == "verify_file_content_contains":
            result = verify_file_content_contains(args.get("path", ""), args.get("substring", ""))
        elif strategy_name == "verify_file_does_not_exist":
            result = verify_file_does_not_exist(args.get("path", ""))
        else:
            # Default fallback
            result = verify_tool_output_success(prev_output)
            
        print(f"[Auditor] Result: {'✅ PASS' if result.passed else '❌ FAIL'}")
        print(f"          Message: {result.message}")
        
        # Store audit result? 
        # For now, just print. Ideally, if failed, we might want to stop or retry.
        # But for Phase 1D MVP, simply reporting is the goal.
        
    except Exception as e:
        print(f"[Auditor] ❌ Verification failed: {e}")
    
    return {
        "current_step_index": idx + 1
    }
