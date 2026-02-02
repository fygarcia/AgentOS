"""Test structured outputs with both models."""

import os
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["ENABLE_OBSERVABILITY"] = "false"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel
from pydantic_ai import Agent
from typing import List, Literal

class PlanStep(BaseModel):
    role: Literal["Actor", "Auditor"]
    instruction: str

class Plan(BaseModel):
    plan: List[PlanStep]

print("=" * 60)
print("Testing Structured Outputs with Both Models")
print("=" * 60)

# Test 1: llama3.1:8b (Actor model)
print("\n[1] Testing llama3.1:8b...")
try:
    agent1: Agent[None, Plan] = Agent('ollama:llama3.1:8b', system_prompt="Generate a plan")
    result1 = agent1.run_sync("Create a file named test.txt")
    print(f"✅ Response type: {type(result1.output)}")
    print(f"✅ Response: {result1.output}")
    if isinstance(result1.output, Plan):
        print(f"✅ Plan has {len(result1.output.plan)} steps")
    else:
        print(f"❌ Expected Plan, got {type(result1.output)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: gpt-oss:20b (Planner model)
print("\n[2] Testing gpt-oss:20b...")
try:
    agent2: Agent[None, Plan] = Agent('ollama:gpt-oss:20b', system_prompt="Generate a plan")
    result2 = agent2.run_sync("Create a file named test.txt")
    print(f"✅ Response type: {type(result2.output)}")
    print(f"✅ Response: {result2.output}")
    if isinstance(result2.output, Plan):
        print(f"✅ Plan has {len(result2.output.plan)} steps")
    else:
        print(f"❌ Expected Plan, got {type(result2.output)}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
