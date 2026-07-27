import fnmatch
from typing import List
from .models import Action, GuardRule


class Guardrail:
    def __init__(self, rules: List[GuardRule]):
        self.rules = rules

    def evaluate(self, action: Action) -> str:
        if action.type == "finish":
            return "pass"
        for rule in self.rules:
            if not self._match_action_type(rule.action_type, action.tool):
                continue
            param_str = ""
            if action.params:
                param_str = " ".join(str(v) for v in action.params.values())
            combined = f"{action.tool} {param_str}" if action.tool else param_str
            if fnmatch.fnmatch(combined, f"*{rule.pattern}*") or fnmatch.fnmatch(param_str, rule.pattern):
                return rule.verdict
        return "pass"

    def _match_action_type(self, rule_type: str, tool: str) -> bool:
        if rule_type == "*" or rule_type == tool:
            return True
        if fnmatch.fnmatch(tool, rule_type):
            return True
        return False
