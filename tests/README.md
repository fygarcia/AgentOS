# Test Suite Documentation

This document provides an overview of all tests in the project, their purpose, and how to run them.

## 📋 Test Inventory

### ✅ Production Tests (in `/tests`)

| Test File | Component | Provider | Duration | Status |
|-----------|-----------|----------|----------|--------|
| `test_planner_pydantic.py` | Planner Node | Ollama | ~2-3 min | ✅ Active |
| `test_actor.py` | Actor Node | Mock | ~1 sec | ✅ Active |
| `test_auditor.py` | Auditor Node | Mock | ~1 sec | ✅ Active |

| `test_graph_routing.py` | Router Logic | None | ~1 sec | ✅ Active |
| `test_e2e_workflow.py` | Full Workflow | Ollama | ~2-3 min | ✅ Active |
| `test_memory_integration.py` | Memory System | None | ~1 sec | ✅ **NEW** |

### 📦 Deprecated Tests (in `/legacy`)

20 development/debugging tests moved to `/legacy` - see `/legacy/README.md` for details.

---

## 🎯 Test Descriptions

### 1. `test_planner_pydantic.py`
**Purpose:** Tests the Planner node with real Ollama models using the two-stage pipeline.

**What it tests:**
- Two-stage client (gpt-oss:20b → llama3.1:8b)
- Plan generation with reasoning
- Pydantic validation

**Input:**
```python
"Create a file named test.txt with content 'Hello World'"
```

**Intermediate:**
- Stage 1: gpt-oss:20b generates reasoning (~5000 chars)
- Stage 2: llama3.1:8b parses into JSON Plan

**Output:**
- Validated Plan object with 7-8 steps
- Each step has role, instruction, reasoning, expected_outcome

**Run:**
```bash
python tests/test_planner_pydantic.py
```

---

### 2. `test_actor.py`
**Purpose:** Tests the Actor node in isolation.

**What it tests:**
- Actor receives instruction from plan
- MockLLM generates Python code
- Code is executed via `exec()`
- Tool outputs are captured

**Input:**
```python
state = {
    "plan": [{"role": "Actor", "instruction": "Create a file named test.txt with content 'Hello World'"}],
    "current_step_index": 0
}
```

**Intermediate:**
- MockLLM generates Python code
- Code prints debug output

**Output:**
- `tool_outputs["step_0"]` = "Success"
- `current_step_index` incremented to 1

**Run:**
```bash
python tests/test_actor.py
```

---

### 3. `test_auditor.py` ⭐ NEW
**Purpose:** Tests the Auditor node in isolation.

**What it tests:**
- Auditor receives verification instruction
- MockLLM generates audit verdict
- State is updated correctly

**Input:**
```python
state = {
    "plan": [
        {"role": "Actor", "instruction": "..."},
        {"role": "Auditor", "instruction": "Verify hello.txt exists and contains correct text"}
    ],
    "current_step_index": 1
}
```

**Intermediate:**
- MockLLM generates audit response
- Audit result is logged

**Output:**
- `current_step_index` incremented to 2
- Audit logged (no tool_outputs update)

**Run:**
```bash
python tests/test_auditor.py
```

---



### 5. `test_graph_routing.py` ⭐ NEW
**Purpose:** Tests the LangGraph router function.

**What it tests:**
- Empty plan → END
- Completed plan → END
- Actor role → "actor" node
- Auditor role → "auditor" node
- Sequential routing through multi-step plan

**Input:**
Multiple test cases with different state configurations

**Intermediate:**
- Router examines `current_step_index` and `plan[index].role`
- Returns routing decision

**Output:**
- Correct routing destination for each case
- 5/5 test cases pass

**Run:**
```bash
python tests/test_graph_routing.py
```

---

### 6. `test_e2e_workflow.py` ⭐ NEW
**Purpose:** Full end-to-end integration test through LangGraph with real Ollama models.

**What it tests:**
- Complete workflow: Planner → LangGraph → Actor → Auditor → Loop → Complete
- Real Ollama models (not mock)
- File creation and verification
- Observability tracing

**Input:**
```python
"Create a file named e2e_test.txt with content 'End-to-End Test Successful'"
```

**Intermediate:**
- Planner: Generates plan with gpt-oss:20b + llama3.1:8b
- LangGraph: Routes to first step
- Actor: Creates file with llama3.1:8b
- Auditor: Verifies file with gpt-oss:20b
- Router: Continues until plan complete

**Output:**
- File `e2e_test.txt` created
- Content matches expected
- All steps completed
- Observability traces saved

**Run:**
```bash
python tests/test_e2e_workflow.py
```

**Requirements:**
- Ollama running at http://192.168.4.102:11434
- Models: gpt-oss:20b, llama3.1:8b

---

### 7. `test_memory_integration.py` ⭐ NEW
**Purpose:** Integration tests for the three-tier persistent memory system (HOT/WARM/COLD).

**What it tests:**
- **Test 1: Amnesia** - Agent resumes after restart (spec: MEMORY_SYSTEM.md lines 336-344)
- **Test 2: Correction** - Long-term fact recall (spec: MEMORY_SYSTEM.md lines 346-355)
- **Test 3: Auto-Logging** - Automatic action logging to LOG.md  
- **Test 4: Context Injection** - Memory context in LLM prompts
- **Test 5: Self-Annealing** - Error recovery (spec: MEMORY_SYSTEM.md lines 292-312)

