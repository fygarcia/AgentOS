# AgentOS Technical Specification

> **Version:** 1.0  
> **Status:** Foundation Phase  
> **Last Updated:** 2026-01-31

---

## 🎯 Executive Summary

**AgentOS** is a domain-agnostic agentic operating system that provides orchestration, skill management, self-healing, and multi-agent coordination capabilities. It serves as the "chassis" upon which domain-specific agents (like Agent Finn) can be built.

**Core Philosophy:** "Operating System for Autonomous Agents"
- Provides infrastructure, not domain logic
- Reusable across any domain (finance, code, research, etc.)
- Extensible through plugins (agents, skills, workflows)

---

## 🏗️ Architecture Overview

### Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Domain Agents (Finn, Code, Research, etc.)       │
│  ═══════════════════════════════════════════════════════    │
│  • Agent-specific skills                                    │
│  • Domain knowledge graphs                                  │
│  • Specialized workflows                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Orchestration & Workflows (AgentOS Core)         │
│  ═══════════════════════════════════════════════════════    │
│  • Intent Classification (Task vs Question) [NEW]           │
│  • Workflow routing (Planner vs Responder)  [NEW]           │
│  • Multi-agent coordination                                 │
│  • Self-healing loops                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Execution Nodes                                  │
│  ═══════════════════════════════════════════════════════    │
│  • Classifier: Input → IntentType                           │
│  • Responder: Question → Answer                             │
│  • Planner: Task → Plan                                     │
│  • Actor: Plan → Execution                                  │
│  • Auditor: Execution → Verification                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Infrastructure (LLMs, Tools, State)              │
│  ═══════════════════════════════════════════════════════    │
│  • LLM providers (Ollama, mock)                             │
│  • Skill registry                                           │
│  • State management (LangGraph)                             │
│  • Observability                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Core Components

### 1. **Execution Nodes**

#### 1.0 Classifier Node [NEW]
**Purpose:** Determine if user input is a Task, Question, or Chat
**Location:** `core/nodes/classifier.py`
**Models:** `PARSER_MODEL` (for reliable JSON)
**Outputs:** intent_type (TASK, QUESTION, CHAT)

#### 1.0.1 Responder Node [NEW]
**Purpose:** Fast-path response for Questions and Chat (bypassing Planner)
**Location:** `core/nodes/responder.py`
**Models:** `REASONING_MODEL`
**Outputs:** final_response

#### 1.1 Planner Node
**Purpose:** Transform user intent into executable plan

**Location:** `core/nodes/planner.py`

**Inputs:**
- User intent (string)
- Available skills (from registry)
- Context (memory, previous state)

**Processing:**
1. Uses **reasoning model** (e.g., gpt-oss:20b, deepseek-r1) to analyze intent
2. Generates detailed reasoning with step-by-step logic
3. Uses **parser model** (e.g., llama3.1:8b) to structure into JSON
4. Validates against Plan Pydantic schema

**Outputs:**
- Plan object with ordered steps
- Each step has: role, instruction, reasoning, expected_outcome

**Models Used:**
- Primary: `REASONING_MODEL` (configured in .env)
- Secondary: `PARSER_MODEL` (configured in .env)

**Configuration:**
```env
REASONING_MODEL=gpt-oss:20b
PARSER_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://192.168.4.102:11434
```

---

#### 1.2 Actor Node
**Purpose:** Execute plan steps that require actions

**Location:** `core/nodes/actor.py`

**Inputs:**
- Instruction from current plan step
- Available tools/skills
- State context

**Processing:**
1. Uses **tool-calling model** to generate execution code/commands
2. Executes in controlled environment
3. Captures outputs and errors

**Outputs:**
- Tool execution results
- Success/failure status
- Updated state

**Models Used:**
- Primary: `TOOL_MODEL` (configured in .env, can be same as PARSER_MODEL)

**Execution Environment:**
- Python exec() with controlled globals
- Access to skill registry
- Sandboxed file operations

---

#### 1.3 Auditor Node
**Purpose:** Verify execution results and ensure correctness

**Location:** `core/nodes/auditor.py`

