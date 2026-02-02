---
name: sqlite-crud
description: Generic SQLite database CRUD operations. Use when you need to interact with SQLite databases for creating, reading, updating, or deleting records, executing queries, or managing database schemas. This is a core AgentOS skill - use for ANY SQLite operations across any domain.
---

# SQLite Database Operations

When working with SQLite databases, use the `scripts/crud.py` tool for all database interactions.

## Quick Reference

The crud.py script provides 5 operations:

1. **query** - SELECT statements (retrieve data)
2. **insert** - INSERT statements (add records)
3. **update** - UPDATE statements (modify records)
4. **delete** - DELETE statements (remove records)
5. **execute** - Any SQL (CREATE TABLE, ALTER, etc.)

## How to Use

### Read Data (Query)

Use the `query` operation for SELECT statements:

```python
from core.skills.database.scripts.crud import execute

result = execute(
    operation="query",
    db_path="path/to/database.db",
    sql="SELECT * FROM users WHERE active = ?",
    params=(True,)
)
# Returns: {"status": "success", "data": [...], "message": "..."}
```

### Insert Records

Use the `insert` operation to add new records:

```python
result = execute(
    operation="insert",
    db_path="path/to/database.db",
    sql="INSERT INTO users (name, email) VALUES (?, ?)",
    params=("Alice", "alice@example.com")
)
# Returns: {"status": "success", "rows_affected": 1}
```

For bulk inserts, set `many=True` and pass list of tuples:

```python
result = execute(
    operation="insert",
    db_path="path/to/database.db",
    sql="INSERT INTO users (name, email) VALUES (?, ?)",
    params=[("Alice", "a@ex.com"), ("Bob", "b@ex.com")],
    many=True
)
```

### Update Records

Use the `update` operation to modify existing records:

```python
result = execute(
    operation="update",
    db_path="path/to/database.db",
    sql="UPDATE users SET active = ? WHERE id = ?",
    params=(False, 123)
)
```

### Delete Records

Use the `delete` operation to remove records:

```python
result = execute(
    operation="delete",
    db_path="path/to/database.db",
    sql="DELETE FROM users WHERE last_login < ?",
    params=("2024-01-01",)
)
```

### Schema Operations

Use the `execute` operation for DDL (CREATE, ALTER, DROP):

```python
result = execute(
    operation="execute",
    db_path="path/to/database.db",
    sql="CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"
)
```

## Critical Rules

1. **Always use parameterized queries** - Never interpolate values directly into SQL strings
2. **Check result status** - All operations return `{"status": "success"|"error", ...}`
3. **Handle errors gracefully** - Check status before using data
4. **Use appropriate data types** - TEXT for decimals in financial data
5. **Create parent directories** - The tool creates them automatically

## Error Handling

All operations return a consistent structure:

```python
{
    "status": "success" | "error",
    "message": "Description of what happened",
    "data": [...],  # For queries
    "rows_affected": 0  # For inserts/updates/deletes
}
```

Always check `status` before proceeding:

```python
result = execute(...)
if result["status"] == "error":
    print(f"Database error: {result['message']}")
else:
    # Use result["data"] or result["rows_affected"]
```

## When NOT to Use This Skill

- Don't use for domain-specific database operations that have their own skills
- If an agent has a specialized database skill, defer to that
- This is for GENERIC operations only

## Tool Location

`core/skills/database/scripts/crud.py`
