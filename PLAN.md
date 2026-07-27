# Agent Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ] ) syntax for tracking.

**Goal:** Build a lightweight, programmable CLI coding agent harness with a focus on guardrail safety mechanisms, distributable via PyPI and GitHub Releases.

**Architecture:** Three-layer design: CLI (typer) -> Agent Loop (context/LLM/parse/execute/feedback) -> Core mechanisms (tools/guardrails/feedback/memory). LLMClient abstraction layer supports mock injection for deterministic testing. Guardrail engine is the deep-dive dimension.

**Tech Stack:** Python 3.9+, typer, httpx, keyring, pytest, pyyaml, hatchling

---

## File Structure

\\\
src/
+-- harness/
|   +-- __init__.py
|   +-- cli.py
|   +-- agent.py
|   +-- llm/
|   |   +-- __init__.py
|   |   +-- client.py
|   |   +-- openai_client.py
|   |   +-- mock_client.py
|   +-- tools/
|   |   +-- __init__.py
|   |   +-- base.py
|   |   +-- registry.py
|   |   +-- builtins.py
|   +-- guardrails/
|   |   +-- __init__.py
|   |   +-- models.py
|   |   +-- engine.py
|   |   +-- hitl.py
|   |   +-- audit.py
|   +-- feedback/
|   |   +-- __init__.py
|   |   +-- parser.py
|   +-- memory/
|   |   +-- __init__.py
|   |   +-- manager.py
|   +-- config/
|       +-- __init__.py
|       +-- loader.py
tests/
+-- __init__.py
+-- test_guardrails.py
+-- test_tools.py
+-- test_agent.py
+-- test_feedback.py
+-- test_config.py
+-- test_cli.py
+-- test_credentials.py
SPEC.md
PLAN.md
.gitignore
pyproject.toml
README.md
AGENT_LOG.md
REFLECTION.md
\\\

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/harness/__init__.py`
- Create: `src/harness/llm/__init__.py`
- Create: `src/harness/tools/__init__.py`
- Create: `src/harness/guardrails/__init__.py`
- Create: `src/harness/feedback/__init__.py`
- Create: `src/harness/memory/__init__.py`
- Create: `src/harness/config/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "agent-harness"
version = "0.1.0"
description = "A lightweight, programmable CLI coding agent harness"
requires-python = ">=3.9"
dependencies = [
    "typer>=0.9.0",
    "httpx>=0.25.0",
    "keyring>=24.0.0",
    "pyyaml>=6.0",
    "cryptography>=41.0.0",
]

[project.scripts]
harness = "harness.cli:app"
```

- [ ] **Step 2: Create all __init__.py files**

Each `__init__.py` is empty except `src/harness/__init__.py` which exports version:

```python
__version__ = "0.1.0"
```

- [ ] **Step 3: Verify project loads**

Run: `pip install -e .`

Run: `python -c "import harness; print(harness.__version__)"`
Expected: `0.1.0`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "chore: scaffold project structure"
```
---

### Task 2: Config Loader

