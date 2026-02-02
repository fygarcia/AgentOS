# 📋 Documentation Overview - Quick Reference

> **For LLMs & Future Context:** This is your entry point to understand the entire project

---

## 🎯 Project Summary

**Name:** Omni-Finn  
**Type:** Two-layer autonomous agent system  
**Status:** Phase 1A - Building AgentOS Core (40% complete)  
**Updated:** 2026-01-31

**Two Components:**
1. **AgentOS** - Domain-agnostic agentic framework
2. **Agent Finn** - Financial portfolio manager

**Philosophy:** "Chassis + Driver" - AgentOS is the chassis, Finn is the driver

---

## 📚 Documentation Hierarchy

### 🌟 **START HERE (For New LLMs/Developers):**

```
1. README.md           → Project overview, quick start
2. ROADMAP.md          → What we're building, priorities, phases
3. STATUS.md           → Current state, progress, blockers
4. AGENTIOS_SPEC.md    → Technical details, architecture
```

### 📁 **By Purpose:**

#### **Understanding the Vision:**
- `README.md` - Project overview
- `finn/config/PRD.md` - Product requirements & vision
- `finn/config/AGENTS.md` - Agent architecture philosophy

#### **Development Planning:**
- `ROADMAP.md` - **⭐ CRITICAL** - Development phases, priorities, milestones
- `STATUS.md` - Current progress, blockers, next steps
- `AGENTIOS_SPEC.md` - Technical specification & requirements

#### **Implementation Details:**
- `STRUCTURE.md` - File organization
- `tests/README.md` - Test suite documentation
- Code comments in `/core` and `/finn`

#### **Configuration:**
- `.env` - Environment variables (models, URLs)
- `finn/config/SKILLS.md` - Skill catalog (TBD)
- SOPs in `finn/directives/` (TBD - empty currently)

---

## 🗺️ Document Reading Order

### For Understanding the Project (First Time):
1. **README.md** - Get the big picture
2. **ROADMAP.md** - See what we're building
3. **finn/config/PRD.md** - Understand the vision
4. **AGENTIOS_SPEC.md** - Deep dive into architecture

### For Development Work:
1. **STATUS.md** - What's current state?
2. **ROADMAP.md** - What should I work on?
3. **AGENTIOS_SPEC.md** - How should I build it?
4. **tests/README.md** - How should I test it?

### For Troubleshooting:
1. **STATUS.md** - Known issues section
2. **AGENTIOS_SPEC.md** - Requirements & constraints
3. **tests/README.md** - Test cases to verify

---

## 📊 Key Information Quick Access

### Current Phase & Priority
- **Phase:** 1A - AgentOS Foundation
- **Priority:** Build CORE first (not Finn)
- **Focus:** Model config, skill registry, intent classification
- **Progress:** 40% overall, 70% for current workflow

### Architecture Decisions
- **Models:** Variable-based (in .env), not hardcoded
- **Primary Reasoning Model:** gpt-oss:20b (or similar 20B+ model)
- **Parser/Tool Model:** llama3.1:8b (or similar 7B+ model)
- **Framework:** LangGraph for state management
- **Validation:** Pydantic V2
- **Testing:** 80% coverage target

### What Works vs What Doesn't
- ✅ **Works:** Planner → Actor → Auditor workflow
- ✅ **Works:** Two-stage reasoning pipeline
- ✅ **Works:** Tests (6 tests, all passing)
- ❌ **Missing:** Skill registry
- ❌ **Missing:** Intent classification
- ❌ **Broken:** Auditor verification (just increments step)

### Next Steps (Priority Order)
1. Model configuration to .env
2. Skill registry implementation
3. Intent classifier
4. Enhanced auditor verification

---

## 🎯 For Future LLM Context

### When Starting a New Chat Session:

**Read These First:**
1. `README.md` - Project overview
2. `STATUS.md` - Current state & blockers
3. `ROADMAP.md` - Current phase & priorities

