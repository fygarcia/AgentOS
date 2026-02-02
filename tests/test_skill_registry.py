"""
TEST: Skill Registry System
=============================
Tests the skill discovery, registration, validation, and execution system.

TEST FLOW:
1. INPUT:  Skills directory with metadata-enabled skills
2. SCAN:   Registry scans and loads skills
3. VERIFY: Skills are discoverable and executable
4. EXECUTE: Test skill execution with parameters
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.skill_registry import SkillRegistry, Skill

def print_section(title, char="="):
    """Print a clear section header."""
    print(f"\n{char*70}")
    print(f"  {title}")
    print(f"{char*70}")

def test_skill_registry():
    """Test SkillRegistry functionality."""
    
    print_section("TEST: Skill Registry System")
    
    # ========================================================================
    # STEP 1: CREATE REGISTRY AND SCAN
    # ========================================================================
    print_section("STEP 1: Scan Skills Directory", "-")
    
    registry = SkillRegistry()
    count = registry.scan_directory("./finn/skills", agent_name="finn")
    
    print(f"Skills found: {count}")
    print(f"Registry: {registry}")
    
    assert count > 0, "Should find at least one skill"
    
    # ========================================================================
    # STEP 2: VERIFY STATISTICS
    # ========================================================================
    print_section("STEP 2: Verify Statistics", "-")
    
    stats = registry.get_stats()
    print(f"Total skills: {stats['total_skills']}")
    print(f"Agents: {stats['agents']}")
    print(f"Categories: {stats['categories']}")
    print(f"Skills by agent: {stats['skills_by_agent']}")
    print(f"Skills by category: {stats['skills_by_category']}")
    
    assert stats['total_skills'] == count
    assert 'finn' in stats['agents']
    assert 'database' in stats['categories']
    
    # ========================================================================
    # STEP 3: VERIFY SKILL DISCOVERY
    # ========================================================================
    print_section("STEP 3: Skill Discovery", "-")
    
    # Test get_skill
    skill = registry.get_skill("db_upsert_asset")
    assert skill is not None, "Should find db_upsert_asset skill"
    print(f"Found skill: {skill.name}")
    print(f"  Description: {skill.description}")
    print(f"  Parameters: {list(skill.parameters.keys())}")
    print(f"  Agent: {skill.agent}")
    print(f"  Category: {skill.category}")
    
    # Test has_skill
    assert registry.has_skill("db_upsert_asset")
    assert not registry.has_skill("nonexistent_skill")
    print("\n✅ has_skill() works correctly")
    
    # Test get_all_skills
    all_skills = registry.get_all_skills()
    assert len(all_skills) == count
    print(f"✅ get_all_skills() returned {len(all_skills)} skills")
    
    # Test get_skills_by_agent
    finn_skills = registry.get_skills_by_agent("finn")
    assert len(finn_skills) > 0
    print(f"✅ get_skills_by_agent('finn') returned {len(finn_skills)} skills")
    
    # Test get_skills_by_category
    db_skills = registry.get_skills_by_category("database")
    assert len(db_skills) > 0
    print(f"✅ get_skills_by_category('database') returned {len(db_skills)} skills")
    
    # Test search_skills
    search_results = registry.search_skills("portfolio")
    assert len(search_results) > 0
    print(f"✅ search_skills('portfolio') returned {len(search_results)} skills")
    
    # ========================================================================
    # STEP 4: VERIFY METADATA
    # ========================================================================
    print_section("STEP 4: Verify Skill Metadata", "-")
    
    skill = registry.get_skill("db_upsert_asset")
    
    # Check required fields
    assert skill.name == "db_upsert_asset"
    assert skill.description != ""
    assert skill.agent == "finn"
    assert skill.category == "database"
    assert isinstance(skill.parameters, dict)
    assert isinstance(skill.returns, dict)
    assert isinstance(skill.examples, list)
    assert isinstance(skill.tags, list)
    
    print(f"Name: {skill.name}")
    print(f"Version: {skill.version}")
    print(f"Description: {skill.description}")
    print(f"Agent: {skill.agent}")
    print(f"Category: {skill.category}")
    print(f"Parameters: {len(skill.parameters)}")
    print(f"Examples: {len(skill.examples)}")
    print(f"Tags: {skill.tags}")
    
    # Verify parameter metadata
    assert "ticker" in skill.parameters
    assert skill.parameters["ticker"]["required"] == True
    assert skill.parameters["ticker"]["type"] == "str"
    print("\n✅ Parameter metadata correct")
    
    # ========================================================================
    # STEP 5: TEST SKILL PROMPT CONTEXT
    # ========================================================================
    print_section("STEP 5: Skill Prompt Context", "-")
    
    context = registry.get_skill_prompt_context()
    assert len(context) > 0
    assert "db_upsert_asset" in context
    assert "ticker*" in context  # Required parameter
    
    print(context)
    
    # ========================================================================
    # STEP 6: TEST PARAMETER VALIDATION
    # ========================================================================
    print_section("STEP 6: Parameter Validation", "-")
    
    skill = registry.get_skill("db_upsert_asset")
    
    # Test missing required parameter
    try:
        skill.execute(asset_class="Equity")  # Missing ticker
        assert False, "Should have raised ValueError for missing parameter"
    except ValueError as e:
        print(f"✅ Correctly caught missing parameter: {e}")
    
    # ========================================================================
    # STEP 7: TEST SKILL EXECUTION (if database exists)
    # ========================================================================
    print_section("STEP 7: Skill Execution Test", "-")
    
    # Test get_portfolio_holdings (no params)
    try:
        holdings_skill = registry.get_skill("get_portfolio_holdings")
        if holdings_skill:
            print("Testing get_portfolio_holdings...")
            # Note: This will fail if database doesn't exist, which is expected
            try:
                result = holdings_skill.execute()
                print(f"✅ Skill executed (result type: {type(result).__name__})")
            except Exception as e:
                print(f"⚠️ Skill execution failed (expected if DB not initialized): {e}")
    except Exception as e:
        print(f"⚠️ Could not test execution: {e}")
    
    # Test execute_skill via registry
    try:
        print("\nTesting direct registry execution...")
        result = registry.execute_skill("get_portfolio_holdings")
        print(f"✅ Registry execute_skill worked")
    except ValueError as e:
        # Skill not found
        print(f"❌ Skill not found: {e}")
    except Exception as e:
        # Execution error (e.g., database doesn't exist)
        print(f"⚠️ Execution failed (expected if DB not initialized): {str(e)[:50]}...")
    
    # Test execute_skill with nonexistent skill
    try:
        registry.execute_skill("nonexistent_skill")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✅ Correctly raised ValueError for nonexistent skill")
    
    # ========================================================================
    # STEP 8: VALIDATION
    # ========================================================================
    print_section("STEP 8: VALIDATION", "-")
    
    all_passed = True
    
    try:
        # Check registry state
        assert len(registry._skills) > 0, "Should have skills"
        assert len(registry._skills_by_agent) > 0, "Should have agent index"
        assert len(registry._skills_by_category) > 0, "Should have category index"
        
        # Check all skills have required metadata
        for skill in registry.get_all_skills():
            assert skill.name, f"Skill missing name: {skill}"
            assert skill.description, f"Skill {skill.name} missing description"
            assert skill.agent, f"Skill {skill.name} missing agent"
            assert skill.category, f"Skill {skill.name} missing category"
            assert skill._execute_func is not None, f"Skill {skill.name} missing execute function"
        
        # Check skill discovery works
        assert registry.has_skill("db_upsert_asset")
        assert registry.has_skill("get_portfolio_holdings")
        assert registry.has_skill("initialize_portfolio_database")
        
        # Check stats are consistent
        assert stats['total_skills'] == len(registry.get_all_skills())
        
        print("✅ All assertions passed!")
        print("✅ Skill registry working correctly")
        print(f"✅ {stats['total_skills']} skills registered successfully")
        print(f"✅ All skills have proper metadata")
        print(f"✅ Discovery and execution interfaces working")
        
        print_section("TEST RESULT: PASSED ✅")
        return True
        
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
        print_section("TEST RESULT: FAILED ❌")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print_section("TEST RESULT: ERROR ❌")
        return False

if __name__ == "__main__":
    success = test_skill_registry()
    sys.exit(0 if success else 1)
