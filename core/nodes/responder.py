"""
RESPONDER NODE
==============

Purpose:
Handles direct responses for "Question" and "Chat" intents, bypassing the complex
planning/execution loop.
"""

import requests
from typing import Dict, Any
from core.state import AgentState
from core.config import config
from core.observability import get_tracer

def responder_node(state: AgentState) -> Dict[str, Any]:
    """
    Generates a direct response to the user.
    Used for Q&A and Chat interactions.
    """
    print("\n[Node] RESPONDER: Generating answer...")
    
    tracer = get_tracer()
    user_input = state["messages"][0]["content"]
    intent_type = state.get("intent_type", "QUESTION")
    
    # Configuration
    model = config.REASONING_MODEL # Use reasoning model for better answers
    base_url = config.OLLAMA_BASE_URL.rstrip('/')
    
    system_prompt = "You are a helpful AI assistant. Answer the user's question clearly and concisely."
    if intent_type == "CHAT":
        system_prompt = "You are a helpful and friendly AI assistant. Engage in conversation."
    
    prompt = f"{system_prompt}\n\nUser: {user_input}"
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        answer = response.json()["response"]
        
        print(f"[Responder] Generated response ({len(answer)} chars)")
        
        tracer.add_span(
            span_name="Responder",
            span_type="agent",
            details={
                "input": user_input,
                "model": model,
                "response_length": len(answer)
            }
        )
        
        return {"final_response": answer}
        
    except Exception as e:
        print(f"[Responder] ❌ Error: {e}")
        return {"final_response": "I'm sorry, I encountered an error while generating a response."}
