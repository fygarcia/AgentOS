"""
Memory Manager - Core persistent memory system for AgentOS

Implements the three-tier memory architecture:
- HOT (NOW.md): Current objective and next steps
- WARM (LOG.md): Recent activity history (~20 actions)
- COLD (LanceDB): Long-term semantic memory

Each agent instance has isolated memory storage.
"""

import os
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import requests

# LanceDB imports
try:
    import lancedb
    LANCEDB_AVAILABLE = True
except (ImportError, Exception) as e:
    LANCEDB_AVAILABLE = False
    print(f"INFO: LanceDB not available ({type(e).__name__}). Cold memory disabled.")

from core.config import config



class MemoryManager:
    """
    Central memory orchestration for an agent.
    
    Each agent gets its own MemoryManager instance with isolated storage.
    """
    
    def __init__(self, agent_name: str, base_path: Optional[Path] = None):
        """
        Initialize memory manager for a specific agent.
        
        Args:
            agent_name: Name of the agent (e.g., 'finn', 'code-agent')
            base_path: Base path for agent files (defaults to ./agents/<agent_name>)
        """
        self.agent_name = agent_name
        # UPDATE: Default path is now ./agents/<agent_name>
        self.base_path = base_path or Path(f"./agents/{agent_name}")
        self.memory_path = self.base_path / "memory"
        
        # File paths
        self.now_file = self.memory_path / "NOW.md"
        self.log_file = self.memory_path / "LOG.md"
        self.db_file = self.memory_path / "memory.db"
        self.lancedb_path = self.memory_path / "lancedb"
        
        # Configuration
        self.log_max_size_kb = 50  # Trigger compaction at 50KB
        self.log_max_entries = 100  # Or 100 entries
        self.embedding_dimension = 768  # Default for nomic-embed-text
        
        # Initialize storage
        self._initialize_storage()
        self._initialize_database()
        if LANCEDB_AVAILABLE:
            self._initialize_lancedb()
        else:
            self.lance_db = None
            self.lance_table = None
    
    def _initialize_storage(self):
        """Create memory directory structure if it doesn't exist."""
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize NOW.md with default content
        if not self.now_file.exists():
            self.now_file.write_text(
                "# Current Status\n\n"
                "Status: Idle\n\n"
                "## Next Steps\n"
                "- Awaiting user input\n",
                encoding='utf-8'
            )
        
        # Initialize LOG.md with header
        if not self.log_file.exists():
            self.log_file.write_text(
                f"# Activity Log - {self.agent_name}\n\n"
                f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "---\n\n",
                encoding='utf-8'
            )
    
    def _initialize_database(self):
        """Initialize SQLite database with schema."""
        schema_file = Path(__file__).parent / "memory_schema.sql"
        
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        # Execute schema
        if schema_file.exists():
            schema_sql = schema_file.read_text()
            cursor.executescript(schema_sql)
        else:
            # Fallback inline schema (in case file not found)
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS log_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    entry_type TEXT NOT NULL,
                    content_hash TEXT,
                    compacted BOOLEAN DEFAULT 0,
                    line_number INTEGER,
                    token_count INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS compaction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    compacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    entries_count INTEGER NOT NULL,
                    summary TEXT,
                    archive_id TEXT,
                    original_size_kb REAL,
                    new_size_kb REAL
                );
            """)
        
        conn.commit()
        conn.close()
    
    def _initialize_lancedb(self):
        """Initialize LanceDB for semantic/cold memory."""
        try:
            self.lance_db = lancedb.connect(self.lancedb_path)
            
            # Table name includes agent name to avoid collisions if sharing DB (though we segregate folders)
            table_name = f"{self.agent_name}_memory"
            
            # Create table if not exists (schema is inferred from first data or we can force it)
            # We'll lazy load/create on first store to avoid schema definition complexity here
            # Or check if exists
            if table_name in self.lance_db.table_names():
                self.lance_table = self.lance_db.open_table(table_name)
            else:
                self.lance_table = None # Will create on first insert
                
        except Exception as e:
            print(f"WARNING: LanceDB initialization failed: {e}")
            self.lance_db = None
            self.lance_table = None

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Ollama."""
        try:
            url = f"{config.OLLAMA_BASE_URL}/api/embeddings"
            response = requests.post(url, json={
                "model": config.EMBEDDING_MODEL,
                "prompt": text
            })
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                print(f"Error getting embedding: {response.text}")
                return [0.0] * self.embedding_dimension # Fallback
        except Exception as e:
            print(f"Error calling embedding API: {e}")
            return [0.0] * self.embedding_dimension
    
    # ========================================
    # HOT MEMORY (NOW.md) - Current State
    # ========================================
    
    def read_now(self) -> str:
        """Read current status from NOW.md."""
        if self.now_file.exists():
            return self.now_file.read_text(encoding='utf-8')
        return "Status: Idle"
    
    def update_now(self, new_status: str, next_steps: Optional[List[str]] = None) -> bool:
        """
        Update NOW.md with new status and next steps.
        
        Args:
            new_status: Current objective/goal
            next_steps: Optional list of next actions
            
        Returns:
            True if successful
        """
        try:
            content = f"# Current Status\n\n"
            content += f"Status: {new_status}\n\n"
            content += f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if next_steps:
                content += "## Next Steps\n"
                for step in next_steps:
                    content += f"- {step}\n"
            
            self.now_file.write_text(content, encoding='utf-8')
            
            # Log the status update
            self.append_log(
                entry_type="SYSTEM",
                content=f"Status updated: {new_status}"
            )
            
            return True
        except Exception as e:
            print(f"ERROR updating NOW.md: {e}")
            return False
    
    # ========================================
    # WARM MEMORY (LOG.md) - Recent History
    # ========================================
    
    def read_log(self, last_n_entries: Optional[int] = None) -> str:
        """
        Read recent activity log.
        
        Args:
            last_n_entries: Optional, return only last N entries
            
        Returns:
            LOG.md content
        """
        if not self.log_file.exists():
            return ""
        
        content = self.log_file.read_text(encoding='utf-8')
        
        if last_n_entries:
            # Split by entry separator and return last N
            entries = content.split('\n---\n')
            return '\n---\n'.join(entries[-last_n_entries:])
        
        return content
    
    def append_log(
        self, 
        entry_type: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Append entry to LOG.md.
        
        Args:
            entry_type: TOOL_USE, THOUGHT, USER_FEEDBACK, ERROR, SYSTEM
            content: Log entry content
            metadata: Optional additional metadata
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            # Format entry
            entry = f"\n## [{entry_type}] {timestamp}\n\n"
            entry += f"{content}\n"
            
            if metadata:
                entry += f"\nMetadata: {json.dumps(metadata, indent=2)}\n"
            
            entry += "\n---\n"
            
            # Append to file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            # Store metadata in database
            self._store_log_metadata(
                entry_type=entry_type,
                content_hash=content_hash,
                token_count=len(content.split())  # Rough estimate
            )
            
            # Check if compaction needed
            self._check_compaction_needed()
            
            return True
        except Exception as e:
            print(f"ERROR appending to LOG.md: {e}")
            return False
    
    def _store_log_metadata(self, entry_type: str, content_hash: str, token_count: int):
        """Store log entry metadata in database."""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO log_metadata (entry_type, content_hash, token_count) VALUES (?, ?, ?)",
            (entry_type, content_hash, token_count)
        )
        
        conn.commit()
        conn.close()
    
    def _check_compaction_needed(self) -> bool:
        """Check if LOG.md needs compaction."""
        # Check file size
        file_size_kb = self.log_file.stat().st_size / 1024
        
        if file_size_kb > self.log_max_size_kb:
            print(f"LOG.md size ({file_size_kb:.2f}KB) exceeds limit. Triggering compaction...")
            return True
        
        # Check entry count
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM log_metadata WHERE compacted = 0")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > self.log_max_entries:
            print(f"LOG.md entries ({count}) exceeds limit. Triggering compaction...")
            return True
        
        return False
    
    def compact_log(self, summary: str) -> bool:
        """
        Compact LOG.md by archiving to LanceDB and keeping summary.
        
        Args:
            summary: LLM-generated summary of the log
            
        Returns:
            True if successful
        """
        try:
            # Read current log
            original_content = self.read_log()
            original_size = self.log_file.stat().st_size / 1024
            
            # Archive to LanceDB
            archive_id = None
            if self.lance_db:
                archive_id = f"archive_{datetime.now().timestamp()}"
                self.store_memory(
                    content=original_content,
                    metadata={
                        "type": "archived_log",
                        "agent": self.agent_name,
                        "archived_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "summary": summary
                    }
                )
            
            # Count entries
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM log_metadata WHERE compacted = 0")
            entries_count = cursor.fetchone()[0]
            
            # Mark all as compacted
            cursor.execute("UPDATE log_metadata SET compacted = 1 WHERE compacted = 0")
            
            # Record compaction
            cursor.execute(
                """INSERT INTO compaction_history 
                   (entries_count, summary, archive_id, original_size_kb) 
                   VALUES (?, ?, ?, ?)""",
                (entries_count, summary, archive_id, original_size)
            )
            
            conn.commit()
            conn.close()
            
            # Rewrite LOG.md with summary
            new_content = f"# Activity Log - {self.agent_name}\n\n"
            new_content += f"Compacted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            new_content += f"## Summary of Previous Activity\n\n{summary}\n\n"
            new_content += "---\n\n"
            
            self.log_file.write_text(new_content, encoding='utf-8')
            
            new_size = self.log_file.stat().st_size / 1024
            print(f"Compaction complete: {original_size:.2f}KB → {new_size:.2f}KB")
            
            return True
        except Exception as e:
            print(f"ERROR during log compaction: {e}")
            return False
    
    # ========================================
    # COLD MEMORY (LanceDB) - Semantic Search
    # ========================================
    
    def recall_memory(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search cold memory for relevant information.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant memory chunks with metadata
        """
        if not self.lance_db:
            print("WARNING: LanceDB not available. Cannot recall from cold memory.")
            return []
        
        try:
            table_name = f"{self.agent_name}_memory"
            if table_name not in self.lance_db.table_names():
                return []
                
            tbl = self.lance_db.open_table(table_name)
            
            # Generate query embedding
            query_embedding = self._get_embedding(query)
            
            # Search
            results = tbl.search(query_embedding).limit(n_results).to_list()
            
            memories = []
            for res in results:
                memories.append({
                    'content': res['text'],
                    'metadata': json.loads(res['metadata']) if res.get('metadata') else {},
                    'distance': res.get('_distance', 0.0)
                })
            
            return memories
        except Exception as e:
            print(f"ERROR recalling memory: {e}")
            return []
    
    def store_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store information in cold memory.
        
        Args:
            content: Content to store
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        if not self.lance_db:
            print("WARNING: LanceDB not available. Cannot store to cold memory.")
            return False
        
        try:
            doc_id = f"memory_{datetime.now().timestamp()}"
            vector = self._get_embedding(content)
            
            meta = metadata or {}
            meta['agent'] = self.agent_name
            meta['stored_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            data = [{
                "id": doc_id,
                "vector": vector,
                "text": content,
                "metadata": json.dumps(meta) # Flatten metadata to string for simplicity
            }]
            
            table_name = f"{self.agent_name}_memory"
            if table_name in self.lance_db.table_names():
                tbl = self.lance_db.open_table(table_name)
                tbl.add(data)
            else:
                self.lance_db.create_table(table_name, data=data)
            
            return True
        except Exception as e:
            print(f"ERROR storing memory: {e}")
            return False
    
    # ========================================
    # USER FACTS (SQLite) - Structured Data
    # ========================================
    
    def save_fact(
        self, 
        key: str, 
        value: str, 
        category: str = "general"
    ) -> bool:
        """
        Save user fact/preference.
        
        Args:
            key: Fact identifier (e.g., 'user_name', 'api_key')
            value: Fact value
            category: Category (general, preference, personal, config)
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT OR REPLACE INTO user_facts (key, value, category, updated_at) 
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                (key, value, category)
            )
            
            conn.commit()
            conn.close()
            
            # Log the fact save
            self.append_log(
                entry_type="SYSTEM",
                content=f"Saved fact: {key} = {value} (category: {category})"
            )
            
            return True
        except Exception as e:
            print(f"ERROR saving fact: {e}")
            return False
    
    def get_fact(self, key: str) -> Optional[str]:
        """
        Retrieve user fact by key.
        
        Args:
            key: Fact identifier
            
        Returns:
            Fact value or None if not found
        """
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM user_facts WHERE key = ?", (key,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"ERROR retrieving fact: {e}")
            return None
    
    def get_all_facts(self, category: Optional[str] = None) -> Dict[str, str]:
        """
        Get all user facts, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of key-value pairs
        """
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            if category:
                cursor.execute("SELECT key, value FROM user_facts WHERE category = ?", (category,))
            else:
                cursor.execute("SELECT key, value FROM user_facts")
            
            facts = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return facts
        except Exception as e:
            print(f"ERROR retrieving facts: {e}")
            return {}
    
    # ========================================
    # CONTEXT INJECTION - For LLM Prompts
    # ========================================
    
    def read_context(self) -> Dict[str, str]:
        """
        Read all memory context for injection into LLM prompts.
        
        Returns:
            Dictionary with 'now', 'log', and 'facts' sections
        """
        return {
            'now': self.read_now(),
            'log': self.read_log(last_n_entries=20),  # Last 20 entries
            'facts': json.dumps(self.get_all_facts(), indent=2)
        }
    
    def format_context_for_prompt(self) -> str:
        """
        Format memory context for inclusion in system prompt.
        
        Returns:
            Formatted string ready for prompt injection
        """
        context = self.read_context()
        
        formatted = "=== CURRENT MENTAL STATE (Do not ignore) ===\n"
        formatted += "You are currently working on:\n"
        formatted += context['now'] + "\n\n"
        
        formatted += "=== RECENT ACTIVITY LOG ===\n"
        formatted += context['log'] + "\n\n"
        
        if context['facts'] != "{}":
            formatted += "=== KNOWN USER FACTS ===\n"
            formatted += context['facts'] + "\n\n"
        
        return formatted
