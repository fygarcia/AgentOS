"""
PLANNER NODE - Agentic Workflow Entry Point
============================================

PURPOSE:
First node in the agentic workflow. Analyzes user intent and generates
a detailed, validated execution plan with reasoning and success criteria.

ARCHITECTURE - Two-Stage Pipeline:
┌─────────────────────────────────────────────────────────────┐
│ INPUT: AgentState with user intent                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: 🧠 gpt-oss:20b (Reasoning)                        │
│ - Analyzes intent deeply                                   │
│ - Generates 4500-5000 char reasoning plan                  │
│ - Includes why, what, and success criteria                 │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: 🔧 llama3.1:8b (Parsing)                          │
│ - Structures reasoning into JSON                           │
│ - Validates against Plan schema                            │
│ - Returns 7-8 step validated plan                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: Updated AgentState                                 │
│ - plan: List[dict] (7-8 steps with reasoning)              │
│ - current_step_index: 0                                    │
│ - objective: str                                            │
└─────────────────────────────────────────────────────────────┘

WORKFLOW (Step-by-Step):
1. Extract user intent from state["messages"][0]["content"]
2. Check LLM_PROVIDER (ollama vs other)
3. If ollama:
   a. Create TwoStageOllamaClient
   b. Call generate_with_reasoning()
   c. Receive validated Plan object
   d. Convert to dicts for state
   e. Add observability trace
4. Return updated state with plan

OUTPUT STRUCTURE:
Each plan step contains:
- role: "Actor" or "Auditor"
- instruction: Clear action to take
- reasoning: Why this step is needed (from gpt-oss reasoning)
- expected_outcome: Success criteria

OBSERVABILITY:
Traces capture:
- reasoning_model: gpt-oss:20b
- parser_model: llama3.1:8b
- objective: Plan goal
- num_steps: 7-8 typically
- has_reasoning: true

PRODUCTION STATUS: ✅ Tested and working
PERFORMANCE: ~120-160 seconds total (reasoning + parsing)
NEXT NODE: Actor (executes first step)
"""

from core.state import AgentState
from core.models import Plan
from core.two_stage_client import TwoStageOllamaClient
from core.observability import get_tracer
from core.config import config
from core.skill_registry import SkillRegistry

# ============================================================================
# PLANNER NODE
# ============================================================================

def planner_node(state: AgentState, registry: SkillRegistry = None):
    """
    Planner node - analyzes user intent and creates execution plan.
    
    Args:
        state: Current agent state
        registry: SkillRegistry instance (deprecated, use state["agent_instance"] instead)
        
    Returns:
        Updated state with plan
    """
    print("\n[Node] PLANNER: Analyzing intent...")
    
    tracer = get_tracer()
    
    # Get the user intent
    user_intent = state["messages"][0]["content"]
    
    # Use centralized configuration
    provider = config.LLM_PROVIDER
    
    # Get registry from agent_instance if available (NEW)
    agent_instance = state.get("agent_instance")
    if agent_instance:
        registry = agent_instance.registry
        print(f"[Planner] Using Agent '{agent_instance.name}' with {len(registry.get_all_skills())} skills")
    elif registry is None:
        # Fallback: create temporary registry
        print("[Planner] Warning: No agent_instance or registry provided, creating temporary registry")
        registry = SkillRegistry(agent_name="finn")
        registry.initialize()
    
    # Get available skills for context
    skills_context = registry.get_skill_prompt_context()
    
    if provider == "ollama":
        # Two-stage approach: reasoning + parsing
        reasoning_model = config.REASONING_MODEL
        parser_model = config.PARSER_MODEL
        
        print(f"[Planner] 🧠 Reasoning: {reasoning_model}")
        print(f"[Planner] 🔧 Parser: {parser_model}")
        print(f"[Planner] 🛠️  Available Skills: {len(registry.get_all_skills())}")
        
        # Get memory context from state
        memory_context = state.get("memory_context", "")
        
        # Enhanced system prompt with skill awareness AND memory context
        system_prompt = f"""You are an expert planning assistant. Create detailed, well-reasoned execution plans.

{skills_context}

When creating plans, you can reference these skills by name in your instructions.
The Actor will be able to execute these skills directly.

{memory_context}

Use the above memory context to understand:
1. What you're currently working on (NOW.md)
2. What you've done recently (LOG.md)
3. Any user facts or preferences

If the user says "continue" or similar, check NOW.md to see what you should resume."""
        
        try:
            client = TwoStageOllamaClient()
            
            plan_obj = client.generate_with_reasoning(
                reasoning_model=reasoning_model,
                parser_model=parser_model,
                prompt=user_intent,
                schema=Plan,
                system_prompt=system_prompt
            )
            
            print(f"\n[Planner] ✅ Generated {len(plan_obj.plan)} steps with full reasoning")
            
            # Trace the planning
            tracer.add_span(
                span_name="Planner.two_stage_generation",
                span_type="agent",
                details={
                    "reasoning_model": reasoning_model,
                    "parser_model": parser_model,
                    "objective": plan_obj.objective,
                    "num_steps": len(plan_obj.plan),
                    "has_reasoning": any(step.reasoning for step in plan_obj.plan)
                }
            )
            
            # Convert to dicts for state
            plan_dicts = [
                {
                    "role": step.role,
                    "instruction": step.instruction,
                    "reasoning": step.reasoning,
                    "expected_outcome": step.expected_outcome
                }
                for step in plan_obj.plan
            ]
            
            return {
                "plan": plan_dicts,
                "current_step_index": 0,
                "objective": plan_obj.objective
            }
            
        except Exception as e:
            print(f"[Planner] ❌ Error: {e}")
            
            tracer.add_span(
                span_name="Planner.two_stage_generation",
                span_type="agent",
                details={
                    "reasoning_model": reasoning_model,
                    "parser_model": parser_model,
                    "error": str(e),
                    "status": "error"
                }
            )
            
            return {"plan": []}
    else:
        # Fallback for other providers
        from core.llm_pydantic import get_pydantic_agent
        
        agent = get_pydantic_agent("Planner", Plan, "Generate execution plan")
        result = agent.run_sync(user_intent)
        
        plan = result.output.plan if hasattr(result.output, 'plan') else []
        plan_dicts = [{"role": step.role, "instruction": step.instruction} for step in plan]
        
        return {"plan": plan_dicts, "current_step_index": 0}
