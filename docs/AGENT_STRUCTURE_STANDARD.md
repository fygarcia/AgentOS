# Agent Structure Standard

## Overview

This document defines the canonical directory structure and file organization for all AgentOS agents. Following this standard ensures:
- Consistent agent architecture
- Memory system integration
- Skill discoverability
- Clear separation of concerns

## Standard Directory Layout

```
/<agent-name>/                    # Root directory for the agent
│
├── /config                       # Agent configuration and identity
│   ├── AGENT.md                  # Agent identity, rules, capabilities
│   ├── SKILLS.md                 # (Optional) Skill catalog/documentation
│   ├── PRD.md                    # (Optional) Product requirements
│   └── ORCHESTRATOR.md           # (Optional) Custom orchestration logic
│
├── /memory                       # ⭐ PERSISTENT MEMORY (Required for AgentOS)
│   ├── NOW.md                    # Hot: Current objective & next steps
│   ├── LOG.md                    # Warm: Recent activity log
│   ├── memory.db                 # SQLite: User facts & metadata
│   └── /chroma_db                # Cold: Vector store (auto-created)
│
├── /skills                       # Agent-specific skills (Layer 1)
│   ├── /skill-name
│   │   ├── SKILL.md              # Skill documentation with frontmatter
│   │   ├── __init__.py           # (Optional) Package initialization
│   │   └── /scripts              # (Optional) Executable scripts
│   │       ├── tool1.py
│   │       └── tool2.py
│   └── /another-skill
│       └── ...
│
├── /directives                   # (Optional) SOPs and procedures
│   ├── SOP_DataIngestion.md
│   ├── SOP_ErrorHandling.md
│   └── ...
│
└── /inbox                        # (Optional) Watch folder for file ingestion
    └── ...
```

## Required vs Optional Components

### Required (for AgentOS integration)

✅ **Must Have**:
- `/<agent-name>/` - Root directory (agent name should be lowercase, hyphens for spaces)
- `/memory/` - Memory directory (auto-created if using MemoryManager)
  - `NOW.md` (auto-created)
  - `LOG.md` (auto-created)
  - `memory.db` (auto-created)
  - `/chroma_db` (auto-created)

### Recommended

📋 **Should Have**:
- `/config/AGENT.md` - Define agent identity, purpose, rules
- `/skills/` - Agent-specific skills directory
- Each skill should have `SKILL.md` with YAML frontmatter

### Optional

🔧 **Nice to Have**:
- `/config/SKILLS.md` - Catalog of available skills
- `/config/PRD.md` - Product requirements document
- `/directives/` - Standard operating procedures
- `/inbox/` - File ingestion watch folder

## File Naming Conventions

### Directory Names
- Lowercase with hyphens: `skill-name`, `agent-name`
- Descriptive: `file-operations`, `database-tools`
- No spaces, underscores, or special characters

### File Names

**Markdown Documentation**:
- UPPERCASE for core docs: `AGENT.md`, `SKILLS.md`, `README.md`
- Title case for reference: `ProductRequirements.md`
- UPPERCASE for SOPs: `SOP_ProcessName.md`

**Python Files**:
- snake_case: `skill_registry.py`, `update_status.py`
- Descriptive: `database_operations.py` not `db.py`

**Memory Files** (auto-managed):
- Fixed names: `NOW.md`, `LOG.md`, `memory.db`
- Do not rename or move these files

## Memory Integration Requirements

### Automatic Initialization

When creating a new agent, initialize memory:

```bash
# Command line
python -m core.memory_initializer --agent <agent-name>

# Or programmatically
from core.memory_initializer import initialize_agent_memory
initialize_agent_memory("<agent-name>")
```

### Memory Files

All agents **must** maintain these files in `/memory/`:

1. **NOW.md** - Hot Memory
   - Contains: Current objective, next steps
   - Format: Markdown with headers
   - Updated: When objective changes
   - Read: Before every LLM call

2. **LOG.md** - Warm Memory
   - Contains: Recent activity (timestamped entries)
   - Format: Markdown with timestamp headers
   - Updated: Auto-logged for all actions
   - Read: Before every LLM call (last ~20 entries)

3. **memory.db** - Structured Data
   - Contains: User facts, metadata, compaction history
   - Format: SQLite database
   - Schema: Defined in `core/memory_schema.sql`
   - Access: Via MemoryManager API

4. **/chroma_db** - Semantic Memory
   - Contains: Vector embeddings for semantic search
   - Format: ChromaDB persistent storage
   - Updated: During log compaction, explicit stores
   - Access: Via `recall_memory()` skill

### .gitignore

Add to `.gitignore`:
```gitignore
# Agent memory (contains runtime state and user data)
*/memory/NOW.md
*/memory/LOG.md
*/memory/memory.db
*/memory/chroma_db/
```

## Skill Organization

### Skill Directory Structure

Each skill should follow this pattern:

```
/skills/<skill-name>/
├── SKILL.md              # Required: Documentation with YAML frontmatter
├── __init__.py           # Optional: Package initialization
└── /scripts              # Optional: Executable tools
    ├── tool1.py
    └── tool2.py
```

### SKILL.md Format

