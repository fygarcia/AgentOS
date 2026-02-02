"""Test Pydantic AI with Ollama using environment variables."""

import os

# Set the environment variable BEFORE importing pydantic_ai
os.environ["OLLAMA_BASE_URL"] = "http://192.168.4.102:11434"

from pydantic_ai import Agent

print(f"OLLAMA_BASE_URL set to: {os.environ.get('OLLAMA_BASE_URL')}")
print("\nTesting connection to Ollama with llama3.1:8b...")

try:
    # Use string format with env var set
    agent: Agent[None, str] = Agent('ollama:llama3.1:8b')
    print("Agent created, running test...")
    
    result = agent.run_sync('Say "Hello from Ollama!"')
    print(f"\n✅ SUCCESS!")
    print(f"Result: {result.output}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
