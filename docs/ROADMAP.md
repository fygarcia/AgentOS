# ROADMAP.md - Project Omni-Finn Development Plan

> **Last Updated:** 2026-02-01  
> **Status:** Phase 1 - Foundation COMPLETE (MVP 1.0) ✅  
> **Next Milestone:** Phase 2 - Self-Healing Loops

---

## 🎯 Project Vision

**Omni-Finn** is a two-layer autonomous system:
1. **AgentOS** - Domain-agnostic agentic framework (the "operating system")
2. **Agent Finn** - Financial specialist that runs on AgentOS (the "application")

**Architecture Philosophy:** "Chassis + Driver"
- AgentOS provides orchestration, skill management, self-healing
- Finn provides financial domain knowledge, SOPs, specialized tools

---

## 📋 Development Priorities

### ✅ **CONFIRMED PRIORITIES (User-Defined):**

1. **PRD is VALID** - All features in PRD.md are still goals
2. **PRIORITY: Option A** - Complete AgentOS (CORE) first
3. **SCOPE: Framework** - Build reusable AgentOS, test thoroughly, then apply to Finn

### 🎯 **Strategic Approach:**

```
Phase 1: AgentOS Foundation (CURRENT)
    ↓
Phase 2: AgentOS Advanced Features
    ↓
Phase 3: Agent Finn Integration
    ↓
Phase 4: Production Deployment
```

---

## 🏗️ PHASE 1: AgentOS Foundation (CURRENT PHASE)

**Goal:** Build a working, tested, domain-agnostic agentic core

**Status:** 100% Complete (✅ Phase 1A + 1B + 1C + 1D + 1E done)

### Phase 1A: Core Workflow ✅ **COMPLETE**

**Completed:**
- ✅ Basic LangGraph setup (Planner → Actor → Auditor)
- ✅ Two-stage reasoning pipeline (reasoning model + parser model)
- ✅ State management (AgentState TypedDict)
- ✅ Router function (role-based routing)
- ✅ Mock & Ollama LLM providers
- ✅ Pydantic V2 migration
- ✅ Model configuration management (✅ via .env)
- ✅ Environment-based model selection (✅ via config)
- ✅ Centralized configuration system (core/config.py)
- ✅ Test suite (8 tests, 90% coverage)
- ✅ Documentation (README, ROADMAP, STATUS, SPEC)

**Acceptance Criteria:**
- [x] All tests pass with both Mock and Ollama providers
- [x] Models are configurable via .env
- [x] Can swap reasoning/tool models without code changes
- [x] Centralized configuration with validation

---

### Phase 1B: Skill Registry System ✅ **COMPLETE**

**Goal:** Build a dynamic skill discovery and registration system AND integrate with Agent class

**Completed:**
- ✅ Skill Registry (core/skill_registry.py - 400 lines)
- ✅ Skill metadata standard defined and documented
- ✅ Directory scanner with auto-discovery
- ✅ Integration with Planner (skills visible in prompt)
- ✅ Safe skill execution with parameter validation
- ✅ 3 Finn skills updated with metadata
- ✅ Test coverage (test_skill_registry.py)
- ✅ Skills auto-load at module import
- ✅ Agent class created (core/agent.py)
- ✅ **Agent-Engine Integration**: Bridged Agent class to LangGraph workflow

**Acceptance Criteria:**
- [x] Registry discovers all skills in scan directory
- [x] Skills can be registered dynamically
- [x] Planner sees available skills in prompt
- [x] Safe execution with validation
- [x] Test coverage for registry operations
- [x] Works with skills from multiple agents
- [x] **Agent("finn").run(intent) works end-to-end**

---

### Phase 1C: Intent Classification ✅ **COMPLETE**

**Goal:** Route different types of user intents to appropriate workflows

**Components to Build:**

#### 1. **Intent Classifier Node (`core/nodes/classifier.py`)**
```python
def classify_intent(user_input: str) -> str:
    """
    Returns: "question" | "task" | "complex_task" | "chat"
    """
    pass
```

**Classification Logic:**
- **Question** - "What is X?", "How does Y work?"
- **Simple Task** - "Create a file", "Calculate X"
- **Complex Task** - "Analyze portfolio", "Generate report"
- **Chat** - General conversation

#### 2. **Multiple Workflow Templates**

**Simple Q&A Workflow:**
```
User Intent → Classifier → Direct LLM Response
```

**Task Workflow (Current):**
```
User Intent → Classifier → Planner → Actor → Auditor → Loop
```

**Complex Workflow (Future):**
```
User Intent → Classifier → Orchestrator → Multi-Agent → Coordinator
```

#### 3. **Dynamic Entry Point Selection**
```python
def get_workflow_for_intent(intent_type: str) -> Graph:
    if intent_type == "question":
        return create_qa_graph()
    elif intent_type == "task":
        return create_task_graph()
    elif intent_type == "complex_task":
        return create_complex_graph()
```

**Acceptance Criteria:**
- [x] Classifier accurately categorizes intents (>90% accuracy)
- [x] Multiple workflow templates exist (Responder vs Planner)
- [x] Router selects correct workflow based on classification
- [x] Simple questions don't go through full planning
- [x] Test coverage for all intent types

---

