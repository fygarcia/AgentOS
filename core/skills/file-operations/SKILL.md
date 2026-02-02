---
name: file-operations
description: Filesystem operations for reading, writing, and managing files and directories. Use when you need to read files (text, JSON, CSV), write/append to files, create/delete/move files, list directories, or check file existence. This is a core AgentOS skill for ANY filesystem interactions across any domain.
---

# File Operations

Core skill for filesystem operations. Use the `scripts/` tools for deterministic file I/O.

## Quick Reference

**Read Operations:**
- `read_text()` - Read plain text files
- `read_json()` - Read and parse JSON files
- `read_csv()` - Read CSV files

**Write Operations:**
- `write_text()` - Write/overwrite text files
- `append_text()` - Append to existing files
- `write_json()` - Write JSON data to files

**File Management:**
- `file_exists()` - Check if file exists
- `delete_file()` - Delete a file
- `move_file()` - Move or rename a file  
- `copy_file()` - Copy a file

**Directory Operations:**
- `list_dir()` - List directory contents
- `create_dir()` - Create directory (with parents)
- `delete_dir()` - Delete directory
- `dir_exists()` - Check if directory exists

## How to Use

### Read a Text File

```python
from core.skills.file-operations.scripts.file_ops import read_text

content = read_text("path/to/file.txt")
# Returns: string content or None on error
```

### Write to a File

```python
from core.skills.file-operations.scripts.file_ops import write_text

success = write_text("path/to/output.txt", "Hello, World!")
# Creates parent directories if needed
# Returns: True on success, False on error
```

### Read JSON

```python
from core.skills.file-operations.scripts.file_ops import read_json

data = read_json("config.json")
# Returns: dict/list or None on error
```

### List Directory

```python
from core.skills.file-operations.scripts.file_ops import list_dir

files = list_dir("path/to/directory")
# Returns: list of file/directory names
```

## Error Handling

All operations handle errors gracefully:
- Return `None` for read operations on failure
- Return `False` for write/modify operations on failure
- Return `True` for successful write/modify operations
- Print error messages to console

Always check return values before proceeding.

## Best Practices

1. Always use absolute paths or document relative path behavior
2. Check file existence before reading
3. Handle potential None/False returns
4. Create parent directories automatically (the tools do this)
5. Use appropriate encoding (default: utf-8)

## Tool Location

`core/skills/file-operations/scripts/file_ops.py`
