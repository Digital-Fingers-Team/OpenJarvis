"""Manage persistent agent memory via DatabaseManager."""

from __future__ import annotations

import json
from typing import Any

from openjarvis.core import DatabaseManager
from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec


@ToolRegistry.register("memory_manage")
class MemoryManageTool(BaseTool):
    """Manage persistent agent memory via DatabaseManager."""

    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or DatabaseManager()

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="memory_manage",
            description=(
                "Read, add, update, or remove entries in persistent agent memory."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["read", "add", "update", "remove"],
                        "description": "Action to perform on memory.",
                    },
                    "entry": {
                        "type": "string",
                        "description": (
                            "The memory entry content (for add/update/remove)."
                        ),
                    },
                    "new_entry": {
                        "type": "string",
                        "description": (
                            "Replacement content (for update action only)."
                        ),
                    },
                    "category": {
                        "type": "string",
                        "description": "Memory category (e.g., 'short_term', 'long_term').",
                        "default": "general"
                    }
                },
                "required": ["action"],
            },
            category="memory",
        )

    def execute(self, **params: Any) -> ToolResult:
        action = params.get("action", "read")
        entry = params.get("entry", "")
        new_entry = params.get("new_entry", "")
        category = params.get("category", "general")
        
        if action == "read":
            return self._read(category)
        elif action == "add":
            return self._add(entry, category)
        elif action == "update":
            return self._update(entry, new_entry, category)
        elif action == "remove":
            return self._remove(entry, category)
        
        return ToolResult(
            tool_name=self.spec.name,
            success=False,
            content=f"Unknown action: {action}",
        )

    def _read(self, category: str) -> ToolResult:
        rows = self._db.execute(
            "SELECT value FROM memory_entries WHERE category = ? ORDER BY created_at DESC",
            (category,)
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

    def _add(self, entry: str, category: str) -> ToolResult:
        if not entry:
            return ToolResult(
                tool_name=self.spec.name,
                success=False,
                content="Entry cannot be empty.",
            )
        
        self._db.add_memory(key="agent_memory", value=entry, category=category)
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=f"Added to {category} memory: {entry}",
        )

    def _update(self, old: str, new: str, category: str) -> ToolResult:
        # For simplicity in this minimal fix, we update by value match
        row = self._db.execute(
            "SELECT id FROM memory_entries WHERE category = ? AND value = ?",
            (category, json.dumps(old))
        ).fetchone()
        
        if not row:
            return ToolResult(
                tool_name=self.spec.name,
                success=False,
                content=f"Entry not found in {category} memory: {old}",
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
            content=f"Updated in {category} memory: {old} -> {new}",
        )

    def _remove(self, entry: str, category: str) -> ToolResult:
        self._db.execute(
            "DELETE FROM memory_entries WHERE category = ? AND value = ?",
            (category, json.dumps(entry))
        )
        self._db.commit()
        
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=f"Removed from {category} memory: {entry}",
        )
