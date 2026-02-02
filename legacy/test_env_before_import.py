"""Test using Ollama with environment variable."""

import os

# Set OLLAMA_BASE_URL before importing
os.environ["OLLAMA_BASE_URL"] = "http://192.168.4.102:11434"

from pydantic_ai import Agent

print("Testing with OLLAMA_BASE_URL environment variable...")

try:
    # Now try string format with env var
    agent: Agent[None, str] = Agent('ollama:llama3.1:8b')
    print("Agent created, running test...")
    result = agent.run_sync('Say "Hello from Ollama!"')
    print(f"\n✅ SUCCESS!")
    print(f"Result: {result.output}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
