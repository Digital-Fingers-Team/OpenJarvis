from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent


class ReflectorAgent(BaseAgent):
    async def execute(self, input: AgentInput) -> AgentOutput:
        return AgentOutput(result="Execution reviewed. Continue.", confidence=0.8, reasoning=["Reflected on execution result"])