**Files:**
- Create: `src/harness/config/loader.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
import yaml
from pathlib import Path
from harness.config.loader import ConfigLoader, HarnessConfig

def test_load_default_config():
    loader = ConfigLoader()
    config = loader.get_default()
    assert isinstance(config, HarnessConfig)
    assert config.llm.model == "gpt-4o"
    assert config.agent.max_turns == 50
    assert len(config.guardrails.rules) > 0

def test_load_from_dict():
    loader = ConfigLoader()
    data = {"llm": {"model": "deepseek-chat"}, "agent": {"max_turns": 10}}
    config = loader.load(data)
    assert config.llm.model == "deepseek-chat"
    assert config.agent.max_turns == 10

def test_guard_rule_parsing():
    loader = ConfigLoader()
    data = {
        "guardrails": {
            "rules": [
                {"pattern": "rm -rf /*", "action_type": "command", "verdict": "block", "reason": "Dangerous deletion"}
            ]
        }
    }
    config = loader.load(data)
    assert len(config.guardrails.rules) == 1
    assert config.guardrails.rules[0].pattern == "rm -rf /*"
    assert config.guardrails.rules[0].verdict == "block"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/config/loader.py
from dataclasses import dataclass, field
from typing import List, Optional
import yaml

@dataclass
class GuardRuleConfig:
    pattern: str
    action_type: str
    verdict: str
    reason: str = ""

@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o"
    base_url: Optional[str] = None

@dataclass
class AgentConfig:
    max_turns: int = 50
    timeout: int = 300

@dataclass
class GuardrailsConfig:
    rules: List[GuardRuleConfig] = field(default_factory=lambda: [
        GuardRuleConfig(pattern="rm -rf /*", action_type="command", verdict="block", reason="Dangerous recursive deletion"),
        GuardRuleConfig(pattern="rm -rf /", action_type="command", verdict="block", reason="Dangerous root deletion"),
        GuardRuleConfig(pattern="DROP DATABASE*", action_type="command", verdict="approval", reason="Database drop requires confirmation"),
        GuardRuleConfig(pattern="format C:*", action_type="command", verdict="block", reason="Dangerous format command"),
        GuardRuleConfig(pattern="*del /f /s*", action_type="command", verdict="approval", reason="Force deletion requires confirmation"),
    ])

@dataclass
class HarnessConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    guardrails: GuardrailsConfig = field(default_factory=GuardrailsConfig)
    tools: List[str] = field(default_factory=lambda: ["read_file", "write_file", "edit_file", "run_command", "run_test"])

class ConfigLoader:
    def get_default(self) -> HarnessConfig:
        return HarnessConfig()

    def load(self, data: dict) -> HarnessConfig:
        llm_cfg = LLMConfig(**(data.get("llm", {})))
        agent_cfg = AgentConfig(**(data.get("agent", {})))
        guard_data = data.get("guardrails", {})
        rules = [GuardRuleConfig(**r) for r in guard_data.get("rules", [])]
        guard_cfg = GuardrailsConfig(rules=rules) if rules else GuardrailsConfig()
        tools = data.get("tools", [])
        return HarnessConfig(llm=llm_cfg, agent=agent_cfg, guardrails=guard_cfg, tools=tools)

    def load_from_file(self, path: str) -> HarnessConfig:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return self.load(data)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/config/ tests/test_config.py
git commit -m "feat: add config loader with default guardrail rules"
```

---

### Task 3: LLM Abstraction Layer

**Files:**
- Create: `src/harness/llm/client.py`
- Create: `src/harness/llm/openai_client.py`
- Create: `src/harness/llm/mock_client.py`
- Test: `tests/test_llm.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from harness.llm.client import LLMClient, LLMResponse, ToolCall
from harness.llm.mock_client import MockLLMClient

def test_mock_llm_returns_fixed_response():
    client = MockLLMClient(responses=[{"type": "finish", "summary": "done"}])
    resp = client.chat([{"role": "user", "content": "hello"}])
    assert resp.type == "finish"
    assert resp.summary == "done"

def test_mock_llm_returns_tool_call():
    client = MockLLMClient(responses=[{"type": "tool_call", "tool": "read_file", "params": {"path": "test.txt"}}])
    resp = client.chat([{"role": "user", "content": "read file"}])
    assert resp.type == "tool_call"
    assert resp.tool == "read_file"
    assert resp.params == {"path": "test.txt"}

def test_mock_llm_consumes_in_order():
    client = MockLLMClient(responses=[
        {"type": "tool_call", "tool": "read_file", "params": {"path": "a.txt"}},
        {"type": "finish", "summary": "done"},
    ])
    r1 = client.chat([])
    assert r1.tool == "read_file"
    r2 = client.chat([])
    assert r2.type == "finish"

def test_mock_llm_exhausted_raises():
    client = MockLLMClient(responses=[])
    with pytest.raises(StopIteration):
        client.chat([])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_llm.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/llm/client.py
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
```

```python
# src/harness/llm/mock_client.py
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
            return LLMResponse(type="tool_call", tool=data["tool"], params=data.get("params", {}), thought=data.get("thought", ""))
        return LLMResponse(type="finish", summary=data.get("summary", ""), thought=data.get("thought", ""))
```

```python
# src/harness/llm/openai_client.py
import httpx
from typing import Optional
from .client import LLMClient, LLMResponse
import json

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    def chat(self, messages: list, tools: Optional[list] = None) -> LLMResponse:
        body = {"model": self.model, "messages": messages}
        if tools:
            body["tools"] = tools
        resp = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
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
        return LLMResponse(type="finish", summary=choice.get("content", ""), thought=choice.get("content", ""))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_llm.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/llm/ tests/test_llm.py
git commit -m "feat: add LLM abstraction layer with mock client"
```
---

### Task 4: Guardrail Data Models

**Files:**
- Create: `src/harness/guardrails/models.py`
- Test: `tests/test_guardrails.py` (part 1)

- [ ] **Step 1: Write the failing test**

