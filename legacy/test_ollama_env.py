"""Test Pydantic AI with Ollama - trying different base URL configs."""

import os

# Try setting base URL via environment variable
os.environ["OLLAMA_BASE_URL"] = "http://192.168.4.102:11434"

from pydantic_ai import Agent

print("Test 1: Using OLLAMA_BASE_URL env var")
try:
    agent: Agent[None, str] = Agent('ollama:llama3.1:8b')
    result = agent.run_sync('Say hello')
    print(f"✅ Success with OLLAMA_BASE_URL! Result: {result.output[:50]}")
except Exception as e:
    print(f"❌ Failed: {str(e)[:100]}")

# Try with different env var names
print("\nTest 2: Using localhost (default)")
os.environ.pop("OLLAMA_BASE_URL", None)
os.environ["OLLAMA_HOST"] = "http://192.168.4.102:11434"

try:
    agent2: Agent[None, str] = Agent('ollama:llama3.1:8b')
    result2 = agent2.run_sync('Say hello')
    print(f"✅ Success with OLLAMA_HOST! Result: {result2.output[:50]}")
except Exception as e:
    print(f"❌ Failed: {str(e)[:100]}")
