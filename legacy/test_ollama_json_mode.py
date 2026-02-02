"""Test with Ollama's native format parameter for JSON mode."""

import requests
import json

print("=" * 70)
print("Testing Ollama Native JSON Mode")
print("=" * 70)

# Test with llama3.1:8b using native Ollama API
url = "http://192.168.4.102:11434/api/generate"

# Define the schema
schema = {
    "type": "object",
    "properties": {
        "plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "enum": ["Actor", "Auditor"]},
                    "instruction": {"type": "string"}
                },
                "required": ["role", "instruction"]
            }
        }
    },
    "required": ["plan"]
}

prompt = f"""You are a planning expert. Create a structured execution plan.

User request: Create a file named test.txt with content 'Hello World'

Respond with a JSON object matching this schema:
{json.dumps(schema, indent=2)}

Your response must be valid JSON only, nothing else."""

models_to_test = ["llama3.1:8b", "gpt-oss:20b"]

for model_name in models_to_test:
    print(f"\n{'='*70}")
    print(f"🤖 MODEL: {model_name}")
    print(f"{'='*70}")
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json"  # Enable JSON mode
    }
    
    print(f"Sending request... ", end="", flush=True)
    try:
        response = requests.post(url, json=payload, timeout=120)
        print(f"✅ Status {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            
            print(f"\n📄 Raw response ({len(generated_text)} chars):")
            print(generated_text[:500])
            
            # Try to parse as JSON
            try:
                parsed = json.loads(generated_text)
                print(f"\n✅ Valid JSON! Structure:")
                if "plan" in parsed:
                    print(f"   - Plan has {len(parsed['plan'])} steps")
                    for i, step in enumerate(parsed['plan'], 1):
                        print(f"   {i}. [{step.get('role', 'N/A')}] {step.get('instruction', 'N/A')[:60]}...")
                else:
                    print(f"   Keys: {list(parsed.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON Parse Error: {e}")
                
        else:
            print(f"\n❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

print(f"\n{'='*70}")
