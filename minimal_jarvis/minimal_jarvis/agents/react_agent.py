"""Minimal ReAct agent."""

from minimal_jarvis.agents.tool_parser import parse_tool_call
from minimal_jarvis.core.registry import ToolRegistry
from minimal_jarvis.core.types import Message, Response, ToolResult, TOOL_CALL_TEMPLATE
from minimal_jarvis.engine.base import InferenceEngine
from minimal_jarvis.memory.conversation import ConversationMemory


class ReactAgent:
    """Runs a simple Think-Act-Observe loop with tool use."""

    def __init__(self, engine: InferenceEngine, tools: ToolRegistry, memory: ConversationMemory) -> None:
        self.engine = engine
        self.tools = tools
        self.memory = memory

    def think_and_act(self, query: str, max_turns: int = 5) -> Response:
        """Process a user query with iterative reasoning and tool execution."""
        self.memory.add(Message(role="user", content=query))
        tool_calls: list[ToolResult] = []
        reasoning: list[str] = []

        for turn in range(1, max_turns + 1):
            prompt = (
                "You are a helpful assistant.\n"
                "Available tools:\n"
                f"{self.tools.get_descriptions()}\n\n"
                "When a tool is needed, emit exactly this format:\n"
                f"{TOOL_CALL_TEMPLATE}\n\n"
                "Conversation:\n"
                f"{self.memory.get_context()}\n"
            )
            llm_output = self.engine.generate(prompt=prompt, max_tokens=512)
            reasoning.append(llm_output)

            parsed = parse_tool_call(llm_output)
            if parsed is None:
                self.memory.add(Message(role="assistant", content=llm_output))
                return Response(response=llm_output, tool_calls=tool_calls, reasoning=reasoning, turns=turn)

            tool_name = str(parsed["name"])
            args = parsed["args"]
            tool = self.tools.get(tool_name)
            if tool is None:
                observation = f"Tool error: unknown tool '{tool_name}'"
                tool_calls.append(ToolResult(tool_name=tool_name, result="", error=observation))
            else:
                result = tool.execute(**args)
                tool_calls.append(ToolResult(tool_name=tool_name, result=result))
                observation = f"Tool {tool_name} result: {result}"

            self.memory.add(Message(role="tool", content=observation, tool_name=tool_name))

        return Response(
            response="Reached max turns without a final answer.",
            tool_calls=tool_calls,
            reasoning=reasoning,
            turns=max_turns,
        )