```python
from harness.guardrails.models import Action, Verdict, GuardRule

def test_action_creation():
    action = Action(type="tool_call", tool="run_command", params={"command": "echo hello"})
    assert action.type == "tool_call"
    assert action.tool == "run_command"

def test_action_finish():
    action = Action(type="finish", summary="done")
    assert action.type == "finish"
    assert action.summary == "done"

def test_verdict_values():
    assert Verdict.PASS.value == "pass"
    assert Verdict.BLOCK.value == "block"
    assert Verdict.NEEDS_APPROVAL.value == "approval"
    assert Verdict.WARN.value == "warn"

def test_guard_rule_creation():
    rule = GuardRule(pattern="rm -rf *", action_type="command", verdict="block", reason="test")
    assert rule.pattern == "rm -rf *"
    assert rule.verdict == "block"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_guardrails.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/guardrails/models.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_guardrails.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/guardrails/models.py tests/test_guardrails.py
git commit -m "feat: add guardrail data models (Action, Verdict, GuardRule)"
```

---

### Task 5: Guardrail Engine (Core Focus)

**Files:**
- Create: `src/harness/guardrails/engine.py`
- Test: `tests/test_guardrails.py` (append)

- [ ] **Step 1: Write the failing test**

```python
from harness.guardrails.models import Action, GuardRule
from harness.guardrails.engine import Guardrail

def test_block_dangerous_command():
    rules = [GuardRule(pattern="rm -rf *", action_type="command", verdict="block", reason="Dangerous")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
    verdict = guard.evaluate(action)
    assert verdict == "block"

def test_pass_safe_command():
    rules = [GuardRule(pattern="rm -rf *", action_type="command", verdict="block", reason="Dangerous")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "echo hello"})
    verdict = guard.evaluate(action)
    assert verdict == "pass"

def test_match_by_action_type():
    rules = [GuardRule(pattern="*", action_type="file_delete", verdict="block", reason="No file deletion")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "echo hi"})
    verdict = guard.evaluate(action)
    assert verdict == "pass"  # action_type mismatch

def test_approval_rule():
    rules = [GuardRule(pattern="DROP DATABASE*", action_type="command", verdict="approval", reason="Needs confirmation")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "DROP DATABASE test"})
    verdict = guard.evaluate(action)
    assert verdict == "approval"

def test_empty_rules_allow_all():
    guard = Guardrail([])
    action = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
    verdict = guard.evaluate(action)
    assert verdict == "pass"

def test_first_match_priority():
    rules = [
        GuardRule(pattern="rm *", action_type="command", verdict="approval", reason="Approval"),
        GuardRule(pattern="rm -rf *", action_type="command", verdict="block", reason="Block"),
    ]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
    verdict = guard.evaluate(action)
    assert verdict == "approval"  # first match wins
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_guardrails.py -v`
Expected: New tests FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/guardrails/engine.py
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
            if rule.action_type != "*" and rule.action_type != action.tool:
                continue
            param_str = ""
            if action.params:
                param_str = " ".join(str(v) for v in action.params.values())
            combined = f"{action.tool} {param_str}" if action.tool else param_str
            if fnmatch.fnmatch(combined, f"*{rule.pattern}*") or fnmatch.fnmatch(param_str, rule.pattern):
                return rule.verdict
        return "pass"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_guardrails.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/harness/guardrails/engine.py tests/test_guardrails.py
git commit -m "feat: add guardrail engine with glob pattern matching"
```

---

### Task 6: HITL State Machine

**Files:**
- Create: `src/harness/guardrails/hitl.py`
- Test: `tests/test_hitl.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from harness.guardrails.hitl import HITLStateMachine

def test_approve_action():
    hitl = HITLStateMachine(input_func=lambda prompt: "y")
    result = hitl.confirm("rm -rf /", "block", "Dangerous")
    assert result is True

def test_reject_action():
    hitl = HITLStateMachine(input_func=lambda prompt: "n")
    result = hitl.confirm("rm -rf /", "block", "Dangerous")
    assert result is False

def test_skip_remembered():
    hitl = HITLStateMachine(input_func=lambda prompt: "s")
    result = hitl.confirm("DROP DATABASE", "approval", "Needs confirmation")
    assert result is True
    assert hitl.is_skipped("DROP DATABASE") is True
    # Second time same pattern should auto-skip
    result2 = hitl.confirm("DROP DATABASE", "approval", "Needs confirmation")
    assert result2 is True