### Phase 1D: Enhanced Auditor ✅ **COMPLETE**

**Goal:** Make Auditor actually verify results, not just move to next step

**Current Problem:**
- Auditor currently just increments step index
- No actual verification logic
- No failure detection

**Components to Build:**

#### 1. **Verification Strategies**
```python
class VerificationStrategy:
    def verify_file_creation(expected: dict, actual: dict) -> AuditResult
    def verify_database_operation(expected: dict, actual: dict) -> AuditResult
    def verify_calculation(expected: dict, actual: dict) -> AuditResult
```

#### 2. **Audit Result Actions**
```python
class AuditResult:
    passed: bool
    message: str
    next_step: Literal["continue", "retry", "abort", "heal"]
```

#### 3. **Integration with Self-Healing** (Phase 2)
- If audit fails → trigger self-healing
- Collect failure context for diagnosis

**Acceptance Criteria:**
- [x] Auditor performs actual verification (file exists, content correct, etc.)
- [x] Returns meaningful audit results
- [x] Can detect failures and trigger appropriate action
- [x] Test coverage for verification strategies

---

### Phase 1E: Persistent Memory ✅ **COMPLETE**

**Goal:** Implement robust memory system (HOT/WARM/COLD)

**Completed:**
- ✅ 3-Tier Architecture
- ✅ MemoryManager with LanceDB support
- ✅ Auto-context injection
- ✅ Self-annealing logs
- ✅ Integration with Agent class

**Acceptance Criteria:**
- [x] Memory persists across sessions
- [x] Context available in LLM prompts
- [x] Semantic search working (LanceDB)
- [x] Tests passing

---

## 🏗️ PHASE 2: AgentOS Advanced Features

**Status:** 0% Complete - Will start after Phase 1

### Phase 2A: Self-Healing Loop (The Annealing Process)
**Goal:** Automatic detection, diagnosis, and fixing of failed operations

### Phase 2B: Multi-Agent Support
**Goal:** Support multiple specialized agents working together

### Phase 2C: Advanced Workflow Patterns
**Goal:** Support complex workflow patterns (parallel, branching, loops)

---

## 🏗️ PHASE 3: Agent Finn Integration

**Status:** 0% Complete - Will start after Phase 2

**Goal:** Build the financial specialist on top of AgentOS

### Phase 3A: Finn Foundation
### Phase 3B: Ingestion Pipeline
### Phase 3C: Research & Analysis
### Phase 3D: Finn Sub-Agents

---

## 🏗️ PHASE 4: Production Deployment

**Status:** 0% Complete - Future

---

## 📊 Current Status Summary

| Component | Phase | Status | Progress | Next Action |
|-----------|-------|--------|----------|-------------|
| **Basic Workflow** | 1A | ✅ Complete | 100% | Done |
| **Skill Registry** | 1B | ✅ Complete | 100% | Done |
| **Agent Integration**| 1B | ✅ Complete | 100% | Done |
| **Memory System** | 1E | ✅ Complete | 100% | Done (LanceDB) |
| **Intent Classifier** | 1C | ✅ Complete| 100% | Done (Smart Routing) |
| **Enhanced Auditor** | 1D | ✅ Complete | 100% | Done (Strategies) |
| **Self-Healing** | 2A | 🔄 Next | 0% | Design Phase |
| **Multi-Agent** | 2B | ❌ Not Started | 0% | After self-healing |
| **Finn Skills** | 3A | 🔄 Partial | 20% | After Phase 2 |

---

## 🎯 Immediate Next Steps (Priority Order)

### Current Sprint: Phase 2 - Self-Healing Loops (Phase 2A)
1. ⬜ Design Self-Healing architecture
2. ⬜ Implement Error Analysis Node
3. ⬜ Implement Retry Logic
4. ⬜ Implement Context Rollover

### Completed:
- ✅ Phase 1C: Intent Classification
- ✅ Phase 1D: Enhanced Auditor

---

## 📝 Notes for Future Development

### When Building Finn (Phase 3):
- Use AgentOS skill registry (don't reinvent)
- Follow skill metadata standard
- SOPs should be machine-readable (YAML/JSON + Markdown)
- All financial math must use `decimal` library
- Database operations must be audited

### When Adding New Agents:
- Each agent lives in its own folder (`/agent-name`)
- Each agent has: `/config`, `/skills`, `/directives`, `/memory`
- Agents register with AgentOS at startup
- Use consistent metadata format

### When Extending AgentOS:
- Keep core domain-agnostic
- Domain-specific logic goes in agent folders
- Don't hardcode agent knowledge in core
- Use dependency injection for extensibility

---

## 🔗 Related Documentation

- [PRD.md](./finn/config/PRD.md) - Product requirements (vision)
- [STRUCTURE.md](./STRUCTURE.md) - File organization
- [AGENTIOS_SPEC.md](./AGENTIOS_SPEC.md) - AgentOS technical specification
- [tests/README.md](./tests/README.md) - Test suite documentation
- [finn/config/AGENTS.md](./finn/config/AGENTS.md) - Agent architecture

---

**Last Updated:** 2026-02-01  
**Current Status:** Phase 1 Complete (MVP 1.0)  
**Next Milestone:** Self-Healing Loops (Phase 2)
