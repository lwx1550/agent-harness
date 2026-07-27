import json
from typing import Optional

import httpx

from .client import LLMClient, LLMResponse


class OpenAIClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    def chat(self, messages: list, tools: Optional[list] = None) -> LLMResponse:
        body = {"model": self.model, "messages": messages}
        if tools:
            body["tools"] = tools
        resp = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]["message"]
        if choice.get("tool_calls"):
            tc = choice["tool_calls"][0]
            fn = tc.get("function", {})
            return LLMResponse(
                type="tool_call",
                tool=fn.get("name", ""),
                params=json.loads(fn.get("arguments", "{}")),
                thought=choice.get("content", ""),
            )
        return LLMResponse(
            type="finish",
            summary=choice.get("content", ""),
            thought=choice.get("content", ""),
        )