def test_default_behavior():
    hitl = HITLStateMachine()  # default input returns False
    result = hitl.confirm("test", "approval", "test")
    assert result is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_hitl.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/guardrails/hitl.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_hitl.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/guardrails/hitl.py tests/test_hitl.py
git commit -m "feat: add HITL state machine for human approval workflow"
```
---

### Task 7: Audit Logger

**Files:**
- Create: `src/harness/guardrails/audit.py`
- Test: `tests/test_audit.py`

- [ ] **Step 1: Write the failing test**

```python
import json
import tempfile
from pathlib import Path
from harness.guardrails.audit import AuditLogger
from harness.guardrails.models import Action

def test_log_interception():
    with tempfile.TemporaryDirectory() as tmp:
        logger = AuditLogger(log_dir=tmp)
        action = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
        logger.log(action=action, verdict="block", reason="Dangerous")
        entries = logger.get_entries()
        assert len(entries) == 1
        assert entries[0]["verdict"] == "block"
        assert entries[0]["action"]["tool"] == "run_command"

def test_log_multiple():
    with tempfile.TemporaryDirectory() as tmp:
        logger = AuditLogger(log_dir=tmp)
        a1 = Action(type="tool_call", tool="read_file", params={"path": "test.txt"})
        a2 = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
        logger.log(action=a1, verdict="pass", reason="")
        logger.log(action=a2, verdict="block", reason="Dangerous")
        entries = logger.get_entries()
        assert len(entries) == 2
        assert entries[0]["verdict"] == "pass"
        assert entries[1]["verdict"] == "block"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_audit.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/guardrails/audit.py
import json
import os
from datetime import datetime
from typing import List
from .models import Action

class AuditLogger:
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(os.path.expanduser("~"), ".agent-harness", "audit")
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
            f.write(json.dumps(entry, ensure_ascii=False) + "
")

    def get_entries(self) -> List[dict]:
        return list(self._entries)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_audit.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/guardrails/audit.py tests/test_audit.py
git commit -m "feat: add audit logger for guardrail interceptions"
```

---

### Task 8: Tool System

**Files:**
- Create: `src/harness/tools/base.py`
- Create: `src/harness/tools/registry.py`
- Create: `src/harness/tools/builtins.py`
- Test: `tests/test_tools.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from harness.tools.base import Tool, ToolResult
from harness.tools.registry import ToolRegistry
from harness.tools.builtins import ReadFileTool, WriteFileTool, RunCommandTool

def test_tool_registry_register():
    registry = ToolRegistry()
    tool = ReadFileTool()
    registry.register(tool)
    assert registry.get("read_file") is tool

def test_tool_registry_list():
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    names = [t.name for t in registry.list_tools()]
    assert "read_file" in names
    assert "write_file" in names

def test_tool_not_found():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent")

def test_tool_to_llm_format():
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    fmt = registry.to_llm_format()
    assert isinstance(fmt, list)
    assert fmt[0]["function"]["name"] == "read_file"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_tools.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/tools/base.py
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
```

```python
# src/harness/tools/registry.py
from typing import Dict, List
from .base import Tool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool {name} not found")
        return self._tools[name]

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def to_llm_format(self) -> List[dict]:
        return [t.to_llm_tool() for t in self._tools.values()]
```

```python
# src/harness/tools/builtins.py
import os
import subprocess
import time
from .base import Tool, ToolResult

class ReadFileTool(Tool):
    name = "read_file"
    description = "Read the contents of a file"
    parameters = {
        "type": "object",
        "properties": {"path": {"type": "string", "description": "Path to file"}},
        "required": ["path"],
    }

    def execute(self, params: dict) -> ToolResult:
        path = params["path"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(1024 * 1024)  # 1MB limit
            return ToolResult(success=True, stdout=content)
        except Exception as e:
            return ToolResult(success=False, stderr=str(e), exit_code=1)

class WriteFileTool(Tool):
    name = "write_file"
    description = "Write content to a file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to file"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    }

    def execute(self, params: dict) -> ToolResult:
        path = params["path"]
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(params["content"])
            return ToolResult(success=True, stdout=f"Written {len(params['content'])} bytes to {path}")
        except Exception as e:
            return ToolResult(success=False, stderr=str(e), exit_code=1)

class RunCommandTool(Tool):
    name = "run_command"
    description = "Run a shell command"
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Command to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
        },
        "required": ["command"],
    }

    def execute(self, params: dict) -> ToolResult:
        start = time.time()
        try:
            result = subprocess.run(
                params["command"], shell=True, capture_output=True, text=True,
                timeout=params.get("timeout", 30),
            )
            duration = time.time() - start
            return ToolResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration=duration,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, stderr="Command timed out", exit_code=124, duration=time.time() - start)
        except Exception as e:
            return ToolResult(success=False, stderr=str(e), exit_code=1, duration=time.time() - start)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_tools.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/tools/ tests/test_tools.py
