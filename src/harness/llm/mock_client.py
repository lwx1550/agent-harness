from typing import Optional
from .client import LLMClient, LLMResponse


class MockLLMClient(LLMClient):
    def __init__(self, responses: list):
        self._responses = list(responses)

    def chat(self, messages: list, tools: Optional[list] = None) -> LLMResponse:
        if not self._responses:
            raise StopIteration("No more mock responses available")
        data = self._responses.pop(0)
        if data["type"] == "tool_call":
            return LLMResponse(
                type="tool_call",
                tool=data["tool"],
                params=data.get("params", {}),
                thought=data.get("thought", ""),
            )
        return LLMResponse(
            type="finish",
            summary=data.get("summary", ""),
            thought=data.get("thought", ""),
        )
