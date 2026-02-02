---
name: file-operations
description: Read, write, create, delete, and manage files and directories. Use when you need to interact with the filesystem for reading files (text, JSON, CSV), writing data, creating/moving/deleting files or directories, checking file existence, or getting file metadata. This is a core AgentOS skill - use for ANY filesystem operations.
---

# File & Directory Operations

When working with files and directories, use the `scripts/operations.py` tool for all filesystem interactions.

## Tool Status

⚠️ **Coming Soon** - Implementation in progress

The `operations.py` script will provide these operations:

## Planned Operations

### 1. Read Files
- Read text files (UTF-8, ASCII)
- Read and parse JSON files
- Read and parse CSV files
- Read binary files
- Read large files line-by-line

### 2. Write Files
- Write text to files
- Write JSON (with pretty printing)
- Write CSV from data structures
- Append to existing files
- Atomic writes (temp file + rename)

### 3. Directory Operations
- Create directories (with parents)
- List directory contents
- Recursive directory traversal
- Find files by pattern/extension
- Get directory tree

### 4. File Management
- Copy files
- Move/rename files
- Delete files
- Check existence
- Get file metadata (size, modified time)

### 5. Path Operations
- Join paths safely (cross-platform)
- Get absolute paths
- Get file extension
- Get filename without extension
- Get parent directory

## Critical Rules (When Implemented)

1. **Always use absolute paths** or resolve relative paths first
2. **Check file existence** before reading
3. **Handle encoding explicitly** (UTF-8 default)
4. **Create parent directories** when writing new files
5. **Use atomic writes** for critical data

## Temporary Workaround

Until implementation is complete, use Python's built-in libraries directly:

```python
from pathlib import Path
import json

# Read file
content = Path("file.txt").read_text()

# Write file
Path("file.txt").write_text(content)

# JSON operations
data = json.loads(Path("data.json").read_text())
Path("output.json").write_text(json.dumps(data, indent=2))
```

## Tool Location

`core/skills/filesystem/operations.py` (Coming soon)
