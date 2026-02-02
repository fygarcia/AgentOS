"""
Generic SQLite CRUD Operations
Part of AgentOS Core Skills - Universal database operations
"""

import sqlite3
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

# ============================================================================
# SKILL METADATA - Required for AgentOS Skill Registry
# ============================================================================

SKILL_METADATA = {
    "name": "sqlite_crud",
    "version": "1.0.0",
    "description": "Generic SQLite database CRUD operations (Create, Read, Update, Delete)",
    "agent": "core",  # Core AgentOS skill
    "category": "database",
    
    "parameters": {
        "operation": {
            "type": "str",
            "required": True,
            "description": "Operation type: 'query', 'insert', 'update', 'delete', 'execute'"
        },
        "db_path": {
            "type": "str",
            "required": True,
            "description": "Path to SQLite database file"
        },
        "sql": {
            "type": "str",
            "required": True,
            "description": "SQL query or statement to execute"
        },
        "params": {
            "type": "tuple",
            "required": False,
            "default": None,
            "description": "Parameters for parameterized query (prevents SQL injection)"
        },
        "many": {
            "type": "bool",
            "required": False,
            "default": False,
            "description": "For bulk inserts - params should be list of tuples"
        }
    },
    
    "returns": {
        "type": "dict",
        "description": "Result with status, message, data, and rows_affected",
        "schema": {
            "status": "str (success|error)",
            "message": "str",
            "data": "list (for queries)",
            "rows_affected": "int (for inserts/updates/deletes)"
        }
    },
    
    "examples": [
        {
            "description": "Query all rows from table",
            "input": {
                "operation": "query",
                "db_path": "data/app.db",
                "sql": "SELECT * FROM users WHERE active = ?",
                "params": (True,)
            },
            "output": {
                "status": "success",
                "message": "Query executed successfully",
                "data": [{"id": 1, "name": "Alice", "active": True}]
            }
        },
        {
            "description": "Insert a new record",
            "input": {
                "operation": "insert",
                "db_path": "data/app.db",
                "sql": "INSERT INTO users (name, email) VALUES (?, ?)",
                "params": ("Bob", "bob@example.com")
            },
            "output": {
                "status": "success",
                "message": "1 row inserted",
                "rows_affected": 1
            }
        }
    ],
    
    "tags": ["database", "sqlite", "crud", "sql", "core"]
}

# ============================================================================
# IMPLEMENTATION
# ============================================================================

def execute(**params) -> Dict[str, Any]:
    """
    Main entry point for skill execution.
    Executes SQLite operations based on operation type.
    """
    operation = params.get("operation")
    db_path = params.get("db_path")
    sql = params.get("sql")
    sql_params = params.get("params", ())
    many = params.get("many", False)
    
    try:
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        cursor = conn.cursor()
        
        result = {"status": "success", "message": "", "data": None, "rows_affected": 0}
        
        if operation == "query":
            # SELECT query
            cursor.execute(sql, sql_params)
            rows = cursor.fetchall()
            result["data"] = [dict(row) for row in rows]
            result["message"] = f"Query returned {len(rows)} rows"
            
        elif operation == "insert":
            # INSERT statement
            if many:
                cursor.executemany(sql, sql_params)
            else:
                cursor.execute(sql, sql_params)
            conn.commit()
            result["rows_affected"] = cursor.rowcount
            result["message"] = f"{cursor.rowcount} row(s) inserted"
            
        elif operation == "update":
            # UPDATE statement
            cursor.execute(sql, sql_params)
            conn.commit()
            result["rows_affected"] = cursor.rowcount
            result["message"] = f"{cursor.rowcount} row(s) updated"
            
        elif operation == "delete":
            # DELETE statement
            cursor.execute(sql, sql_params)
            conn.commit()
            result["rows_affected"] = cursor.rowcount
            result["message"] = f"{cursor.rowcount} row(s) deleted"
            
        elif operation == "execute":
            # Generic execution (CREATE TABLE, ALTER, etc.)
            cursor.execute(sql, sql_params)
            conn.commit()
            result["message"] = "Statement executed successfully"
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
            
        conn.close()
        return result
        
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}",
            "data": None,
            "rows_affected": 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "data": None,
            "rows_affected": 0
        }


# ============================================================================
# HELPER FUNCTIONS (Optional - for convenience)
# ============================================================================

def query(db_path: str, sql: str, params: Tuple = ()) -> Dict[str, Any]:
    """Convenience function for SELECT queries."""
    return execute(operation="query", db_path=db_path, sql=sql, params=params)


def insert(db_path: str, sql: str, params: Tuple, many: bool = False) -> Dict[str, Any]:
    """Convenience function for INSERT statements."""
    return execute(operation="insert", db_path=db_path, sql=sql, params=params, many=many)


def update(db_path: str, sql: str, params: Tuple = ()) -> Dict[str, Any]:
    """Convenience function for UPDATE statements."""
    return execute(operation="update", db_path=db_path, sql=sql, params=params)


def delete(db_path: str, sql: str, params: Tuple = ()) -> Dict[str, Any]:
    """Convenience function for DELETE statements."""
    return execute(operation="delete", db_path=db_path, sql=sql, params=params)


# ============================================================================
# MAIN - For testing
# ============================================================================

if __name__ == "__main__":
    # Test the skill
    test_db = "test_crud.db"
    
    # Create table
    result = execute(
        operation="execute",
        db_path=test_db,
        sql="CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)"
    )
    print("Create table:", result)
    
    # Insert
    result = insert(test_db, "INSERT INTO test (name) VALUES (?)", ("Alice",))
    print("Insert:", result)
    
    # Query
    result = query(test_db, "SELECT * FROM test")
    print("Query:", result)
    
    # Cleanup
    os.remove(test_db)
    print("Test database removed")
