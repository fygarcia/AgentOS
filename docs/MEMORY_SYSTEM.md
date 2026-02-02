# Memory System Architecture Documentation

## Overview

The persistent memory system implements a three-tier "file-system-as-state" architecture that allows AgentOS agents to maintain state across independent execution sessions. This enables agents to remember context, resume interrupted tasks, and build long-term knowledge bases.

## Core Philosophy

> **The file system is the agent's RAM**  
> If the process is killed and restarted, the agent reads the files and resumes exactly where it left off.

## Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  HOT MEMORY (NOW.md)                                        │
│  ═══════════════════════════════════════════════════════    │
│  • Current objective and immediate next steps               │
│  • Read on EVERY LLM call                                   │
│  • Overwritten when objective changes                       │
│  • Single source of truth for "what am I doing?"            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  WARM MEMORY (LOG.md)                                       │
│  ═══════════════════════════────────────────────────────    │
│  • Recent activity history (~20-100 entries)                │
│  • Append-only log with timestamps                          │
│  • Auto-logged for all tool executions                      │
│  • Compacted when exceeds 50KB → archived to cold memory    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  COLD MEMORY (ChromaDB + SQLite)                            │
│  ═══════════════════════════════════════════════════════    │
│  • Vector DB: Semantic search of archived logs/knowledge    │
│  • SQLite: Structured user facts & preferences              │
│  • Only accessed via explicit recall queries                │
│  • Unlimited storage, indexed for fast retrieval            │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

Each agent has isolated memory storage:

```
/<agent-name>/              # e.g., /finn, /code-agent
  ├── /config
  │   └── AGENT.md          # Identity, rules, capabilities
  ├── /memory               # ⭐ MEMORY STACK (isolated per agent)
  │   ├── NOW.md            # Hot: Current status
  │   ├── LOG.md            # Warm: Recent history
  │   ├── memory.db         # SQLite: Facts, metadata
  │   └── /chroma_db        # Vector store: Semantic memory
  ├── /skills
  └── /directives
```

## Components

### 1. MemoryManager Class

**Location**: `core/memory_manager.py`

Central orchestration for all memory operations. Each agent gets its own instance with isolated storage.

**Key Methods**:
- `update_now(status, next_steps)` - Update hot memory
- `append_log(entry_type, content, metadata)` - Append to warm memory
- `recall_memory(query, n_results)` - Search cold memory
- `save_fact(key, value, category)` - Store structured data
- `get_fact(key)` - Retrieve structured data
- `format_context_for_prompt()` - Get full context for LLM injection

**Initialization**:
```python
from core.memory_manager import MemoryManager

# Create manager for specific agent
manager = MemoryManager("finn")

# Auto-initializes:
# - /finn/memory directory
# - NOW.md with default content
# - LOG.md with header
# - memory.db with schema
# - ChromaDB collection
```

### 2. Memory Database Schema

**Location**: `core/memory_schema.sql`

**Tables**:

1. **user_facts** - Key-value store for user preferences/info
   ```sql
   CREATE TABLE user_facts (
       id INTEGER PRIMARY KEY,
       key TEXT UNIQUE,
       value TEXT,
       category TEXT,  -- general, preference, personal, config
       created_at TIMESTAMP,
       updated_at TIMESTAMP
   );
   ```

2. **log_metadata** - Tracking for LOG.md entries
   ```sql
   CREATE TABLE log_metadata (
       id INTEGER PRIMARY KEY,
       timestamp TIMESTAMP,
       entry_type TEXT,  -- TOOL_USE, THOUGHT, USER_FEEDBACK, ERROR, SYSTEM
       content_hash TEXT,
       compacted BOOLEAN,
       token_count INTEGER
   );
   ```

3. **compaction_history** - Track LOG.md compactions
   ```sql
   CREATE TABLE compaction_history (
       id INTEGER PRIMARY KEY,
       compacted_at TIMESTAMP,
       entries_count INTEGER,
       summary TEXT,  -- LLM-generated summary
       archive_id TEXT,
       original_size_kb REAL,
       new_size_kb REAL
   );
   ```

### 3. LanceDB (Cold Memory)

We use LanceDB for semantic storage because:
1. **Embedded**: Runs in-process, no separate server needed
2. **Fast**: Built on Arrow, extremely performant
3. **Simple**: Zero-config, just a file folder
4. **Python Compatible**: Works with Python 3.10+ (unlike ChromaDB which had issues)

