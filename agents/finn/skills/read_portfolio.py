import sqlite3
import os
import json
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = os.path.join("memory", "portfolio.db")

# ============================================================================
# SKILL METADATA
# ============================================================================

SKILL_METADATA = {
    "name": "get_portfolio_holdings",
    "version": "1.0.0",
    "description": "Retrieve current portfolio holdings from the database",
    "agent": "finn",
    "category": "database",
    
    "parameters": {},  # No parameters required
    
    "returns": {
        "type": "str",
        "description": "JSON string with holdings data (ticker, total_quantity, net_invested)"
    },
    
    "examples": [
        {
            "description": "Get all holdings",
            "input": {},
            "output": "[{\"ticker\": \"AAPL\", \"total_quantity\": 100, \"net_invested\": 15000.00}]"
        }
    ],
    
    "tags": ["database", "portfolio", "read", "holdings", "query"]
}

# ============================================================================
# SKILL EXECUTION
# ============================================================================

def execute(**params):
    """Main entry point for skill execution."""
    return get_holdings()

def get_holdings():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM holdings_view")
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        return json.dumps(results, indent=2)
    except Exception as e:
        return str(e)
    finally:
        conn.close()

if __name__ == "__main__":
    print(get_holdings())
