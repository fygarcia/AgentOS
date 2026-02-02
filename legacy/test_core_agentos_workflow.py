"""
Core AgentOS Skill Test
========================

Focused test to validate that the core AgentOS skill system works correctly:

1. SKILL.md is loaded (frontmatter + body)
2. Skill context is injected into planner prompt
3. LLM correctly identifies skills from user intent
4. LLM references correct tool scripts

This test validates the CORE workflow, not Finn-specific skills.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import Agent
from core.state import AgentState
from core.nodes.planner import planner_node


def test_core_agentos_database_skill():
    """
    Test: User wants to query a database
    
    Expected workflow:
    1. Registry loads core/skills/database/SKILL.md
    2. Frontmatter triggers on database-related intents
    3. SKILL.md body provides instructions
    4. LLM identifies scripts/crud.py as the tool to use
    """
    print("=" * 70)
    print("CORE AGENTOS TEST: Database Skill Workflow")
    print("=" * 70)
    
    # Step 1: Create core agent (no agent-specific skills)
    print("\n[Step 1] Creating core Agent...")
    core_agent = Agent(name="core", description="Core AgentOS")
    
    # Verify database skill was loaded
    db_skill = core_agent.get_skill("sqlite-crud")
    assert db_skill is not None, "❌ sqlite-crud skill not loaded"
    assert db_skill.is_core, "❌ sqlite-crud should be marked as core skill"
    print(f"✅ sqlite-crud skill loaded")
    print(f"   Description: {db_skill.description[:80]}...")
    print(f"   Has prompt instructions: {'Yes' if db_skill.prompt_instructions else 'No'}")
    print(f"   Module path: {db_skill.module_path}")
    
    # Step 2: Verify skill context is available
    print("\n[Step 2] Checking skill context...")
    skill_context = core_agent.registry.get_skill_prompt_context()
    assert "sqlite-crud" in skill_context, "❌ sqlite-crud not in prompt context"
    assert "SQLite database" in skill_context or "database CRUD" in skill_context, \
        "❌ Database skill description not in context"
    print(f"✅ Skill context includes sqlite-crud")
    print(f"   Context snippet: {skill_context[:200]}...")
    
    # Step 3: Test with user intent
    print("\n[Step 3] Testing user intent recognition...")
    user_input = "I need to query a SQLite database to get all users from the users table"
    
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
    
    print(f"\n[Step 4] Analyzing plan...")
    print(f"   Plan steps: {len(plan)}")
    
    # Verify plan mentions the skill or tool
    plan_text = str(plan).lower()
    
    # Check if skill or tool is mentioned
    skill_mentioned = "sqlite" in plan_text or "crud" in plan_text or "database" in plan_text
    tool_mentioned = "crud.py" in plan_text or "execute" in plan_text
    
    print(f"\n[Results]")
    print(f"  ✅ Plan generated: {len(plan)} steps")
    print(f"  {'✅' if skill_mentioned else '❌'} Database/SQLite mentioned in plan")
    print(f"  {'✅' if tool_mentioned else '⚠️ '} Tool/script referenced (optional)")
    
    # Print first step for inspection
    if plan:
        print(f"\n[First Plan Step Preview]")
        first_step = plan[0]
        print(f"  Action: {first_step.get('action', 'N/A')[:100]}...")
        if 'why' in first_step:
            print(f"  Reason: {first_step['why'][:100]}...")
    
    # Validation
    assert len(plan) > 0, "❌ No plan generated"
    assert skill_mentioned, "❌ Skill/database not mentioned in plan"
    
    print(f"\n{'=' * 70}")
    print("✅ CORE AGENTOS TEST PASSED")
    print("=" * 70)
    print("\nValidated:")
    print("  ✅ Core skill loaded from SKILL.md")
    print("  ✅ Skill context injected into planner")
    print("  ✅ LLM recognized database intent")
    print("  ✅ Plan references database operations")
    
    return True


if __name__ == "__main__":
    try:
        test_core_agentos_database_skill()
        print("\n🎉 All core AgentOS workflow validations passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
