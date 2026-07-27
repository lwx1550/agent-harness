import tempfile
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
