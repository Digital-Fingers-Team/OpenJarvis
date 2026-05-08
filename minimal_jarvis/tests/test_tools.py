from minimal_jarvis.tools.calculator import CalculatorTool
from minimal_jarvis.tools.shell import ShellTool
from minimal_jarvis.tools.web_search import WebSearchTool


def test_calculator_tool() -> None:
    tool = CalculatorTool()
    assert tool.execute(expression="2+2") == "2+2 = 4"


def test_shell_tool() -> None:
    tool = ShellTool()
    output = tool.execute(command="echo hello")
    assert "hello" in output


def test_web_search_tool() -> None:
    tool = WebSearchTool()
    output = tool.execute(query="latest AI news")
    assert "Mock results" in output
