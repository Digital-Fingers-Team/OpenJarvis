from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    data: str
    context: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    result: str
    confidence: float = 0.5
    reasoning: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    def __init__(self, engine: Any, tools: Any, memory: Any) -> None:
        self.engine = engine
        self.tools = tools
        self.memory = memory
        self.name = self.__class__.__name__

    @abstractmethod
    async def execute(self, input: AgentInput) -> AgentOutput:
        raise NotImplementedError

    def build_prompt(self, **kwargs: Any) -> str:
        return ""
