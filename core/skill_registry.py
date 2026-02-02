"""
Skill Registry System for AgentOS
===================================

Provides dynamic skill discovery, registration, validation, and execution.

Architecture:
- Skills are Python files with SKILL_METADATA dict and execute() function
- Registry scans directories and builds a catalog of available skills
- Planner can discover skills for plan generation
- Actor can execute skills by name

Usage:
    from core.skill_registry import registry
    
    # Scan for skills
    registry.scan_directory("./finn/skills", agent_name="finn")
    
    # Get skill info
    skill = registry.get_skill("db_upsert_asset")
    
    # Execute skill
    result = registry.execute_skill("db_upsert_asset", ticker="AAPL", ...)
"""

import os
import sys
import importlib.util
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
import traceback


@dataclass
class Skill:
    """
    Represents a registered skill with its metadata and execution function.
    """
    name: str
    description: str
    agent: str
    category: str
    module_path: str
    
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    returns: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    
    # NEW: Architecture updates
    is_core: bool = False  # True if this is a core AgentOS skill
    overrides_core: bool = False  # True if this agent skill overrides a core skill
    prompt_instructions: Optional[str] = None  # Instructions from SKILL.md body
    
    # Internal
    _execute_func: Optional[Callable] = None
    
    def execute(self, **params) -> Any:
        """Execute the skill with given parameters."""
        if self._execute_func is None:
            raise RuntimeError(f"Skill {self.name} has no execute function loaded")
        
        # Validate required parameters
        for param_name, param_spec in self.parameters.items():
            if param_spec.get("required", False) and param_name not in params:
                raise ValueError(
                    f"Missing required parameter '{param_name}' for skill '{self.name}'"
                )
        
        # Execute
        try:
            return self._execute_func(**params)
        except Exception as e:
            raise RuntimeError(f"Skill '{self.name}' execution failed: {str(e)}") from e
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "agent": self.agent,
            "category": self.category,
            "version": self.version,
            "is_core": self.is_core,
            "overrides_core": self.overrides_core,
            "parameters": self.parameters,
            "returns": self.returns,
            "examples": self.examples,
            "tags": self.tags,
        }
    
    def __repr__(self) -> str:
        override_marker = " [OVERRIDES CORE]" if self.overrides_core else ""
        core_marker = " [CORE]" if self.is_core else ""
        return f"Skill(name='{self.name}', agent='{self.agent}'{core_marker}{override_marker})"


