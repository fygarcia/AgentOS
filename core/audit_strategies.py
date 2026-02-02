"""
AUDIT STRATEGIES
================

Library of verification functions used by the Auditor node.
Each strategy returns an AuditResult.
"""

import os
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class AuditResult:
    passed: bool
    message: str
    severity: Literal["INFO", "WARNING", "ERROR"] = "INFO"

def verify_file_exists(path: str) -> AuditResult:
    """Verifies that a file exists at the given path."""
    if os.path.exists(path):
        return AuditResult(True, f"File '{path}' exists.", "INFO")
    else:
        return AuditResult(False, f"File '{path}' NOT found.", "ERROR")

def verify_file_content_contains(path: str, substring: str) -> AuditResult:
    """Verifies that a file contains the expected substring."""
    if not os.path.exists(path):
        return AuditResult(False, f"File '{path}' does not exist.", "ERROR")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if substring in content:
            return AuditResult(True, f"File '{path}' contains expected text.", "INFO")
        else:
            preview = content[:50] + "..." if len(content) > 50 else content
            return AuditResult(False, f"File '{path}' content mismatch. Found: '{preview}'", "ERROR")
    except Exception as e:
        return AuditResult(False, f"Error reading file '{path}': {str(e)}", "ERROR")

def verify_file_does_not_exist(path: str) -> AuditResult:
    """Verifies that a file does NOT exist."""
    if not os.path.exists(path):
        return AuditResult(True, f"File '{path}' correctly does not exist.", "INFO")
    else:
        return AuditResult(False, f"File '{path}' exists but should not.", "ERROR")

def verify_tool_output_success(previous_output: str) -> AuditResult:
    """Verifies that the previous tool execution reported success."""
    if "error" in previous_output.lower() or "exception" in previous_output.lower() or "failed" in previous_output.lower():
         return AuditResult(False, f"Previous step reported error: {previous_output}", "ERROR")
    return AuditResult(True, "Previous step executed successfully.", "INFO")
