"""
Direct Ollama integration bypassing Pydantic AI's tool-calling.
Uses Ollama's native JSON mode which we know works.
"""

import requests
import json
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class OllamaJSONClient:
    """Simple client for Ollama with native JSON mode support."""
    
    def __init__(self, base_url: str = "http://192.168.4.102:11434"):
        self.base_url = base_url
        
    def generate(self, model: str, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        """
        Generate structured output using Ollama's native JSON mode.
        
        Args:
            model: Model name (e.g. "llama3.1:8b")
            prompt: User prompt
            schema: Pydantic model class for validation
            system_prompt: Optional system instructions
            
        Returns:
            Validated Pydantic model instance
        """
        url = f"{self.base_url}/api/generate"
        
        # Build prompt describing the expected structure (not raw schema)
        full_prompt = f"""{system_prompt}

User request: {prompt}

Respond with a JSON object containing a "plan" array. Each plan step should have:
- "role": either "Actor" or "Auditor"
- "instruction": what to do

Example format:
{{"plan": [{{"role": "Actor", "instruction": "do something"}}, {{"role": "Auditor", "instruction": "verify it"}}]}}

Generate the plan now as valid JSON:"""
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json"  # Enable native JSON mode
        }
        
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        
        result = response.json()
        generated_json = result.get('response', '{}')
        
        # Validate and return
        return schema.model_validate_json(generated_json)


# Test it
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from core.models import Plan
    
    client = OllamaJSONClient()
    
    models_to_test = [
        ("llama3.1:8b", "🔧 Tool-calling"),
        ("gpt-oss:20b", "🧠 Reasoning")
    ]
    
    for model_name, desc in models_to_test:
        print(f"\n{'='*70}")
        print(f"🤖 MODEL: {model_name} - {desc}")
        print(f"{'='*70}")
        
        system_prompt = "You are a planning expert. Analyze user requests and create structured execution plans." if "reasoning" in desc.lower() else "You are a helpful assistant that generates structured plans."
        
        try:
            plan = client.generate(
                model=model_name,
                prompt="Create a file named test.txt with content 'Hello World'",
                schema=Plan,
                system_prompt=system_prompt
            )
            
            print(f"✅ SUCCESS! Got Plan with {len(plan.plan)} steps:")
            for i, step in enumerate(plan.plan, 1):
                print(f"  {i}. [{step.role}] {step.instruction}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
