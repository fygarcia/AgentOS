"""
Recall Memory - Search semantic long-term memory (ChromaDB)

This tool performs vector similarity search on cold memory.
Use this when:
- NOW.md and LOG.md don't contain the needed information
- Looking for information from past sessions
- Querying for user facts that may have been mentioned earlier
"""

from typing import List, Dict, Any, Optional
from pathlib import Path


SKILL_METADATA = {
    "name": "recall_memory",
    "version": "1.0.0",
    "description": "Search semantic long-term memory (ChromaDB) for relevant information",
    "agent": "core",
    "category": "memory",
    
    "parameters": {
        "agent_name": {
            "type": "str",
            "required": True,
            "description": "Name of the agent"
        },
        "query": {
            "type": "str",
            "required": True,
            "description": "Search query"
        },
        "n_results": {
            "type": "int",
            "required": False,
            "default": 3,
            "description": "Number of results to return (default: 3)"
        }
    },
    
    "returns": {
        "type": "list",
        "description": "List of relevant memory chunks with metadata and similarity scores"
    },
    
    "examples": [
        {
            "input": {
                "agent_name": "finn",
                "query": "What is the user's API key?",
                "n_results": 3
            },
            "output": [
                {
                    "content": "User provided API key: 12345",
                    "metadata": {"type": "user_fact", "timestamp": "2026-01-15"},
                    "distance": 0.15
                }
            ],
            "description": "Search for specific user information"
        }
    ],
    
    "tags": ["memory", "cold", "semantic", "search", "chromadb"]
}


def execute(
    agent_name: str,
    query: str,
    n_results: int = 3,
    base_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Search cold memory for relevant information.
    
    Args:
        agent_name: Name of the agent
        query: Search query
        n_results: Number of results to return
        base_path: Optional base path
        
    Returns:
        List of memory chunks, each with:
        - content: The memory text
        - metadata: Associated metadata
        - distance: Similarity score (lower is better)
    """
    try:
        from core.memory_manager import MemoryManager
        
        manager = MemoryManager(agent_name, base_path)
        return manager.recall_memory(query, n_results)
        
    except Exception as e:
        print(f"ERROR in recall_memory: {e}")
        return []
