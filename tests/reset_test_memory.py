"""
Utility to reset/clean memory for test agents.

Use this to clean up memory from test runs.
"""

import shutil
from pathlib import Path


def reset_agent_memory(agent_name: str, base_path: str = "."):
    """
    Reset all memory for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'test_agent', 'agent1')
        base_path: Base path where agent folders are located
    """
    agent_path = Path(base_path) / agent_name
    
    if not agent_path.exists():
        print(f"Agent '{agent_name}' has no memory folder - nothing to reset")
        return
    
    print(f"Resetting memory for agent: {agent_name}")
    print(f"  Location: {agent_path}")
    
    # Remove the entire agent folder
    try:
        shutil.rmtree(agent_path)
        print(f"  ✅ Memory reset complete for '{agent_name}'")
    except Exception as e:
        print(f"  ❌ Error resetting memory: {e}")


def reset_all_test_memory(base_path: str = "."):
    """
    Reset memory for all test agents (test_agent, agent1, agent2, legacy_test).
    
    Args:
        base_path: Base path where agent folders are located
    """
    test_agents = ["test_agent", "agent1", "agent2", "legacy_test"]
    
    print("="*60)
    print("RESETTING ALL TEST AGENT MEMORY")
    print("="*60)
    
    for agent in test_agents:
        reset_agent_memory(agent, base_path)
    
    print("="*60)
    print("✅ All test memory reset complete")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            reset_all_test_memory()
        else:
            reset_agent_memory(sys.argv[1])
    else:
        print("\nUsage:")
        print("  python reset_test_memory.py --all          # Reset all test agents")
        print("  python reset_test_memory.py <agent_name>   # Reset specific agent")
        print("\nExample:")
        print("  python reset_test_memory.py test_agent")