**This Tells You:**
- What the project is (AgentOS + Finn)
- What's implemented vs planned
- What you should work on next
- What constraints/requirements exist

### Critical Context Points

**DO:**
- ✅ Maintain separation: AgentOS (core) vs Finn (domain)
- ✅ Make models configurable (.env)
- ✅ Follow Pydantic V2 patterns
- ✅ Write tests for everything (80% coverage)
- ✅ Use skill registry (when implemented)

**DON'T:**
- ❌ Hardcode model names
- ❌ Put domain logic in /core
- ❌ Use Pydantic V1 patterns (like __init__)
- ❌ Skip tests
- ❌ Break the "chassis + driver" architecture

### Understanding Priorities

**Current Priority:** **CORE FIRST**
1. Complete AgentOS (Phases 1-2)
2. Then integrate Finn (Phase 3)
3. Then production deployment (Phase 4)

**Phase 1 (Current):**
- 1A: Core workflow ✅ 70% done
- 1B: Skill registry ❌ Next up
- 1C: Intent classifier ❌ After 1B
- 1D: Enhanced auditor ❌ After 1C

---

## 📁 File Locations Cheat Sheet

### Critical Core Files:
```
/core/engine.py           - Entry point
/core/graph.py            - LangGraph workflow
/core/nodes/planner.py    - Planning node
/core/nodes/actor.py      - Execution node
/core/nodes/auditor.py    - Verification node
/core/two_stage_client.py - Reasoning pipeline
/core/models.py           - Pydantic schemas
/core/state.py            - State definition
```

### Documentation Files:
```
/README.md                - Project overview
/ROADMAP.md              - Development plan ⭐
/STATUS.md               - Current state ⭐
/AGENTIOS_SPEC.md        - Technical spec ⭐
/STRUCTURE.md            - File organization
/tests/README.md         - Test docs
/finn/config/PRD.md      - Vision & requirements
/finn/config/AGENTS.md   - Architecture
```

### Test Files:
```
/tests/test_planner_pydantic.py - Planner test
/tests/test_actor.py            - Actor test
/tests/test_auditor.py          - Auditor test
/tests/test_graph_routing.py    - Router test
/tests/test_basic_flow.py       - Manual flow test
/tests/test_e2e_workflow.py     - Full E2E test
```

### Finn Files (Not Integrated Yet):
```
/finn/config/              - Configuration
/finn/skills/              - Skills (exist but not used)
/finn/directives/          - SOPs (EMPTY - TBD)
/finn/memory/portfolio.db  - Database
```

---

## 🔍 Common Scenarios

### "What should I work on?"
→ Read `ROADMAP.md` → Check current phase → See "Immediate Next Steps"

### "What's the current status?"
→ Read `STATUS.md` → See progress metrics & known issues

### "How does X work?"
→ Read `AGENTIOS_SPEC.md` → Find component section → See architecture

### "How do I test?"
→ Read `tests/README.md` → Follow patterns in existing tests

### "What's broken?"
→ Read `STATUS.md` → "Known Issues" section

### "What's the vision?"
→ Read `finn/config/PRD.md` → Product requirements

---

## 📈 Metrics to Track

- **Overall Progress:** 40% (as of 2026-01-31)
- **Test Coverage:** ~80%
- **Tests Passing:** 6/6 (100%)
- **Phase 1A:** 70% complete
- **Phase 1B-D:** 0% complete
- **Documentation:** 70% complete

---

## 🚨 Critical Reminders

1. **AgentOS is domain-agnostic** - Keep it that way
2. **Models are variables** - Never hardcode
3. **Skill registry is key** - Don't bypass it (when implemented)
4. **Pydantic V2** - Use `@model_validator`, not `__init__`
5. **Test everything** - 80% coverage minimum

---

**This document updated:** 2026-01-31  
**Purpose:** Quick reference for LLMs/developers entering the project  
**Usage:** Read this first, then dive into specific docs
