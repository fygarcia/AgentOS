import os
import sys
import subprocess

def create_skill(name, path="finn/skills"):
    """Tool: Initialize a new skill structure."""
    print(f"[Tool] Creating skill '{name}' in '{path}'...")
    # Adjust path to relative to project root
    script = os.path.join("finn", "skills", "skill_creator", "scripts", "init.py")
    try:
        # We want to see output in real time
        subprocess.run([sys.executable, script, name, "--path", path], check=True)
        print(f"[Tool] Success: Skill '{name}' created.")
    except Exception as e:
        print(f"[Tool] Error: {e}")
