"""
File Operations - Core AgentOS Skill
=====================================

Provides deterministic filesystem operations for reading, writing,
and managing files and directories.

This module can be:
1. Imported and used directly by other Python code
2. Referenced in SKILL.md for LLM context
3. Executed via the execute() function

Usage:
    from core.skills.file_operations.scripts.file_ops import execute
    
    result = execute(operation="read_text", path="file.txt")
"""

import json
import csv
import os
import shutil
from pathlib import Path
from typing import Any, Optional, List, Dict


# ============================================================================
# READ OPERATIONS
# ============================================================================

def read_text(filepath: str, encoding: str = "utf-8") -> Optional[str]:
    """
    Read a text file and return its contents.
    
    Args:
        filepath: Path to the file
        encoding: File encoding (default: utf-8)
        
    Returns:
        File contents as string, or None on error
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"[file_ops] Error reading {filepath}: {e}")
        return None


def read_json(filepath: str, encoding: str = "utf-8") -> Optional[Any]:
    """
    Read and parse a JSON file.
    
    Args:
        filepath: Path to JSON file
        encoding: File encoding (default: utf-8)
        
    Returns:
        Parsed JSON (dict/list), or None on error
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        print(f"[file_ops] Error reading JSON {filepath}: {e}")
        return None


def read_csv(filepath: str, encoding: str = "utf-8") -> Optional[List[List[str]]]:
    """
    Read a CSV file and return rows as list of lists.
    
    Args:
        filepath: Path to CSV file
        encoding: File encoding (default: utf-8)
        
    Returns:
        List of rows (each row is a list of values), or None on error
    """
    try:
        with open(filepath, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f)
            return list(reader)
    except Exception as e:
        print(f"[file_ops] Error reading CSV {filepath}: {e}")
        return None


# ============================================================================
# WRITE OPERATIONS
# ============================================================================

def write_text(filepath: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> bool:
    """
    Write text to a file (overwrites existing content).
    
    Args:
        filepath: Path to the file
        content: Text content to write
        encoding: File encoding (default: utf-8)
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        True on success, False on error
    """
    try:
        if create_dirs:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[file_ops] Error writing {filepath}: {e}")
        return False


def append_text(filepath: str, content: str, encoding: str = "utf-8") -> bool:
    """
    Append text to a file.
    
    Args:
        filepath: Path to the file
        content: Text content to append
        encoding: File encoding (default: utf-8)
        
    Returns:
        True on success, False on error
    """
    try:
        with open(filepath, 'a', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[file_ops] Error appending to {filepath}: {e}")
        return False


def write_json(filepath: str, data: Any, encoding: str = "utf-8", indent: int = 2, create_dirs: bool = True) -> bool:
    """
    Write data to a JSON file.
    
    Args:
        filepath: Path to JSON file
        data: Data to write (must be JSON-serializable)
        encoding: File encoding (default: utf-8)
        indent: JSON indentation (default: 2)
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        True on success, False on error
    """
    try:
        if create_dirs:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"[file_ops] Error writing JSON {filepath}: {e}")
        return False


# ============================================================================
# FILE MANAGEMENT
# ============================================================================

def file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).is_file()


def delete_file(filepath: str) -> bool:
    """
    Delete a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        True on success, False on error
    """
    try:
        Path(filepath).unlink()
        return True
    except Exception as e:
        print(f"[file_ops] Error deleting {filepath}: {e}")
        return False


def move_file(src: str, dst: str, create_dirs: bool = True) -> bool:
    """
    Move or rename a file.
    
    Args:
        src: Source file path
        dst: Destination file path
        create_dirs: Create destination parent directories
        
    Returns:
        True on success, False on error
    """
    try:
        if create_dirs:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(src, dst)
        return True
    except Exception as e:
        print(f"[file_ops] Error moving {src} to {dst}: {e}")
        return False


def copy_file(src: str, dst: str, create_dirs: bool = True) -> bool:
    """
    Copy a file.
    
    Args:
        src: Source file path
        dst: Destination file path
        create_dirs: Create destination parent directories
        
    Returns:
        True on success, False on error
    """
    try:
        if create_dirs:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"[file_ops] Error copying {src} to {dst}: {e}")
        return False


# ============================================================================
# DIRECTORY OPERATIONS
# ============================================================================

def list_dir(dirpath: str) -> Optional[List[str]]:
    """
    List directory contents.
    
    Args:
        dirpath: Path to directory
        
    Returns:
        List of file/directory names, or None on error
    """
    try:
        return os.listdir(dirpath)
    except Exception as e:
        print(f"[file_ops] Error listing {dirpath}: {e}")
        return None


def create_dir(dirpath: str, parents: bool = True) -> bool:
    """
    Create a directory.
    
    Args:
        dirpath: Path to directory
        parents: Create parent directories if needed
        
    Returns:
        True on success, False on error
    """
    try:
        Path(dirpath).mkdir(parents=parents, exist_ok=True)
        return True
    except Exception as e:
        print(f"[file_ops] Error creating directory {dirpath}: {e}")
        return False


