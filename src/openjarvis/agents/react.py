from __future__ import annotations

from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent


class ReactAgent(BaseAgent):
    """Lightweight async wrapper for compatibility with advanced orchestration APIs."""

    async def execute(self, input: AgentInput) -> AgentOutput:
        return AgentOutput(
            result=input.data,
            confidence=0.6,
            reasoning=["Delegated to compatibility ReactAgent wrapper"],
        )
