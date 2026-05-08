"""Public API for Minimal Jarvis."""

from minimal_jarvis.agents.react_agent import ReactAgent
from minimal_jarvis.core.registry import ToolRegistry
from minimal_jarvis.engine.ollama import OllamaEngine
from minimal_jarvis.memory.conversation import ConversationMemory
from minimal_jarvis.tools.calculator import CalculatorTool
from minimal_jarvis.tools.shell import ShellTool
from minimal_jarvis.tools.web_search import WebSearchTool


class Jarvis:
    """Main class for interacting with Minimal Jarvis."""

    def __init__(self, model: str = "llama2", engine: str = "ollama", tools: list[str] | None = None) -> None:
        self.engine_name = engine
        self.engine = OllamaEngine(model=model)
        self.memory = ConversationMemory()
        self.registry = ToolRegistry()

        available_tools = {
            "calculator": CalculatorTool(),
            "shell": ShellTool(),
            "web_search": WebSearchTool(),
        }
        selected_tools = tools if tools is not None else list(available_tools.keys())
        for tool_name in selected_tools:
            tool = available_tools.get(tool_name)
            if tool is not None:
                self.registry.register(tool)

        self.agent = ReactAgent(engine=self.engine, tools=self.registry, memory=self.memory)

    def ask(self, query: str, max_turns: int = 5) -> dict[str, object]:
        """Ask a question and return structured response dictionary."""
        response = self.agent.think_and_act(query=query, max_turns=max_turns)
        return {
            "response": response.response,
            "tool_calls": [
                {"tool": call.tool_name, "result": call.result, "error": call.error}
                for call in response.tool_calls
            ],
            "reasoning_steps": response.reasoning,
            "turns": response.turns,
        }

    def clear_memory(self) -> None:
        """Reset conversation memory."""
        self.memory.clear()
