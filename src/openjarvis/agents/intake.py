import json
from typing import List

from pydantic import BaseModel

from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent


class ParsedIntent(BaseModel):
    goal: str
    entities: List[str]
    constraints: List[str]
    complexity: str
    requires_planning: bool


class IntakeAgent(BaseAgent):
    async def execute(self, input: AgentInput) -> AgentOutput:
        intent = ParsedIntent(goal=input.data, entities=[], constraints=[], complexity="simple", requires_planning=False)
        return AgentOutput(result=json.dumps(intent.model_dump()), confidence=0.9, reasoning=["Parsed user intent from query"])
