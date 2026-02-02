"""Test explicit output_type parameter with Pydantic AI."""

import os
os.environ["LLM_PROVIDER"] = "ollama"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_ai import Agent
from core.models import Plan

print("=" * 70)
print("Testing output_type Parameter")
print("=" * 70)

# Try with explicit output_type parameter
print("\n[Test] Using output_type parameter explicitly...")

agent = Agent(
    'ollama:llama3.1:8b',
    output_type=Plan,  # Explicit output type
    system_prompt="You are a planning assistant. Generate a structured execution plan."
)

user_intent = "Create a file named test.txt with content 'Hello World'"

result = agent.run_sync(f"Create a plan to: {user_intent}")

print(f"\nResult type: {type(result.output)}")
print(f"Result value: {result.output}")

if isinstance(result.output, Plan):
    print(f"\n✅ SUCCESS! Got Plan with {len(result.output.plan)} steps:")
    for i, step in enumerate(result.output.plan, 1):
        print(f"  {i}. [{step.role}] {step.instruction}")
else:
    print(f"\n❌ Still string: {result.output[:200]}")

print("\n" + "=" * 70)
