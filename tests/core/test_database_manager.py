from __future__ import annotations

import threading

import pytest

from openjarvis.core.database import DatabaseError, DatabaseManager


def test_schema_migration_bootstrap(tmp_path):
    db_file = tmp_path / "openjarvis.db"
    with DatabaseManager(db_file) as db:
        row = db.fetchone("SELECT MAX(version) AS version FROM schema_migrations")
        assert row is not None
        assert row["version"] >= 1


def test_preference_roundtrip(tmp_path):
    with DatabaseManager(tmp_path / "prefs.db") as db:
        db.store_preference("theme", {"mode": "dark", "font_scale": 1.1})
        assert db.get_preference("theme") == {"mode": "dark", "font_scale": 1.1}
        assert db.get_preference("missing", default="x") == "x"


def test_memory_roundtrip_decodes_json(tmp_path):
    with DatabaseManager(tmp_path / "memory.db") as db:
        memory_id = db.add_memory(
            key="agent_memory",
            value={"fact": "Earth orbits Sun"},
            category="long_term",
            metadata={"source": "user"},
        )
        rows = db.get_memory("agent_memory")
        assert rows
        assert rows[0]["id"] == memory_id
        assert rows[0]["value"] == {"fact": "Earth orbits Sun"}
        assert rows[0]["metadata"] == {"source": "user"}


def test_characterization_execute_commit_api_still_works(tmp_path):
    with DatabaseManager(tmp_path / "legacy.db") as db:
        db.execute(
            "INSERT INTO user_preferences (key, value, updated_at) VALUES (?, ?, ?)",
            ("k", '"v"', 1.0),
        )
        db.commit()
        row = db.execute("SELECT value FROM user_preferences WHERE key = ?", ("k",)).fetchone()
        assert row is not None
        assert row["value"] == '"v"'


def test_concurrent_memory_writes_thread_safe(tmp_path):
    with DatabaseManager(tmp_path / "concurrency.db") as db:
        errors: list[Exception] = []

        def writer(idx: int) -> None:
            try:
                db.add_memory(key="k", value=f"v-{idx}", category="general")
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        rows = db.get_memory("k")
        assert len(rows) == 20


def test_close_rejects_new_work(tmp_path):
    db = DatabaseManager(tmp_path / "close.db")
    db.close()
    with pytest.raises(DatabaseError, match="closed"):
        db.execute("SELECT 1")
