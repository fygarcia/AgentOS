"""Quick test to understand Pydantic AI API."""

from pydantic import BaseModel
from pydantic_ai import Agent

class TestResult(BaseModel):
    name: str
    value: int

# Try creating an agent
try:
    # Attempt 1: Generic type annotation
    agent: Agent[None, TestResult] = Agent('test', system_prompt="Test")
    print("✅ Attempt 1 worked: Agent[None, TestResult] = Agent('test')")
except Exception as e:
    print(f"❌ Attempt 1 failed: {e}")

try:
    # Attempt 2: result_retval parameter
    agent2 = Agent('test', result_retval=TestResult)
    print("✅ Attempt 2 worked: Agent('test', result_retval=TestResult)")
except Exception as e:
    print(f"❌ Attempt 2 failed: {e}")

try:
    # Attempt 3: just the type annotation
    agent3: Agent[None, TestResult] = Agent[None, TestResult]('test')
    print("✅ Attempt  3 worked: Agent[None, TestResult]('test')")
except Exception as e:
    print(f"❌ Attempt 3 failed: {e}")

print("\nAgent attributes:")
print(dir(Agent))