**Location**: `/agents/<name>/memory/lancedb`

### 4. Memory Skills

**Location**: `core/skills/memory/`

Five native skills available to all agents:

1. **update_status** - Update NOW.md
2. **log_activity** - Append to LOG.md
3. **recall_memory** - Search LanceDB
4. **save_fact** - Store user fact
5. **get_fact** - Retrieve user fact

Each skill follows the AgentOS skill standard with `SKILL_METADATA` and `execute()` function.

## Integration with AgentOS

### State Extension

**File**: `core/state.py`

```python
class AgentState(TypedDict):
    # ... existing fields ...
    
    # Memory system fields
    memory_context: Optional[str]     # Injected NOW + LOG + facts
    agent_name: Optional[str]         # For memory isolation
    auto_log_enabled: Optional[bool]  # Auto-log all actions
```

### Engine Integration

**File**: `core/engine.py`

**Before Execution**:
1. Initialize MemoryManager for agent
2. Read memory context (NOW + LOG + facts)
3. Inject into state
4. Log incoming user intent

**After Execution**:
1. Log final response to LOG.md
2. Update NOW.md with "task complete" status

**On Error** (Self-Annealing):
1. Log error traceback to LOG.md
2. Update NOW.md with recovery steps
3. Enable agent to resume on restart

### Planner Integration

**File**: `core/nodes/planner.py`

Memory context is included in system prompt:

```python
system_prompt = f"""...
{memory_context}

Use the above memory context to understand:
1. What you're currently working on (NOW.md)
2. What you've done recently (LOG.md)
3. Any user facts or preferences

If the user says "continue", check NOW.md to see what you should resume.
"""
```

## Usage Examples

### 1. Initialize Agent Memory

```bash
# Command line
python -m core.memory_initializer --agent finn

# Or programmatically
from core.memory_initializer import initialize_agent_memory
initialize_agent_memory("finn")
```

### 2. Run Agent with Memory

```bash
# Finn agent handles a request
python core/engine.py --agent finn "Research Python asyncio and create a summary"

# Memory is automatically:
# - Read before execution (NOW + LOG injected)
# - Updated during execution (auto-logged)
# - Saved after completion (status updated)
```

### 3. Manual Memory Operations

```python
from core.skills.memory.scripts.update_status import execute as update_status
from core.skills.memory.scripts.save_fact import execute as save_fact
from core.skills.memory.scripts.recall_memory import execute as recall_memory

# Update current status
update_status(
    agent_name="finn",
    new_status="Analyzing portfolio data",
    next_steps=["Load CSV", "Calculate returns", "Generate report"]
)

# Save user preference
save_fact(
    agent_name="finn",
    key="preferred_currency",
    value="USD",
    category="preference"
)

# Recall past information
memories = recall_memory(
    agent_name="finn",
    query="What stocks did the user ask about last week?",
    n_results=3
)
```

## Automatic vs Manual Memory

### Automatic (by AgentOS)

✅ **Always happens**:
- Reading NOW + LOG before each LLM call
- Logging user intents
- Logging tool executions
- Logging final responses
- Logging errors with traceback
- Updating status on completion/error

### Manual (by Agent/Skills)

🛠️ **Agent decides when**:
- Updating NOW.md mid-task (objective changed)
- Logging thoughts/reasoning steps
- Saving user facts (name, preferences, etc.)
- Recalling from cold memory (semantic search)
- Storing important information for long-term

## Compaction Protocol

**Trigger**: LOG.md exceeds 50KB or 100 entries

**Process**:
1. Read full LOG.md content
2. Send to LLM: "Summarize these logs into coherent narrative"
3. Store summary in LanceDB (with archive_id)
4. Update `compaction_history` table
5. Rewrite LOG.md with summary as first entry
6. Mark all old entries as `compacted=1` in database

**Result**: LOG.md size reduced ~90%, full history retained in searchable cold memory

## Cold Memory Details (LanceDB)

- **Storage**: LanceDB (Local vector database)
- **Format**: Text chunks + Embeddings (nomic-embed-text)
- **Retrieval**: Semantic similarity search (Top-K)

## Self-Annealing (Error Recovery)

When an error occurs:

