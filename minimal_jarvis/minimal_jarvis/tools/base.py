"""Base class for tools."""

from abc import ABC, abstractmethod


class Tool(ABC):
    """Abstract base class for all tools."""

    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: str) -> str:
        """Execute a tool action and return string output."""
