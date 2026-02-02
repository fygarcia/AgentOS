# Omni-Finn: AgentOS + Agent Finn

> **A domain-agnostic agentic operating system with a financial specialist**  
> **Status:** Phase 1 - Foundation COMPLETE (MVP 1.0)
> **Last Updated:** 2026-02-01

---

For New Developers/LLMs:
**BEFORE RUNNING ANYTHING REMEMBER TO ACTIVATE VENV**
1. Start with **README.md** (this file)
2. Read [docs/ROADMAP.md](./docs/ROADMAP.md) (what we're building)
3. Read [docs/STATUS.md](./docs/STATUS.md) (current state)
4. Read [docs/AGENTOS_SPEC.md](./docs/AGENTOS_SPEC.md) (how to build)
5. Read [docs/STRUCTURE.md](./docs/STRUCTURE.md) (where things are)

---

## 🎯 What is This?

**Omni-Finn** is a two-layer autonomous system:

1. **AgentOS** - A reusable agentic framework (the "operating system")
   - Provides orchestration, skill management, persistent memory
   - Domain-agnostic - can power any type of agent
   - Built on LangGraph + Local Ollama LLMs
   - **NEW:** Three-tier memory system (HOT/WARM/COLD) with LanceDB

2. **Agent Finn** - A financial portfolio manager (the "application")
   - Autonomous data ingestion from bank statements
   - Zero-error financial calculations (decimal precision)
   - Proactive research and delta reports

**Current Focus:** Building AgentOS first, then integrating Finn

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Agent Finn (Financial Specialist)                          │
│  • Portfolio management                                     │
│  • Data ingestion & reconciliation                          │
│  • Research & analysis                                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  AgentOS (Domain-Agnostic Framework)                        │
│  • Classifier Node (Task vs Question Routing) [NEW]         │
│  • Planner → Actor → Auditor workflow                       │
│  • Enhanced Auditor with Verification Strategies [NEW]      │
│  • Skill registry & execution                               │
│  • Persistent memory (NOW.md + LOG.md + SQLite + LanceDB)   │
│  • Self-healing loops (Phase 2)                             │
│  • Multi-agent orchestration (Phase 2)                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Infrastructure                                             │
│  • Local Ollama LLMs (RTX 4090)                             │
│  • LangGraph for state management                           │
│  • SQLite for structured memory & facts                     │
│  • LanceDB for semantic search (Cold Memory)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
- Python 3.10+ (3.14 supported)
- Ollama running locally
- Models: gpt-oss:20b, llama3.1:8b

# Check Ollama is running
curl http://192.168.4.102:11434/api/tags
```

### Installation

```bash
# Clone and setup
git clone <repo-url>
cd Agent-FIN

# Create virtual environment
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pydantic, yaml; print('✅ Dependencies OK')"

# Configure environment
cp .env.example .env
# Edit .env with your Ollama URL and model names
```

### Configuration

Create `.env` file:
```env
# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://192.168.4.102:11434

# Models
REASONING_MODEL=gpt-oss:20b
PARSER_MODEL=llama3.1:8b
TOOL_MODEL=llama3.1:8b

# Observability
ENABLE_OBSERVABILITY=true
```

### Run Tests

```bash
# Quick tests (mock provider)
python tests/test_auditor.py
python tests/test_graph_routing.py
python tests/test_actor.py

# Integration tests (requires Ollama)
python tests/test_planner_pydantic.py
python tests/test_agent_integration.py
```

### Run AgentOS

```bash
# Run a simple workflow
python core/engine.py "Create a file named hello.txt with content 'AgentOS is working'"

# OR via Agent class (Recommended)
# See scripts or interactive shell
```

---

## 📁 Project Structure

```
/Agent-FIN
├── /core                   # AgentOS - Domain-Agnostic Framework
│   ├── engine.py           # Main entry point
│   ├── agent.py            # Agent class definition
│   ├── graph.py            # LangGraph workflow definition
│   ├── state.py            # AgentState schema
│   ├── models.py           # Pydantic models (Plan, PlanStep, etc.)
│   ├── memory_manager.py   # Persistent memory system (LanceDB)
│   ├── memory_schema.sql   # Memory database schema
│   ├── llm.py              # LLM provider interface
│   ├── two_stage_client.py # Reasoning + parsing pipeline
│   ├── observability.py    # Tracing & monitoring
│   ├── /nodes              # Execution nodes
│   │   ├── planner.py      # Intent → Plan
│   │   ├── actor.py        # Plan → Execution
│   │   └── auditor.py      # Execution → Verification
│   └── /skills/memory      # Native memory skills
│
├── /docs                   # 📚 All Documentation
│   ├── ROADMAP.md          # Development roadmap
│   ├── STATUS.md           # Current status
│   ├── AGENTOS_SPEC.md     # Technical specification
│   ├── STRUCTURE.md        # File organization
│   ├── MEMORY_SYSTEM.md    # Memory architecture
│   ├── AGENT_STRUCTURE_STANDARD.md # Agent directory standard
│   └── /legacy             # Archived documentation
│
├── /finn                   # Agent Finn - Financial Specialist
│   ├── /config             # Agent configuration & SOPs
│   ├── /skills             # Finn-specific skills
│   ├── /directives         # SOPs & procedures
│   ├── /memory             # Agent memory (NOW.md, LOG.md, memory.db)
│   └── /inbox              # Watch folder for ingestion
│
├── /tests                  # Test suite
│   ├── README.md           # Test documentation
│   ├── test_*.py           # Test files
│   └── /results            # Test outputs & artifacts
│
├── README.md               # This file - start here
├── requirements.txt        # Python dependencies
└── .env                    # Environment configuration
```

---

## 📚 Documentation

### 🌟 **Start Here:**
1. **[docs/ROADMAP.md](./docs/ROADMAP.md)** - Development plan, priorities, milestones
2. **[docs/STATUS.md](./docs/STATUS.md)** - Current state, progress, known issues
3. **[docs/AGENTOS_SPEC.md](./docs/AGENTOS_SPEC.md)** - Technical specification

### Detailed Docs:
- **[docs/STRUCTURE.md](./docs/STRUCTURE.md)** - File system organization
- **[docs/MEMORY_SYSTEM.md](./docs/MEMORY_SYSTEM.md)** - Memory architecture
- **[docs/AGENT_STRUCTURE_STANDARD.md](./docs/AGENT_STRUCTURE_STANDARD.md)** - Directory standards
- **[finn/config/PRD.md](./finn/config/PRD.md)** - Product vision & requirements
- **[finn/config/AGENTS.md](./finn/config/AGENTS.md)** - Agent architecture philosophy
- **[tests/README.md](./tests/README.md)** - Test suite documentation

---

## 🎯 Current Status

### ✅ What's Working
- ✅ **Intent Classification** (Smart Routing)
  - Distinguishes between Tasks ("Create file") and Questions ("What is X?")
  - Routes Questions to fast-path `Responder` node
  - Routes Tasks to full `Planner` loop
- ✅ **Enhanced Auditor** (Reliable Verification)
  - Verifies actual side-effects (file creation, content presence)
  - Uses strategy pattern (`verify_file_exists`, `verify_content`, etc.)
- ✅ Planner → Actor → Auditor workflow
- ✅ **Agent-Engine Integration** (Agent class drives workflow)
- ✅ Two-stage reasoning (gpt-oss:20b + llama3.1:8b)
- ✅ LangGraph state management
- ✅ **Persistent Memory System** (HOT/WARM/COLD architecture)
  - NOW.md for current status
  - LOG.md for activity history
  - SQLite for user facts & metadata
  - **LanceDB** for semantic search (Cold Memory)
  - Auto-logging & context injection
  - Self-annealing error recovery
- ✅ Skill registry system with metadata discovery
- ✅ Memory skills (update_status, log_activity, save_fact, etc.)
- ✅ Test suite (All passing)

### 🔄 In Progress
- 🔄 Phase 2: Self-Healing Loops

### ❌ Not Yet Implemented
- ❌ Multi-agent support (Phase 2)
- ❌ Agent Finn integration (Phase 3)

**See [docs/STATUS.md](./docs/STATUS.md) for detailed progress**

---

## 🚦 Development Phases

### Phase 1: AgentOS Foundation (COMPLETE - 100%)
**Goal:** Build tested, reusable agentic core

- **1A:** Core workflow ✅ 100%
- **1B:** Skill Registry & Integration ✅ 100%
- **1C:** Intent Classification ✅ 100% (Smart Routing)
- **1D:** Enhanced auditor ✅ 100% (Strategy Verification)
- **1E:** Persistent memory ✅ 100% (LanceDB)

### Phase 2: AgentOS Advanced Features (Not Started)
- Self-healing loops
- Multi-agent support
- Advanced workflow patterns

### Phase 3: Agent Finn Integration (Not Started)
- Financial skill catalog
- Ingestion pipeline
- Sub-agents (Accountant, OCR, Researcher)

### Phase 4: Production Deployment (Future)
- Observability & monitoring
- Performance optimization
- User interface

**See [docs/ROADMAP.md](./docs/ROADMAP.md) for detailed breakdown**

---

## 🧪 Testing

```bash
# Run all quick tests (<5 seconds)
python tests/test_auditor.py && \
python tests/test_graph_routing.py && \
python tests/test_actor.py

# Run integration tests (requires Ollama, ~30 seconds)
python tests/test_planner_pydantic.py
python tests/test_agent_integration.py

# Run full E2E test (requires Ollama, ~2-3 minutes)
python tests/test_e2e_workflow.py
```

**Test Coverage:** ~85%
- Unit tests: Passing
- Integration tests: Passing
- End-to-end tests: Passing

**See [tests/README.md](./tests/README.md) for detailed test documentation**

---

## 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | LangGraph | State management & workflow routing |
| **LLM Server** | Ollama | Local LLM inference |
| **Reasoning Model** | gpt-oss:20b | Planning & high-level reasoning |
| **Tool Model** | llama3.1:8b | Code generation & structured output |
| **Validation** | Pydantic V2 | Type-safe data models |
| **Database** | SQLite | Portfolio data + memory storage |
| **Vector DB** | LanceDB | Semantic memory (cold tier) |
| **Observability** | LangSmith | Tracing & debugging |

---

## 🤝 Contributing

### Development Workflow

1. **Read the docs**
   - Start with [docs/ROADMAP.md](./docs/ROADMAP.md)
   - Check [docs/STATUS.md](./docs/STATUS.md) for current state
   - Review [docs/AGENTOS_SPEC.md](./docs/AGENTOS_SPEC.md) for technical details

2. **Pick a task**
   - See docs/ROADMAP.md for current sprint
   - Check GitHub issues (if available)

3. **Write tests first**
   - Follow existing test patterns in `/tests`
   - See tests/README.md for guidelines

4. **Submit PR** (if applicable)
   - Include tests
   - Update documentation
   - Follow Pydantic V2 patterns

---

## 📝 Key Design Principles

### 1. **Separation of Concerns**
- **AgentOS** = Domain-agnostic infrastructure
- **Agents** = Domain-specific knowledge & skills
- Never mix domain logic into core

### 2. **Skill-Oriented Architecture**
- All capabilities as discoverable skills
- Metadata-driven skill registry
- Dynamic skill loading & execution

### 3. **Model Flexibility**
- All models configurable via environment
- Support for local & cloud LLMs
- Graceful degradation

### 4. **Test-Driven Development**
- >80% code coverage target
- Tests for every component
- Mock for speed, Ollama for integration

### 5. **Observability First**
- Trace every LLM call
- Log all state transitions
- Debug-friendly error messages

---

## 🐛 Known Issues

1. **Auditor Loop** - Failed verification doesn't yet trigger automatic retry/healing (Phase 2)
2. **Context Window** - Very long conversation histories may hit context limits (Need to implement summary rollover)

**See [docs/STATUS.md](./docs/STATUS.md) for full list**

---

## 🔗 Links & Resources

- **Ollama:** https://ollama.ai
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **Pydantic:** https://docs.pydantic.dev/latest/
- **LanceDB:** https://lancedb.com/

---

## 📄 License

[To be determined]

---

## 👥 Team

- **Development:** [Your Name]
- **Architecture:** AI-Assisted Design
- **Infrastructure:** RTX 4090 Homelab

---

## 📞 Support

For questions about:
- **AgentOS Core:** See [docs/AGENTOS_SPEC.md](./docs/AGENTOS_SPEC.md)
- **Agent Finn:** See [finn/config/PRD.md](./finn/config/PRD.md)
- **Development:** See [docs/ROADMAP.md](./docs/ROADMAP.md)
- **Current Status:** See [docs/STATUS.md](./docs/STATUS.md)

---

**Last Updated:** 2026-02-01  
**Version:** 1.0 (MVP - Phase 1 Complete)  
**Next Milestone:** Self-Healing Loops (Phase 2)
