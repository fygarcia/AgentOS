import sqlite3
import os
import json
import sys
from decimal import Decimal, InvalidOperation

# Add project root to path to allow imports if needed later
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = os.path.join("memory", "portfolio.db")

# ============================================================================
# SKILL METADATA - Required for AgentOS Skill Registry
# ============================================================================

SKILL_METADATA = {
    "name": "db_upsert_asset",
    "version": "1.0.0",
    "description": "Insert or update an asset in the portfolio database",
    "agent": "finn",
    "category": "database",
    
    "parameters": {
        "ticker": {
            "type": "str",
            "required": True,
            "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')"
        },
        "asset_class": {
            "type": "str",
            "required": True,
            "description": "Asset class (e.g., 'Equity', 'Bond', 'Crypto')"
        },
        "sector": {
            "type": "str",
            "required": False,
            "default": None,
            "description": "Sector classification (e.g., 'Technology', 'Healthcare')"
        },
        "currency": {
            "type": "str",
            "required": False,
            "default": "USD",
            "description": "Currency code (e.g., 'USD', 'EUR')"
        }
    },
    
    "returns": {
        "type": "dict",
        "description": "Result with status and message",
        "schema": {
            "status": "str (success|error)",
            "message": "str (description)"
        }
    },
    
    "examples": [
        {
            "description": "Add Apple stock",
            "input": {
                "ticker": "AAPL",
                "asset_class": "Equity",
                "sector": "Technology",
                "currency": "USD"
            },
            "output": {
                "status": "success",
                "message": "Asset AAPL upserted."
            }
        }
    ],
    
    "tags": ["database", "portfolio", "crud", "upsert", "asset"]
}

# ============================================================================
# SKILL EXECUTION ENTRY POINT
# ============================================================================

def execute(**params):
    """
    Main entry point for skill execution via registry.
    
    This function is called by the SkillRegistry when the skill is executed.
    It wraps the underlying upsert_asset function.
    
    Args:
        **params: Parameters from SKILL_METADATA.parameters
        
    Returns:
        Result dict from upsert_asset
    """
    return upsert_asset(
        ticker=params["ticker"],
        asset_class=params["asset_class"],
        sector=params.get("sector"),
        currency=params.get("currency", "USD")
    )

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def upsert_asset(ticker, asset_class, sector=None, currency="USD"):
    """
    Inserts a new asset or ignores if it already exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO assets (ticker, asset_class, sector, currency)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
                asset_class=excluded.asset_class,
                sector=COALESCE(excluded.sector, assets.sector),
                currency=excluded.currency
        """, (ticker, asset_class, sector, currency))
        conn.commit()
        return {"status": "success", "message": f"Asset {ticker} upserted."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def insert_transaction(date, ticker, action, quantity, price, fees="0.00", source_file=None):
    """
    Inserts a new transaction.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Validate decimals
    try:
        q = Decimal(str(quantity))
        p = Decimal(str(price))
        f = Decimal(str(fees))
        total = (q * p) + f # Basic logic, might need adjustment based on Buy/Sell sign convention
        
        # For SELL, quantity should ideally be negative in the view, but here we store absolute
        # and handle logic in the View or Application layer. 
        # However, the View definition: 
        # SUM(CASE WHEN action = 'BUY' THEN CAST(quantity AS DECIMAL) 
        #          WHEN action = 'SELL' THEN -CAST(quantity AS DECIMAL) 
        # implies we store positive values in the table.
        
    except InvalidOperation:
        return {"status": "error", "message": "Invalid decimal format for quantity, price, or fees."}

    try:
        # Ensure asset exists first? 
        # The FK constraint will fail if not. 
        # We could auto-create, but better to fail or require explicit asset creation.
        
        cursor.execute("""
            INSERT INTO transactions (date, ticker, action, quantity, price, fees, total_amount, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, ticker, action, str(q), str(p), str(f), str(total), source_file))
        
        conn.commit()
        return {"status": "success", "message": f"Transaction for {ticker} recorded."}
    except sqlite3.IntegrityError:
         return {"status": "error", "message": f"Asset {ticker} does not exist. Create it first."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    # Simple CLI for testing
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "add_asset":
            # python execution/db_upsert.py add_asset AAPL Equity Technology USD
            print(upsert_asset(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
        elif command == "add_tx":
            # python execution/db_upsert.py add_tx 2023-10-27 AAPL BUY 10 150.00 5.00 manual_entry
            print(insert_transaction(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8]))
    else:
        print("Usage: python db_upsert.py [add_asset|add_tx] ...")
