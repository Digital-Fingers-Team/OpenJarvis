"""Calculator tool."""

from minimal_jarvis.tools.base import Tool


class CalculatorTool(Tool):
    """Tool that evaluates simple arithmetic expressions."""

    name = "calculator"
    description = "Solve math problems. Usage: calculator(expression='2+2')"

    def execute(self, **kwargs: str) -> str:
        """Evaluate a math expression with eval for MVP."""
        expression = kwargs.get("expression", "")
        try:
            result = eval(expression)
            return f"{expression} = {result}"
        except Exception as exc:
            return f"Calculator error: {exc}"