**Inputs:**
- Verification instruction from plan step
- Expected outcome
- Actual execution results
- State context

**Processing:**
1. Uses **reasoning model** to analyze results
2. Compares expected vs actual
3. Determines if verification passes
4. Decides next action (continue, retry, abort, heal)

**Outputs:**
- AuditResult (passed, message, next_step)
- Updated state

**Models Used:**
- Primary: `REASONING_MODEL` (same as Planner for consistency)

**Verification Strategies:**
- `verify_file_exists` - Checks file presence
- `verify_file_content_contains` - Checks substring in file
- `verify_file_does_not_exist` - Ensures clean state
- `verify_tool_output_success` - Fallback check

---

### 2. **LLM Provider System**

#### 2.1 Provider Interface
**Location:** `core/llm.py`

**Supported Providers:**
- **MockLLM** - For testing, returns fixed responses
- **OllamaLLM** - For local Ollama inference
- **CloudLLM** - (Future) For cloud providers (OpenAI, Anthropic, Google)

**Selection:**
```python
# Via environment variable
LLM_PROVIDER=ollama  # or "mock" for testing
```

**Capabilities:**
- Text generation
- System/user prompts
- Temperature control
- Max tokens configuration

---

#### 2.2 Two-Stage Client
**Location:** `core/two_stage_client.py`

**Purpose:** Combine reasoning model + parser model for structured outputs

**Architecture:**
```
Stage 1: Reasoning Model
    Input:  User request + system prompt
    Output: Detailed reasoning text (~5000 chars)
    Mode:   Natural language (no JSON constraints)
    Model:  gpt-oss:20b, deepseek-r1, etc.
    
Stage 2: Parser Model
    Input:  Reasoning text + JSON schema
    Output: Validated Pydantic model
    Mode:   JSON mode (format="json")
    Model:  llama3.1:8b, qwen2.5-coder, etc.
```

**Why Two Stages:**
- Reasoning models excel at logic but struggle with JSON formatting
- Parser models excel at structure but have less sophisticated reasoning
- Two-stage combines strengths of both

**Usage:**
```python
client = TwoStageOllamaClient()
plan = client.generate_with_reasoning(
    reasoning_model=os.getenv("REASONING_MODEL"),
    parser_model=os.getenv("PARSER_MODEL"),
    prompt=user_intent,
    schema=Plan
)
```

---

### 3. **Skill Registry System** (Phase 1B - To Be Implemented)

#### 3.1 Skill Metadata Standard

Every skill MUST define:
```python
# /finn/skills/example_skill.py

SKILL_METADATA = {
    "name": "example_skill",
    "version": "1.0.0",
    "description": "Short description of what this skill does",
    "agent": "finn",  # Which agent owns this
    "category": "database",  # database, file, web, calculation, etc.
    
    "parameters": {
        "param1": {
            "type": "str",
            "required": True,
            "description": "Description of param1"
        },
        "param2": {
            "type": "int",
            "required": False,
            "default": 10,
            "description": "Description of param2"
        }
    },
    
    "returns": {
        "type": "dict",
        "description": "What this skill returns"
    },
    
    "examples": [
        {
            "input": {"param1": "value1", "param2": 5},
            "output": {"result": "success"},
            "description": "Example usage"
        }
    ],
    
    "tags": ["database", "crud", "upsert"]
}

def execute(**params):
    """
    Main entry point for skill execution.
    
    Args from SKILL_METADATA.parameters
    Returns as defined in SKILL_METADATA.returns
    """
    # Implementation
    pass
```

---

#### 3.2 SkillRegistry Class

**Location:** `core/skill_registry.py` (to be created)

