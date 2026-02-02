"""Test with environment variable set in PowerShell."""

import os

# Check if env var is set
ollama_url = os.getenv("OLLAMA_BASE_URL")
print(f"OLLAMA_BASE_URL from environment: {ollama_url}")

if not ollama_url:
    print("❌ OLLAMA_BASE_URL not set!")
    exit(1)

from pydantic_ai import Agent
import asyncio

async def test():
    agent: Agent[None, str] = Agent('ollama:llama3.1:8b')
    result = await agent.run('Say hello')
    print(f"✅ Result: {result.output}")

asyncio.run(test())
