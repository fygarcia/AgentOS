"""
Log Activity - Append entry to LOG.md

This tool appends a timestamped entry to the activity log.
Use this when:
- Executing a tool/action
- Recording a thought or reasoning step
- Logging user feedback
- Recording errors or system events
"""

from typing import Optional, Dict, Any
from pathlib import Path


SKILL_METADATA = {
    "name": "log_activity",
    "version": "1.0.0",
    "description": "Append entry to activity log (LOG.md)",
    "agent": "core",
    "category": "memory",
    
    "parameters": {
        "agent_name": {
            "type": "str",
            "required": True,
            "description": "Name of the agent"
        },
        "entry_type": {
            "type": "str",
            "required": True,
            "description": "Type of entry: TOOL_USE, THOUGHT, USER_FEEDBACK, ERROR, SYSTEM"
        },
        "content": {
            "type": "str",
            "required": True,
            "description": "Content of the log entry"
        },
        "metadata": {
            "type": "dict",
            "required": False,
            "default": None,
            "description": "Optional metadata to attach to entry"
        }
    },
    
    "returns": {
        "type": "bool",
        "description": "True if successful, False otherwise"
    },
    
    "examples": [
        {
            "input": {
                "agent_name": "finn",
                "entry_type": "TOOL_USE",
                "content": "Created file hello.txt",
                "metadata": {"file": "hello.txt", "size": 42}
            },
            "output": True,
            "description": "Log a tool execution"
        },
        {
            "input": {
                "agent_name": "finn",
                "entry_type": "THOUGHT",
                "content": "Need to validate data before processing"
            },
            "output": True,
            "description": "Log a reasoning step"
        }
    ],
    
    "tags": ["memory", "warm", "log", "activity"]
}


def execute(
    agent_name: str,
    entry_type: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    base_path: Optional[Path] = None
) -> bool:
    """
    Append entry to LOG.md.
    
    Args:
        agent_name: Name of the agent
        entry_type: TOOL_USE, THOUGHT, USER_FEEDBACK, ERROR, SYSTEM
        content: Log entry content
        metadata: Optional metadata dict
        base_path: Optional base path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from core.memory_manager import MemoryManager
        
        # Validate entry type
        valid_types = ["TOOL_USE", "THOUGHT", "USER_FEEDBACK", "ERROR", "SYSTEM"]
        if entry_type not in valid_types:
            print(f"WARNING: Invalid entry_type '{entry_type}'. Using 'SYSTEM'.")
            entry_type = "SYSTEM"
        
        manager = MemoryManager(agent_name, base_path)
        return manager.append_log(entry_type, content, metadata)
        
    except Exception as e:
        print(f"ERROR in log_activity: {e}")
        return False