**Interface:**
```python
class SkillRegistry:
    """Central registry for all available skills."""
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        
    def scan_directory(self, directory: Path, agent_name: str) -> int:
        """
        Scan directory for skills and register them.
        
        Args:
            directory: Path to skills folder
            agent_name: Name of agent (e.g., "finn")
            
        Returns:
            Number of skills found
        """
        pass
    
    def register_skill(self, skill: Skill) -> None:
        """Register a single skill."""
        pass
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get skill by name."""
        pass
    
    def get_skills_by_agent(self, agent: str) -> List[Skill]:
        """Get all skills owned by an agent."""
        pass
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a category."""
        pass
    
    def search_skills(self, query: str) -> List[Skill]:
        """Search skills by name/description/tags."""
        pass
    
    def execute_skill(self, name: str, **params) -> Any:
        """
        Execute a skill by name with parameters.
        
        Includes:
        - Parameter validation
        - Error handling
        - Result validation
        """
        pass
    
    def get_skill_prompt_context(self) -> str:
        """
        Generate a string describing all available skills
        for inclusion in LLM prompts.
        
        Returns:
            Formatted string like:
            "Available skills:
            - db_upsert: Insert or update database records
            - create_file: Create a new file with content
            ..."
        """
        pass
```

---

#### 3.3 Integration Points

**Planner Integration:**
```python
# In planner node
registry = SkillRegistry()
registry.scan_directory("./finn/skills", "finn")

skills_context = registry.get_skill_prompt_context()

system_prompt = f"""
You are the Planner.
{skills_context}

When creating a plan, you can reference these skills by name.
"""
```

**Actor Integration:**
```python
# In actor node
skill_name = extract_skill_from_instruction(instruction)
if skill_name and registry.has_skill(skill_name):
    result = registry.execute_skill(skill_name, **params)
else:
    # Fall back to code generation
    code = llm.generate_code(instruction)
    result = exec(code)
```

---

### 4. **State Management**

#### 4.1 AgentState Schema

**Location:** `core/state.py`

**Definition:**
```python
from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """The shared state that flows through the graph."""
    
    # Core workflow state
    messages: List[Dict[str, str]]        # Conversation history
    plan: List[Dict[str, Any]]            # Execution plan from Planner
    current_step_index: int               # Which step we're on
    tool_outputs: Dict[str, Any]          # Results from each step
    final_response: Optional[str]         # Final output to user
    
    # Optional context (populated as needed)
    user_intent: Optional[str]            # Original user request
    intent_type: Optional[str]            # "question" | "task" | "complex"
    available_skills: Optional[List[str]] # Skills from registry
    agent_name: Optional[str]             # Which agent is handling this
    error_context: Optional[Dict]         # For self-healing
```

**State Flow:**
```
Entry → Planner (populates plan)
     → Router (reads plan[current_step_index])
     → Actor/Auditor (updates tool_outputs, increments current_step_index)
     → Router (checks if done)
     → END or loop back
```

---

#### 4.2 LangGraph Structure

**Location:** `core/graph.py`

**Current Graph:**
```python
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("actor", actor_node)
workflow.add_node("auditor", auditor_node)

# Edges
workflow.set_entry_point("planner")
workflow.add_conditional_edges(
    "planner",
    route_step,
    {"actor": "actor", "auditor": "auditor", END: END}
)
workflow.add_conditional_edges(
    "actor",
    route_step,
    {"actor": "actor", "auditor": "auditor", END: END}
)
workflow.add_conditional_edges(
    "auditor",
    route_step,
    {"actor": "actor", "auditor": "auditor", END: END}
)
```

**Router Function:**
```python
def route_step(state: AgentState) -> str:
    """Determine next node based on current step."""
    if state["current_step_index"] >= len(state["plan"]):
        return END
    
    current_step = state["plan"][state["current_step_index"]]
    role = current_step["role"]
    
    if role == "Actor":
        return "actor"
    elif role == "Auditor":
        return "auditor"
    else:
        return END
```

---

### 5. **Workflow Templates** (Phase 1C - To Be Implemented)

#### 5.1 Simple Q&A Workflow
```python
def create_qa_graph() -> Graph:
    """For simple questions that don't need planning."""
    workflow = StateGraph(AgentState)
    workflow.add_node("qa", qa_node)
    workflow.set_entry_point("qa")
    workflow.add_edge("qa", END)
    return workflow.compile()
```

#### 5.2 Task Workflow (Current)
```python
def create_task_graph() -> Graph:
    """For tasks that need planning and execution."""
    # Current implementation in graph.py
    pass
```

