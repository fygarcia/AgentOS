"""Test Pydantic AI with model_settings to enable JSON mode."""

import os
os.environ["LLM_PROVIDER"] = "ollama"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_ai import Agent
from pydantic_ai.models import ModelSettings
from core.models import Plan

print("=" * 70)
print("Testing model_settings for JSON Mode")
print("=" * 70)

# Try with model_settings to pass format parameter
models_to_test = [
    ("llama3.1:8b", "🔧 Tool-calling model"),
    ("gpt-oss:20b", "🧠 Reasoning model")
]

for model_name, description in models_to_test:
    print(f"\n{'='*70}")
    print(f"🤖 MODEL: {model_name} - {description}")
    print(f"{'='*70}")
    
    try:
        # Create agent with JSON mode enabled via model_settings
        agent = Agent(
            f'ollama:{model_name}',
            output_type=Plan,
            system_prompt="Generate a structured execution plan.",
            model_settings=ModelSettings(
                extra_body={"format": "json"}  # Try passing format parameter
            )
        )
        
        print("Agent created, running", end="", flush=True)
        result = agent.run_sync("Create a file named test.txt with 'Hello World'")
        print(" ✅")
        
        print(f"\n📊 Result type: {type(result.output)}")
        
        if isinstance(result.output, Plan):
            print(f"✅ SUCCESS! Got Plan with {len(result.output.plan)} steps:")
            for i, step in enumerate(result.output.plan, 1):
                print(f"  {i}. [{step.role}] {step.instruction[:60]}...")
        else:
            print(f"❌ Got string ({len(str(result.output))} chars):")
            print(f"{str(result.output)[:200]}...")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)[:200]}")

print(f"\n{'='*70}")
