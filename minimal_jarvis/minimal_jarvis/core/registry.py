"""Tool registry for Minimal Jarvis."""

from minimal_jarvis.tools.base import Tool


class ToolRegistry:
    """Stores and retrieves tools by name."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Return a tool by name if present."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List registered tool names."""
        return list(self._tools.keys())

    def get_descriptions(self) -> str:
        """Return one-line descriptions for prompt injection."""
        return "\n".join(f"- {tool.name}: {tool.description}" for tool in self._tools.values())
