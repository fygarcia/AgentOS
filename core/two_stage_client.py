"""
TWO-STAGE OLLAMA CLIENT - Production Module
============================================

PURPOSE:
Combines the strengths of two Ollama models to generate structured,  
validated outputs with rich reasoning.

ARCHITECTURE:
┌──────────────────────────────────────────────────────────────┐
│ Stage 1: Reasoning Model (gpt-oss:20b)                      │
│ - Generates detailed, well-reasoned plan (~4500-5000 chars) │
│ - Natural language thinking, no JSON constraints            │
│ - Captures why each step is needed + success criteria       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 2: Parser Model (llama3.1:8b)                         │
│ - Converts reasoning into structured JSON                    │
│ - Uses Ollama's native format="json" mode                   │
│ - Validates against Pydantic schema                          │
└──────────────────────────────────────────────────────────────┘
                            ↓
                  Validated Pydantic Model

WORKFLOW (Step-by-Step):
1. Client receives: reasoning_model, parser_model, prompt, schema
2. Stage 1 calls Ollama with reasoning model (no JSON mode)
3. Reasoning model generates ~5000 char detailed plan  
4. Stage 2 receives reasoning text + explicit JSON structure
5. Parser model converts to JSON with exact field names
6. Pydantic validates and returns typed object

WHY THIS WORKS:
- gpt-oss:20b excels at reasoning but struggles with JSON
- llama3.1:8b excels at JSON structure but less sophisticated reasoning
- Two-stage leverages each model's strength perfectly

USAGE EXAMPLE:
```python
client = TwoStageOllamaClient()
plan = client.generate_with_reasoning(
    reasoning_model="gpt-oss:20b",
    parser_model="llama3.1:8b",
    prompt="Create file test.txt",
    schema=Plan  # Pydantic model
)
# Returns: Plan(objective="...", plan=[PlanStep(...), ...])
```

PRODUCTION STATUS: ✅ Ready
DEPENDENCIES: requests, pydantic
RELATED: core/models.py (schemas), core/nodes/planner.py (integration)
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path
from typing import TypeVar, Type, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class TwoStageOllamaClient:
    """
    Two-stage pipeline for structured output generation:
    1. Reasoning model generates detailed plan (text)
    2. Parser model structures it into JSON
    """
    
    def __init__(self, base_url: str = None, verbose: bool = True, save_outputs: bool = True):
        """
        Initialize client.
        
        Args:
            base_url: Ollama server URL. If None, loads from config.
            verbose: If True, print full outputs. If False, print summaries only.
            save_outputs: If True, save outputs to .tmp/llm_outputs/
        """
        if base_url is None:
            from core.config import config
            base_url = config.OLLAMA_BASE_URL
        
        # Remove /v1 or /api suffix if present for consistency
        self.base_url = base_url.rstrip('/v1').rstrip('/api').rstrip('/')
        self.verbose = verbose
        self.save_outputs = save_outputs
        
        # Create output directory
        if self.save_outputs:
            self.output_dir = Path(".tmp/llm_outputs")
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_with_reasoning(
        self,
        reasoning_model: str,
        parser_model: str,
        prompt: str,
        schema: Type[T],
        system_prompt: str = ""
    ) -> T:
        """
        Two-stage generation: reasoning → parsing.
        
        Args:
            reasoning_model: Model for generating detailed reasoning (e.g., gpt-oss:20b)
            parser_model: Model for parsing to JSON (e.g., llama3.1:8b)
            prompt: User's request
            schema: Pydantic model to validate against
            system_prompt: Optional system instructions
            
        Returns:
            Validated Pydantic model instance
        """
        # Get tracer for observability
        from core.observability import get_tracer
        tracer = get_tracer()
        
        # STAGE 1: Reasoning model generates detailed plan
        print(f"\n[Stage 1] 🧠 {reasoning_model} - Generating reasoning plan...")
        
        reasoning_prompt = f"""{system_prompt}

User request: {prompt}

Think through this request step-by-step and create a detailed execution plan. For each step:
- Specify who should do it (Actor performs actions, Auditor validates)
- Explain what needs to be done
- Explain why it's necessary
- Describe what success looks like

Generate a comprehensive, well-reasoned plan:"""

        # Trace Stage 1
        tracer.add_span(
            span_name="Stage 1: Reasoning Model",
            span_type="llm",
            details={
                "model": reasoning_model,
                "prompt_length": len(reasoning_prompt),
                "stage": "reasoning"
            }
        )
        
        stage1_response = self._call_ollama(
            model=reasoning_model,
            prompt=reasoning_prompt,
            json_mode=False  # Let it reason naturally
        )
        
        print(f"✅ Generated reasoning ({len(stage1_response)} chars)")
        
        # Display full output if verbose
        if self.verbose:
            print(f"\n{'─'*70}")
            print("FULL REASONING OUTPUT:")
            print(f"{'─'*70}")
            print(stage1_response)
            print(f"{'─'*70}\n")
        else:
            print(f"Preview: {stage1_response[:1000]}...\n")
        
        # Save Stage 1 output
        if self.save_outputs:
            self._save_output(
                stage="stage1_reasoning",
                model=reasoning_model,
                content=stage1_response,
                prompt=reasoning_prompt
            )
        
        # STAGE 2: Parser model structures the reasoning into JSON
        print(f"\n[Stage 2] 🔧 {parser_model} - Parsing into structured format...")
        
        parsing_prompt = f"""Convert the following reasoning plan into valid JSON.

