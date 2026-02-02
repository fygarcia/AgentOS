"""Test Pydantic AI Ollama with explicit base URL."""

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel

print("Testing Pydantic AI with Ollama using explicit model configuration...")

try:
    # Create Ollama model with explicit base URL
    model = OllamaModel(
        model_name='llama3.1:8b',
        base_url='http://192.168.4.102:11434'
    )
    
    agent: Agent[None, str] = Agent(model)
    result = agent.run_sync('Say "Hello from Ollama!"')
    print(f"✅ Success! Result: {result.output}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
