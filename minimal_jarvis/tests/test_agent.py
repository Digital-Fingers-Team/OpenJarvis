from minimal_jarvis.agents.react_agent import ReactAgent
from minimal_jarvis.core.registry import ToolRegistry
from minimal_jarvis.engine.base import InferenceEngine
from minimal_jarvis.memory.conversation import ConversationMemory
from minimal_jarvis.tools.calculator import CalculatorTool


class FakeEngine(InferenceEngine):
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str, max_tokens: int) -> str:
        self.calls += 1
        if self.calls == 1:
            return "[TOOL_START]\nname: calculator\nargs: expression=2+2\n[TOOL_END]"
        return "The answer is 4."


def test_react_agent_tool_loop() -> None:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    agent = ReactAgent(engine=FakeEngine(), tools=registry, memory=ConversationMemory())
    response = agent.think_and_act("What is 2+2?")
    assert response.response == "The answer is 4."
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].tool_name == "calculator"