def delete_dir(dirpath: str) -> bool:
    """
    Delete a directory (must be empty).
    
    Args:
        dirpath: Path to directory
        
    Returns:
        True on success, False on error
    """
    try:
        Path(dirpath).rmdir()
        return True
    except Exception as e:
        print(f"[file_ops] Error deleting directory {dirpath}: {e}")
        return False


def dir_exists(dirpath: str) -> bool:
    """Check if a directory exists."""
    return Path(dirpath).is_dir()


# ============================================================================
# SKILL EXECUTION INTERFACE
# ============================================================================

SKILL_METADATA = {
    "name": "file-operations",
    "description": "Filesystem operations for reading, writing, and managing files and directories",
    "category": "general",
    "parameters": {
        "operation": {
            "type": "string",
            "required": True,
            "description": "Operation to perform",
            "options": [
                "read_text", "read_json", "read_csv",
                "write_text", "append_text", "write_json",
                "file_exists", "delete_file", "move_file", "copy_file",
                "list_dir", "create_dir", "delete_dir", "dir_exists"
            ]
        },
        "filepath": {
            "type": "string",
            "required": False,
            "description": "File path (for file operations)"
        },
        "dirpath": {
            "type": "string",
            "required": False,
            "description": "Directory path (for directory operations)"
        },
        "content": {
            "type": "string",
            "required": False,
            "description": "Content to write (for write operations)"
        },
        "data": {
            "type": "any",
            "required": False,
            "description": "Data to write as JSON"
        },
        "src": {
            "type": "string",
            "required": False,
            "description": "Source path (for move/copy operations)"
        },
        "dst": {
            "type": "string",
            "required": False,
            "description": "Destination path (for move/copy operations)"
        }
    },
    "returns": {
        "type": "varies",
        "description": "Depends on operation - content, boolean, or list"
    },
    "examples": [
        {
            "description": "Read a text file",
            "code": "execute(operation='read_text', filepath='data.txt')"
        },
        {
            "description": "Write JSON to file",
            "code": "execute(operation='write_json', filepath='config.json', data={'key': 'value'})"
        }
    ],
    "tags": ["filesystem", "file", "io", "core"],
    "version": "1.0.0"
}


def execute(operation: str, **kwargs) -> Any:
    """
    Execute a file operation.
    
    Args:
        operation: Operation name (see SKILL_METADATA for options)
        **kwargs: Operation-specific parameters
        
    Returns:
        Result of the operation (varies by operation type)
    """
    # Map operations to functions
    ops = {
        "read_text": lambda: read_text(kwargs.get("filepath"), kwargs.get("encoding", "utf-8")),
        "read_json": lambda: read_json(kwargs.get("filepath"), kwargs.get("encoding", "utf-8")),
        "read_csv": lambda: read_csv(kwargs.get("filepath"), kwargs.get("encoding", "utf-8")),
        "write_text": lambda: write_text(kwargs.get("filepath"), kwargs.get("content", ""), kwargs.get("encoding", "utf-8")),
        "append_text": lambda: append_text(kwargs.get("filepath"), kwargs.get("content", ""), kwargs.get("encoding", "utf-8")),
        "write_json": lambda: write_json(kwargs.get("filepath"), kwargs.get("data"), kwargs.get("encoding", "utf-8")),
        "file_exists": lambda: file_exists(kwargs.get("filepath")),
        "delete_file": lambda: delete_file(kwargs.get("filepath")),
        "move_file": lambda: move_file(kwargs.get("src"), kwargs.get("dst")),
        "copy_file": lambda: copy_file(kwargs.get("src"), kwargs.get("dst")),
        "list_dir": lambda: list_dir(kwargs.get("dirpath")),
        "create_dir": lambda: create_dir(kwargs.get("dirpath")),
        "delete_dir": lambda: delete_dir(kwargs.get("dirpath")),
        "dir_exists": lambda: dir_exists(kwargs.get("dirpath")),
    }
    
    if operation not in ops:
        print(f"[file_ops] Unknown operation: {operation}")
        return None
    
    return ops[operation]()


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("File Operations Skill - Test")
    print("=" * 70)
    
    # Test write and read
    test_file = "/tmp/test_file_ops.txt"
    print(f"\n[TEST] Writing to {test_file}")
    success = write_text(test_file, "Hello, File Operations!")
    print(f"  Result: {'✅' if success else '❌'}")
    
    print(f"\n[TEST] Reading from {test_file}")
    content = read_text(test_file)
    print(f"  Content: {content}")
    print(f"  Result: {'✅' if content else '❌'}")
    
    # Test JSON
    test_json = "/tmp/test_data.json"
    test_data = {"name": "file-operations", "type": "core_skill"}
    print(f"\n[TEST] Writing JSON to {test_json}")
    success = write_json(test_json, test_data)
    print(f"  Result: {'✅' if success else '❌'}")
    
    print(f"\n[TEST] Reading JSON from {test_json}")
    data = read_json(test_json)
    print(f"  Data: {data}")
    print(f"  Result: {'✅' if data else '❌'}")
    
    print("\n" + "=" * 70)
    print("✅ File Operations Skill working correctly")
    print("=" * 70)
