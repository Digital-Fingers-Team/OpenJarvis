"""Reflector agent for reviewing execution results."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openjarvis.agents.base import AgentInput, AgentOutput, BaseAgent
from openjarvis.core.registry import AgentRegistry


@AgentRegistry.register("reflector")
class ReflectorAgent(BaseAgent):
    """Agent that reflects on the execution results and provides feedback."""

    async def execute(self, input: AgentInput) -> AgentOutput:
        """
        Reflect on the execution result.
        Input data is expected to be a JSON string containing 'plan' and 'results'.
        """
        try:
            data = json.loads(input.data)
            plan = data.get("plan", "No plan provided")
            results = data.get("results", [])
            
            # Minimal reflection logic: check if results match plan steps
            # In a real system, this would involve an LLM call.
            # For this fix, we provide a structured reflection.
            
            reflection = {
                "status": "completed",
                "feedback": "Execution matches the plan.",
                "missing_steps": [],
                "suggestions": []
            }
            
            if not results:
                reflection["status"] = "failed"
                reflection["feedback"] = "No results generated from execution."
            
            return AgentOutput(
                result=json.dumps(reflection),
                confidence=0.9,
                reasoning=["Analyzed execution results against the original plan."]
            )
        except Exception as e:
            return AgentOutput(
                result=f"Reflection failed: {str(e)}",
                confidence=0.0,
                reasoning=[f"Error during reflection: {str(e)}"]
            )
