from minimal_jarvis.core.types import Message
from minimal_jarvis.memory.conversation import ConversationMemory


def test_memory_add_get_clear() -> None:
    memory = ConversationMemory()
    memory.add(Message(role="user", content="hi"))
    memory.add(Message(role="assistant", content="hello"))
    context = memory.get_context()
    assert "user: hi" in context
    assert "assistant: hello" in context
    memory.clear()
    assert memory.get_context() == ""
