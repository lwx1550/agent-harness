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
