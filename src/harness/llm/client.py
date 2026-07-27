from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    type: str  # "tool_call" | "finish"
    tool: Optional[str] = None
    params: Optional[dict] = None
    summary: str = ""
    thought: str = ""


class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list, tools: Optional[list] = None) -> LLMResponse:
        ...
