"""Shell tool."""

import subprocess

from minimal_jarvis.tools.base import Tool


class ShellTool(Tool):
    """Tool that runs shell commands."""

    name = "shell"
    description = "Execute shell commands. Usage: shell(command='ls')"

    def execute(self, **kwargs: str) -> str:
        """Execute shell command and return stdout/stderr."""
        command = kwargs.get("command", "")
        try:
            completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = completed.stdout.strip() or completed.stderr.strip()
            return output or "Command executed with no output."
        except Exception as exc:
            return f"Shell error: {exc}"