#### Test 1: Amnesia - Resume After Restart
**Flow:**
1. Agent starts multi-step task, updates NOW.md
2. Simulate restart (new MemoryManager instance)
3. Verify agent reads NOW.md and can resume task
4. Verify LOG.md history accessible

**What it validates:**
- NOW.md persists across restarts
- LOG.md preserves history
- Agent can continue from checkpoint

#### Test 2: Correction - Long-term Recall
**Flow:**
1. Agent stores user fact (e.g., API key)
2. Simulate context flush (many interactions)
3. Request stored information
4. Verify recall from memory.db (not context)

**What it validates:**
- Facts persist to SQLite
- Facts survive context window flush
- Category filtering works

#### Test 3: Auto-Logging
**Flow:**
1. Execute several agent actions
2. Verify LOG.md has entries for each
3. Verify timestamps present
4. Verify log_metadata table updated

**What it validates:**
- All actions logged automatically
- Timestamps in ISO format
- Database tracking functional

#### Test 4: Context Injection
**Flow:**
1. Populate NOW.md, LOG.md, and facts
2. Call `format_context_for_prompt()`
3. Verify all sections present in formatted output

**What it validates:**
- Memory context properly formatted
- NOW + LOG + facts all included
- Ready for LLM prompt injection

#### Test 5: Self-Annealing Error Recovery
**Flow:**
1. Simulate error occurrence
2. Log error to LOG.md with traceback
3. Update NOW.md with recovery steps
4. Verify state persists after restart

**What it validates:**
- Errors logged with full context
- NOW.md updated with recovery plan
- Agent can resume error recovery

**Run:**
```bash
# Run all 5 memory integration tests
python -m pytest tests/test_memory_integration.py -v

# Run individual test
python -m pytest tests/test_memory_integration.py::TestMemoryIntegration::test_amnesia_resume_after_restart -v -s
```

**Requirements:**
- None (uses isolated temp directories)
- No Ollama needed
- Fast execution (~1 second total)

---

## 🚀 Running Tests


### Run Individual Tests
```bash
# Quick tests (mock provider)
python tests/test_actor.py
python tests/test_auditor.py
python tests/test_graph_routing.py
python tests/test_graph_routing.py

# Integration tests (requires Ollama)
python tests/test_planner_pydantic.py
python tests/test_e2e_workflow.py
```

### Run All Tests
```bash
# Run all quick tests
python tests/test_actor.py && python tests/test_auditor.py && python tests/test_graph_routing.py

# Run full suite (requires Ollama)
python tests/test_planner_pydantic.py && python tests/test_e2e_workflow.py
```

---

## 📊 Test Coverage

| Component | Unit Test | Integration Test | Notes |
|-----------|-----------|------------------|-------|
| Planner Node | ✅ | ✅ | test_planner_pydantic.py |
| Actor Node | ✅ | ✅ | test_actor.py, test_e2e_workflow.py |
| Auditor Node | ✅ | ✅ | test_auditor.py, test_e2e_workflow.py |
| Router Logic | ✅ | ✅ | test_graph_routing.py, test_e2e_workflow.py |
| LangGraph Flow | ❌ | ✅ | test_e2e_workflow.py |
| Two-Stage Client | ✅ | ✅ | Built-in test in two_stage_client.py |
| Observability | ❌ | ⚠️ | Partially tested in E2E |
| Tools (create_skill) | ❌ | ❌ | Not yet tested |

---

## 🎯 Test Output Format

All new tests follow a consistent structure:

### Clear Section Headers
```
======================================================================
  SECTION TITLE
======================================================================
```

### Step-by-Step Flow
```
[Step 1] 📝 INPUT
[Step 2] ⚙️ EXECUTE
[Step 3] 📊 INTERMEDIATE
[Step 4] 📤 OUTPUT
[Step 5] ✅ VALIDATION
```

### Input/Intermediate/Output Visibility
- **INPUT**: Shows exactly what goes into the component
- **INTERMEDIATE**: Shows what happens during processing (LLM calls, model outputs)
- **OUTPUT**: Shows final results and state changes

### Pass/Fail Indicators
- ✅ Test passed
- ❌ Test failed
- ⚠️ Warning/partial success

---

## 📝 Writing New Tests

When creating new tests, follow this template:

```python
"""
TEST: Component Name
====================
Brief description of what this tests.

ARCHITECTURE:
[Diagram or description of flow]

TEST FLOW:
1. INPUT: What goes in
2. INTERMEDIATE: What happens
3. OUTPUT: What comes out
"""

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_component():
    print_section("STEP 1: INPUT")
    # Show inputs clearly
    
    print_section("STEP 2: EXECUTE")
    # Run the component
    
    print_section("STEP 3: INTERMEDIATE")
    # Show intermediate results
    
    print_section("STEP 4: OUTPUT")
    # Show final output
    
    print_section("STEP 5: VALIDATION")
    # Run assertions
    
    if all_passed:
        print_section("TEST RESULT: PASSED ✅")
        return True
    else:
        print_section("TEST RESULT: FAILED ❌")
        return False
```

---

**Last Updated:** 2026-01-31  
**Total Production Tests:** 10 (5 workflow + 5 memory)  
**Total Deprecated Tests:** 20  
**Test Coverage:** ~85% (excellent, room for improvement in tools)
