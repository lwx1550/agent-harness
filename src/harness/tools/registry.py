from typing import Dict, List
from .base import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def to_llm_format(self) -> List[dict]:
        return [t.to_llm_tool() for t in self._tools.values()]
