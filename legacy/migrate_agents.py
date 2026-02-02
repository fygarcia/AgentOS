import shutil
from pathlib import Path
import os

def migrate_agent(agent_name):
    """Move agent folder to ./agents/{agent_name}."""
    root = Path(".")
    old_path = root / agent_name
    new_agents_dir = root / "agents"
    new_path = new_agents_dir / agent_name
    
    if not old_path.exists():
        print(f"Skipping {agent_name}: {old_path} not found")
        return
        
    if not old_path.is_dir():
        print(f"Skipping {agent_name}: Not a directory")
        return
        
    print(f"Migrating {agent_name}...")
    
    # Create agents directory
    new_agents_dir.mkdir(exist_ok=True)
    
    if new_path.exists():
        print(f"Warning: {new_path} already exists. Merging/Overwriting...")
        # Simple strategy: copytree with dirs_exist_ok=True, then remove old
        shutil.copytree(old_path, new_path, dirs_exist_ok=True)
        shutil.rmtree(old_path)
    else:
        shutil.move(str(old_path), str(new_path))
        
    print(f"✓ Moved {old_path} -> {new_path}")

def main():
    print("Starting Agent Folder Migration...")
    
    # Agents to migrate
    agents = ["finn", "default"]
    
    for agent in agents:
        migrate_agent(agent)
        
    # Also migrate any other folders that look like agents? 
    # For now, just explicit list to avoid moving core/docs/tests
    
    print("\nMigration Complete.")
    print("New structure:")
    if Path("agents").exists():
        for item in Path("agents").iterdir():
            if item.is_dir():
                print(f"  - agents/{item.name}/")

if __name__ == "__main__":
    main()
