"""In-memory conversation store."""

from minimal_jarvis.core.types import Message


class ConversationMemory:
    """Stores message history for prompt context."""

    def __init__(self) -> None:
        self.messages: list[Message] = []

    def add(self, message: Message) -> None:
        """Append a message to the memory."""
        self.messages.append(message)

    def get_context(self) -> str:
        """Render conversation messages to a simple text context block."""
        return "\n".join(f"{message.role}: {message.content}" for message in self.messages)

    def clear(self) -> None:
        """Clear all conversation history."""
        self.messages.clear()
