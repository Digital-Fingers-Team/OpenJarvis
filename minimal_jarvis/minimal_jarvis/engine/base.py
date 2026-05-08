"""Inference engine abstraction."""

from abc import ABC, abstractmethod


class InferenceEngine(ABC):
    """Abstract base class for text generation engines."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int) -> str:
        """Generate a response from a prompt."""