class SkillRegistry:
    """
    Central registry for all available skills.
    
    Architecture:
    - Each Agent owns its own SkillRegistry instance
    - Layer 0: Core skills (from core/skills/) - universal, all agents
    - Layer 1: Agent skills (from {agent}/skills/) - agent-specific
    - Agent skills can override core skills (explicit)
    
    Responsibilities:
    - Scan directories for skills (SKILL.md + Python files)
    - Load and validate skill metadata
    - Provide skill discovery interface
    - Execute skills safely
    - Track core vs agent skills and overrides
    """
    
    def __init__(self, agent_name: str = "core"):
        """
        Initialize the registry for a specific agent.
        
        Args:
            agent_name: Name of the agent owning this registry (default: "core")
        """
        self.agent_name = agent_name
        self._skills: Dict[str, Skill] = {}
        self._core_skills: Dict[str, Skill] = {}  # Track core skills separately
        self._skills_by_agent: Dict[str, List[str]] = {}
        self._skills_by_category: Dict[str, List[str]] = {}
        self._initialized = False
    
    def initialize(self) -> None:
        """
        Initialize the registry with layered loading.
        
        Loads skills in this order:
        1. Core skills (core/skills/) - Layer 0
        2. Agent skills ({agent_name}/skills/) - Layer 1
        
        Agent skills can override core skills if they have the same name.
        """
        if self._initialized:
            print(f"[SkillRegistry] Already initialized for agent '{self.agent_name}'")
            return
        
        # Layer 0: Core skills (ALWAYS load)
        core_count = self.scan_directory(
            directory="./core/skills",
            agent_name="core",
            is_core=True,
            recursive=True  # Scan subdirectories
        )
        
        # Layer 1: Agent-specific skills (if not core agent)
        agent_count = 0
        if self.agent_name != "core":
            # UPDATE: Agent skills are now in ./agents/<agent_name>/skills
            agent_path = f"./agents/{self.agent_name}/skills"
            if Path(agent_path).exists():
                agent_count = self.scan_directory(
                    directory=agent_path,
                    agent_name=self.agent_name,
                    is_core=False,
                    recursive=True
                )
        
        self._initialized = True
        
        # Report
        total = len(self._skills)
        core_count_final = len(self._core_skills)
        overrides = sum(1 for s in self._skills.values() if s.overrides_core)
        
        print(f"[SkillRegistry] Initialized for agent '{self.agent_name}':")
        print(f"  - Core skills: {core_count_final}")
        print(f"  - Agent skills: {total - core_count_final}")
        print(f"  - Overrides: {overrides}")
        print(f"  - Total available: {total} skills")
    
    def scan_directory(
        self, 
        directory: str, 
        agent_name: str,
        is_core: bool = False,
        recursive: bool = False
    ) -> int:
        """
        Scan directory for skill files and register them.
        
        Supports two formats:
        1. SKILL.md format: skill_name/SKILL.md (Claude Skills format)
        2. Python format: skill_name.py (Legacy format with SKILL_METADATA)
        
        Args:
            directory: Path to skills directory
            agent_name: Name of agent owning these skills
            is_core: Whether these are core skills (Layer 0)
            recursive: Whether to scan subdirectories
            
        Returns:
            Number of skills found and registered
        """
        directory_path = Path(directory).resolve()
        
        if not directory_path.exists():
            if is_core:
                print(f"[SkillRegistry] Warning: Core directory not found: {directory}")
            return 0
        
        if not directory_path.is_dir():
            print(f"[SkillRegistry] Warning: Not a directory: {directory}")
            return 0
        
        count = 0
        
        # Scan for SKILL.md directories (Claude Skills format)
        for item in directory_path.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    try:
                        skill = self._load_skill_from_directory(item, agent_name, is_core)
                        if skill:
                            self.register_skill(skill)
                            count += 1
                    except Exception as e:
                        print(f"[SkillRegistry] Error loading {item.name}/SKILL.md: {e}")
                        if is_core:  # Show traceback for core skills
                            traceback.print_exc()
        
        # Scan for legacy Python files (for backward compatibility)
        pattern = "**/*.py" if recursive else "*.py"
        for py_file in directory_path.glob(pattern):
            # Skip __init__.py and __pycache__
            if py_file.name.startswith("__"):
                continue
            
            # Skip if already loaded from SKILL.md
            skill_name = py_file.stem
            if self.has_skill(skill_name):
                continue
            
            try:
                skill = self._load_skill_from_file(py_file, agent_name, is_core)
                if skill:
                    self.register_skill(skill)
                    count += 1
            except Exception as e:
                print(f"[SkillRegistry] Error loading {py_file.name}: {e}")
                if is_core:
                    traceback.print_exc()
        
        if count > 0:
            layer_type = "core" if is_core else "agent"
            print(f"[SkillRegistry] Registered {count} {layer_type} skills from {directory}")
        
        return count
    
    def _load_skill_from_file(self, file_path: Path, agent_name: str, is_core: bool = False) -> Optional[Skill]:
        """
        Load a skill from a Python file (legacy format).
        
        Returns:
            Skill object if valid, None otherwise
        """
        try:
            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(
                f"skill_{file_path.stem}", 
                file_path
            )
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for required components
            if not hasattr(module, "SKILL_METADATA"):
                print(f"[SkillRegistry] Skipping {file_path.name}: No SKILL_METADATA")
                return None
            
            if not hasattr(module, "execute"):
                print(f"[SkillRegistry] Skipping {file_path.name}: No execute() function")
                return None
            
            metadata = module.SKILL_METADATA
            
            # Create Skill object
            skill = Skill(
                name=metadata.get("name", file_path.stem),
                description=metadata.get("description", "No description"),
                agent=metadata.get("agent", agent_name),
                category=metadata.get("category", "general"),
                module_path=str(file_path),
                parameters=metadata.get("parameters", {}),
                returns=metadata.get("returns", {}),
                examples=metadata.get("examples", []),
                tags=metadata.get("tags", []),
                version=metadata.get("version", "1.0.0"),
                is_core=is_core,  # NEW
                _execute_func=module.execute
            )
            
            return skill
            
        except Exception as e:
            print(f"[SkillRegistry] Error loading {file_path}: {e}")
            traceback.print_exc()
            return None
    
    def _load_skill_from_directory(self, skill_dir: Path, agent_name: str, is_core: bool = False) -> Optional[Skill]:
        """
        Load a skill from a directory with SKILL.md (Claude Skills format).
        
        Args:
            skill_dir: Path to skill directory containing SKILL.md
            agent_name: Agent name
            is_core: Whether this is a core skill
            
        Returns:
            Skill object if valid, None otherwise
        """
        try:
            # Import parser (handle both module and script execution)
            try:
                from core.skill_md_parser import parse_skill_md
            except ImportError:
                # Running as script, not module
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                from skill_md_parser import parse_skill_md
            
            skill_md_path = skill_dir / "SKILL.md"
            if not skill_md_path.exists():
                return None
            
            # Parse SKILL.md
            frontmatter, markdown_body = parse_skill_md(str(skill_md_path))
            
            if not frontmatter.get("name"):
                print(f"[SkillRegistry] Skipping {skill_dir.name}/SKILL.md: No 'name' in frontmatter")
                return None
            
            if not frontmatter.get("description"):
                print(f"[SkillRegistry] Skipping {skill_dir.name}/SKILL.md: No 'description' in frontmatter")
                return None
            
            # Look for Python script in same directory
            # Common patterns: crud.py, operations.py, or skill_name.py
            execute_func = None
            python_files = list(skill_dir.glob("*.py"))
            
            for py_file in python_files:
                if py_file.name == "__init__.py":
                    continue
                    
                # Try to load execute function
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"skill_{skill_dir.name}_{py_file.stem}",
                        py_file
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, "execute"):
                            execute_func = module.execute
                            
                            # Also inherit SKILL_METADATA if present (merge with SKILL.md)
                            if hasattr(module, "SKILL_METADATA"):
                                metadata = module.SKILL_METADATA
                                # Python metadata can override SKILL.md for technical details
                                frontmatter.setdefault("parameters", metadata.get("parameters", {}))
                                frontmatter.setdefault("returns", metadata.get("returns", {}))
                                frontmatter.setdefault("examples", metadata.get("examples", []))
                                frontmatter.setdefault("tags", metadata.get("tags", []))
                                frontmatter.setdefault("version", metadata.get("version", "1.0.0"))
                            break
                except:
                    continue
            
            # Create Skill object
            skill = Skill(
                name=frontmatter["name"],
                description=frontmatter["description"],
                agent=agent_name,
                category=frontmatter.get("category", "general"),
                module_path=str(skill_dir),
                parameters=frontmatter.get("parameters", {}),
                returns=frontmatter.get("returns", {}),
                examples=frontmatter.get("examples", []),
                tags=frontmatter.get("tags", []),
                version=frontmatter.get("version", "1.0.0"),
                is_core=is_core,
                prompt_instructions=markdown_body,  # NEW: Store markdown instructions
                _execute_func=execute_func  # May be None if skill is documentation-only
            )
            
            return skill
            
        except Exception as e:
            print(f"[SkillRegistry] Error loading {skill_dir.name}/SKILL.md: {e}")
            traceback.print_exc()
            return None
    
    def register_skill(self, skill: Skill) -> None:
        """
        Register a skill in the registry.
        
        Handles override detection: if an agent skill has the same name as a core skill,
        it overrides the core skill and the override is tracked.
        
        Args:
            skill: Skill object to register
        """
        # Check for override (agent skill overriding core skill)
        if skill.name in self._skills:
            existing = self._skills[skill.name]
            
            if existing.is_core and not skill.is_core:
                # Agent skill overriding core skill
                skill.overrides_core = True
                print(f"[SkillRegistry] Agent skill '{skill.name}' overrides core skill")
            elif skill.is_core and not existing.is_core:
                # Core skill loaded after agent skill (shouldn't happen with layered loading)
                print(f"[SkillRegistry] Warning: Core skill '{skill.name}' loaded after agent skill")
            else:
                print(f"[SkillRegistry] Warning: Duplicate skill '{skill.name}'")
        
        # Store in core skills dict if it's a core skill
        if skill.is_core:
            self._core_skills[skill.name] = skill
        
        # Register
        self._skills[skill.name] = skill
        
        # Index by agent
        if skill.agent not in self._skills_by_agent:
            self._skills_by_agent[skill.agent] = []
        if skill.name not in self._skills_by_agent[skill.agent]:
            self._skills_by_agent[skill.agent].append(skill.name)
        
        # Index by category
        if skill.category not in self._skills_by_category:
            self._skills_by_category[skill.category] = []
        if skill.name not in self._skills_by_category[skill.category]:
            self._skills_by_category[skill.category].append(skill.name)
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get skill by name."""
        return self._skills.get(name)
    
    def has_skill(self, name: str) -> bool:
        """Check if skill exists."""
        return name in self._skills
    
    def get_all_skills(self) -> List[Skill]:
        """Get all registered skills."""
        return list(self._skills.values())
    
    def get_skills_by_agent(self, agent: str) -> List[Skill]:
        """Get all skills owned by an agent."""
        skill_names = self._skills_by_agent.get(agent, [])
        return [self._skills[name] for name in skill_names]
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a category."""
        skill_names = self._skills_by_category.get(category, [])
        return [self._skills[name] for name in skill_names]
    
    def search_skills(self, query: str) -> List[Skill]:
        """
        Search skills by name, description, or tags.
        
        Args:
            query: Search term (case-insensitive)
            
        Returns:
            List of matching skills
        """
        query = query.lower()
        matches = []
        
        for skill in self._skills.values():
            # Search in name
            if query in skill.name.lower():
                matches.append(skill)
                continue
            
            # Search in description
            if query in skill.description.lower():
                matches.append(skill)
                continue
            
            # Search in tags
            if any(query in tag.lower() for tag in skill.tags):
                matches.append(skill)
                continue
        
        return matches
    
    def execute_skill(self, name: str, **params) -> Any:
        """
        Execute a skill by name with parameters.
        
        Args:
            name: Skill name
            **params: Parameters to pass to skill
            
        Returns:
            Result from skill execution
            
        Raises:
            ValueError: If skill not found
            RuntimeError: If execution fails
        """
        skill = self.get_skill(name)
        
        if skill is None:
            raise ValueError(f"Skill '{name}' not found in registry")
        
        return skill.execute(**params)
    
    def get_skill_prompt_context(self, agent: Optional[str] = None) -> str:
        """
        Generate a formatted string describing available skills for LLM prompts.
        
        Args:
            agent: If provided, only include skills for this agent
            
        Returns:
            Formatted string for prompt inclusion
        """
        if agent:
            skills = self.get_skills_by_agent(agent)
        else:
            skills = self.get_all_skills()
        
        if not skills:
            return "No skills available."
        
        lines = ["Available skills:"]
        
        for skill in sorted(skills, key=lambda s: s.name):
            params_str = ", ".join(
                f"{name}{'*' if spec.get('required') else ''}"
                for name, spec in skill.parameters.items()
            )
            
            lines.append(
                f"  - {skill.name}({params_str}): {skill.description}"
            )
        
        lines.append("\n(* = required parameter)")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_skills": len(self._skills),
            "agents": list(self._skills_by_agent.keys()),
            "categories": list(self._skills_by_category.keys()),
            "skills_by_agent": {
                agent: len(skills) 
                for agent, skills in self._skills_by_agent.items()
            },
            "skills_by_category": {
                category: len(skills) 
                for category, skills in self._skills_by_category.items()
            }
        }
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"SkillRegistry(skills={stats['total_skills']}, agents={len(stats['agents'])})"


