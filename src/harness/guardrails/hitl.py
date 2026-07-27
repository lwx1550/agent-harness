from typing import Callable, Optional, Set


class HITLStateMachine:
    def __init__(self, input_func: Optional[Callable[[str], str]] = None):
        self._input = input_func or (lambda prompt: "n")
        self._skipped_patterns: Set[str] = set()

    def confirm(self, action_detail: str, verdict: str, reason: str) -> bool:
        if verdict != "approval":
            return True
        if action_detail in self._skipped_patterns:
            return True
        prompt = f"[HITL] Action: {action_detail}\nRisk: {reason}\nAllow? [y/n/s (skip for session)]: "
        answer = self._input(prompt).strip().lower()
        if answer == "s":
            self._skipped_patterns.add(action_detail)
            return True
        return answer == "y"

    def is_skipped(self, pattern: str) -> bool:
        return pattern in self._skipped_patterns
