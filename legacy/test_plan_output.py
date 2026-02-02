"""Test to understand how Pydantic AI handles structured outputs."""

from pydantic import BaseModel
from pydantic_ai import Agent
from typing import List, Literal

class PlanStep(BaseModel):
    role: Literal["Actor", "Auditor"]
    instruction: str

class Plan(BaseModel):
    plan: List[PlanStep]

# Create agent with Plan output types
agent: Agent[None, Plan] = Agent('test', system_prompt="Generate a plan")

# Run and inspect
result = agent.run_sync("Create a file")

print(f"Result type: {type(result)}")
print(f"Output type: {type(result.output)}")
print(f"Output value: {result.output}")

if isinstance(result.output, Plan):
    print("✅ Output is a Plan object!")
    print(f"Number of steps: {len(result.output.plan)}")
else:
    print(f"❌ Output is NOT a Plan, it's a {type(result.output)}")
