import json

from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent


class SynthesizerAgent(BaseAgent):
    async def execute(self, input: AgentInput) -> AgentOutput:
        state = json.loads(input.data)
        summary = "; ".join([r.get("result", "") for r in state.get("step_results", [])])
        return AgentOutput(result=summary or state.get("query", ""), confidence=0.9, reasoning=["Synthesized final answer from all steps"])
