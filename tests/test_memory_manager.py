"""
Test Memory Manager - Unit tests for the memory management system

Tests all three memory tiers:
- HOT (NOW.md)
- WARM (LOG.md)
- COLD (ChromaDB - if available)
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import os

from core.memory_manager import MemoryManager


class TestMemoryManager:
    """Test suite for MemoryManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = Path(tempfile.mkdtemp())
        yield temp
        # Cleanup
        if temp.exists():
            shutil.rmtree(temp)
    
    @pytest.fixture
    def memory_manager(self, temp_dir):
        """Create a MemoryManager instance for testing."""
        return MemoryManager("test_agent", base_path=temp_dir / "test_agent")
    
    def test_initialization(self, memory_manager):
        """Test that memory structure is created correctly."""
        assert memory_manager.now_file.exists()
        assert memory_manager.log_file.exists()
        assert memory_manager.db_file.exists()
        
        # Check initial content
        now_content = memory_manager.read_now()
        assert "Status: Idle" in now_content
    
    def test_update_now(self, memory_manager):
        """Test updating NOW.md."""
        success = memory_manager.update_now(
            new_status="Testing memory system",
            next_steps=["Run tests", "Verify functionality"]
        )
        
        assert success is True
        
        # Read back and verify
        content = memory_manager.read_now()
        assert "Testing memory system" in content
        assert "Run tests" in content
        assert "Verify functionality" in content
    
    def test_append_log(self, memory_manager):
        """Test appending to LOG.md."""
        success = memory_manager.append_log(
            entry_type="TOOL_USE",
            content="Created test file",
            metadata={"file": "test.txt"}
        )
        
        assert success is True
        
        # Read back and verify
        log_content = memory_manager.read_log()
        assert "TOOL_USE" in log_content
        assert "Created test file" in log_content
    
    def test_save_and_get_fact(self, memory_manager):
        """Test saving and retrieving user facts."""
        # Save fact
        success = memory_manager.save_fact(
            key="test_key",
            value="test_value",
            category="general"
        )
        assert success is True
        
        # Retrieve fact
        value = memory_manager.get_fact("test_key")
        assert value == "test_value"
        
        # Test non-existent key
        none_value = memory_manager.get_fact("nonexistent")
        assert none_value is None
    
    def test_get_all_facts(self, memory_manager):
        """Test retrieving all facts."""
        # Save multiple facts
        memory_manager.save_fact("fact1", "value1", "category1")
        memory_manager.save_fact("fact2", "value2", "category2")
        memory_manager.save_fact("fact3", "value3", "category1")
        
        # Get all facts
        all_facts = memory_manager.get_all_facts()
        assert len(all_facts) == 3
        assert all_facts["fact1"] == "value1"
        
        # Get facts by category
        category1_facts = memory_manager.get_all_facts(category="category1")
        assert len(category1_facts) == 2
    
    def test_context_reading(self, memory_manager):
        """Test reading full context."""
        # Setup: Update NOW and LOG
        memory_manager.update_now("Working on tests")
        memory_manager.append_log("THOUGHT", "Testing context reading")
        memory_manager.save_fact("user_name", "Test User")
        
        # Read context
        context = memory_manager.read_context()
        
        assert "now" in context
        assert "log" in context
        assert "facts" in context
        
        # Check content
        assert "Working on tests" in context["now"]
        assert "Testing context reading" in context["log"]
        assert "user_name" in context["facts"]
    
    def test_formatted_context_for_prompt(self, memory_manager):
        """Test formatted context for LLM prompts."""
        memory_manager.update_now("Active task")
        memory_manager.append_log("SYSTEM", "System started")
        
        formatted = memory_manager.format_context_for_prompt()
        
        assert "CURRENT MENTAL STATE" in formatted
        assert "RECENT ACTIVITY LOG" in formatted
        assert "Active task" in formatted
    
    def test_agent_isolation(self, temp_dir):
        """Test that different agents have isolated memory."""
        agent1 = MemoryManager("agent1", base_path=temp_dir / "agent1")
        agent2 = MemoryManager("agent2", base_path=temp_dir / "agent2")
        
        # Each agent updates their own memory
        agent1.save_fact("key", "agent1_value")
        agent2.save_fact("key", "agent2_value")
        
        # Verify isolation
        assert agent1.get_fact("key") == "agent1_value"
        assert agent2.get_fact("key") == "agent2_value"
        
        # Verify different directories
        assert agent1.memory_path != agent2.memory_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
