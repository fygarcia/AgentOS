"""
Update Status - Update NOW.md with current objective and next steps

This tool overwrites NOW.md to reflect the agent's current focus.
Use this when:
- Starting a new task
- Completing a major step
- Pivoting to a different objective
"""

from typing import List, Optional
from pathlib import Path


SKILL_METADATA = {
    "name": "update_status",
    "version": "1.0.0",
    "description": "Update NOW.md with current objective and next steps",
    "agent": "core",  # Core AgentOS skill
    "category": "memory",
    
    "parameters": {
        "agent_name": {
            "type": "str",
            "required": True,
            "description": "Name of the agent (e.g., 'finn')"
        },
        "new_status": {
            "type": "str",
            "required": True,
            "description": "Current objective or goal"
        },
        "next_steps": {
            "type": "list",
            "required": False,
            "default": None,
            "description": "List of next actions to take"
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
                "new_status": "Analyzing portfolio performance",
                "next_steps": ["Load data", "Calculate metrics", "Generate report"]
            },
            "output": True,
            "description": "Update status with new objective and steps"
        }
    ],
    
    "tags": ["memory", "hot", "status", "now"]
}


def execute(
    agent_name: str,
    new_status: str,
    next_steps: Optional[List[str]] = None,
    base_path: Optional[Path] = None
) -> bool:
    """
    Update NOW.md with current status and next steps.
    
    Args:
        agent_name: Name of the agent
        new_status: Current objective/goal
        next_steps: Optional list of next actions
        base_path: Optional base path (defaults to ./<agent_name>)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from core.memory_manager import MemoryManager
        
        manager = MemoryManager(agent_name, base_path)
        return manager.update_now(new_status, next_steps)
        
    except Exception as e:
        print(f"ERROR in update_status: {e}")
        return False
