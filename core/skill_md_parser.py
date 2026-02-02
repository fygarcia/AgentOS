"""
Helper function to load SKILL.md from a skill directory.
Uses PyYAML for proper frontmatter parsing.
"""

import yaml
from typing import Tuple, Dict, Any


def parse_skill_md(skill_md_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse SKILL.md file with YAML frontmatter and markdown body.
    
    Format:
        ---
        name: skill-name
        description: What the skill does
        ---
        
        # Markdown content
        
    Args:
        skill_md_path: Path to SKILL.md file
        
    Returns:
        (frontmatter_dict, markdown_body)
    """
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse frontmatter
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    # Use PyYAML for proper parsing
    frontmatter_text = parts[1].strip()
    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as e:
        print(f"[SkillMDParser] Warning: YAML parsing error: {e}")
        frontmatter = {}
    
    markdown_body = parts[2].strip()
    
    return frontmatter, markdown_body


if __name__ == "__main__":
    # Test
    try:
        fm, body = parse_skill_md("core/skills/database/SKILL.md")
        print("Frontmatter:", fm)
        print("\nBody preview:", body[:200])
    except FileNotFoundError:
        print("Test file not found - run from project root")
