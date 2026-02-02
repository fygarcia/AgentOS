"""
Agent Class for AgentOS
=======================

Represents an individual agent instance with its own configuration,
skill registry, and execution context.

Each agent (e.g., Finn) is an instance of this class and maintains:
- Agent identity (name, description)
- Skill registry (core + agent-specific skills)
- Configuration
- State management

Usage:
    finn = Agent(name="finn", description="Financial portfolio agent")
    finn.initialize()
    
    # Access skills
    skill = finn.registry.get_skill("sqlite-crud")
"""

from typing import Optional, List
from pathlib import Path
import sys

# Handle imports for both module and script execution
try:
    from core.skill_registry import SkillRegistry
    from core.config import config
except ImportError:
    # Running as script, add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.skill_registry import SkillRegistry
    from core.config import config


class Agent:
    """
    Represents an agent instance in AgentOS.
    
    Architecture:
    - Each agent has its own SkillRegistry
    - Skills are loaded in layers: core → agent-specific
    - Agent maintains its own state and configuration
    
    Attributes:
        name: Agent identifier (e.g., "finn", "code", "research")
        description: What this agent does
        registry: SkillRegistry instance (core + agent skills)
        config: Agent-specific configuration
    """
    
    def __init__(
        self,
        name: str = None,
        description: str = "",
        auto_initialize: bool = True,
        **kwargs
    ):
        """
        Initialize an agent.
        
        Args:
            name: Agent name (lowercase, used for directory paths)
            description: Brief description of agent's purpose
            auto_initialize: If True, automatically initialize skills
            **kwargs: Compatibility args (e.g., agent_name)
        """
        # Handle param aliases
        if name is None:
            name = kwargs.get("agent_name", "default_agent")
        self.name = name.lower()
        self.description = description
        self.registry = SkillRegistry(agent_name=self.name)
        self._initialized = False
        
        if auto_initialize:
            self.initialize()
    
    def initialize(self) -> None:
        """
        Initialize the agent's skill registry.
        
        Loads:
        1. Core skills from core/skills/
        2. Agent-specific skills from {agent_name}/skills/
        """
        if self._initialized:
            print(f"[Agent:{self.name}] Already initialized")
            return
        
        print(f"[Agent:{self.name}] Initializing...")
        self.registry.initialize()
        self._initialized = True
        
        stats = self.registry.get_stats()
        print(f"[Agent:{self.name}] ✅ Ready with {stats['total_skills']} skills")
    
    def get_skill(self, name: str):
        """Get a skill by name from this agent's registry."""
        return self.registry.get_skill(name)
    
    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """
        List available skill names.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of skill names
        """
        if category:
            skills = self.registry.get_skills_by_category(category)
        else:
            skills = self.registry.get_all_skills()
        
        return [s.name for s in skills]
    
    def execute_skill(self, skill_name: str, **params):
        """
        Execute a skill by name.
        
        Args:
            skill_name: Name of skill to execute
            **params: Parameters to pass to skill
            
        Returns:
            Skill execution result
        """
        return self.registry.execute_skill(skill_name, **params)
    
    def run(self, intent: str) -> dict:
        """
        Execute an intent using the LangGraph orchestration engine.
        
        This is the main entry point for agent execution. It:
        1. Calls the LangGraph engine (Planner→Actor→Auditor)
        2. Injects this agent's skill registry into the workflow
        3. Uses this agent's memory context
        4. Returns the execution result
        
        Args:
            intent: User's request or intent to execute
            
        Returns:
            Dictionary containing execution results with keys:
            - final_response: The final output
            - plan: Generated execution plan
            - tool_outputs: Results from each step
            
        Example:
            >>> finn = Agent("finn")
            >>> result = finn.run("Create a file called test.txt")
            >>> print(result["final_response"])
        """
        # Import here to avoid circular dependency
        from core.engine import run_agent_with_instance
        
        if not self._initialized:
            raise RuntimeError(
                f"Agent '{self.name}' not initialized. "
                "Call agent.initialize() first or set auto_initialize=True"
            )
        
        return run_agent_with_instance(
            intent=intent,
            agent_instance=self
        )
    
    def __repr__(self) -> str:
        status = "initialized" if self._initialized else "not initialized"
        skill_count = len(self.registry.get_all_skills()) if self._initialized else 0
        return f"Agent(name='{self.name}', skills={skill_count}, status={status})"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_finn_agent() -> Agent:
    """
    Create and initialize the Finn agent (financial portfolio management).
    
    Returns:
        Initialized Finn agent
    """
    finn = Agent(
        name="finn",
        description="Financial portfolio management agent with skills for tracking assets, analyzing holdings, and generating reports"
    )
    return finn


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Agent Class Test")
    print("=" * 70)
    
    # Test 1: Create Finn agent
    print("\n[TEST 1] Creating Finn Agent")
    finn = create_finn_agent()
    print(finn)
    
    # Test 2: List skills
    print("\n[TEST 2] Finn's Skills")
    core_skills = [s for s in finn.list_skills() if finn.get_skill(s).is_core]
    agent_skills = [s for s in finn.list_skills() if not finn.get_skill(s).is_core]
    
    print(f"  Core skills: {len(core_skills)}")
    for skill_name in sorted(core_skills):
        skill = finn.get_skill(skill_name)
        print(f"    - {skill_name}: {skill.description[:60]}...")
    
    print(f"\n  Finn-specific skills: {len(agent_skills)}")
    for skill_name in sorted(agent_skills):
        skill = finn.get_skill(skill_name)
        print(f"    - {skill_name}: {skill.description[:60]}...")
    
    # Test 3: Get skill categories
    print("\n[TEST 3] Skills by Category")
    stats = finn.registry.get_stats()
    for category, count in stats['skills_by_category'].items():
        print(f"  - {category}: {count} skills")
    
    print("\n" + "=" * 70)
    print("✅ Agent class working correctly")
    print("=" * 70)
