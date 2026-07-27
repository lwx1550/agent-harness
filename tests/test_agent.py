from harness.agent import AgentLoop
from harness.llm.mock_client import MockLLMClient
from harness.guardrails.models import GuardRule
from harness.tools.builtins import ReadFileTool, RunCommandTool
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
    registry.register(RunCommandTool())
    rules = [GuardRule(pattern="rm -rf *", action_type="run_command", verdict="block", reason="Dangerous")]
    agent = AgentLoop(llm=mock, tool_registry=registry, guardrails=rules)
    result = agent.run("delete everything")
    assert result["status"] == "completed"
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
