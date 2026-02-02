---
name: memory
description: Persistent memory management for maintaining agent state across sessions. Use when you need to update current status (NOW.md), log activities and thoughts (LOG.md), recall past information from semantic memory (ChromaDB), or save/retrieve user facts and preferences (SQLite). This is a core AgentOS skill for managing agent memory across any domain.
---

# Memory Management

Core skill for persistent memory operations. Use the `scripts/` tools for memory management across the three-tier architecture: Hot (NOW.md), Warm (LOG.md), and Cold (ChromaDB).

## Quick Reference

**Hot Memory (NOW.md):**
- `update_status()` - Update current objective and next steps
- `read_status()` - Read current status

**Warm Memory (LOG.md):**
- `log_activity()` - Append entry to activity log
- `read_recent_log()` - Read recent log entries

**Cold Memory (ChromaDB):**
- `recall_memory()` - Search semantic long-term memory
- `store_memory()` - Store information in long-term memory

**User Facts (SQLite):**
- `save_fact()` - Save user preference or information
- `get_fact()` - Retrieve user fact by key
- `get_all_facts()` - Get all user facts

## How to Use

### Update Current Status

```python
from core.skills.memory.scripts.update_status import execute

execute(
    agent_name="finn",
    new_status="Researching Python decorators",
    next_steps=["Read documentation", "Create examples", "Write summary"]
)
# Updates NOW.md with current objective
```

### Log an Activity

```python
from core.skills.memory.scripts.log_activity import execute

execute(
    agent_name="finn",
    entry_type="TOOL_USE",  # TOOL_USE, THOUGHT, USER_FEEDBACK, ERROR, SYSTEM
    content="Created file hello.txt with sample content",
    metadata={"file": "hello.txt", "size_bytes": 42}
)
# Appends entry to LOG.md with timestamp
```

### Recall Past Information

```python
from core.skills.memory.scripts.recall_memory import execute

results = execute(
    agent_name="finn",
    query="What was the user's API key?",
    n_results=3
)
# Searches ChromaDB and returns relevant memories
```

### Save User Fact

```python
from core.skills.memory.scripts.save_fact import execute

execute(
    agent_name="finn",
    key="user_name",
    value="Felipe",
    category="personal"
)
# Stores in SQLite for quick retrieval
```

### Get User Fact

```python
from core.skills.memory.scripts.get_fact import execute

name = execute(
    agent_name="finn",
    key="user_name"
)
# Returns: "Felipe"
```

## Memory Architecture

### Three-Tier System

1. **HOT (NOW.md)** - Current objective, immediate next steps
   - Read on every LLM call
   - Updated when objective changes
   - Single point of truth for "what am I doing right now?"

2. **WARM (LOG.md)** - Recent activity history
   - Append-only log of last ~20-100 actions
   - Auto-logged for all tool executions
   - Compacted when exceeds 50KB

3. **COLD (ChromaDB)** - Long-term semantic memory
   - Vector database for semantic search
   - Archived compacted logs
   - Explicit recall via query

### Automatic vs Manual

**Automatic** (handled by AgentOS engine):
- Reading NOW.md and LOG.md before each LLM call
- Logging tool executions to LOG.md
- Compacting LOG.md when size limit exceeded

**Manual** (agent explicitly calls these skills):
- Updating NOW.md when objective changes
- Saving user facts
- Recalling from cold memory
- Storing important information for long-term

## Error Handling

All operations handle errors gracefully:
- Return `True`/`False` for write operations
- Return `None` for failed read operations
- Return empty list `[]` for failed searches
- Print error messages to console

Always check return values before proceeding.

## Best Practices

1. **Update status frequently** - Whenever your objective changes
2. **Log important thoughts** - Not just tool use, but reasoning steps
3. **Save user facts immediately** - Don't rely on context window
4. **Query cold memory** - When NOW + LOG don't have the info
5. **Use appropriate entry types** - TOOL_USE vs THOUGHT vs USER_FEEDBACK

## Agent Isolation

Each agent has its own isolated memory:
- `/<agent-name>/memory/NOW.md`
- `/<agent-name>/memory/LOG.md`
- `/<agent-name>/memory/memory.db`
- `/<agent-name>/memory/chroma_db/`

Agents cannot access each other's memories.

## Tool Locations

All scripts in `core/skills/memory/scripts/`:
- `update_status.py`
- `log_activity.py`
- `recall_memory.py`
- `save_fact.py`
- `get_fact.py`
- `read_status.py`
- `read_recent_log.py`
