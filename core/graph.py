from langgraph.graph import StateGraph, END
from core.state import AgentState
from core.nodes.planner import planner_node
from core.nodes.actor import actor_node
from core.nodes.auditor import auditor_node
from core.nodes.classifier import classifier_node
from core.nodes.responder import responder_node

def route_intent(state: AgentState):
    """
    Router for the classifier output.
    Routes to 'planner' for tasks, or 'responder' for questions/chat.
    """
    intent = state.get("intent_type", "TASK")
    
    if intent == "TASK":
        return "planner"
    else:
        return "responder"

def route_step(state: AgentState):
    """
    Router function to determine which node to execute next.
    Checks the current step's role and routes accordingly.
    """
    idx = state.get("current_step_index", 0)
    plan = state.get("plan", [])
    
    # If all steps are complete, end
    if idx >= len(plan):
        return END
    
    # Get current step's role
    step = plan[idx]
    role = step.get("role")
    
    if role == "Actor":
        return "actor"
    elif role == "Auditor":
        return "auditor"
    else:
        # Unknown role, skip
        return END

def create_graph():
    """
    Creates and compiles the LangGraph StateGraph for the agent.
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("actor", actor_node)
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("responder", responder_node)
    
    # Set entry point
    workflow.set_entry_point("classifier")
    
    # Add edges
    
    # 1. Classifier -> (Planner OR Responder)
    workflow.add_conditional_edges(
        "classifier",
        route_intent,
        {
            "planner": "planner",
            "responder": "responder"
        }
    )
    
    # 2. Responder -> END
    workflow.add_edge("responder", END)
    
    # 3. Planner -> Actor/Auditor (via route_step)
    workflow.add_conditional_edges("planner", route_step)
    
    # 4. Step execution loop
    workflow.add_conditional_edges("actor", route_step)
    workflow.add_conditional_edges("auditor", route_step)
    
    # Compile the graph
    app = workflow.compile()
    return app
