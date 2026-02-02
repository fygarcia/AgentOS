# DEPRECATED TEST FILES - For Cleanup
# ====================================
#  
# The following test files were used during development/debugging
# and can be safely removed after final integration testing.
#
# DEBUGGING TESTS (Pydantic AI connection testing):
# - test_both_models.py - Tested both models for structured output
# - test_env_before_import.py - Environment variable timing test
# - test_explicit_client.py - OllamaProvider instantiation test
# - test_model_settings.py - model_settings parameter test
# - test_ollama_connection.py - Basic Ollama connectivity
# - test_ollama_env.py - Environment variable tests
# - test_ollama_explicit.py - Explicit provider tests
# - test_ollama_final.py - Final Ollama test iteration
# - test_ollama_json_mode.py - Native JSON mode testing
# - test_output_type.py - output_type parameter test
# - test_plan_output.py - Plan output validation
# - test_provider_usage.py - Provider usage patterns
# - test_pydantic_api.py - Pydantic AI API exploration
# - test_result.py - Result object testing
# - test_two_stage.py - Two-stage pipeline development test
# - test_with_env.py - Environment variable loading test
#
# KEEP THESE (Production tests):
# ✅ test_planner_pydantic.py - Production Planner node test
# ✅ test_actor.py - Actor node test
# ✅ test_langgraph.py - LangGraph integration test
# ✅ test_basic_flow.py - Basic workflow test
#
# RECOMMENDATION:
# After confirming production tests pass, run:
# ```bash
# rm tests/test_both_models.py tests/test_env_before_import.py \
#    tests/test_explicit_client.py tests/test_model_settings.py \
#    tests/test_ollama_*.py tests/test_output_type.py \
#    tests/test_plan_output.py tests/test_provider_usage.py \
#    tests/test_pydantic_api.py tests/test_result.py \
#    tests/test_two_stage.py tests/test_with_env.py
# ```
