"""Test Pydantic AI with explicit AsyncOpenAI client for Ollama."""

from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.providers.ollama import OllamaProvider
import asyncio

async def test_ollama():
    print("Creating OllamaProvider with AsyncOpenAI client...")
    
    # Create AsyncOpenAI client pointing to Ollama
    openai_client = AsyncOpenAI(
        base_url="http://192.168.4.102:11434/v1",
        api_key="not-needed"  # Ollama doesn't need API key
    )
    
    # Create Ollama provider with the client
    provider = OllamaProvider(openai_client=openai_client)
    
    # Create agent with the provider
    agent: Agent[None, str] = Agent(provider, model_name='llama3.1:8b')
    
    print("Running agent...")
    result = await agent.run('Say "Hello from Ollama!"')
    
    print(f"\n✅ SUCCESS!")
    print(f"Result: {result.output}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
