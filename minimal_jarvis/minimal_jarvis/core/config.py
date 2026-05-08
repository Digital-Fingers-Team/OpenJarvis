"""Configuration model for Minimal Jarvis."""

from pydantic import BaseModel, Field


class JarvisConfig(BaseModel):
    """Configuration for creating a Jarvis instance."""

    model: str = "llama2"
    engine: str = "ollama"
    tools: list[str] = Field(default_factory=lambda: ["calculator", "shell", "web_search"])
