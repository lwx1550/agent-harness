import json
import os
from datetime import datetime
from typing import List
from .models import Action


class AuditLogger:
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(os.path.expanduser("~"), ".codex-harness", "audit")
        os.makedirs(self.log_dir, exist_ok=True)
        self._entries: List[dict] = []

    def log(self, action: Action, verdict: str, reason: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": {"type": action.type, "tool": action.tool, "params": action.params},
            "verdict": verdict,
            "reason": reason,
        }
        self._entries.append(entry)
        log_file = os.path.join(self.log_dir, f"audit-{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_entries(self) -> List[dict]:
        return list(self._entries)
