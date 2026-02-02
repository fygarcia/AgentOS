"""
Integration Tests for Persistent Memory System
===============================================

Tests the three-tier memory architecture (HOT/WARM/COLD) in real agent workflows.

Implements:
1. Amnesia Test - Resume after restart (MEMORY_SYSTEM.md lines 336-344)
2. Correction Test - Long-term recall (MEMORY_SYSTEM.md lines 346-355)
3. Auto-Logging Test - Verify automatic logging
4. Context Injection Test - Memory in prompts
5. Self-Annealing Test - Error recovery (MEMORY_SYSTEM.md lines 292-312)
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_manager import MemoryManager


class TestMemoryIntegration:
    """Integration tests for the persistent memory system."""
    
    @pytest.fixture
    def temp_agent_dir(self):
        """Create a temporary directory for test agent."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_agent_name(self):
        """Generate unique test agent name."""
        return f"test_agent_{int(time.time() * 1000)}"
    
    @pytest.fixture
    def memory_manager(self, test_agent_name, temp_agent_dir):
        """Create a MemoryManager instance for testing."""
        return MemoryManager(test_agent_name, base_path=temp_agent_dir / test_agent_name)
    
    # ========================================================================
    # Helper Functions
    # ========================================================================
    
    def verify_now_contains(self, memory_manager: MemoryManager, expected_text: str) -> bool:
        """Assert that NOW.md contains expected text."""
        now_content = memory_manager.read_now()
        assert expected_text in now_content, f"NOW.md should contain '{expected_text}'"
        return True
    
    def verify_log_contains(self, memory_manager: MemoryManager, expected_text: str) -> bool:
        """Assert that LOG.md contains expected text."""
        log_content = memory_manager.read_log()
        assert expected_text in log_content, f"LOG.md should contain '{expected_text}'"
        return True
    
    def verify_log_entry_type(self, memory_manager: MemoryManager, entry_type: str) -> bool:
        """Assert that LOG.md has an entry of the specified type."""
        log_content = memory_manager.read_log()
        assert f"[{entry_type}]" in log_content, f"LOG.md should have [{entry_type}] entry"
        return True
    
    def verify_fact_exists(self, memory_manager: MemoryManager, key: str, expected_value: str) -> bool:
        """Assert that a fact exists with expected value."""
        actual_value = memory_manager.get_fact(key)
        assert actual_value == expected_value, f"Fact '{key}' should be '{expected_value}', got '{actual_value}'"
        return True
    
    # ========================================================================
    # TEST 1: Amnesia Test - Resume After Restart
    # ========================================================================
    
    def test_amnesia_resume_after_restart(self, memory_manager, test_agent_name):
        """
        Test that agent can resume a multi-step task after restart.
        
        Spec: MEMORY_SYSTEM.md lines 336-344
        
        Flow:
        1. Start agent with multi-step task
        2. Update NOW.md with task in progress
        3. Simulate restart (new MemoryManager instance)
        4. Verify agent reads NOW.md and knows what to resume
        """
        print("\n" + "="*70)
        print("TEST: Amnesia - Resume After Restart")
        print("="*70)
        
        # Step 1: Agent starts a multi-step task
        task_description = "Create file A.txt, then create file B.txt"
        memory_manager.update_now(
            new_status=f"Working on: {task_description}",
            next_steps=[
                "Create A.txt with content 'File A'",
                "Create B.txt with content 'File B'"
            ]
        )
        
        memory_manager.append_log(
            entry_type="SYSTEM",
            content=f"Started multi-step task: {task_description}"
        )
        
        # Verify NOW.md has the task
        self.verify_now_contains(memory_manager, "Create file A.txt")
        self.verify_now_contains(memory_manager, "Create B.txt")
        print("✓ Step 1: Task started and logged to NOW.md")
        
        # Step 2: Simulate process restart
        print("\n🔄 Simulating agent restart (creating new MemoryManager instance)...")
        
        # Create a NEW memory manager instance (same agent name, same path)
        # This simulates the agent being killed and restarted
        restarted_manager = MemoryManager(
            test_agent_name, 
            base_path=memory_manager.base_path.parent / test_agent_name
        )
        
        # Step 3: Verify the restarted agent can read the previous state
        now_content = restarted_manager.read_now()
        
        assert "Create file A.txt" in now_content, "Restarted agent should see task in NOW.md"
        assert "Create B.txt" in now_content, "Restarted agent should see all next steps"
        print("✓ Step 2: Restarted agent successfully read NOW.md")
        
        # Step 4: Verify LOG.md is also accessible
        log_content = restarted_manager.read_log()
        assert "Started multi-step task" in log_content, "Restarted agent should have log history"
        print("✓ Step 3: Restarted agent has access to LOG.md history")
        
        # Step 5: Verify the agent can continue the task
        # The restarted agent updates status as it continues
        restarted_manager.update_now(
            new_status="Continuing previous task - Creating A.txt",
            next_steps=["Create B.txt with content 'File B'"]
        )
        
        self.verify_now_contains(restarted_manager, "Continuing previous task")
        print("✓ Step 4: Restarted agent can continue the task")
        
        print("\n✅ AMNESIA TEST PASSED")
        print("   - Agent state persisted across restart")
        print("   - NOW.md correctly stored task information")
        print("   - LOG.md preserved history")
        print("   - Agent can resume from checkpoint")
    
    # ========================================================================
    # TEST 2: Correction Test - Long-term Memory Recall
    # ========================================================================
    
    def test_correction_long_term_memory_recall(self, memory_manager, test_agent_name):
        """
        Test that agent can recall facts after context is flushed.
        
        Spec: MEMORY_SYSTEM.md lines 346-355
        
        Flow:
        1. Agent stores user fact
        2. Simulate context flush (new manager instance)
        3. Verify agent can recall fact from memory.db
        """
        print("\n" + "="*70)
        print("TEST: Correction - Long-term Memory Recall")
        print("="*70)
        
        # Step 1: Agent stores a user fact
        api_key = "SECRET_API_KEY_12345"
        memory_manager.save_fact("api_key", api_key, category="config")
        
        self.verify_fact_exists(memory_manager, "api_key", api_key)
        print(f"✓ Step 1: Stored fact 'api_key' = '{api_key}'")
        
        # Step 2: Simulate many interactions / context flush
        # In reality, this would be 50+ turns of conversation
        # We simulate by creating a new MemoryManager instance
        print("\n🔄 Simulating context flush (many interactions later)...")
        
        flushed_manager = MemoryManager(
            test_agent_name,
            base_path=memory_manager.base_path.parent / test_agent_name
        )
        
        # Step 3: Verify the fact can still be recalled
        recalled_key = flushed_manager.get_fact("api_key")
        
        assert recalled_key == api_key, f"Should recall API key, got {recalled_key}"
        print(f"✓ Step 2: Successfully recalled 'api_key' = '{recalled_key}'")
        
        # Step 4: Verify all facts can be retrieved
        all_facts = flushed_manager.get_all_facts()
        assert "api_key" in all_facts, "api_key should be in all facts"
        print(f"✓ Step 3: All facts retrieved: {list(all_facts.keys())}")
        
        # Step 5: Test category filtering
        config_facts = flushed_manager.get_all_facts(category="config")
        assert "api_key" in config_facts, "api_key should be in 'config' category"
        print(f"✓ Step 4: Category filtering works (config: {list(config_facts.keys())})")
        
        print("\n✅ CORRECTION TEST PASSED")
        print("   - Facts persisted to memory.db")
        print("   - Facts survive context flush")
        print("   - Fact retrieval works correctly")
        print("   - Category filtering functional")
    
    # ========================================================================
    # TEST 3: Auto-Logging Test
    # ========================================================================
    
    def test_auto_logging_enabled(self, memory_manager):
        """
        Test that auto-logging captures all agent actions.
        
        Flow:
        1. Execute several actions
        2. Verify LOG.md has entries for each
        3. Verify log_metadata table updated
        """
        print("\n" + "="*70)
        print("TEST: Auto-Logging Verification")
        print("="*70)
        
        # Step 1: Simulate various agent actions
        memory_manager.append_log("TOOL_USE", "Created file test.txt")
        memory_manager.append_log("THOUGHT", "Analyzing next steps")
        memory_manager.append_log("USER_FEEDBACK", "User requested status update")
        
        print("✓ Step 1: Logged 3 different entry types")
        
        # Step 2: Verify LOG.md contains all entries
        self.verify_log_entry_type(memory_manager, "TOOL_USE")
        self.verify_log_entry_type(memory_manager, "THOUGHT")
        self.verify_log_entry_type(memory_manager, "USER_FEEDBACK")
        print("✓ Step 2: All entry types found in LOG.md")
        
        # Step 3: Verify entries have timestamps
        log_content = memory_manager.read_log()
        
        # Check for ISO timestamp format (YYYY-MM-DD)
        import re
        timestamps = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', log_content)
        assert len(timestamps) >= 3, f"Should have at least 3 timestamps, found {len(timestamps)}"
        print(f"✓ Step 3: Found {len(timestamps)} timestamps in LOG.md")
        
        # Step 4: Verify metadata stored in database
        import sqlite3
        conn = sqlite3.connect(str(memory_manager.db_file))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM log_metadata")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count >= 3, f"Should have at least 3 log metadata entries, found {count}"
        print(f"✓ Step 4: Found {count} entries in log_metadata table")
        
        print("\n✅ AUTO-LOGGING TEST PASSED")
        print("   - All log entries captured")
        print("   - Timestamps present")
        print("   - Metadata tracked in database")
    
    # ========================================================================
    # TEST 4: Context Injection Test
    # ========================================================================
    
    def test_context_injection_in_prompts(self, memory_manager):
        """
        Test that memory context is properly formatted for LLM prompts.
        
        Flow:
        1. Populate NOW.md, LOG.md, and facts
        2. Call format_context_for_prompt()
        3. Verify all sections present
        """
        print("\n" + "="*70)
        print("TEST: Context Injection in Prompts")
        print("="*70)
        
        # Step 1: Populate all memory tiers
        memory_manager.update_now(
            new_status="Testing context injection",
            next_steps=["Verify formatted output"]
        )
        
        memory_manager.append_log("SYSTEM", "Context injection test started")
        memory_manager.save_fact("user_name", "Test User", category="personal")
        
        print("✓ Step 1: Populated NOW.md, LOG.md, and facts")
        
        # Step 2: Get formatted context
        formatted_context = memory_manager.format_context_for_prompt()
        
        print(f"\n📄 Formatted Context ({len(formatted_context)} chars):")
        print("-" * 70)
        print(formatted_context[:500] + "..." if len(formatted_context) > 500 else formatted_context)
        print("-" * 70)
        
        # Step 3: Verify sections present
        assert "CURRENT MENTAL STATE" in formatted_context, "Should have NOW section"
        assert "RECENT ACTIVITY LOG" in formatted_context, "Should have LOG section"
        assert "KNOWN USER FACTS" in formatted_context, "Should have FACTS section"
        print("✓ Step 2: All required sections present")
        
        # Step 4: Verify content in each section
        assert "Testing context injection" in formatted_context, "NOW content should be present"
        assert "Context injection test started" in formatted_context, "LOG content should be present"
        assert "user_name" in formatted_context, "Facts should be present"
        print("✓ Step 3: All content properly included")
        
        # Step 5: Test read_context() method
        context_dict = memory_manager.read_context()
        
        assert "now" in context_dict, "Context dict should have 'now'"
        assert "log" in context_dict, "Context dict should have 'log'"
        assert "facts" in context_dict, "Context dict should have 'facts'"
        print("✓ Step 4: read_context() returns proper structure")
        
        print("\n✅ CONTEXT INJECTION TEST PASSED")
        print("   - Context properly formatted")
        print("   - All sections included")
        print("   - Ready for LLM prompt injection")
    
    # ========================================================================
    # TEST 5: Self-Annealing Error Recovery
    # ========================================================================
    
    def test_self_annealing_error_recovery(self, memory_manager):
        """
        Test that errors are logged and recovery steps added to NOW.md.
        
        Spec: MEMORY_SYSTEM.md lines 292-312
        
        Flow:
        1. Simulate an error occurring
        2. Log error to memory (as engine.py does)
        3. Update NOW.md with recovery steps
        4. Verify both LOG and NOW updated correctly
        """
        print("\n" + "="*70)
        print("TEST: Self-Annealing Error Recovery")
        print("="*70)
        
        # Step 1: Simulate an error
        error_message = "FileNotFoundError: /invalid/path.txt not found"
        error_traceback = "Traceback (most recent call last):\n  File 'test.py', line 10\n    open('/invalid/path.txt')\nFileNotFoundError: [Errno 2] No such file or directory"
        
        # Step 2: Log error (mimicking engine.py error handling)
        memory_manager.append_log(
            entry_type="ERROR",
            content=f"Error during execution: {error_message}",
            metadata={"traceback": error_traceback}
        )
        
        self.verify_log_entry_type(memory_manager, "ERROR")
        self.verify_log_contains(memory_manager, error_message)
        print("✓ Step 1: Error logged to LOG.md with traceback")
        
        # Step 3: Update NOW.md with recovery steps (mimicking engine.py)
        memory_manager.update_now(
            new_status="Error encountered - Recovery needed",
            next_steps=[
                "Review error in LOG.md",
                "Analyze root cause",
                "Implement fix"
            ]
        )
        
        self.verify_now_contains(memory_manager, "Error encountered")
        self.verify_now_contains(memory_manager, "Review error in LOG.md")
        print("✓ Step 2: NOW.md updated with recovery steps")
        
        # Step 4: Verify agent can read error state after restart
        print("\n🔄 Simulating restart to verify error state persists...")
        
        restarted_manager = MemoryManager(
            memory_manager.agent_name,
            base_path=memory_manager.base_path.parent / memory_manager.agent_name
        )
        
        now_content = restarted_manager.read_now()
        assert "Error encountered" in now_content, "Restarted agent should see error state"
        assert "Review error in LOG.md" in now_content, "Recovery steps should be visible"
        print("✓ Step 3: Restarted agent can see error state")
        
        # Step 5: Verify error details in LOG
        log_content = restarted_manager.read_log()
        assert "ERROR" in log_content, "Error entry should be in LOG"
        assert error_message in log_content, "Error message should be in LOG"
        print("✓ Step 4: Error details preserved in LOG.md")
        
        print("\n✅ SELF-ANNEALING TEST PASSED")
        print("   - Errors logged with full context")
        print("   - NOW.md updated with recovery plan")
        print("   - State persists across restart")
        print("   - Agent can resume error recovery")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
