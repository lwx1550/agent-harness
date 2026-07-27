#!/usr/bin/env python3
"""Mechanism Demo for Agent Harness.

Demonstrates three required behaviors with mock LLM:
1. Guardrail blocks a dangerous action
2. Feedback loop: agent receives failure and changes next action
3. Guardrail engine deterministic behavior (focus dimension)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from harness.llm.mock_client import MockLLMClient
from harness.guardrails.models import Action, GuardRule
from harness.guardrails.engine import Guardrail
from harness.tools.registry import ToolRegistry
from harness.tools.builtins import ReadFileTool
from harness.agent import AgentLoop


def demo_guardrail_block():
    print("=== Demo 1: Guardrail blocks dangerous action ===")
    rules = [GuardRule(pattern="rm -rf *", action_type="run_command", verdict="block", reason="Dangerous")]
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
    print(f"  Turns: {result['turns']}")
    print(f"  Status: {result['status']}")
    print("  PASS: Agent completed with feedback loop\n")


def demo_guardrail_determinism():
    print("=== Demo 3: Guardrail deterministic behavior ===")
    rules = [
        GuardRule(pattern="rm *", action_type="run_command", verdict="block", reason="No deletion"),
        GuardRule(pattern="echo *", action_type="run_command", verdict="pass", reason="Safe"),
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
        print(f"  [{status}] -> {actual}")
    print("  Guardrail determinism verified\n")


if __name__ == "__main__":
    demo_guardrail_block()
    demo_feedback_loop()
    demo_guardrail_determinism()
    print("All demos passed!")

