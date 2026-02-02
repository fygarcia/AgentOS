"""
CLASSIFIER NODE
===============

Purpose:
Analyzes user input to determine the core intent (Task vs Question vs Chat).
Routes the workflow to the appropriate path.
"""

import json
import requests
from typing import Dict, Any, Literal
from core.state import AgentState
from core.config import config
from core.observability import get_tracer

def classifier_node(state: AgentState) -> Dict[str, Any]:
    """
    Classifies the user's intent into categories:
    - TASK: Requires planning and execution (file ops, data processing)
    - QUESTION: Requires informational answer (knowledge lookup)
    - CHAT: General conversation
    """
    print("\n[Node] CLASSIFIER: Analyzing intent...")
    
    tracer = get_tracer()
    user_input = state["messages"][0]["content"]
    
    # Configuration
    model = config.PARSER_MODEL  # Use Parser model for reliable JSON
    base_url = config.OLLAMA_BASE_URL.rstrip('/')
    
    prompt = f"""You are an intelligent intent classifier.
    
    Analyze the following user input and classify it into one of these categories:
    
    1. "TASK": The user wants you to DO something (create files, calculate, research, analyze, write code).
    2. "QUESTION": The user is asking a specific question that can be answered directly without side effects.
    3. "CHAT": The user is greeting you or making small talk.
    
    User Input: "{user_input}"
    
    Return ONLY a JSON object with this format:
    {{
        "intent_type": "TASK" | "QUESTION" | "CHAT",
        "reasoning": "brief explanation"
    }}
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()["response"]
        
        data = json.loads(result)
        intent_type = data.get("intent_type", "TASK").upper()
        
        print(f"[Classifier] Detected Intent: {intent_type} ({data.get('reasoning')})")
        
        tracer.add_span(
            span_name="Classifier",
            span_type="agent",
            details={
                "input": user_input,
                "intent": intent_type,
                "model": model
            }
        )
        
        return {"intent_type": intent_type}
        
    except Exception as e:
        print(f"[Classifier] ❌ Error: {e}, defaulting to TASK")
        return {"intent_type": "TASK"}
