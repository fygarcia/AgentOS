"""
Skill Intent Recognition Test Suite
====================================

Tests that the Agent (Planner) correctly:
1. Understands user intent
2. Identifies appropriate skills to use
3. Generates expected plan structure

This is an ongoing test suite - add new cases as edge cases are discovered.

Usage:
    pytest tests/test_skill_intent_recognition.py -v
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import Agent
from core.state import AgentState
from core.nodes.planner import planner_node


@dataclass
class IntentTestCase:
    """
    Represents a test case for intent recognition.
    
    Attributes:
        id: Unique test case identifier
        user_input: What the user asks
        expected_skills: List of skill names that should be identified
        expected_plan_steps: Expected number of plan steps (approximate)
        description: Human-readable description of what we're testing
        tags: Categories for organizing tests (e.g., "database", "portfolio", "read")
    """
    id: str
    user_input: str
    expected_skills: List[str]
    expected_plan_steps: int
    description: str
    tags: List[str] = None
    
    # Optional: More specific assertions
    should_not_use_skills: List[str] = None  # Skills that should NOT be called
    expected_output_type: str = None  # "table", "chart", "json", "narrative"


# ============================================================================
# TEST CASES LIBRARY
# ============================================================================

INTENT_TEST_CASES = [
    
    # ========== PORTFOLIO READ OPERATIONS ==========
    
    IntentTestCase(
        id="TC001",
        user_input="Show me my portfolio holdings",
        expected_skills=["get_portfolio_holdings"],
        expected_plan_steps=2,  # Read + Present
        description="Basic portfolio read - should use get_portfolio_holdings skill",
        tags=["portfolio", "read", "database"],
        expected_output_type="table"
    ),
    
    IntentTestCase(
        id="TC002",
        user_input="What stocks do I own?",
        expected_skills=["get_portfolio_holdings"],
        expected_plan_steps=2,
        description="Natural language portfolio query - same as TC001",
        tags=["portfolio", "read", "natural_language"],
        expected_output_type="table"
    ),
    
    IntentTestCase(
        id="TC003",
        user_input="List all my investments",
        expected_skills=["get_portfolio_holdings"],
        expected_plan_steps=2,
        description="Another variant of portfolio read",
        tags=["portfolio", "read", "natural_language"],
        expected_output_type="table"
    ),
    
    # ========== PORTFOLIO WRITE OPERATIONS ==========
    
    IntentTestCase(
        id="TC004",
        user_input="Add Apple stock to my portfolio",
        expected_skills=["db_upsert_asset"],
        expected_plan_steps=3,  # Gather info + Upsert + Confirm
        description="Adding a new asset - should use db_upsert_asset",
        tags=["portfolio", "write", "database", "asset"],
        should_not_use_skills=["get_portfolio_holdings"]
    ),
    
    IntentTestCase(
        id="TC005",
        user_input="I bought 100 shares of TSLA yesterday",
        expected_skills=["db_upsert_asset"],
        expected_plan_steps=3,
        description="Implicit asset addition with transaction details",
        tags=["portfolio", "write", "transaction", "natural_language"],
    ),
    
    # ========== DATABASE SETUP ==========
    
    IntentTestCase(
        id="TC006",
        user_input="Initialize the portfolio database",
        expected_skills=["initialize_portfolio_database"],
        expected_plan_steps=1,
        description="Database initialization - setup operation",
        tags=["database", "setup", "initialization"],
    ),
    
    IntentTestCase(
        id="TC007",
        user_input="Set up my portfolio tracking system",
        expected_skills=["initialize_portfolio_database"],
        expected_plan_steps=2,  # Initialize + Confirm
        description="Natural language database setup",
        tags=["database", "setup", "natural_language"],
    ),
    
    # ========== GENERIC DATABASE OPERATIONS ==========
    
    IntentTestCase(
        id="TC008",
        user_input="Query the database for all assets in the Technology sector",
        expected_skills=["sqlite-crud"],
        expected_plan_steps=2,  # Construct query + Execute
        description="Generic SQL query - should use core sqlite-crud skill",
        tags=["database", "query", "core_skill"],
        should_not_use_skills=["get_portfolio_holdings"]  # Too specific
    ),
    
    IntentTestCase(
        id="TC009",
        user_input="Show me the database schema",
        expected_skills=["sqlite-crud"],
        expected_plan_steps=2,
        description="Schema inspection - generic database operation",
        tags=["database", "schema", "core_skill"],
    ),
    
    # ========== MULTI-SKILL OPERATIONS ==========
    
    IntentTestCase(
        id="TC010",
        user_input="Add Microsoft to my portfolio and then show all my holdings",
        expected_skills=["db_upsert_asset", "get_portfolio_holdings"],
        expected_plan_steps=4,  # Add asset + Confirm + Read holdings + Present
        description="Sequential operations requiring multiple skills",
        tags=["portfolio", "multi_skill", "read", "write"],
    ),
    
    # ========== EDGE CASES & AMBIGUITY ==========
    
    IntentTestCase(
        id="TC011",
        user_input="Tell me about my portfolio",
        expected_skills=["get_portfolio_holdings"],
        expected_plan_steps=3,  # Read + Analyze + Present
        description="Ambiguous request - should default to showing holdings",
        tags=["portfolio", "ambiguous", "read"],
    ),
    
    IntentTestCase(
        id="TC012",
        user_input="What's in the assets table?",
        expected_skills=["sqlite-crud"],  # Generic query, not portfolio-specific
        expected_plan_steps=2,
        description="Direct table query - should use generic SQL skill",
        tags=["database", "query", "technical"],
    ),
]


# ============================================================================
# TEST EXECUTION
# ============================================================================

class TestSkillIntentRecognition:
    """
    Test suite for validating intent recognition and skill routing.
    """
    
    @classmethod
    def setup_class(cls):
        """Initialize agent once for all tests."""
        print("\n" + "=" * 70)
        print("Setting up Finn Agent for Intent Recognition Tests")
        print("=" * 70)
        cls.finn = Agent(name="finn", description="Financial portfolio agent")
        print(f"✅ Agent initialized with {len(cls.finn.list_skills())} skills")
    
    def _run_planner(self, user_input: str) -> Dict[str, Any]:
        """
        Run planner with user input and return results.
        
        Returns:
            Dict with:
                - state: Updated state
                - plan: Generated plan
                - skills_used: List of skill names mentioned in plan
        """
        mock_state: AgentState = {
            "messages": [{"role": "user", "content": user_input}],
            "plan": [],
            "current_step_index": 0,
            "tool_outputs": {},
            "final_response": None
        }
        
        # Run planner
        updated_state = planner_node(mock_state, registry=self.finn.registry)
        
        # Extract skills mentioned in plan
        plan = updated_state.get("plan", [])
        skills_used = set()
        
        for step in plan:
            # Check if step mentions any skills
            step_text = str(step).lower()
            for skill in self.finn.list_skills():
                if skill.lower() in step_text or skill.replace("_", " ") in step_text:
                    skills_used.add(skill)
        
        return {
            "state": updated_state,
            "plan": plan,
            "skills_used": list(skills_used)
        }
    
    def test_case(self, test_case: IntentTestCase):
        """
        Execute a single test case.
        
        Args:
            test_case: The test case to run
        """
        print(f"\n{'=' * 70}")
        print(f"[{test_case.id}] {test_case.description}")
        print(f"User Input: \"{test_case.user_input}\"")
        print(f"Expected Skills: {test_case.expected_skills}")
        
        # Run planner
        result = self._run_planner(test_case.user_input)
        plan = result["plan"]
        skills_used = result["skills_used"]
        
        print(f"Plan Steps Generated: {len(plan)}")
        print(f"Skills Identified: {skills_used}")
        
        # Assertions
        failures = []
        
        # 1. Check expected skills are present
        for expected_skill in test_case.expected_skills:
            if expected_skill not in skills_used:
                failures.append(f"❌ Missing expected skill: {expected_skill}")
            else:
                print(f"  ✅ Found expected skill: {expected_skill}")
        
        # 2. Check skills that should NOT be used
        if test_case.should_not_use_skills:
            for forbidden_skill in test_case.should_not_use_skills:
                if forbidden_skill in skills_used:
                    failures.append(f"❌ Used forbidden skill: {forbidden_skill}")
        
        # 3. Check plan step count (allow ±1 variance)
        step_diff = abs(len(plan) - test_case.expected_plan_steps)
        if step_diff > 1:
            failures.append(
                f"❌ Plan steps mismatch: expected ~{test_case.expected_plan_steps}, got {len(plan)}"
            )
        else:
            print(f"  ✅ Plan steps within expected range")
        
        # Report
        if failures:
            print("\n⚠️  FAILURES:")
            for failure in failures:
                print(f"  {failure}")
            assert False, f"Test case {test_case.id} failed:\n" + "\n".join(failures)
        else:
            print(f"\n✅ {test_case.id} PASSED")
    
    # ========== INDIVIDUAL TEST METHODS ==========
    
    def test_tc001_basic_portfolio_read(self):
        """TC001: Show me my portfolio holdings"""
        self.test_case(INTENT_TEST_CASES[0])
    
    def test_tc002_natural_portfolio_query(self):
        """TC002: What stocks do I own?"""
        self.test_case(INTENT_TEST_CASES[1])
    
    def test_tc003_list_investments(self):
        """TC003: List all my investments"""
        self.test_case(INTENT_TEST_CASES[2])
    
    def test_tc004_add_asset(self):
        """TC004: Add Apple stock"""
        self.test_case(INTENT_TEST_CASES[3])
    
    def test_tc005_record_transaction(self):
        """TC005: I bought 100 shares of TSLA"""
        self.test_case(INTENT_TEST_CASES[4])
    
    def test_tc006_initialize_database(self):
        """TC006: Initialize portfolio database"""
        self.test_case(INTENT_TEST_CASES[5])
    
    def test_tc007_setup_system(self):
        """TC007: Set up portfolio tracking system"""
        self.test_case(INTENT_TEST_CASES[6])
    
    def test_tc008_generic_sql_query(self):
        """TC008: Query database for Tech sector"""
        self.test_case(INTENT_TEST_CASES[7])
    
    def test_tc009_show_schema(self):
        """TC009: Show database schema"""
        self.test_case(INTENT_TEST_CASES[8])
    
    def test_tc010_multi_skill_operation(self):
        """TC010: Add MSFT and show holdings"""
        self.test_case(INTENT_TEST_CASES[9])
    
    def test_tc011_ambiguous_request(self):
        """TC011: Tell me about my portfolio"""
        self.test_case(INTENT_TEST_CASES[10])
    
    def test_tc012_direct_table_query(self):
        """TC012: What's in the assets table?"""
        self.test_case(INTENT_TEST_CASES[11])


# ============================================================================
# MANUAL TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run intent recognition tests")
    parser.add_argument("--test", help="Run specific test case by ID (e.g., TC001)")
    parser.add_argument("--tag", help="Run tests with specific tag (e.g., portfolio)")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = TestSkillIntentRecognition()
    test_suite.setup_class()
    
    # Filter test cases
    tests_to_run = INTENT_TEST_CASES
    
    if args.test:
        tests_to_run = [tc for tc in INTENT_TEST_CASES if tc.id == args.test]
    elif args.tag:
        tests_to_run = [tc for tc in INTENT_TEST_CASES if args.tag in (tc.tags or [])]
    
    if not tests_to_run:
        print(f"❌ No tests found matching criteria")
        sys.exit(1)
    
    # Run tests
    print(f"\n🧪 Running {len(tests_to_run)} test case(s)...")
    
    passed = 0
    failed = 0
    
    for test_case in tests_to_run:
        try:
            test_suite.test_case(test_case)
            passed += 1
        except AssertionError:
            failed += 1
            continue
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    sys.exit(0 if failed == 0 else 1)
