"""
Pydantic AI wrapper for structured, type-safe LLM interactions.

NOTE: For Ollama, set OLLAMA_BASE_URL=http://host:port/v1 in .env
The /v1 suffix is required for OpenAI-compatible API endpoints.
"""

from typing import Type, TypeVar
from pydantic import BaseModel
from pydantic_ai import Agent
from core.config import config

T = TypeVar('T', bound=BaseModel)

def get_pydantic_agent(role: str, result_type: Type[T], instructions: str = "") -> Agent[None, T]:
    """
    Factory function to create a Pydantic AI agent.
    
    Args:
        role: The role of the agent (Planner, Actor, Auditor)
        result_type: Pydantic model class for the output (not used directly, but T is inferred)
        instructions: System instructions for the agent
    
    Returns:
        Configured Pydantic AI agent
    """
    provider = config.LLM_PROVIDER
    
    # Build model string based on provider
    if provider == "ollama":
        # Select model based on role
        if role in ["Planner", "Auditor"]:
            model_name = config.REASONING_MODEL
        else:
            model_name = config.TOOL_MODEL
        
        # Use string format - OLLAMA_BASE_URL env var must be set
        model = f"ollama:{model_name}"
        
    elif provider == "openai":
        model = "openai:gpt-4"
        
    elif provider == "anthropic":
        model = "anthropic:claude-sonnet-4-0"
        
    elif provider == "google":
        if role in ["Planner", "Auditor"]:
            model = "gemini:gemini-1.5-pro"
        else:
            model = "gemini:gemini-1.5-flash"
    else:
        # Mock/test mode
        model = "test"
    
    # Create the agent - type annotation Agent[None, T] specifies output type
    agent: Agent[None, T] = Agent(model, system_prompt=instructions)
    
    return agent

def get_planner_instructions() -> str:
    """Get system instructions for the Planner agent."""
    return """You are the Planner agent. Your role is to analyze the user's intent and create a structured execution plan.

The plan must be a list of steps, where each step has:
- role: Either "Actor" (for code execution) or "Auditor" (for verification)
- instruction: A clear, actionable instruction for that role

Break down complex tasks into simple, atomic steps.
Always include at least one Auditor step to verify the work.

Be concise and focused. Do not be conversational."""

def get_actor_instructions() -> str:
    """Get system instructions for the Actor agent."""
    return """You are the Actor agent. Your role is to write Python code to accomplish tasks.

Return ONLY clean, executable Python code.
Do NOT include markdown formatting, comments, or explanations unless specifically asked.
The code should be production-ready and handle errors gracefully.

You have access to these tools:
- create_skill(name, path): Create a new skill
- Standard Python libraries (os, sys, subprocess, json, etc.)"""

def get_auditor_instructions() -> str:
    """Get system instructions for the Auditor agent."""
    return """You are the Auditor agent. Your role is to verify that tasks were completed correctly.

Check the instruction and determine if it was successfully accomplished.
Return:
- status: "success" if the task was completed correctly, "failure" otherwise
- message: A brief explanation of your findings

Be thorough but concise."""
