import sqlite3
import os

DB_PATH = os.path.join("memory", "portfolio.db")

# ============================================================================
# SKILL METADATA
# ============================================================================

SKILL_METADATA = {
    "name": "initialize_portfolio_database",
    "version": "1.0.0",
    "description": "Initialize the portfolio database schema (assets, transactions, views)",
    "agent": "finn",
    "category": "database",
    
    "parameters": {},  # No parameters required
    
    "returns": {
        "type": "str",
        "description": "Success message"
    },
    
    "examples": [
        {
            "description": "Initialize database",
            "input": {},
            "output": "Database initialized successfully at memory/portfolio.db"
        }
    ],
    
    "tags": ["database", "setup", "schema", "initialization"]
}

# ============================================================================
# SKILL EXECUTION
# ============================================================================

def execute(**params):
    """Main entry point for skill execution."""
    create_schema()
    return f"Database initialized successfully at {DB_PATH}"

def create_schema():
    """Initializes the SQLite schema for the portfolio database."""
    
    # Ensure memory directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Assets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT UNIQUE NOT NULL,
        asset_class TEXT NOT NULL,
        sector TEXT,
        currency TEXT DEFAULT 'USD'
    );
    """)
    
    # 2. Transactions Table
    # Storing financial values as TEXT to ensure Decimal precision in Python
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        action TEXT NOT NULL CHECK(action IN ('BUY', 'SELL', 'DIVIDEND', 'INTEREST')),
        quantity TEXT NOT NULL,
        price TEXT NOT NULL,
        fees TEXT DEFAULT '0.00',
        total_amount TEXT NOT NULL,
        source_file TEXT,
        FOREIGN KEY(ticker) REFERENCES assets(ticker)
    );
    """)
    
    # 3. Holdings View (Simple aggregation)
    cursor.execute("DROP VIEW IF EXISTS holdings_view;")
    cursor.execute("""
    CREATE VIEW holdings_view AS
    SELECT 
        ticker,
        SUM(CASE WHEN action = 'BUY' THEN CAST(quantity AS DECIMAL) 
                 WHEN action = 'SELL' THEN -CAST(quantity AS DECIMAL) 
                 ELSE 0 END) as total_quantity,
        SUM(CASE WHEN action = 'BUY' THEN CAST(total_amount AS DECIMAL)
                 WHEN action = 'SELL' THEN -CAST(total_amount AS DECIMAL)
                 ELSE 0 END) as net_invested
    FROM transactions
    GROUP BY ticker;
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    create_schema()
