"""Web search tool (mock implementation)."""

from minimal_jarvis.tools.base import Tool


class WebSearchTool(Tool):
    """Tool that returns mock search results for MVP."""

    name = "web_search"
    description = "Search the web. Usage: web_search(query='latest AI news')"

    def execute(self, **kwargs: str) -> str:
        """Return mock web search output."""
        query = kwargs.get("query", "")
        try:
            return f"Mock results for '{query}': 1) Example result A 2) Example result B"
        except Exception as exc:
            return f"Web search error: {exc}"
