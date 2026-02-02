import sys
import os

# Allow running directly (fixes ModuleNotFoundError when running `python core/engine.py`)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.graph import create_graph
from core.state import AgentState
from core.observability import init_observability, get_tracer

def run_agent(intent: str, agent_name: str = "default"):
    """
    Main entry point for the agentic OS.
    Creates the graph and runs it with the given user intent.
    
    Args:
        intent: User's request/intent
        agent_name: Name of the agent handling this request (default: "default")
    """
    # Initialize observability
    init_observability()
    
    print(f"\n=== Agentic OS: Processing Intent ===")
    print(f"Agent: {agent_name}")
    print(f"Intent: {intent}\n")
    
    # Start tracing
    tracer = get_tracer()
    tracer.start_trace("Agent Execution", metadata={
        "intent": intent,
        "agent": agent_name
    })
    
    # Initialize memory manager for this agent
    from core.memory_manager import MemoryManager
    memory_manager = MemoryManager(agent_name)
    
    # Read memory context (NOW + LOG + facts)
    memory_context = memory_manager.format_context_for_prompt()
    
    # Log the incoming intent
    memory_manager.append_log(
        entry_type="USER_FEEDBACK",
        content=f"User intent: {intent}"
    )
    
    # Create the graph
    app = create_graph()
    
    # Initialize state with memory
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": intent}],
        "plan": [],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None,
        "memory_context": memory_context,
        "agent_name": agent_name,
        "auto_log_enabled": True
    }
    
    # Run the graph
    try:
        result = app.invoke(initial_state)
        print(f"\n=== Execution Complete ===")
        print(f"Final State: {result}")
        
        # Log completion to memory
        if result.get("final_response"):
            memory_manager.append_log(
                entry_type="SYSTEM",
                content=f"Task completed. Response: {result['final_response'][:200]}..."
            )
        
        # Update status: task complete
        memory_manager.update_now(
            new_status="Idle - Task completed",
            next_steps=["Awaiting next user input"]
        )
        
        # End trace successfully
        tracer.end_trace(status="success")
        tracer.save_traces()
        
        return result
    except Exception as e:
        print(f"\n=== Error ===")
        print(f"{e}")
        
        # Self-Annealing: Log error to memory
        import traceback
        error_trace = traceback.format_exc()
        
        memory_manager.append_log(
            entry_type="ERROR",
            content=f"Error during execution: {str(e)}",
            metadata={"traceback": error_trace}
        )
        
        # Update status with error info
        memory_manager.update_now(
            new_status="Error encountered - Recovery needed",
            next_steps=[
                "Review error in LOG.md",
                "Analyze root cause",
                "Implement fix"
            ]
        )
        
        # End trace with error
        tracer.end_trace(status="error")
        tracer.save_traces()
        
        return None


def run_agent_with_instance(intent: str, agent_instance):
    """
    Run the agentic OS with a specific Agent instance.
    
    This function enables the Agent.run() integration by accepting an Agent
    instance and injecting it into the workflow state. The Agent's skill
    registry and configuration become available to all nodes (Planner, Actor, Auditor).
    
    Args:
        intent: User's request/intent
        agent_instance: Agent object with initialized SkillRegistry
        
    Returns:
        Result dictionary from graph execution
        
    Example:
        >>> from core.agent import Agent
        >>> finn = Agent("finn")
        >>> result = run_agent_with_instance("Analyze portfolio", finn)
    """
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from core.agent import Agent
        
    # Initialize observability
    init_observability()
    
    agent_name = agent_instance.name
    
    print(f"\n=== Agentic OS: Processing Intent (Agent Instance) ===")
    print(f"Agent: {agent_name}")
    print(f"Intent: {intent}\n")
    
    # Start tracing
    tracer = get_tracer()
    tracer.start_trace("Agent Execution (Instance)", metadata={
        "intent": intent,
        "agent": agent_name,
        "using_agent_instance": True
    })
    
    # Initialize memory manager for this agent
    from core.memory_manager import MemoryManager
    memory_manager = MemoryManager(agent_name)
    
    # Read memory context (NOW + LOG + facts)
    memory_context = memory_manager.format_context_for_prompt()
    
    # Log the incoming intent
    memory_manager.append_log(
        entry_type="USER_FEEDBACK",
        content=f"User intent: {intent}"
    )
    
    # Create the graph
    app = create_graph()
    
    # Initialize state with memory AND agent instance
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": intent}],
        "plan": [],
        "current_step_index": 0,
        "tool_outputs": {},
        "final_response": None,
        "memory_context": memory_context,
        "agent_name": agent_name,
        "auto_log_enabled": True,
        "agent_instance": agent_instance  # NEW: Pass agent instance to nodes
    }
    
    # Run the graph
    try:
        result = app.invoke(initial_state)
        print(f"\n=== Execution Complete ===")
        print(f"Final State: {result}")
        
        # Log completion to memory
        if result.get("final_response"):
            memory_manager.append_log(
                entry_type="SYSTEM",
                content=f"Task completed. Response: {result['final_response'][:200]}..."
            )
        
        # Update status: task complete
        memory_manager.update_now(
            new_status="Idle - Task completed",
            next_steps=["Awaiting next user input"]
        )
        
        # End trace successfully
        tracer.end_trace(status="success")
        tracer.save_traces()
        
        return result
    except Exception as e:
        print(f"\n=== Error ===")
        print(f"{e}")
        
        # Self-Annealing: Log error to memory
        import traceback
        error_trace = traceback.format_exc()
        
        memory_manager.append_log(
            entry_type="ERROR",
            content=f"Error during execution: {str(e)}",
            metadata={"traceback": error_trace}
        )
        
        # Update status with error info
        memory_manager.update_now(
            new_status="Error encountered - Recovery needed",
            next_steps=[
                "Review error in LOG.md",
                "Analyze root cause",
                "Implement fix"
            ]
        )
        
        # End trace with error
        tracer.end_trace(status="error")
        tracer.save_traces()
        
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AgentOS with a given intent")
    parser.add_argument("intent", nargs="+", help="The user's intent/request")
    parser.add_argument("--agent", default="default", help="Agent name (default: default)")
    
    args = parser.parse_args()
    
    intent = " ".join(args.intent)
    run_agent(intent, agent_name=args.agent)
