"""
Configuration Management for AgentOS
====================================

Centralized configuration loading and validation for all AgentOS components.

This module handles:
- Environment variable loading
- Model configuration
- Provider selection
- Default fallbacks
- Validation

Usage:
    from core.config import config
    
    # Get model names
    reasoning_model = config.REASONING_MODEL
    parser_model = config.PARSER_MODEL
    
    # Get provider settings
    provider = config.LLM_PROVIDER
    base_url = config.OLLAMA_BASE_URL
"""

import os
from typing import Optional, Literal
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class AgentOSConfig:
    """Centralized configuration for AgentOS."""
    
    # ========================================================================
    # LLM PROVIDER CONFIGURATION
    # ========================================================================
    
    LLM_PROVIDER: Literal["ollama", "mock", "google"] = "ollama"
    """Which LLM provider to use: ollama (local), mock (testing), google (cloud)"""
    
    # ========================================================================
    # OLLAMA CONFIGURATION
    # ========================================================================
    
    OLLAMA_BASE_URL: str = "http://192.168.4.102:11434"
    """Base URL for Ollama server (without /v1 or /api suffix)"""
    
    REASONING_MODEL: str = "gpt-oss:20b"
    """
    Model for high-level reasoning and planning.
    Should be a large model (20B+) with strong reasoning capabilities.
    Examples: gpt-oss:20b, deepseek-r1-32b, qwen2.5-think-7b
    """
    
    PARSER_MODEL: str = "llama3.1:8b"
    """
    Model for parsing text into structured JSON.
    Should be good at following formats and structured output.
    Examples: llama3.1:8b, qwen2.5-coder-7b, codellama:7b
    """
    
    TOOL_MODEL: str = "llama3.1:8b"
    """
    Model for tool calling and code generation.
    Can be the same as PARSER_MODEL or a specialized code model.
    Examples: llama3.1:8b, qwen2.5-coder-7b, codellama:7b
    """

    EMBEDDING_MODEL: str = "nomic-embed-text"
    """
    Model for generating vector embeddings.
    Must be an embedding model loaded in Ollama.
    Examples: nomic-embed-text, mxbai-embed-large, all-minilm
    """
    
    # ========================================================================
    # GOOGLE GEMINI CONFIGURATION (Future)
    # ========================================================================
    
    GOOGLE_API_KEY: Optional[str] = None
    """Google API key for Gemini models"""
    
    GOOGLE_REASONING_MODEL: str = "gemini-1.5-pro-latest"
    """Gemini model for reasoning"""
    
    GOOGLE_PARSER_MODEL: str = "gemini-1.5-flash-latest"
    """Gemini model for parsing/tools"""
    
    # ========================================================================
    # OBSERVABILITY
    # ========================================================================
    
    ENABLE_OBSERVABILITY: bool = True
    """Enable LangSmith tracing"""
    
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate configuration values."""
        # Validate provider
        valid_providers = ["ollama", "mock", "google"]
        if self.LLM_PROVIDER not in valid_providers:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {self.LLM_PROVIDER}. "
                f"Must be one of: {valid_providers}"
            )
        
        # Validate Ollama URL if using Ollama
        if self.LLM_PROVIDER == "ollama":
            if not self.OLLAMA_BASE_URL:
                raise ValueError("OLLAMA_BASE_URL must be set when using ollama provider")
            
            if not self.OLLAMA_BASE_URL.startswith("http"):
                raise ValueError(
                    f"OLLAMA_BASE_URL must start with http:// or https://, "
                    f"got: {self.OLLAMA_BASE_URL}"
                )
        
        # Validate Google API key if using Google
        if self.LLM_PROVIDER == "google":
            if not self.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY must be set when using google provider")
    
    @classmethod
    def from_env(cls) -> "AgentOSConfig":
        """
        Load configuration from environment variables.
        
        Returns:
            AgentOSConfig instance with values from .env
        """
        # Helper to convert string to bool
        def to_bool(value: Optional[str], default: bool = False) -> bool:
            if value is None:
                return default
            return value.lower() in ("true", "1", "yes", "on")
        
        # Determine provider
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        # Load Ollama configuration
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://192.168.4.102:11434")
        # Sanitize URL: remove /v1, /api, and trailing slashes
        if ollama_base_url:
            ollama_base_url = ollama_base_url.rstrip('/').rstrip('/v1').rstrip('/api').rstrip('/')

        
        # Load model names based on provider
        if provider == "ollama":
            reasoning_model = os.getenv("MODEL_LOCAL_PLANNER", "gpt-oss:20b")
            parser_model = os.getenv("MODEL_LOCAL_ACTOR", "llama3.1:8b")
            tool_model = os.getenv("MODEL_LOCAL_ACTOR", "llama3.1:8b")
        elif provider == "google":
            reasoning_model = os.getenv("MODEL_PLANNER", "gemini-1.5-pro-latest")
            parser_model = os.getenv("MODEL_ACTOR", "gemini-1.5-flash-latest")
            tool_model = parser_model
        else:  # mock
            reasoning_model = "mock"
            parser_model = "mock"
            tool_model = "mock"
        
        return cls(
            LLM_PROVIDER=provider,
            OLLAMA_BASE_URL=ollama_base_url,
            REASONING_MODEL=reasoning_model,
            PARSER_MODEL=parser_model,
            TOOL_MODEL=tool_model,
            GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"),
            GOOGLE_REASONING_MODEL=os.getenv("MODEL_PLANNER", "gemini-1.5-pro-latest"),
            GOOGLE_PARSER_MODEL=os.getenv("MODEL_ACTOR", "gemini-1.5-flash-latest"),
            ENABLE_OBSERVABILITY=to_bool(os.getenv("ENABLE_OBSERVABILITY"), default=True)
        )
    
    def get_active_models(self) -> dict:
        """
        Get the currently active model configuration.
        
        Returns:
            Dict with reasoning_model, parser_model, tool_model
        """
        return {
            "reasoning_model": self.REASONING_MODEL,
            "parser_model": self.PARSER_MODEL,
            "tool_model": self.TOOL_MODEL,
            "provider": self.LLM_PROVIDER
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"AgentOSConfig(\n"
            f"  provider={self.LLM_PROVIDER},\n"
            f"  reasoning_model={self.REASONING_MODEL},\n"
            f"  parser_model={self.PARSER_MODEL},\n"
            f"  tool_model={self.TOOL_MODEL},\n"
            f"  ollama_url={self.OLLAMA_BASE_URL}\n"
            f")"
        )


# ============================================================================
# GLOBAL CONFIG INSTANCE
# ============================================================================

# Load configuration once at import time
config = AgentOSConfig.from_env()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_reasoning_model() -> str:
    """Get the reasoning model name."""
    return config.REASONING_MODEL


def get_parser_model() -> str:
    """Get the parser model name."""
    return config.PARSER_MODEL


def get_tool_model() -> str:
    """Get the tool/actor model name."""
    return config.TOOL_MODEL


def get_ollama_base_url() -> str:
    """Get Ollama base URL."""
    return config.OLLAMA_BASE_URL


def get_provider() -> str:
    """Get active LLM provider."""
    return config.LLM_PROVIDER


def reload_config():
    """Reload configuration from environment (useful for testing)."""
    global config
    load_dotenv(override=True)
    config = AgentOSConfig.from_env()


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AgentOS Configuration")
    print("=" * 70)
    print(config)
    print("\n" + "=" * 70)
    print("Active Models:")
    print("=" * 70)
    for key, value in config.get_active_models().items():
        print(f"  {key}: {value}")
    print("\n✅ Configuration loaded successfully!")
