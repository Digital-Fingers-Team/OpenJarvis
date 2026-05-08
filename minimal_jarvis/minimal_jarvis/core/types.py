"""Core data models and constants for Minimal Jarvis."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, Field

TOOL_CALL_TEMPLATE = """[TOOL_START]\nname: <tool_name>\nargs: arg1=value1, arg2=value2\n[TOOL_END]"""


class Message(BaseModel):
    """Represents a conversation message."""

    role: str
    content: str
    tool_name: Optional[str] = None


class Tool(ABC):
    """Abstract tool interface."""

    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: str) -> str:
        """Execute tool with string kwargs and return string result."""


class ToolResult(BaseModel):
    """Represents a single tool execution result."""

    tool_name: str
    result: str
    error: Optional[str] = None


class Response(BaseModel):
    """Represents the agent response payload."""

    response: str
    tool_calls: list[ToolResult] = Field(default_factory=list)
    reasoning: list[str] = Field(default_factory=list)
    turns: int = 0
