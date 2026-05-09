"""Centralized database manager for OpenJarvis."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class DatabaseManager:
    """Unified interface for all persistent data storage."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            from openjarvis.core.config import DEFAULT_CONFIG_DIR
            db_path = DEFAULT_CONFIG_DIR / "openjarvis.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_tables()

    def _init_tables(self) -> None:
        """Initialize all required tables."""
        # Conversations
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        
        # Agent execution logs (Traces)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                input TEXT,
                output TEXT,
                status TEXT,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                duration REAL
            )
        """)
        
        # Tool execution results
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tool_executions (
                id TEXT PRIMARY KEY,
                execution_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                arguments TEXT,
                result TEXT,
                success INTEGER,
                created_at REAL NOT NULL,
                FOREIGN KEY(execution_id) REFERENCES execution_logs(id)
            )
        """)
        
        # Memory (Short + Long term)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'general', -- 'short_term', 'long_term'
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        
        # User preferences
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        self._conn.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        return self._conn.execute(query, params)

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # --- Helper methods for common operations ---

    def store_preference(self, key: str, value: Any) -> None:
        val_str = json.dumps(value)
        self._conn.execute(
            "INSERT OR REPLACE INTO user_preferences (key, value, updated_at) VALUES (?, ?, ?)",
            (key, val_str, time.time())
        )
        self._conn.commit()

    def get_preference(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute("SELECT value FROM user_preferences WHERE key = ?", (key,)).fetchone()
        if row:
            return json.loads(row["value"])
        return default

    def add_memory(self, key: str, value: Any, category: str = "general", metadata: Dict[str, Any] | None = None) -> str:
        import uuid
        entry_id = str(uuid.uuid4())
        now = time.time()
        self._conn.execute(
            "INSERT INTO memory_entries (id, key, value, category, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (entry_id, key, json.dumps(value), category, json.dumps(metadata or {}), now, now)
        )
        self._conn.commit()
        return entry_id

    def get_memory(self, key: str) -> List[Dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM memory_entries WHERE key = ? ORDER BY updated_at DESC", (key,)).fetchall()
        return [dict(r) for r in rows]
