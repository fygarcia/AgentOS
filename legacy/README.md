# Legacy Code Archive

This folder contains deprecated code and documents that have been superseded by newer implementations.

## Moved on: 2026-01-31

### Test Files (Debugging & Development)

All of the following test files were used during the development and debugging of the Pydantic AI + Ollama integration. They have been superseded by production tests.

**Deprecated Test Files:**
- `test_both_models.py` - Tested both models for structured output
- `test_env_before_import.py` - Environment variable timing test
- `test_explicit_client.py` - OllamaProvider instantiation test
- `test_langgraph.py` - Old mock-based LangGraph test (incompatible with new two-stage planner)
- `test_model_settings.py` - model_settings parameter test
- `test_ollama_connection.py` - Basic Ollama connectivity test
- `test_ollama_env.py` - Environment variable tests
- `test_ollama_explicit.py` - Explicit provider tests
- `test_ollama_final.py` - Final Ollama test iteration
- `test_ollama_json_mode.py` - Native JSON mode testing
- `test_output_type.py` - output_type parameter test
- `test_plan_output.py` - Plan output validation
- `test_provider_usage.py` - Provider usage patterns
- `test_pydantic_api.py` - Pydantic AI API exploration
- `test_result.py` - Result object testing
- `test_two_stage.py` - Two-stage pipeline development test
- `test_with_env.py` - Environment variable loading test

**Current Production Tests** (still in `/tests`):
- `test_planner_pydantic.py` - Production Planner node test
- `test_actor.py` - Actor node test
- `test_basic_flow.py` - Basic workflow test

### Core LLM Implementations (Superseded)

**Deprecated Core Files:**
- `ollama_json_client.py` - Direct Ollama integration using native JSON mode
  - **Issue:** Single-stage approach didn't provide enough reasoning depth
  - **Superseded by:** `two_stage_client.py` (separates reasoning from parsing)

**Current Production Implementation:**
- `/core/two_stage_client.py` - Production two-stage pipeline for Ollama:
  1. **Stage 1:** gpt-oss:20b generates detailed reasoning (4500-5000 chars)
  2. **Stage 2:** llama3.1:8b parses reasoning into validated JSON Plan

**Still Active:**
- `/core/llm.py` - Base LLM wrapper (still used by Actor and Auditor nodes)
- `/core/llm_pydantic.py` - Pydantic AI wrapper (kept as fallback for non-Ollama providers like OpenAI, Anthropic, Google)
- `/core/models.py` - Pydantic data models for Plan, PlanStep, etc.

### Output Files (Testing Artifacts)

**Deprecated Output Files:**
- `hello.txt` - Test file from "Hello World" workflow test
- `full_test.log` - Test execution logs
- `test_full_output.txt` - Full test output capture
- `test_output.txt` - Test output capture

## Architecture Evolution

### Timeline of LLM Integration Approaches

1. **Initial Implementation** (`llm.py`)
   - Basic request/response with Ollama
   - No structured output validation
   - Still used by Actor/Auditor for simple text generation

2. **Native JSON Mode** (`ollama_json_client.py`) ❌ **DEPRECATED**
   - Used Ollama's native `format: "json"` parameter
   - Better but lacked reasoning depth
   - Learned: Need dedicated reasoning step

3. **Two-Stage Pipeline** (`two_stage_client.py`) ✅ **PRODUCTION**
   - Stage 1: Reasoning model generates detailed plan as text
   - Stage 2: Parser model structures text into validated JSON
   - Result: 7-8 step plans with full reasoning in 120-160 seconds
   - Status: Working reliably in production for Ollama

4. **Pydantic AI Integration** (`llm_pydantic.py`) ✅ **ACTIVE**
   - Fallback for non-Ollama providers (OpenAI, Anthropic, Google)
   - Uses Pydantic AI's built-in structured output
   - Status: Active as fallback provider

## Why test_langgraph.py Was Deprecated

**Issue:** The test was failing and is incompatible with the new architecture.

**Root Cause:**
1. The test uses `LLM_PROVIDER=mock` to avoid requiring actual LLM API calls
2. The old `MockLLM` class in `llm.py` has hardcoded responses for the OLD architecture
3. The NEW `planner_node` uses the two-stage client (`TwoStageOllamaClient`) which doesn't work with mock mode
4. When provider is "mock", the planner falls back to `get_pydantic_agent` with `model="test"`, which doesn't provide actual mock responses

**Old Architecture (what the test expected):**
```
Planner → MockLLM → Returns JSON plan directly
Actor → MockLLM → Returns Python code
Auditor → MockLLM → Returns audit result
```

**New Architecture (current production):**
```
Planner → TwoStageOllamaClient → Stage 1: Reasoning → Stage 2: Parsing → Plan
Actor → OllamaLLM → Returns Python code  
Auditor → OllamaLLM → Returns audit result
```

**Recommendation:**
- Use `test_basic_flow.py` for end-to-end workflow testing with mock provider
- Use `test_planner_pydantic.py` for testing the planner with actual Ollama models
- If you need integration testing, run with a real Ollama instance (`LLM_PROVIDER=ollama`)

**Date Deprecated:** 2026-01-31

## Migration Notes

If you need to reference any of these deprecated files, they remain here for historical context. However, **do not use them in new code** - they have known issues that have been resolved in the current production implementation.

## Documentation

- See `DEPRECATED.md` for the original deprecation notice
- See `/core/nodes/planner.py` for detailed documentation of the current two-stage approach
- See conversation history (d967d821-0dd9-42da-8d1b-8ab067ecac40) for the full integration journey

---

**Last Updated:** 2026-01-31  
**Status:** Archived - Keep for reference only
