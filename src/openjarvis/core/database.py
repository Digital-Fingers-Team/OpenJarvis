"""OpenJarvis database access layer.

This module provides a **layered** SQLite persistence abstraction for OpenJarvis.

Layers
------
1) Connection/session management
   - Thread-safe shared connection with WAL mode.
   - Context-managed transactions via :meth:`DatabaseManager.transaction`.
   - Startup/shutdown lifecycle via :meth:`DatabaseManager.close` and context manager protocol.

2) Schema and versioned migrations
   - Lightweight migration system backed by ``schema_migrations``.
   - Monotonic integer versions with idempotent migration functions.

3) Query and domain operations
   - Low-level query helpers (:meth:`execute`, :meth:`fetchone`, :meth:`fetchall`).
   - Domain methods for preferences and memory entries while preserving legacy API.

4) Serialization boundary
   - JSON payload validation/normalization through small Pydantic models.

Backward compatibility
----------------------
The existing public methods remain available:
``execute``, ``commit``, ``close``, ``store_preference``, ``get_preference``,
``add_memory``, and ``get_memory``.

Example
-------
>>> from openjarvis.core.database import DatabaseManager
>>> with DatabaseManager(":memory:") as db:
...     db.store_preference("theme", {"mode": "dark"})
...     assert db.get_preference("theme")["mode"] == "dark"
...     _ = db.add_memory(key="agent_memory", value="remember this")
...     assert db.get_memory("agent_memory")
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional

from pydantic import BaseModel, Field


class DatabaseError(RuntimeError):
    """Base error for database operations."""


class MigrationError(DatabaseError):
    """Raised when schema migration fails."""


class SerializationError(DatabaseError):
    """Raised when JSON serialization or deserialization fails."""


class PreferenceRecord(BaseModel):
    """Validated user preference payload."""

    key: str
    value: Any
    updated_at: float = Field(default_factory=time.time)


class MemoryEntryRecord(BaseModel):
    """Validated memory entry payload."""

    id: str
    key: str
    value: Any
    category: str = "general"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float
    updated_at: float


MigrationFn = Callable[[sqlite3.Connection], None]


class DatabaseManager:
    """Unified, thread-safe interface for OpenJarvis persistent storage."""

    _MIGRATIONS: Dict[int, tuple[str, MigrationFn]] = {
        1: (
            "create_initial_tables",
            lambda conn: _create_initial_schema(conn),
        ),
    }

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            from openjarvis.core.config import DEFAULT_CONFIG_DIR

            db_path = DEFAULT_CONFIG_DIR / "openjarvis.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._closed = False

        try:
            self._conn = sqlite3.connect(
                str(self.db_path), check_same_thread=False, isolation_level=None
            )
            self._conn.row_factory = sqlite3.Row
            self._configure_connection()
            self._apply_migrations()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to initialize database at {self.db_path}: {exc}") from exc

    def _configure_connection(self) -> None:
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.execute("PRAGMA busy_timeout=5000")

    def _ensure_open(self) -> None:
        if self._closed:
            raise DatabaseError("DatabaseManager is closed")

    def _apply_migrations(self) -> None:
        with self.transaction():
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at REAL NOT NULL
                )
                """
            )
            current_version_row = self._conn.execute(
                "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
            ).fetchone()
            current_version = int(current_version_row["version"] if current_version_row else 0)

            for version in sorted(self._MIGRATIONS):
                if version <= current_version:
                    continue
                name, migration = self._MIGRATIONS[version]
                try:
                    migration(self._conn)
                    self._conn.execute(
                        "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                        (version, name, time.time()),
                    )
                except sqlite3.Error as exc:
                    raise MigrationError(
                        f"Failed applying migration v{version} ({name}): {exc}"
                    ) from exc

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Provide a thread-safe transaction scope.

        Commits on success and rolls back on exceptions.
        """

        self._ensure_open()
        with self._lock:
            try:
                self._conn.execute("BEGIN")
                yield self._conn
                self._conn.execute("COMMIT")
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """Execute a SQL statement and return the cursor (legacy API)."""

        self._ensure_open()
        try:
            with self._lock:
                return self._conn.execute(query, params)
        except sqlite3.Error as exc:
            raise DatabaseError(f"SQL execute failed: {exc}") from exc

    def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        """Execute a query and fetch one row."""

        return self.execute(query, params).fetchone()

    def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        """Execute a query and fetch all rows."""

        return self.execute(query, params).fetchall()

    def commit(self) -> None:
        """Commit pending work (legacy API).

        Note: most writes use autocommit or explicit :meth:`transaction`.
        """

        self._ensure_open()
        with self._lock:
            try:
                self._conn.commit()
            except sqlite3.Error as exc:
                raise DatabaseError(f"Commit failed: {exc}") from exc

    def close(self) -> None:
        """Close the underlying connection safely."""

        with self._lock:
            if self._closed:
                return
            self._conn.close()
            self._closed = True

    def __enter__(self) -> DatabaseManager:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    @staticmethod
    def _json_dumps(value: Any) -> str:
        try:
            return json.dumps(value)
        except (TypeError, ValueError) as exc:
            raise SerializationError(f"Failed to serialize value to JSON: {exc}") from exc

    @staticmethod
    def _json_loads(value: str) -> Any:
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise SerializationError(f"Failed to deserialize JSON value: {exc}") from exc

    def store_preference(self, key: str, value: Any) -> None:
        """Store/update user preference by key."""

        record = PreferenceRecord(key=key, value=value)
        payload = self._json_dumps(record.value)
        with self.transaction() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value, updated_at) VALUES (?, ?, ?)",
                (record.key, payload, record.updated_at),
            )

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Load a user preference and JSON-decode it."""

        row = self.fetchone("SELECT value FROM user_preferences WHERE key = ?", (key,))
        if row:
            return self._json_loads(row["value"])
        return default

    def add_memory(
        self,
        key: str,
        value: Any,
        category: str = "general",
        metadata: Dict[str, Any] | None = None,
    ) -> str:
        """Insert a memory entry and return entry id."""

        now = time.time()
        record = MemoryEntryRecord(
            id=str(uuid.uuid4()),
            key=key,
            value=value,
            category=category,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )
        with self.transaction() as conn:
            conn.execute(
                "INSERT INTO memory_entries (id, key, value, category, metadata, created_at, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record.id,
                    record.key,
                    self._json_dumps(record.value),
                    record.category,
                    self._json_dumps(record.metadata),
                    record.created_at,
                    record.updated_at,
                ),
            )
        return record.id

    def get_memory(self, key: str) -> List[Dict[str, Any]]:
        """Return all memory entries for a key, newest first."""

        rows = self.fetchall(
            "SELECT * FROM memory_entries WHERE key = ? ORDER BY updated_at DESC", (key,)
        )
        decoded: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["value"] = self._json_loads(item["value"])
            item["metadata"] = self._json_loads(item["metadata"])
            decoded.append(item)
        return decoded


def _create_initial_schema(conn: sqlite3.Connection) -> None:
    """Create baseline tables for OpenJarvis persistence."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            metadata TEXT NOT NULL DEFAULT '{}',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
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
        """
    )
    conn.execute(
        """
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
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_entries (
            id TEXT PRIMARY KEY,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            metadata TEXT NOT NULL DEFAULT '{}',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )
