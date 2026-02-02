
import sys
import os
import shutil
from pathlib import Path
import json
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import lancedb
    print("✓ LanceDB imported successfully")
except ImportError:
    print("✗ Failed to import lancedb")
    sys.exit(1)

def test_lancedb_basic():
    """Test basic LanceDB operations."""
    print("\n[Test] Basic LanceDB Operations")
    
    # Setup test path
    test_db_path = Path("./tests/results/lancedb_test")
    if test_db_path.exists():
        shutil.rmtree(test_db_path)
    test_db_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Connect
        db = lancedb.connect(test_db_path)
        print("✓ Connected to DB")
        
        # 2. Create Table
        embedding_size = 768
        data = [
            {
                "id": "1", 
                "vector": [0.1] * embedding_size, 
                "text": "Hello world", 
                "metadata": json.dumps({"type": "test"})
            },
            {
                "id": "2", 
                "vector": [0.9] * embedding_size, 
                "text": "Goodbye world", 
                "metadata": json.dumps({"type": "test"})
            }
        ]
        
        tbl = db.create_table("test_memory", data=data)
        print("✓ Created table")
        
        # 3. Search
        query_vector = [0.1] * embedding_size
        results = tbl.search(query_vector).limit(1).to_list()
        
        if len(results) == 1 and results[0]['id'] == '1':
            print("✓ Search successful (found expected ID)")
            print(f"  Match: {results[0]['text']}")
        else:
            print("✗ Search failed or returned unexpected result")
            print(f"  Results: {results}")
            return False
            
        # 4. Add more data
        new_data = [{
            "id": "3", 
            "vector": [0.5] * embedding_size, 
            "text": "Middle world", 
            "metadata": json.dumps({"type": "new"})
        }]
        tbl.add(new_data)
        print("✓ Added new data")
        
        # Verify count
        count = len(tbl)
        if count == 3:
            print(f"✓ Table count correct: {count}")
        else:
            print(f"✗ Table count mismatch: {count}")
            return False

        return True
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if test_db_path.exists():
            shutil.rmtree(test_db_path)

if __name__ == "__main__":
    success = test_lancedb_basic()
    sys.exit(0 if success else 1)
