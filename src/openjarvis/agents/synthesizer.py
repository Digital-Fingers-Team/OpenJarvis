"""Synthesizer agent for creating final responses."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent
from openjarvis.core.registry import AgentRegistry


@AgentRegistry.register("synthesizer")
class SynthesizerAgent(BaseAgent):
    """Agent that synthesizes the final answer from execution results and reflection."""

    async def execute(self, input: AgentInput) -> AgentOutput:
        """
        Synthesize the final answer.
        Input data is expected to be a JSON string containing 'results' and 'reflection'.
        """
        try:
            data = json.loads(input.data)
            results = data.get("results", [])
            reflection = data.get("reflection", {})
            
            # Minimal synthesis logic: combine results into a coherent answer.
            # In a real system, this would involve an LLM call.
            
            if isinstance(reflection, str):
                reflection = json.loads(reflection)
            
            if reflection.get("status") == "failed":
                return AgentOutput(
                    result=f"Task failed: {reflection.get('feedback')}",
                    confidence=1.0,
                    reasoning=["Synthesized failure message based on negative reflection."]
                )
            
            # Combine results
            combined_results = []
            for res in results:
                if isinstance(res, dict) and "result" in res:
                    combined_results.append(str(res["result"]))
                else:
                    combined_results.append(str(res))
            
            final_answer = "\n\n".join(combined_results)
            
            return AgentOutput(
                result=final_answer,
                confidence=0.95,
                reasoning=["Combined all execution results into a final response."]
            )
        except Exception as e:
            return AgentOutput(
                result=f"Synthesis failed: {str(e)}",
                confidence=0.0,
                reasoning=[f"Error during synthesis: {str(e)}"]
            )
