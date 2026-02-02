"""Test proper Pydantic AI Ollama usage."""

from pydantic_ai import Agent
from pydantic_ai.providers.ollama import OllamaProvider

print("Testing Pydantic AI Ollama Provider usage...")

# Create the provider
provider = OllamaProvider(base_url="http://192.168.4.102:11434")

print(f"Provider created: {provider}")
print(f"Provider base_url: {provider.base_url}")

# Try creating agent with provider and model_name
try:
    print("\nAttempt 1: Agent(provider, model_name='llama3.1:8b')")
    agent: Agent[None, str] = Agent(provider, model_name='llama3.1:8b')
    result = agent.run_sync('Say hello')
    print(f"✅ Success! Result: {result.output}")
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