Every skill **must** have a `SKILL.md` with YAML frontmatter:

```markdown
---
name: skill-name
description: Brief description of what this skill does. Use when you need to...
---

# Skill Name

Detailed documentation here.

## Quick Reference
- Function 1
- Function 2

## Usage Examples
...
```

### Skill Metadata (Python)

Python skill files should define:

```python
SKILL_METADATA = {
    "name": "skill_name",
    "version": "1.0.0",
    "description": "What this skill does",
    "agent": "agent-name",  # Which agent owns this
    "category": "category-name",
    "parameters": {
        "param1": {
            "type": "str",
            "required": True,
            "description": "What param1 does"
        }
    },
    "returns": {
        "type": "dict",
        "description": "What is returned"
    },
    "examples": [...],
    "tags": ["tag1", "tag2"]
}

def execute(**params):
    """Main entry point."""
    pass
```

## Configuration Files

### AGENT.md Format

Define agent identity and rules:

```markdown
# Agent Name

## Identity
- **Name**: Agent Name
- **Purpose**: What this agent does
- **Specialization**: Domain expertise

## Core Rules
1. Rule 1
2. Rule 2
3. ...

## Capabilities
- Capability 1
- Capability 2
- ...

## Memory Protocol
[How this agent uses memory system]
```

## Example: Creating a New Agent

### Step 1: Create Directory Structure

```bash
# Create agent directory
mkdir code-agent
cd code-agent

# Create subdirectories
mkdir config skills directives
```

### Step 2: Initialize Memory

```bash
# From project root
python -m core.memory_initializer --agent code-agent
```

### Step 3: Create AGENT.md

```markdown
---
name: code-agent
description: Code analysis and generation specialist
---

# Code Agent

## Identity
- **Name**: Code Agent
- **Purpose**: Analyze, refactor, and generate code
- **Specialization**: Python, JavaScript, system design

## Core Rules
1. Always include tests with generated code
2. Follow PEP 8 for Python, ESLint for JavaScript
3. Prefer composition over inheritance
4. Document all public APIs

## Capabilities
- Code review and refactoring
- Test generation
- Documentation creation
- Design pattern application

## Memory Protocol
- **NOW.md**: Current refactoring task
- **LOG.md**: Code changes made
- **Facts**: User preferences (style guides, frameworks)
```

### Step 4: Add Skills

```bash
# Create first skill
mkdir -p skills/code-review
cd skills/code-review

# Create SKILL.md
cat > SKILL.md << EOF
---
name: code-review
description: Automated code review with suggestions
---

# Code Review

...
EOF

# Create implementation
mkdir scripts
touch scripts/__init__.py
touch scripts/review.py
```

### Step 5: Register with AgentOS

```python
# In your main entry point
from core.agent import Agent

agent = Agent(name="code-agent", base_path="./code-agent")
agent.run("Review the utils.py file")
```

## Migration Guide

### Migrating Existing Agents

If you have an existing agent without the standard structure:

1. **Create memory directory**:
   ```bash
   python -m core.memory_initializer --agent <your-agent>
   ```

2. **Move files to standard locations**:
   ```bash
   # Move configuration
   mv YOUR_CONFIG.md config/AGENT.md
   
   # Organize skills
   mkdir -p skills/existing-skill
   mv existing_skill.py skills/existing-skill/scripts/
   ```

3. **Update imports**:
   ```python
   # Old
   from skills.existing_skill import function
   
   # New
   from skills.existing-skill.scripts.existing_skill import function
   ```

4. **Add .gitignore**:
   ```bash
   echo "*/memory/" >> .gitignore
   ```

## Validation Checklist

Use this checklist when creating or validating an agent:

- [ ] Agent directory exists and follows naming convention
- [ ] `/memory` directory initialized
- [ ] `NOW.md`, `LOG.md`, `memory.db` present
- [ ] `/config/AGENT.md` exists and is complete
- [ ] Skills in `/skills` have `SKILL.md` documentation
- [ ] Memory files in `.gitignore`
- [ ] Agent can be initialized via `MemoryManager`
- [ ] Skills discoverable via `SkillRegistry`

## Best Practices

### DO
✅ Use lowercase, hyphen-separated names  
✅ Initialize memory before first use  
✅ Document all skills with `SKILL.md`  
✅ Keep NOW.md concise (1 page max)  
✅ Categorize user facts appropriately  
✅ Test agent initialization/memory persistence

### DON'T
❌ Commit memory files to git  
❌ Hardcode file paths (use `base_path`)  
❌ Share memory between agents  
❌ Manually edit memory.db (use MemoryManager)  
❌ Skip SKILL.md documentation  
❌ Mix agent logic into AgentOS core

## References

- [MEMORY_SYSTEM.md](./MEMORY_SYSTEM.md) - Memory architecture details
- [STRUCTURE.md](./STRUCTURE.md) - Project-wide organization
- [core/skills/memory/SKILL.md](./core/skills/memory/SKILL.md) - Memory skills reference
- [AGENTIOS_SPEC.md](./AGENTIOS_SPEC.md) - Technical specification

---

**Version**: 1.0  
**Status**: ✅ Official Standard  
**Last Updated**: 2026-01-31