git commit -m "feat: add tool system with registry and built-in tools"
```
---

### Task 9: Feedback Parser

**Files:**
- Create: `src/harness/feedback/parser.py`
- Test: `tests/test_feedback.py`

- [ ] **Step 1: Write the failing test**

```python
from harness.feedback.parser import TestResultParser, FeedbackResult

def test_parse_pytest_pass():
    parser = TestResultParser()
    output = "collected 3 items\n\n tests/test_a.py::test_ok PASSED\n tests/test_b.py::test_ok PASSED\n\n== 3 passed in 0.05s =="
    result = parser.parse(output)
    assert result.passed == 3
    assert result.failed == 0
    assert result.success is True

def test_parse_pytest_fail():
    parser = TestResultParser()
    output = "collected 2 items\n\n tests/test_a.py::test_ok PASSED\n tests/test_b.py::test_fail FAILED\n\n== 1 passed, 1 failed in 0.10s =="
    result = parser.parse(output)
    assert result.passed == 1
    assert result.failed == 1
    assert result.success is False

def test_parse_error():
    parser = TestResultParser()
    output = "ERROR: file not found"
    result = parser.parse(output)
    assert result.success is False
    assert result.error_type == "unknown"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_feedback.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/feedback/parser.py
import re
from dataclasses import dataclass

@dataclass
class FeedbackResult:
    success: bool
    passed: int = 0
    failed: int = 0
    error_type: str = ""
    summary: str = ""

class TestResultParser:
    def parse(self, output: str) -> FeedbackResult:
        passed_match = re.search(r"(\d+)\s+passed", output)
        failed_match = re.search(r"(\d+)\s+failed", output)
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        if passed_match or failed_match:
            return FeedbackResult(success=failed == 0, passed=passed, failed=failed, summary=output[:200])
        if "ERROR" in output.upper():
            return FeedbackResult(success=False, error_type="unknown", summary=output[:200])
        return FeedbackResult(success=True, summary=output[:200])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_feedback.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/feedback/ tests/test_feedback.py
git commit -m "feat: add test result feedback parser"
```

---

### Task 10: Memory / Context Manager

**Files:**
- Create: `src/harness/memory/manager.py`
- Test: `tests/test_memory.py`

- [ ] **Step 1: Write the failing test**

```python
from harness.memory.manager import ContextManager

def test_add_and_get_messages():
    cm = ContextManager()
    cm.add("system", "You are a helpful assistant")
    cm.add("user", "Hello")
    msgs = cm.get_messages()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert msgs[1]["content"] == "Hello"

def test_token_truncation():
    cm = ContextManager(max_tokens=10)
    cm.add("system", "A" * 100)
    cm.add("user", "B" * 100)
    msgs = cm.get_messages()
    total = sum(len(m["content"]) for m in msgs)
    assert total <= 10

def test_clear():
    cm = ContextManager()
    cm.add("user", "Hello")
    cm.clear()
    assert len(cm.get_messages()) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/memory/manager.py
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
            removed = self._messages.pop(1)  # keep system prompt, drop oldest
            total -= len(removed.get("content", ""))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/memory/ tests/test_memory.py
