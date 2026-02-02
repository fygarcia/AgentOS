import os
import json
import requests
from dotenv import load_dotenv
from core.observability import get_tracer

load_dotenv()

class MockLLM:
    """A dummy LLM for testing the architecture without API keys."""
    
    def generate(self, system_prompt, user_prompt):
        tracer = get_tracer()
        
        print(f"\n[MockLLM] System: {system_prompt[:50]}...")
        print(f"[MockLLM] User: {user_prompt[:50]}...")
        
        # Trace the LLM call
        tracer.add_span(
            span_name="MockLLM.generate",
            span_type="llm",
            details={
                "model": "mock",
                "prompt_length": len(system_prompt) + len(user_prompt),
                "system_prompt_preview": system_prompt[:100],
                "user_prompt_preview": user_prompt[:100]
            }
        )
        
        # Logic for "Hello World" test
        if "create a text file" in user_prompt.lower() or "create a file" in user_prompt.lower():
            # Planner Response
            if "Planner" in system_prompt:
                return json.dumps({
                    "plan": [
                        {"role": "Actor", "instruction": "Write 'Agentic OS is Live' to hello.txt in the folder ./tests/results"},
                        {"role": "Auditor", "instruction": "Verify hello.txt exists and contains correct text"}
                    ]
                })
            # Actor Response
            elif "Actor" in system_prompt:
                return """
import os
with open('./tests/results/hello.txt', 'w') as f:
    f.write('Agentic OS is Live')
print("File created.")
"""
            # Auditor Response
            elif "Auditor" in system_prompt:
                return json.dumps({"status": "success", "message": "File exists and content matches."})
        
        return "Mock response"

class OllamaLLM:
    """Interface for Local Ollama instance."""
    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model

    def generate(self, system_prompt, user_prompt):
        tracer = get_tracer()
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"System: {system_prompt}\nUser: {user_prompt}",
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()['response']
            
            # Trace the LLM call
            tracer.add_span(
                span_name=f"Ollama.{self.model}",
                span_type="llm",
                details={
                    "model": self.model,
                    "prompt_length": len(system_prompt) + len(user_prompt),
                    "response_length": len(result),
                    "base_url": self.base_url
                }
            )
            
            return result
        except Exception as e:
            print(f"Ollama Error: {e}")
            
            # Trace the error
            tracer.add_span(
                span_name=f"Ollama.{self.model}",
                span_type="llm",
                details={
                    "model": self.model,
                    "error": str(e),
                    "status": "error"
                }
            )
            
            return ""

def get_llm(role="Generic"):
    """Factory to get the appropriate LLM provider based on env vars."""
    provider = os.getenv("LLM_PROVIDER", "mock")
    
    if provider == "ollama":
        from core.config import config
        base_url = config.OLLAMA_BASE_URL
        planner_model = config.REASONING_MODEL
        actor_model = config.PARSER_MODEL
        
        model = planner_model if role in ["Planner", "Auditor"] else actor_model
        return OllamaLLM(base_url, model)
    else:
        return MockLLM()
