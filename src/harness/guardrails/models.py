from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Verdict(Enum):
    PASS = "pass"
    BLOCK = "block"
    NEEDS_APPROVAL = "approval"
    WARN = "warn"


@dataclass
class GuardRule:
    pattern: str
    action_type: str
    verdict: str
    reason: str = ""


@dataclass
class Action:
    type: str  # "tool_call" | "finish"
    tool: Optional[str] = None
    params: Optional[dict] = None
    summary: str = ""
    thought: str = ""
