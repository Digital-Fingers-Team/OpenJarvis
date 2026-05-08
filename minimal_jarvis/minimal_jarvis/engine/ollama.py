"""Ollama inference engine."""

import requests

from minimal_jarvis.engine.base import InferenceEngine


class OllamaEngine(InferenceEngine):
    """Inference engine that calls local Ollama HTTP API."""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        """Generate response text from Ollama and return full output."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": max_tokens}},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            return str(payload.get("response", "")).strip()
        except requests.RequestException as exc:
            return f"Engine error: unable to reach Ollama ({exc})"
        except ValueError as exc:
            return f"Engine error: invalid JSON response ({exc})"
