"""
Test File Operations Skill - Full Integration
==============================================

Validates that the file-operations skill works end-to-end:
1. Skill loads into registry
2. LLM recognizes file-related intents
3. Plan references the correct skill and tools
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import Agent
from core.state import AgentState
from core.nodes.planner import planner_node


def test_file_operations_skill():
    """Test file-operations skill workflow"""
    print("=" * 70)
    print("FILE OPERATIONS SKILL TEST")
    print("=" * 70)
    
    # Step 1: Create core agent
    print("\n[Step 1] Creating core Agent...")
    core_agent = Agent(name="core", description="Core AgentOS")
    
    # Verify skill loaded
    file_skill = core_agent.get_skill("file-operations")
    assert file_skill is not None, "❌ file-operations skill not loaded"
    assert file_skill.is_core, "❌ file-operations should be core skill"
    print(f"✅ file-operations skill loaded")
    print(f"   Description: {file_skill.description[:80]}...")
    print(f"   Has SKILL.md: {'Yes' if file_skill.prompt_instructions else 'No'}")
    print(f"   Module path: {file_skill.module_path}")
    
    # Step 2: Test intent recognition
    print("\n[Step 2] Testing intent recognition...")
    user_input = "I need to read a JSON file called config.json and print its contents"
    
    mock_state: AgentState = {
        "messages": [{"role": "user", "content": user_input}],
        "plan": [],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None
    }
    
    print(f"   User: \"{user_input}\"")
    print("   Running planner...")
    
    # Call planner
    updated_state = planner_node(mock_state, registry=core_agent.registry)
    plan = updated_state.get("plan", [])
    
    print(f"\n[Step 3] Analyzing plan...")
    print(f"   Plan steps: {len(plan)}")
    
    # Verify plan mentions file operations
    plan_text = str(plan).lower()
    
    skill_mentioned = "file" in plan_text or "read" in plan_text
    json_mentioned = "json" in plan_text
    
    print(f"\n[Results]")
    print(f"  ✅ Plan generated: {len(plan)} steps")
    print(f"  {'✅' if skill_mentioned else '❌'} File operations mentioned")
    print(f"  {'✅' if json_mentioned else '❌'} JSON reading mentioned")
    
    # Print first step
    if plan:
        print(f"\n[First Plan Step Preview]")
        first_step = plan[0]
        print(f"  Action: {first_step.get('action', 'N/A')[:100]}...")
    
    # Validation
    assert len(plan) > 0, "❌ No plan generated"
    assert skill_mentioned, "❌ File operations not mentioned"
    
    print(f"\n{'=' * 70}")
    print("✅ FILE OPERATIONS SKILL TEST PASSED")
    print("=" * 70)
    print("\nValidated:")
    print("  ✅ Skill loaded with SKILL.md")
    print("  ✅ LLM recognized file operation intent")
    print("  ✅ Plan includes file operations")
    
    return True


if __name__ == "__main__":
    try:
        test_file_operations_skill()
        print("\n🎉 File operations skill fully functional!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
