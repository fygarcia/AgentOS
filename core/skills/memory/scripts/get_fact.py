"""
Get Fact - Retrieve user fact from SQLite

This tool retrieves previously saved user facts.
Use this when:
- Need to access user preferences
- Need to retrieve configuration values
- Looking for specific user information
"""

from typing import Optional
from pathlib import Path


SKILL_METADATA = {
    "name": "get_fact",
    "version": "1.0.0",
    "description": "Retrieve user fact from SQLite database",
    "agent": "core",
    "category": "memory",
    
    "parameters": {
        "agent_name": {
            "type": "str",
            "required": True,
            "description": "Name of the agent"
        },
        "key": {
            "type": "str",
            "required": True,
            "description": "Fact identifier to retrieve"
        }
    },
    
    "returns": {
        "type": "str",
        "description": "Fact value or None if not found"
    },
    
    "examples": [
        {
            "input": {
                "agent_name": "finn",
                "key": "user_name"
            },
            "output": "Felipe",
            "description": "Retrieve user's name"
        },
        {
            "input": {
                "agent_name": "finn",
                "key": "nonexistent_key"
            },
            "output": None,
            "description": "Key not found returns None"
        }
    ],
    
    "tags": ["memory", "facts", "sqlite", "user", "retrieve"]
}


def execute(
    agent_name: str,
    key: str,
    base_path: Optional[Path] = None
) -> Optional[str]:
    """
    Retrieve user fact by key.
    
    Args:
        agent_name: Name of the agent
        key: Fact identifier
        base_path: Optional base path
        
    Returns:
        Fact value or None if not found
    """
    try:
        from core.memory_manager import MemoryManager
        
        manager = MemoryManager(agent_name, base_path)
        return manager.get_fact(key)
        
    except Exception as e:
        print(f"ERROR in get_fact: {e}")
        return None
