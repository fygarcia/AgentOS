"""
Memory Initializer - Initialize memory structure for new agents

Usage:
    from core.memory_initializer import initialize_agent_memory
    initialize_agent_memory("finn")
    
Or from command line:
    python core/memory_initializer.py --agent finn
"""

from pathlib import Path
from typing import Optional
import sys


def initialize_agent_memory(
    agent_name: str, 
    base_path: Optional[Path] = None,
    force: bool = False
) -> bool:
    """
    Initialize memory structure for an agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'finn', 'code-agent')
        base_path: Base path for agent (defaults to ./<agent_name>)
        force: If True, reinitialize even if memory exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import MemoryManager here to avoid circular imports
        from core.memory_manager import MemoryManager
        
        # UPDATE: Default path is now ./agents/<agent_name>
        base_path = base_path or Path(f"./agents/{agent_name}")
        memory_path = base_path / "memory"
        
        # Check if already initialized
        if memory_path.exists() and not force:
            print(f"Memory already initialized for agent '{agent_name}' at {memory_path}")
            print("Use --force to reinitialize")
            return False
        
        print(f"Initializing memory for agent '{agent_name}'...")
        
        # Create MemoryManager (this will auto-initialize)
        manager = MemoryManager(agent_name, base_path)
        
        # Verify all components created
        components = {
            'NOW.md': manager.now_file,
            'LOG.md': manager.log_file,
            'memory.db': manager.db_file,
            'chroma_db': manager.chroma_path
        }
        
        print("\n✓ Memory structure created:")
        for name, path in components.items():
            status = "✓" if path.exists() else "✗"
            print(f"  {status} {name}: {path}")
        
        # Write initial status
        manager.update_now(
            new_status="Initialized and ready",
            next_steps=["Awaiting first user input"]
        )
        
        print(f"\n✓ Successfully initialized memory for '{agent_name}'")
        print(f"  Location: {memory_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR initializing memory: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Command-line interface for memory initialization."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Initialize memory structure for an AgentOS agent"
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (e.g., finn, code-agent)"
    )
    parser.add_argument(
        "--path",
        type=Path,
        help="Base path for agent (defaults to ./<agent-name>)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinitialization even if memory exists"
    )
    
    args = parser.parse_args()
    
    success = initialize_agent_memory(
        agent_name=args.agent,
        base_path=args.path,
        force=args.force
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
