from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration: float = 0.0


class Tool(ABC):
    name: str = ""
    description: str = ""
    parameters: dict = {}

    @abstractmethod
    def execute(self, params: dict) -> ToolResult:
        ...

    def to_llm_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
