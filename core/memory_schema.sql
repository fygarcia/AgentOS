-- Memory System Database Schema
-- Purpose: SQLite schema for agent memory persistence
-- Usage: Executed by MemoryManager during initialization

-- User facts and preferences (key-value store)
CREATE TABLE IF NOT EXISTS user_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    category TEXT DEFAULT 'general',  -- general, preference, personal, config
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast fact retrieval
CREATE INDEX IF NOT EXISTS idx_user_facts_key ON user_facts(key);
CREATE INDEX IF NOT EXISTS idx_user_facts_category ON user_facts(category);

-- Metadata for LOG.md entries (for tracking and compaction)
CREATE TABLE IF NOT EXISTS log_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entry_type TEXT NOT NULL,  -- TOOL_USE, THOUGHT, USER_FEEDBACK, ERROR, SYSTEM
    content_hash TEXT,          -- SHA256 hash for deduplication
    compacted BOOLEAN DEFAULT 0,
    line_number INTEGER,        -- Position in LOG.md file
    token_count INTEGER         -- Approximate token count
);

CREATE INDEX IF NOT EXISTS idx_log_metadata_timestamp ON log_metadata(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_metadata_compacted ON log_metadata(compacted);

-- Compaction history (track when LOG.md was compacted)
CREATE TABLE IF NOT EXISTS compaction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entries_count INTEGER NOT NULL,  -- Number of entries compacted
    summary TEXT,                     -- LLM-generated summary
    archive_id TEXT,                  -- ChromaDB collection ID for archived content
    original_size_kb REAL,            -- Size before compaction
    new_size_kb REAL                  -- Size after compaction
);

-- Trigger to update updated_at on user_facts
CREATE TRIGGER IF NOT EXISTS update_user_facts_timestamp 
AFTER UPDATE ON user_facts
BEGIN
    UPDATE user_facts SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