1. **Catch Exception** in engine.py
2. **Log to Memory**:
   ```python
   memory_manager.append_log(
       entry_type="ERROR",
       content=f"Error: {str(e)}",
       metadata={"traceback": traceback.format_exc()}
   )
   ```
3. **Update Status**:
   ```python
   memory_manager.update_now(
       new_status="Error encountered - Recovery needed",
       next_steps=["Review LOG.md", "Analyze root cause", "Implement fix"]
   )
   ```
4. **On Restart**: Agent reads NOW.md, sees recovery steps, continues

## Testing

### Unit Tests

**File**: `tests/test_memory_manager.py`

Tests all core functionality:
- Memory initialization
- NOW.md read/write
- LOG.md append
- User facts CRUD
- Agent isolation
- Context formatting

To run:
```bash
pytest tests/test_memory_manager.py -v
```

### Integration Tests (Spec Validation)

#### The "Amnesia Test"

**Purpose**: Verify state persistence across restarts

**Steps**:
1. Start task: "Research Python decorators and outline a blog post"
2. Wait for research step to complete
3. **Kill python process completely**
4. Restart and say "Continue"
5. **Expected**: Agent reads NOW.md, sees research is done, starts outlining

#### The "Correction Test"

**Purpose**: Verify long-term memory recall

**Steps**:
1. Tell agent: "My API key is 12345"
2. Agent calls `save_fact("api_key", "12345")`
3. Chat for 50+ turns (flush context window)
4. Ask: "What is my API key?"
5. **Expected**: Agent calls `recall_memory()` or `get_fact()`, returns "12345"

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Read NOW.md | <1ms | File read |
| Read LOG.md | <10ms | File read, last 20 entries |
| Append LOG | <5ms | File append + DB insert |
| Update NOW | <5ms | File overwrite |
| Save fact | <5ms | SQLite insert |
| Get fact | <2ms | SQLite select |
| Recall (cold) | ~50ms | LanceDB vector search |
| Compaction | ~30s | LLM summary generation |

## Dependencies

Added to `requirements.txt`:
```txt
lancedb>=0.5.0               # Vector database
# sentence-transformers not needed (using Ollama embedding API)
```

SQLite3 is built-in to Python (no additional dependency).

## Limitations & Future Work

### Current Limitations

1. **No multi-agent shared memory** - Each agent fully isolated
2. **Manual compaction trigger** - Could be made more intelligent
3. **LanceDB setup** - Ensure lancedb library is installed
4. **No cross-session conversation threading** - Each session independent

### Future Enhancements

1. **Shared knowledge base** - Common facts accessible to all agents
2. **Intelligent compaction** - LLM decides when to compact based on relevance
3. **Memory importance scoring** - Weight recent/important memories higher
4. **Cross-agent communication** - Agents can query each other's public memories
5. **Memory visualization** - UI to explore agent memory timeline
6. **Automatic fact extraction** - LLM identifies facts from conversation

## Best Practices

### For Agent Developers

1. **Update NOW.md frequently** - Whenever objective changes
2. **Log important thoughts** - Not just tool execution
3. **Save user facts immediately** - Don't rely on context window
4. **Use semantic search** - When NOW + LOG insufficient
5. **Check NOW.md on startup** - Resume interrupted tasks

### For System Designers

1. **Keep NOW.md concise** - Single page, current focus only
2. **Log metadata rich** - Include tool params, file paths, etc.
3. **Categorize facts** - Use categories for efficient retrieval
4. **Monitor LOG.md size** - Ensure compaction triggers appropriately
5 **Test persistence** - Use Amnesia/Correction tests regularly

## Troubleshooting

### Memory not persisting

**Check**:
- Is memory directory created? (`/<agent>/memory/`)
- Is NOW.md being read? (should see in planner system prompt)
- Is auto_log_enabled in state? (should be `True`)

### LanceDB errors

**Solution**:
- Ensure `lancedb` is installed: `pip install lancedb`
- Check permissions on `/lancedb` directory
- Verify Ollama embedding model is running

### LOG.md growing too large

**Check**:
- Is compaction threshold set? (default: 50KB)
- Is compaction function working? (check `compaction_history` table)
- Manual compact: Call `memory_manager.compact_log(summary)`

## API Reference

See individual files for complete docstrings:
- `core/memory_manager.py` - MemoryManager class
- `core/skills/memory/SKILL.md` - Skill documentation
- `core/memory_schema.sql` - Database schema

---

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-01-31