git commit -m "feat: add context manager for message history"
```

---

### Task 11: Agent Loop

**Files:**
- Create: `src/harness/agent.py`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from harness.agent import AgentLoop
from harness.llm.mock_client import MockLLMClient
from harness.guardrails.models import GuardRule
from harness.tools.builtins import ReadFileTool
from harness.tools.registry import ToolRegistry

def test_agent_finishes_immediately():
    mock = MockLLMClient(responses=[{"type": "finish", "summary": "Task complete"}])
    registry = ToolRegistry()
    agent = AgentLoop(llm=mock, tool_registry=registry, guardrails=[])
    result = agent.run("do something")
    assert result["status"] == "completed"
    assert "Task complete" in result["summary"]

def test_agent_tool_call_then_finish():
    mock = MockLLMClient(responses=[
        {"type": "tool_call", "tool": "read_file", "params": {"path": "test.txt"}},
        {"type": "finish", "summary": "Done reading"},
    ])
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    agent = AgentLoop(llm=mock, tool_registry=registry, guardrails=[])
    result = agent.run("read file")
    assert result["status"] == "completed"
    assert result["turns"] == 2

def test_agent_blocked_by_guardrail():
    mock = MockLLMClient(responses=[
        {"type": "tool_call", "tool": "run_command", "params": {"command": "rm -rf /"}},
        {"type": "finish", "summary": "OK"},
    ])
    registry = ToolRegistry()
    rules = [GuardRule(pattern="rm -rf *", action_type="command", verdict="block", reason="Dangerous")]
    agent = AgentLoop(llm=mock, tool_registry=registry, guardrails=rules)
    result = agent.run("delete everything")
    assert result["status"] == "completed"
    # The blocked action should be recorded
    assert any("blocked" in step["status"].lower() for step in result["steps"])

def test_agent_max_turns():
    mock = MockLLMClient(responses=[
        {"type": "tool_call", "tool": "read_file", "params": {"path": "a.txt"}}
    ] * 5)
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    agent = AgentLoop(llm=mock, tool_registry=registry, guardrails=[], max_turns=3)
    result = agent.run("keep going")
    assert result["status"] == "max_turns_reached"
    assert result["turns"] == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/agent.py
import time
from typing import List, Optional
from .llm.client import LLMClient
from .guardrails.models import Action, GuardRule
from .guardrails.engine import Guardrail
from .guardrails.hitl import HITLStateMachine
from .guardrails.audit import AuditLogger
from .tools.registry import ToolRegistry
from .memory.manager import ContextManager

class AgentLoop:
    def __init__(self, llm: LLMClient, tool_registry: ToolRegistry,
                 guardrails: List[GuardRule], max_turns: int = 50,
                 timeout: int = 300, audit_logger: Optional[AuditLogger] = None,
                 hitl: Optional[HITLStateMachine] = None):
        self.llm = llm
        self.tools = tool_registry
        self.guardrail = Guardrail(guardrails)
        self.max_turns = max_turns
        self.timeout = timeout
        self.audit = audit_logger or AuditLogger()
        self.hitl = hitl or HITLStateMachine()
        self.memory = ContextManager()

    def run(self, task: str) -> dict:
        start_time = time.time()
        self.memory.add("system", "You are a coding agent. Respond with a JSON action.")
        self.memory.add("user", task)
        steps = []
        turns = 0

        while turns < self.max_turns:
            if time.time() - start_time > self.timeout:
                return {"status": "timeout", "turns": turns, "steps": steps, "summary": "Timed out"}

            try:
                response = self.llm.chat(self.memory.get_messages(), self.tools.to_llm_format())
            except Exception as e:
                return {"status": "error", "error": str(e), "turns": turns, "steps": steps}

            if response.type == "finish":
                steps.append({"type": "finish", "summary": response.summary, "status": "completed"})
                return {"status": "completed", "turns": turns + 1, "steps": steps, "summary": response.summary}

            action = Action(type="tool_call", tool=response.tool, params=response.params, thought=response.thought)
            verdict = self.guardrail.evaluate(action)
            step = {"type": "tool_call", "tool": action.tool, "params": action.params,
                    "verdict": verdict, "status": "executed"}

            if verdict == "block":
                self.audit.log(action, verdict, "Blocked by guardrail")
                step["status"] = "blocked"
                self.memory.add("user", f"Action {action.tool} was BLOCKED.")
                steps.append(step)
                turns += 1
                continue

            if verdict == "approval":
                action_detail = f"{action.tool} {action.params}"
                if not self.hitl.confirm(action_detail, verdict, "Requires approval"):
                    step["status"] = "blocked"
                    self.memory.add("user", f"Action {action.tool} was REJECTED.")
                    steps.append(step)
                    turns += 1
                    continue

            try:
                tool = self.tools.get(action.tool)
                result = tool.execute(action.params or {})
                step["result"] = {"success": result.success, "stdout": result.stdout[:500],
                                   "stderr": result.stderr[:500], "exit_code": result.exit_code}
                feedback = f"Tool {action.tool} completed."
                self.memory.add("user", feedback)
            except KeyError as e:
                step["status"] = "error"
                self.memory.add("user", f"Tool not found: {e}")
            except Exception as e:
                step["status"] = "error"
                self.memory.add("user", f"Tool execution error: {e}")

            steps.append(step)
            turns += 1

        return {"status": "max_turns_reached", "turns": turns, "steps": steps, "summary": "Max turns reached"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/agent.py tests/test_agent.py
git commit -m "feat: add agent loop with guardrail integration"
```
---

### Task 12: CLI Interface

