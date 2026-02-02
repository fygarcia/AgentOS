"""Quick test for result attributes."""

from pydantic import BaseModel
from pydantic_ai import Agent

class TestResult(BaseModel):
    x: str

agent: Agent[None, TestResult] = Agent('test')
result = agent.run_sync('test')

print("Result attributes:")
for attr in dir(result):
    if not attr.startswith('_'):
        try:
            val = getattr(result, attr)
            if not callable(val):
                print(f"  {attr}: {val}")
        except:
            pass

print(f"\nResult object: {result}")
print(f"Result type: {type(result)}")
