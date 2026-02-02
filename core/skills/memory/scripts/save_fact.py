"""
Save Fact - Store user preference or information in SQLite

This tool saves structured user facts for quick retrieval.
Use this when:
- User provides personal information (name, preferences, etc.)
- User provides configuration (API keys, settings, etc.)
- Any information that should be permanently remembered
"""

from typing import Optional
from pathlib import Path


SKILL_METADATA = {
    "name": "save_fact",
    "version": "1.0.0",
    "description": "Save user fact or preference to SQLite database",
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
            "description": "Fact identifier (e.g., 'user_name', 'api_key')"
        },
        "value": {
            "type": "str",
            "required": True,
            "description": "Fact value"
        },
        "category": {
            "type": "str",
            "required": False,
            "default": "general",
            "description": "Category: general, preference, personal, config"
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
                "key": "user_name",
                "value": "Felipe",
                "category": "personal"
            },
            "output": True,
            "description": "Save user's name"
        },
        {
            "input": {
                "agent_name": "finn",
                "key": "api_key",
                "value": "12345",
                "category": "config"
            },
            "output": True,
            "description": "Save API key"
        }
    ],
    
    "tags": ["memory", "facts", "sqlite", "user", "preferences"]
}


def execute(
    agent_name: str,
    key: str,
    value: str,
    category: str = "general",
    base_path: Optional[Path] = None
) -> bool:
    """
    Save user fact to SQLite database.
    
    Args:
        agent_name: Name of the agent
        key: Fact identifier
        value: Fact value
        category: Category (general, preference, personal, config)
        base_path: Optional base path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from core.memory_manager import MemoryManager
        
        # Validate category
        valid_categories = ["general", "preference", "personal", "config"]
        if category not in valid_categories:
            print(f"WARNING: Invalid category '{category}'. Using 'general'.")
            category = "general"
        
        manager = MemoryManager(agent_name, base_path)
        return manager.save_fact(key, value, category)
        
    except Exception as e:
        print(f"ERROR in save_fact: {e}")
        return False
