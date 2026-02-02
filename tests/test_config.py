"""
TEST: Configuration Management
===============================
Tests the centralized configuration system to ensure models are properly loaded.

TEST FLOW:
1. INPUT:  .env file with model configurations
2. LOAD:   Configuration system loads and validates
3. OUTPUT: Verify correct models are accessible
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import config, get_reasoning_model, get_parser_model, get_tool_model

def print_section(title, char="="):
    """Print a clear section header."""
    print(f"\n{char*70}")
    print(f"  {title}")
    print(f"{char*70}")

def test_configuration():
    """Test configuration loading and access."""
    
    print_section("TEST: Configuration Management")
    
    # ========================================================================
    # STEP 1: VERIFY CONFIGURATION LOADED
    # ========================================================================
    print_section("STEP 1: Configuration Loaded", "-")
    
    print(f"Provider:         {config.LLM_PROVIDER}")
    print(f"Reasoning Model:  {config.REASONING_MODEL}")
    print(f"Parser Model:     {config.PARSER_MODEL}")
    print(f"Tool Model:       {config.TOOL_MODEL}")
    print(f"Ollama Base URL:  {config.OLLAMA_BASE_URL}")
    
    # ========================================================================
    # STEP 2: VERIFY CONVENIENCE FUNCTIONS
    # ========================================================================
    print_section("STEP 2: Convenience Functions", "-")
    
    reasoning = get_reasoning_model()
    parser = get_parser_model()
    tool = get_tool_model()
    
    print(f"get_reasoning_model(): {reasoning}")
    print(f"get_parser_model():    {parser}")
    print(f"get_tool_model():      {tool}")
    
    # ========================================================================
    # STEP 3: VERIFY ACTIVE MODELS
    # ========================================================================
    print_section("STEP 3: Active Models", "-")
    
    active = config.get_active_models()
    for key, value in active.items():
        print(f"  {key}: {value}")
    
    # ========================================================================
    # STEP 4: VALIDATION
    # ========================================================================
    print_section("STEP 4: VALIDATION", "-")
    
    all_passed = True
    
    try:
        # Check that configuration exists
        assert config is not None, "Config should not be None"
        
        # Check provider
        assert config.LLM_PROVIDER in ["ollama", "mock", "google"], \
            f"Invalid provider: {config.LLM_PROVIDER}"
        
        # Check models are strings
        assert isinstance(config.REASONING_MODEL, str), "Reasoning model should be string"
        assert isinstance(config.PARSER_MODEL, str), "Parser model should be string"
        assert isinstance(config.TOOL_MODEL, str), "Tool model should be string"
        
        # Check models are not empty
        assert len(config.REASONING_MODEL) > 0, "Reasoning model should not be empty"
        assert len(config.PARSER_MODEL) > 0, "Parser model should not be empty"
        assert len(config.TOOL_MODEL) > 0, "Tool model should not be empty"
        
        # Check ollama URL if ollama provider
        if config.LLM_PROVIDER == "ollama":
            assert config.OLLAMA_BASE_URL.startswith("http"), \
                f"Ollama URL should start with http, got: {config.OLLAMA_BASE_URL}"
        
        # Check convenience functions return same values
        assert get_reasoning_model() == config.REASONING_MODEL, \
            "get_reasoning_model() should return config.REASONING_MODEL"
        assert get_parser_model() == config.PARSER_MODEL, \
            "get_parser_model() should return config.PARSER_MODEL"
        assert get_tool_model() == config.TOOL_MODEL, \
            "get_tool_model() should return config.TOOL_MODEL"
        
        # Check active models dict
        assert "reasoning_model" in active, "Active models should have reasoning_model"
        assert "parser_model" in active, "Active models should have parser_model"
        assert "tool_model" in active, "Active models should have tool_model"
        assert "provider" in active, "Active models should have provider"
        
        print("✅ All assertions passed!")
        print("✅ Configuration system working correctly")
        print("✅ Models loaded from .env successfully")
        print(f"✅ Using provider: {config.LLM_PROVIDER}")
        print(f"✅ Reasoning model: {config.REASONING_MODEL}")
        print(f"✅ Parser/Tool model: {config.PARSER_MODEL}")
        
        print_section("TEST RESULT: PASSED ✅")
        return True
        
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
        print_section("TEST RESULT: FAILED ❌")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print_section("TEST RESULT: ERROR ❌")
        return False

if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1)
