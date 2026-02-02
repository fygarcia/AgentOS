"""Test Pydantic AI Ollama connection."""

import os
os.environ["OLLAMA_BASE_URL"] = "http://192.168.4.102:11434"

from pydantic_ai import Agent
from pydantic import BaseModel

class SimpleResponse(BaseModel):
    message: str

print("Testing Pydantic AI with Ollama...")

try:
    # Test with llama3.1:8b first (smaller model)
    agent: Agent[None, str] = Agent('ollama:llama3.1:8b')
    result = agent.run_sync('Say "Hello from Ollama!"')
    print(f"✅ Success! Result: {result.output}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