#### 5.3 Complex Workflow (Future)
```python
def create_complex_graph() -> Graph:
    """For complex tasks needing multi-agent coordination."""
    # Phase 2B implementation
    pass
```

---

## 🔒 Constraints & Requirements

### Model Requirements

**Minimum:**
- Reasoning Model: 20B+ parameters, good at logic/planning
- Parser Model: 7B+ parameters, good at JSON/structured output

**Recommended:**
- Reasoning: gpt-oss:20b, deepseek-r1-32b, qwen2.5-think-7b
- Parser: llama3.1:8b, qwen2.5-coder-7b, codellama:7b

**Configuration:**
Must be variable-based (no hardcoding):
```env
# .env file
REASONING_MODEL=gpt-oss:20b
PARSER_MODEL=llama3.1:8b
TOOL_MODEL=llama3.1:8b  # Can be same as parser
OLLAMA_BASE_URL=http://192.168.4.102:11434
```

---

### Extensibility Requirements

**Agent Plugins:**
- Each agent in its own folder (`/finn`, `/code-agent`, etc.)
- Standard structure: `/config`, `/skills`, `/directives`, `/memory`
- Register with AgentOS at startup

**Skill Plugins:**
- Follow metadata standard
- One skill per file
- Discoverable via registry scan

**Workflow Plugins:**
- Can define custom workflow graphs
- Register with workflow router
- Follow state management contract

---

### Testing Requirements

**Coverage:**
- Minimum 80% code coverage
- All nodes must have unit tests
- All workflows must have integration tests
- All skills must have execution tests

**Test Categories:**
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Multi-component flows
3. **E2E Tests** - Full workflow testing
4. **Performance Tests** - Latency, throughput benchmarks

**Test Providers:**
- Use MockLLM for fast unit tests
- Use Ollama for integration/E2E tests
- Mock external dependencies (databases, APIs)

---

## 📊 Acceptance Criteria

### Phase 1 Completion Criteria

**AgentOS is considered "complete" for Phase 1 when:**

1. ✅ **Core Workflow Works**
   - [ ] Planner generates valid plans
   - [ ] Actor executes plan steps
   - [ ] Auditor verifies results
   - [ ] Router correctly navigates graph
   - [ ] All tests pass with Mock and Ollama providers

2. ✅ **Models are Configurable**
   - [ ] All models defined in .env
   - [ ] Can swap models without code changes
   - [ ] Graceful fallback if model unavailable
   - [ ] Clear error messages for model issues

3. ✅ **Skill Registry Operational**
   - [ ] Scans and discovers all skills
   - [ ] Skills have proper metadata
   - [ ] Planner sees available skills
   - [ ] Actor executes skills by name
   - [ ] Registry handles errors gracefully

4. ✅ **Intent Classification Works**
   - [ ] Classifies intents accurately (>90%)
   - [ ] Routes to appropriate workflow
   - [ ] Simple questions get direct answers
   - [ ] Complex tasks get full planning

5. ✅ **Auditor Actually Verifies**
   - [ ] Performs real verification (not just incrementing)
   - [ ] Returns meaningful audit results
   - [ ] Can detect failures
   - [ ] Triggers appropriate actions

6. ✅ **Documentation Complete**
   - [ ] All components documented
   - [ ] API references complete
   - [ ] Examples for each feature
   - [ ] Troubleshooting guide

7. ✅ **Test Coverage Adequate**
   - [ ] >80% code coverage
   - [ ] All workflows tested end-to-end
   - [ ] Performance benchmarks defined
   - [ ] CI/CD pipeline (optional but recommended)

---

## 🔗 Related Documentation

- [ROADMAP.md](./ROADMAP.md) - Development roadmap
- [PRD.md](./finn/config/PRD.md) - Product requirements
- [STRUCTURE.md](./STRUCTURE.md) - File organization
- [tests/README.md](./tests/README.md) - Test documentation

---

**Version:** 1.0  
**Last Updated:** 2026-01-31  
**Status:** Foundation Phase - 40% Complete