# ============================================================================
# DEPRECATED: Global registry instance (kept for backward compatibility)
# ============================================================================
# WARNING: Each Agent should create its own registry instance.
# This global instance may be removed in future versions.

registry = None  # Deprecated - use SkillRegistry(agent_name) instead


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Skill Registry Test - New Architecture")
    print("=" * 70)
    
    # Test 1: Create core registry
    print("\n[TEST 1] Core Registry")
    core_registry = SkillRegistry(agent_name="core")
    core_registry.initialize()
    print(f"{core_registry}")
    
    # Test 2: Create Finn registry (inherits core + adds finn skills)
    print("\n[TEST 2] Finn Registry (Core + Agent)")
    finn_registry = SkillRegistry(agent_name="finn")
    finn_registry.initialize()
    print(f"{finn_registry}")
    
    print("\n" + "=" * 70)
    print("Finn's Available Skills:")
    print("=" * 70)
    for skill in sorted(finn_registry.get_all_skills(), key=lambda s: (s.agent, s.name)):
        override_marker = " [OVERRIDES CORE]" if skill.overrides_core else ""
        core_marker = " [CORE]" if skill.is_core else ""
        print(f"  - {skill.name}{core_marker}{override_marker}")
        print(f"    Agent: {skill.agent}, Category: {skill.category}")
        print(f"    Description: {skill.description[:80]}...")
    
    print("\n" + "=" * 70)
    print("Statistics:")
    print("=" * 70)
    for key, value in finn_registry.get_stats().items():
        print(f"  {key}: {value}")
