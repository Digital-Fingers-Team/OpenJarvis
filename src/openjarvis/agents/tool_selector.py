import json

from pydantic import BaseModel, Field

from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent


class ToolSelection(BaseModel):
    tool_name: str
    arguments: dict = Field(default_factory=dict)
    rationale: str = ""


class ToolSelectorAgent(BaseAgent):
    async def execute(self, input: AgentInput) -> AgentOutput:
        step = json.loads(input.data)
        tool_name = "calculator" if "+" in step.get("description", "") else "none"
        selection = ToolSelection(tool_name=tool_name, arguments={}, rationale="Basic heuristic")
        return AgentOutput(result=json.dumps(selection.model_dump()), confidence=0.8, reasoning=[f"Selected tool: {tool_name}"])