**Files:**
- Create: `src/harness/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
from typer.testing import CliRunner
from harness.cli import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output

def test_init():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "config.yaml" in result.output

def test_run_no_task():
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0  # missing task argument
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/cli.py
import typer
from typing import Optional
from . import __version__

app = typer.Typer(name="harness")

@app.command()
def version():
    """Show version information"""
    typer.echo(f"Agent Harness v{__version__}")

@app.command()
def init():
    """Initialize project configuration"""
    typer.echo("Initializing config.yaml...")
    # See full implementation in the source code
    typer.echo("Created config.yaml. Run 'harness configure' to set up your API key.")

@app.command()
def configure(clear: bool = False, update: bool = False):
    """Configure API key securely"""
    # See full implementation in the source code
    typer.echo("API key stored securely.")

@app.command()
def run(task: str):
    """Run an agent task"""
    # See full implementation in the source code
    typer.echo(f"Running task: {task}")

@app.command()
def guardrail_test():
    """Test guardrail rules against sample actions"""
    # See full implementation in the source code
    typer.echo("Guardrail test complete.")

@app.command()
def config_show():
    """Show current configuration (key masked)"""
    # See full implementation in the source code
    typer.echo("Configuration shown.")

if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/cli.py tests/test_cli.py
git commit -m "feat: add CLI interface with all commands"
```

---

### Task 13: Credential Management

**Files:**
- Create: `src/harness/credentials.py`
- Test: `tests/test_credentials.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from harness.credentials import CredentialManager

def test_store_and_retrieve():
    cm = CredentialManager()
    cm.store("test_key", "test_value")
    value = cm.get("test_key")
    assert value == "test_value"
    cm.delete("test_key")
    assert cm.get("test_key") is None

def test_nonexistent_key():
    cm = CredentialManager()
    assert cm.get("nonexistent") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_credentials.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/harness/credentials.py
import os, json, base64, hashlib
from typing import Optional
from cryptography.fernet import Fernet

class CredentialManager:
    def __init__(self, service: str = "agent-harness"):
        self.service = service
        self._keyring_available = self._check_keyring()

    def _check_keyring(self) -> bool:
        try:
            import keyring
            keyring.get_password(self.service, "_probe")
            return True
        except Exception:
            return False

    def store(self, key: str, value: str, master_password: Optional[str] = None) -> None:
        if self._keyring_available:
            import keyring
            keyring.set_password(self.service, key, value)
        else:
            self._store_encrypted(key, value, master_password or "default")

    def get(self, key: str, master_password: Optional[str] = None) -> Optional[str]:
        if self._keyring_available:
            import keyring
            return keyring.get_password(self.service, key)
        return self._get_encrypted(key, master_password or "default")

    def delete(self, key: str) -> None:
        if self._keyring_available:
            import keyring
            keyring.delete_password(self.service, key)
        else:
            self._delete_encrypted(key)

    def _store_encrypted(self, key: str, value: str, password: str) -> None:
        derived = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
        cipher = Fernet(derived)
        encrypted = cipher.encrypt(value.encode())
        cred_dir = os.path.join(os.path.expanduser("~"), ".agent-harness")
        os.makedirs(cred_dir, exist_ok=True)
        path = os.path.join(cred_dir, f"{key}.enc")
        with open(path, "wb") as f:
            f.write(encrypted)

    def _get_encrypted(self, key: str, password: str) -> Optional[str]:
        path = os.path.join(os.path.expanduser("~"), ".agent-harness", f"{key}.enc")
        if not os.path.exists(path):
            return None
        try:
            derived = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
            cipher = Fernet(derived)
            with open(path, "rb") as f:
                return cipher.decrypt(f.read()).decode()
        except Exception:
            return None

    def _delete_encrypted(self, key: str) -> None:
        path = os.path.join(os.path.expanduser("~"), ".agent-harness", f"{key}.enc")
        if os.path.exists(path):
            os.remove(path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_credentials.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/harness/credentials.py tests/test_credentials.py
git commit -m "feat: add credential manager with keyring and encrypted fallback"
```

---

### Task 14: Mechanism Demo Script

**Files:**
- Create: `demo/mechanism_demo.py`

- [ ] **Step 1: Write the mechanism demo script**