REASONING PLAN:
{stage1_response}

REQUIRED JSON STRUCTURE:
{{
  "objective": "brief description of the overall goal",
  "plan": [
    {{
      "role": "Actor or Auditor",
      "instruction": "what to do",
      "reasoning": "why it's needed (optional)",
      "expected_outcome": "what success looks like (optional)"
    }}
  ],
  "total_steps": number
}}

CRITICAL RULES:
- Use EXACTLY these field names: "objective", "plan", "role", "instruction", "reasoning", "expected_outcome", "total_steps"
- "role" must be EITHER "Actor" OR "Auditor" - no other values
- Each step must have "role" and "instruction" at minimum
- Maintain the reasoning and expected outcomes from the original plan

Generate the JSON now:"""

        # Trace Stage 2
        tracer.add_span(
            span_name="Stage 2: Parser Model",
            span_type="llm",
            details={
                "model": parser_model,
                "prompt_length": len(parsing_prompt),
                "stage": "parsing"
            }
        )
        
        stage2_response = self._call_ollama(
            model=parser_model,
            prompt=parsing_prompt,
            json_mode=True  # Force JSON output
        )
        
        print(f"✅ Parsed JSON ({len(stage2_response)} chars)")
        
        # Display full JSON if verbose
        if self.verbose:
            print(f"\n{'─'*70}")
            print("FULL JSON OUTPUT:")
            print(f"{'─'*70}")
            # Pretty print JSON
            try:
                parsed = json.loads(stage2_response)
                print(json.dumps(parsed, indent=2))
            except:
                print(stage2_response)
            print(f"{'─'*70}\n")
        
        # Save Stage 2 output
        if self.save_outputs:
            self._save_output(
                stage="stage2_json",
                model=parser_model,
                content=stage2_response,
                prompt=parsing_prompt
            )
        
        # Validate and return
        try:
            return schema.model_validate_json(stage2_response)
        except Exception as e:
            print(f"❌ Validation error: {e}")
            print(f"Raw JSON: {stage2_response[:500]}")
            raise
    
    def _save_output(self, stage: str, model: str, content: str, prompt: str):
        """Save LLM output to file for debugging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{stage}_{model.replace(':', '_')}.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=" * 70 + "\n")
            f.write(f"Stage: {stage}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"=" * 70 + "\n\n")
            f.write("PROMPT:\n")
            f.write(f"{'-' * 70}\n")
            f.write(prompt)
            f.write(f"\n{'-' * 70}\n\n")
            f.write("OUTPUT:\n")
            f.write(f"{'-' * 70}\n")
            f.write(content)
            f.write(f"\n{'-' * 70}\n")
        
        print(f"💾 Saved output to: {filepath}")
    
    def _call_ollama(self, model: str, prompt: str, json_mode: bool = False) -> str:
        """Internal method to call Ollama API."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if json_mode:
            payload["format"] = "json"
        
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '')


# Test the two-stage approach
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from core.models import Plan
    from core.config import config
    
    client = TwoStageOllamaClient()
    
    print("=" * 70)
    print("Testing Two-Stage Reasoning → Parsing Pipeline")
    print("=" * 70)
    print(f"Reasoning Model: {config.REASONING_MODEL}")
    print(f"Parser Model: {config.PARSER_MODEL}")
    print("=" * 70)
    
    try:
        plan = client.generate_with_reasoning(
            reasoning_model=config.REASONING_MODEL,
            parser_model=config.PARSER_MODEL,
            prompt="Create a file named test.txt with content 'Hello World'",
            schema=Plan,
            system_prompt="You are an expert planning assistant."
        )
        
        print(f"\n{'='*70}")
        print("✅ FINAL RESULT - Validated Plan Object")
        print(f"{'='*70}")
        print(f"Objective: {plan.objective}")
        print(f"Total Steps: {plan.total_steps}")
        print(f"\nSteps:")
        for i, step in enumerate(plan.plan, 1):
            print(f"\n  {i}. [{step.role}] {step.instruction}")
            if step.reasoning:
                print(f"     💡 Reasoning: {step.reasoning}")
            if step.expected_outcome:
                print(f"     🎯 Expected: {step.expected_outcome}")
                
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
