"""Tool call parser for ReAct outputs."""

import re


def parse_tool_call(response: str) -> dict[str, object] | None:
    """Parse a [TOOL_START]...[TOOL_END] block into name/args dictionary."""
    pattern = r"\[TOOL_START\]\s*name:\s*(?P<name>[^\n]+)\s*args:\s*(?P<args>[^\n]*)\s*\[TOOL_END\]"
    match = re.search(pattern, response, flags=re.MULTILINE)
    if not match:
        return None
    tool_name = match.group("name").strip()
    args_raw = match.group("args").strip()
    args: dict[str, str] = {}
    if args_raw:
        for part in args_raw.split(","):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            args[key.strip()] = value.strip().strip("\"'")
    return {"name": tool_name, "args": args}
