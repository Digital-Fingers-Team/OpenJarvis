"""Simple model selector."""


class ModelSelector:
    """Returns a model name based on a hint."""

    def select_model(self, hardware_hint: str = "") -> str:
        """Return a hardcoded model name for MVP."""
        _ = hardware_hint
        return "llama2"
