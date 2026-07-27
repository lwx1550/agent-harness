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


# --- Task 5: Guardrail Engine tests ---

from harness.guardrails.engine import Guardrail


def test_block_dangerous_command():
    rules = [GuardRule(pattern="rm -rf *", action_type="run_command", verdict="block", reason="Dangerous")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
    verdict = guard.evaluate(action)
    assert verdict == "block"


def test_pass_safe_command():
    rules = [GuardRule(pattern="rm -rf *", action_type="run_command", verdict="block", reason="Dangerous")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "echo hello"})
    verdict = guard.evaluate(action)
    assert verdict == "pass"


def test_match_by_action_type():
    rules = [GuardRule(pattern="*", action_type="file_delete", verdict="block", reason="No file deletion")]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "echo hi"})
    verdict = guard.evaluate(action)
    assert verdict == "pass"


def test_approval_rule():
    rules = [GuardRule(pattern="DROP DATABASE*", action_type="run_command", verdict="approval", reason="Needs confirmation")]
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
        GuardRule(pattern="rm *", action_type="run_command", verdict="approval", reason="Approval"),
        GuardRule(pattern="rm -rf *", action_type="run_command", verdict="block", reason="Block"),
    ]
    guard = Guardrail(rules)
    action = Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"})
    verdict = guard.evaluate(action)
    assert verdict == "approval"
