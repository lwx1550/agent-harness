from harness.guardrails.hitl import HITLStateMachine


def test_approve_action():
    hitl = HITLStateMachine(input_func=lambda prompt: "y")
    result = hitl.confirm("rm -rf /", "approval", "Dangerous")
    assert result is True


def test_reject_action():
    hitl = HITLStateMachine(input_func=lambda prompt: "n")
    result = hitl.confirm("rm -rf /", "approval", "Dangerous")
    assert result is False


def test_skip_remembered():
    hitl = HITLStateMachine(input_func=lambda prompt: "s")
    result = hitl.confirm("DROP DATABASE", "approval", "Needs confirmation")
    assert result is True
    assert hitl.is_skipped("DROP DATABASE") is True
    result2 = hitl.confirm("DROP DATABASE", "approval", "Needs confirmation")
    assert result2 is True


def test_non_approval_skips_hitl():
    hitl = HITLStateMachine()
    result = hitl.confirm("test", "block", "test")
    assert result is True  # non-approval verdicts pass through


def test_default_behavior():
    hitl = HITLStateMachine()
    result = hitl.confirm("test", "approval", "test")
    assert result is False
