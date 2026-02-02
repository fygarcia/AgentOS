import os
import sys
import json
import subprocess
import re
from core.state import AgentState
from core.llm import get_llm

def actor_node(state: AgentState):
    idx = state.get("current_step_index", 0)
    plan = state.get("plan", [])
    
    if idx >= len(plan):
        return {}
    
    step = plan[idx]
    role = step.get("role")
    instruction = step.get("instruction")
    
    if role != "Actor":
        return {} # Should be handled by router, but just in case
        
    print(f"\n[Node] ACTOR: {instruction}")
    
    # NEW: Try to execute as skill if agent_instance available
    agent_instance = state.get("agent_instance")
    if agent_instance:
        # Check if instruction mentions a skill
        skill_match = re.search(r'(?:use|execute|run)\s+(?:skill\s+)?[\"\']?(\w[\w-]+)[\"\']?', instruction, re.IGNORECASE)
        if skill_match:
            skill_name = skill_match.group(1)
            if agent_instance.registry.has_skill(skill_name):
                print(f"[Actor] Executing skill: {skill_name}")
                try:
                    # TODO: Parse parameters from instruction
                    # For now, execute without params
                    skill_result = agent_instance.execute_skill(skill_name)
                    
                    # Update tool outputs
                    tool_outputs = state.get("tool_outputs", {})
                    tool_outputs[f"step_{idx}"] = f"Skill executed: {skill_result}"
                    
                    return {
                        "tool_outputs": tool_outputs,
                        "current_step_index": idx + 1
                    }
                except Exception as e:
                    print(f"[Actor] Skill execution failed: {e}, falling back to code generation")
    
    # Fallback: Generate and execute code
    llm = get_llm("Actor")
    
    # Generate Code
    code_response = llm.generate(
        system_prompt=(
            "You are the Actor. Write Python code to solve the instruction. "
            "Return ONLY code, no markdown. "
            "Use ONLY standard Python libraries (os, sys, json, etc). "
            "Do NOT import 'file_operations' or other custom modules. "
            "If you need to write a file, use open() and write()."
        ),
        user_prompt=instruction
    )
    
    print(f"[DEBUG] Raw LLM response:\n{repr(code_response)}\n")
    
    # Clean code - remove markdown and strip whitespace
    clean_code = code_response.strip()
    # Remove code fences if present
    if clean_code.startswith("```"):
        lines = clean_code.split("\n")
        # Remove first line if it's a code fence
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove last line if it's a code fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean_code = "\n".join(lines)
    
    # Remove any remaining "```python" or "```" markers
    clean_code = clean_code.replace("```python", "").replace("```", "").strip()
    
    print(f"Executing code:\n{clean_code}\n")
    
    output = "Success"
    try:
        # Expose tools to the execution environment
        exec_globals = {
            "os": os,
            "sys": sys,
            "subprocess": subprocess,
            "json": json
        }
        # Execute Code (Unsafe! In production, use sandbox)
        exec(clean_code, exec_globals)
    except Exception as e:
        print(f"Execution failed: {e}")
        output = f"Error: {e}"
        
    # Update tool outputs
    tool_outputs = state.get("tool_outputs", {})
    tool_outputs[f"step_{idx}"] = output
    
    return {
        "tool_outputs": tool_outputs,
        "current_step_index": idx + 1
    }