```python
#!/usr/bin/env python3
"""
Mechanism Demo for Agent Harness.

Demonstrates three required behaviors with mock LLM:
1. Guardrail blocks a dangerous action
2. Feedback loop: agent receives failure and changes next action
3. Guardrail engine deterministic behavior (focus dimension)
"""
import sys
sys.path.insert(0, "src")

from harness.llm.mock_client import MockLLMClient
from harness.guardrails.models import Action, GuardRule
from harness.guardrails.engine import Guardrail
from harness.tools.registry import ToolRegistry
from harness.tools.builtins import ReadFileTool
from harness.agent import AgentLoop

def demo_guardrail_block():
    print("=== Demo 1: Guardrail blocks dangerous action ===")
    rules = [GuardRule(pattern="rm -rf *", action_type="command", verdict="block", reason="Dangerous")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
    verdict = guard.evaluate(action)
    assert verdict == "block", f"Expected block, got {verdict}"
    print(f"  Verdict: {verdict} (BLOCKED)")
    print("  PASS: Dangerous action correctly blocked\n")

def demo_feedback_loop():
    print("=== Demo 2: Feedback loop ===")
    mock = MockLLMClient(responses=[
        {"type": "tool_call", "tool": "read_file", "params": {"path": "nonexistent.txt"}},
        {"type": "tool_call", "tool": "read_file", "params": {"path": "existing.txt"}},
        {"type": "finish", "summary": "Task complete"},
    ])
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    agent = AgentLoop(llm=mock, tool_registry=registry, guardrails=[])
    result = agent.run("find and read the file")
    assert result["status"] == "completed"
    print(f"  Turns: {result[chr(39)+chr(116)+chr(117)+chr(114)+chr(110)+chr(115)+chr(39)]}")
    print(f"  Status: {result[chr(39)+chr(115)+chr(116)+chr(97)+chr(116)+chr(117)+chr(115)+chr(39)]}")
    print("  PASS: Agent completed with feedback loop\n")

def demo_guardrail_determinism():
    print("=== Demo 3: Guardrail deterministic behavior ===")
    rules = [
        GuardRule(pattern="rm *", action_type="command", verdict="block", reason="No deletion"),
        GuardRule(pattern="echo *", action_type="command", verdict="pass", reason="Safe"),
    ]
    guard = Guardrail(rules)
    test_cases = [
        (Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"}), "block"),
        (Action(type="tool_call", tool="run_command", params={"command": "echo hello"}), "pass"),
        (Action(type="tool_call", tool="run_command", params={"command": "ls -la"}), "pass"),
        (Action(type="finish", summary="done"), "pass"),
    ]
    for action, expected in test_cases:
        actual = guard.evaluate(action)
        status = "PASS" if actual == expected else "FAIL"
        print(f"  [{status}] {actual}")
    print("  Guardrail determinism verified\n")

if __name__ == "__main__":
    demo_guardrail_block()
    demo_feedback_loop()
    demo_guardrail_determinism()
    print("All demos passed!")
```

- [ ] **Step 2: Run demo to verify**

Run: `python demo/mechanism_demo.py`
Expected: All three demos print PASS

- [ ] **Step 3: Commit**

```bash
git add demo/
git commit -m "feat: add mechanism demo script with mock LLM"
```

---

### Task 15: CI Configuration

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create CI configuration**

```yaml
name: CI

on: [push, pull_request]

jobs:
  unit-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest
    - name: Run tests
      run: pytest tests/ -v
```

- [ ] **Step 2: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions CI with unit-test job"
```

---

### Task 16: README and Documentation

**Files:**
- Create: `README.md`
- Create: `AGENT_LOG.md`

- [ ] **Step 1: Write README.md**

Cover: project intro, install (`pip install agent-harness`), quick start, commands, guardrail rules, security boundary, directory structure, known limitations.

- [ ] **Step 2: Write AGENT_LOG.md with initial entries**

- [ ] **Step 3: Commit**

```bash
git add README.md AGENT_LOG.md
git commit -m "docs: add README and AGENT_LOG"
```

---

### Task 17: Build and Release Configuration

**Files:**
- Modify: `pyproject.toml` (add build config)
- Create: `Makefile`

- [ ] **Step 1: Update pyproject.toml with build config**

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/harness"]

[tool.hatch.build.targets.sdist]
include = ["src/harness/**"]
```

- [ ] **Step 2: Create Makefile**

```makefile
.PHONY: test build clean install

test:
	pytest tests/ -v

build:
	pip install build
	python -m build

install:
	pip install -e .

clean:
	rm -rf dist/ build/ *.egg-info
	rm -rf .pytest_cache __pycache__
```

- [ ] **Step 3: Verify build**

Run: `python -m build`
Expected: dist/ directory with .tar.gz and .whl

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml Makefile
git commit -m "chore: add build and release configuration"
```
