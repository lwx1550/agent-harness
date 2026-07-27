from typing import List, Dict


class ContextManager:
    def __init__(self, max_tokens: int = 128000):
        self.max_tokens = max_tokens
        self._messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str):
        self._messages.append({"role": role, "content": content})
        self._truncate()

    def get_messages(self) -> List[Dict[str, str]]:
        return list(self._messages)

    def clear(self):
        self._messages = []

    def _truncate(self):
        total = sum(len(m.get("content", "")) for m in self._messages)
        while total > self.max_tokens and len(self._messages) > 1:
            removed = self._messages.pop(1)
            total -= len(removed.get("content", ""))
        if total > self.max_tokens and len(self._messages) == 1:
            # Also truncate the system prompt if it's too long
            self._messages[0]["content"] = self._messages[0]["content"][:self.max_tokens]
