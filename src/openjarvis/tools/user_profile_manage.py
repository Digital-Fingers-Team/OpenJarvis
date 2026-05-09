"""Manage persistent user profile via DatabaseManager."""

from __future__ import annotations

import json
from typing import Any

from openjarvis.core import DatabaseManager
from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec


@ToolRegistry.register("user_profile_manage")
class UserProfileManageTool(BaseTool):
    """Manage persistent user profile via DatabaseManager."""

    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or DatabaseManager()

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="user_profile_manage",
            description=("Read, add, update, or remove entries in user profile."),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["read", "add", "update", "remove"],
                        "description": "Action to perform on user profile.",
                    },
                    "entry": {
                        "type": "string",
                        "description": (
                            "The profile entry content (for add/update/remove)."
                        ),
                    },
                    "new_entry": {
                        "type": "string",
                        "description": (
                            "Replacement content (for update action only)."
                        ),
                    },
                },
                "required": ["action"],
            },
            category="memory",
        )

    def execute(self, **params: Any) -> ToolResult:
        action = params.get("action", "read")
        entry = params.get("entry", "")
        new_entry = params.get("new_entry", "")
        
        if action == "read":
            return self._read()
        elif action == "add":
            return self._add(entry)
        elif action == "update":
            return self._update(entry, new_entry)
        elif action == "remove":
            return self._remove(entry)
        
        return ToolResult(
            tool_name=self.spec.name,
            success=False,
            content=f"Unknown action: {action}",
        )

    def _read(self) -> ToolResult:
        rows = self._db.execute(
            "SELECT value FROM memory_entries WHERE category = 'user_profile' ORDER BY created_at DESC"
        ).fetchall()
        
        if not rows:
            return ToolResult(
                tool_name=self.spec.name,
                success=True,
                content="(empty)",
            )
        
        entries = [json.loads(r["value"]) for r in rows]
        content = "\n".join([f"- {e}" for e in entries])
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=content,
        )

    def _add(self, entry: str) -> ToolResult:
        if not entry:
            return ToolResult(
                tool_name=self.spec.name,
                success=False,
                content="Entry cannot be empty.",
            )
        
        self._db.add_memory(key="user_profile", value=entry, category="user_profile")
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=f"Added to user profile: {entry}",
        )

    def _update(self, old: str, new: str) -> ToolResult:
        row = self._db.execute(
            "SELECT id FROM memory_entries WHERE category = 'user_profile' AND value = ?",
            (json.dumps(old),)
        ).fetchone()
        
        if not row:
            return ToolResult(
                tool_name=self.spec.name,
                success=False,
                content=f"Entry not found in user profile: {old}",
            )
        
        import time
        self._db.execute(
            "UPDATE memory_entries SET value = ?, updated_at = ? WHERE id = ?",
            (json.dumps(new), time.time(), row["id"])
        )
        self._db.commit()
        
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=f"Updated in user profile: {old} -> {new}",
        )

    def _remove(self, entry: str) -> ToolResult:
        self._db.execute(
            "DELETE FROM memory_entries WHERE category = 'user_profile' AND value = ?",
            (json.dumps(entry),)
        )
        self._db.commit()
        
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=f"Removed from user profile: {entry}",
        )
