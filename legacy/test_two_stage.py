"""
Test two-stage approach:
1. gpt-oss:20b generates plan as text
2. llama3.1:8b parses text into structured Plan
"""

import os
os.environ["LLM_PROVIDER"] = "ollama"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_ai import Agent
from core.models import Plan

print("=" * 70)
print("Two-Stage Plan Generation Test")
print("=" * 70)

user_intent = "Create a file named test.txt with content 'Hello World'"

# STAGE 1: Reasoning model generates the plan
print("\n[Stage 1] gpt-oss:20b (Reasoning) - Generate plan...")
reasoning_prompt = f"""
Analyze this user intent and create an execution plan with these steps:
- Each step has a 'role' (either 'Actor' or 'Auditor')
- Each step has an 'instruction' (what to do)

User intent: {user_intent}

Generate a clear, structured plan.
"""

reasoning_agent: Agent[None, str] = Agent('ollama:gpt-oss:20b', system_prompt="You are a planning expert.")
reasoning_result = reasoning_agent.run_sync(reasoning_prompt)
plan_text = reasoning_result.output

print(f"✅ Generated plan text ({len(plan_text)} chars):")
print(f"{plan_text[:300]}...")

# STAGE 2: Tool-calling model parses into structure
print("\n[Stage 2] llama3.1:8b (Tool-Calling) - Parse into Plan object...")
parsing_prompt = f"""
Extract the plan from this text and format it as a structured list.

Plan text:
{plan_text}

Create a plan with steps that each have:
- role: "Actor" or "Auditor"
- instruction: what to do
"""

parsing_agent: Agent[None, Plan] = Agent(
    'ollama:llama3.1:8b',
    system_prompt="You are a JSON extraction expert. Convert plans into structured format."
)

parsing_result = parsing_agent.run_sync(parsing_prompt)

print(f"Result type: {type(parsing_result.output)}")

if isinstance(parsing_result.output, Plan):
    print(f"✅ SUCCESS! Parsed into Plan with {len(parsing_result.output.plan)} steps")
    for i, step in enumerate(parsing_result.output.plan, 1):
        print(f"  Step {i}: [{step.role}] {step.instruction[:60]}...")
else:
    print(f"❌ Still got string: {parsing_result.output[:200]}")

print("\n" + "=" * 70)
