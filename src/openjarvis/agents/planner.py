import json
from typing import List

from pydantic import BaseModel, Field

from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent
from openjarvis.core.registry import AgentRegistry


class Step(BaseModel):
    number: int
    description: str
    tools_needed: List[str] = Field(default_factory=list)


class Plan(BaseModel):
    goal: str
    steps: List[Step]


@AgentRegistry.register("planner")
class PlannerAgent(BaseAgent):
    async def execute(self, input: AgentInput) -> AgentOutput:
        intent = json.loads(input.data)
        step = Step(number=1, description=intent.get("goal", "Complete task"), tools_needed=[])
        plan = Plan(goal=intent.get("goal", ""), steps=[step])
        return AgentOutput(result=json.dumps(plan.model_dump()), confidence=0.85, reasoning=["Created plan from intent"])
